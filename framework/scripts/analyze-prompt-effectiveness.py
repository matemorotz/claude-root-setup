#!/usr/bin/env python3
"""
analyze-prompt-effectiveness.py — Semantic analysis of which seed rules and agent
system prompts were useful, ignored, or contradicting in a completed session.

Uses a Haiku API call to evaluate the prompt stack against what actually happened.
Runs ONLY when learning mode is on (automatic hook) or learn-session skill is invoked.

Usage:
    analyze-prompt-effectiveness.py <jsonl_file>
        --rules-dir  <seeds/workflows/{workflow}/>
        --agents-dir <.claude/agents/>
        [--output    <path>]
        [--model     claude-haiku-4-5-20251001]
        [--dry-run]
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path
from typing import Optional


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("jsonl", help="Session JSONL file")
    p.add_argument("--rules-dir", required=True,
                   help="Path to seeds/workflows/{workflow}/")
    p.add_argument("--agents-dir", required=True,
                   help="Path to .claude/agents/")
    p.add_argument("--output", "-o", default=None, help="Output JSON path")
    p.add_argument("--model", default="claude-haiku-4-5-20251001",
                   help="Anthropic model for analysis")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the analysis prompt without calling the API")
    return p.parse_args()


# ── JSONL parsing ─────────────────────────────────────────────────────────────

def load_jsonl(path: str) -> list[dict]:
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def get_session_id(events: list[dict]) -> str:
    for e in events:
        sid = e.get("sessionId", "")
        if sid:
            return sid
    return "unknown"


def extract_task_summary(events: list[dict], max_msgs: int = 3) -> str:
    msgs = []
    for e in events:
        if e.get("type") != "user":
            continue
        content = e.get("message", {}).get("content", "")
        text = ""
        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "").strip()
                    break
        if text:
            msgs.append(text[:400])
        if len(msgs) >= max_msgs:
            break
    return "\n".join(msgs) if msgs else "(no user messages found)"


def extract_solution_summary(events: list[dict], max_msgs: int = 2) -> str:
    assistant_texts: list[str] = []
    tool_summaries: list[str] = []

    for e in reversed(events):
        if e.get("type") != "assistant":
            continue
        content = e.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")
            if btype == "text":
                text = block.get("text", "").strip()
                if text and len(assistant_texts) < max_msgs:
                    assistant_texts.append(text[:600])
            elif btype == "tool_use":
                name = block.get("name", "")
                inp = block.get("input", {})
                if name == "Write":
                    tool_summaries.append(f"Wrote: {inp.get('file_path', '?')}")
                elif name == "Edit":
                    tool_summaries.append(f"Edited: {inp.get('file_path', '?')}")
                elif name == "Bash":
                    cmd = inp.get("command", "")[:120]
                    tool_summaries.append(f"Ran: {cmd}")
        if len(assistant_texts) >= max_msgs:
            break

    parts = []
    if assistant_texts:
        parts.append("Assistant summary:\n" + "\n".join(reversed(assistant_texts)))
    if tool_summaries:
        parts.append("Key actions:\n" + "\n".join(tool_summaries[:10]))
    return "\n\n".join(parts) if parts else "(no solution found)"


def find_involved_agents(events: list[dict]) -> list[str]:
    agents: set[str] = set()
    for e in events:
        if e.get("type") != "assistant":
            continue
        content = e.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if (isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") == "Agent"):
                subtype = block.get("input", {}).get("subagent_type", "")
                if subtype:
                    agents.add(subtype)
    return sorted(agents)


# ── Agent .md loading ──────────────────────────────────────────────────────────

def _find_agent_file(agents_dir: str, agent_name: str) -> Optional[str]:
    base = Path(agents_dir)
    if not base.exists():
        return None
    norm = agent_name.lower().replace("-", "").replace("_", "")

    # Direct .md match
    for md in base.rglob("*.md"):
        stem = md.stem.lower().replace("-", "").replace("_", "")
        if stem == norm or norm in stem or stem in norm:
            return str(md)
    # agent.md inside a subdirectory named like the agent
    for agent_md in base.rglob("agent.md"):
        parent = agent_md.parent.name.lower().replace("-", "").replace("_", "")
        if parent == norm or norm in parent or parent in norm:
            return str(agent_md)
    return None


def load_agent_prompts(agents_dir: str, agent_names: list[str]) -> dict[str, str]:
    prompts: dict[str, str] = {}
    for name in agent_names:
        path = _find_agent_file(agents_dir, name)
        if path:
            try:
                raw = Path(path).read_text()
                # Strip YAML frontmatter
                if raw.startswith("---"):
                    parts = raw.split("---", 2)
                    raw = parts[2].strip() if len(parts) >= 3 else raw
                prompts[name] = raw[:2000]
            except Exception:
                prompts[name] = "(could not read agent file)"
        else:
            prompts[name] = "(agent file not found in agents-dir)"
    return prompts


# ── Seed rule loading ─────────────────────────────────────────────────────────

def load_seed_rules(rules_dir: str) -> dict[str, str]:
    rules: dict[str, str] = {}
    rpath = Path(rules_dir)
    if not rpath.exists():
        return rules
    for f in rpath.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            rule_id = data.get("id", f.stem)
            goal = data.get("goal", "")
            rule = data.get("rule", "")
            rules[rule_id] = f"Goal: {goal}\nRule: {rule}" if goal else rule
        except Exception:
            continue
    return rules


# ── Analysis prompt ───────────────────────────────────────────────────────────

def build_prompt(task: str, solution: str,
                 agent_prompts: dict[str, str],
                 seed_rules: dict[str, str]) -> str:
    lines = [
        "You are evaluating a completed Claude Code session to improve future prompt effectiveness.",
        "",
        "=== TASK (what the user asked for) ===",
        task,
        "",
        "=== SOLUTION (what actually happened) ===",
        solution,
        "",
    ]

    if agent_prompts:
        lines += ["=== AGENTS INVOLVED — their system prompts ==="]
        for name, prompt in agent_prompts.items():
            lines += [f"\n[{name}]:", prompt[:1500], ""]

    if seed_rules:
        lines += ["=== ACTIVE SEED RULES ==="]
        for rule_id, rule_text in seed_rules.items():
            lines += [f"\n[{rule_id}]:", rule_text, ""]

    lines += [
        "=== YOUR TASK ===",
        "Respond ONLY with valid JSON (no markdown fences, no explanation).",
        "",
        "For each agent prompt section and each seed rule classify as:",
        "  used_useful   — was relevant and applied during this task",
        "  ignored       — loaded but irrelevant to this task",
        "  contradicting — conflicted with another rule/prompt or caused confusion",
        "",
        "Use this exact JSON structure:",
        """{
  "agent_prompt_analysis": {
    "<agent_name>": {
      "used_useful": ["<section or description>"],
      "ignored": ["<section or description>"],
      "contradicting": [
        {"item": "<description>", "conflicts_with": "<other>", "issue": "<why>"}
      ]
    }
  },
  "seed_rules_analysis": {
    "used_useful":   [{"id": "<rule_id>", "reason": "<why relevant>"}],
    "ignored":       [{"id": "<rule_id>", "reason": "<why irrelevant>"}],
    "contradicting": [{"id": "<rule_id>", "conflicts_with": "<id>", "issue": "<what conflicts>"}]
  },
  "optimal_prompt_section": {
    "seed_rules": [
      {"id": "<rule_id>", "refined_rule": "<improved or unchanged rule text>"}
    ],
    "agent_guidance": {
      "<agent_name>": "<specific change: add/remove/refocus this section>"
    }
  },
  "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"],
  "confidence": 0.0
}""",
    ]

    return "\n".join(lines)


# ── API call ──────────────────────────────────────────────────────────────────

def call_api(prompt: str, model: str) -> dict:
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic package not installed — run: pip install anthropic"}

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY environment variable not set"}

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Strip markdown fences if model wrapped the JSON
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)

    return json.loads(text)


# ── Improvements extractor ────────────────────────────────────────────────────

def extract_improvements_patterns(analysis: dict) -> Optional[dict]:
    """
    If analysis has high confidence and refined rules, produce a pattern-adapter
    format dict that rule-distiller.py can ingest to update existing rules.
    """
    confidence = analysis.get("confidence", 0.0)
    refined = analysis.get("optimal_prompt_section", {}).get("seed_rules", [])
    if not refined or confidence < 0.7:
        return None

    patterns = []
    for rule in refined:
        refined_text = rule.get("refined_rule", "")
        if not refined_text:
            continue
        patterns.append({
            "name": rule.get("id", "refined_rule"),
            "description": refined_text,
            "confidence": min(0.90, confidence),
            "evidence": ["prompt_effectiveness_analysis"],
            "metadata": {
                "source": "prompt_effectiveness",
                "original_id": rule.get("id"),
            },
        })

    if not patterns:
        return None

    return {
        "patterns": {
            "architectural": [],
            "coding": patterns,
            "testing": [],
            "tooling": [],
            "orchestration": [],
        },
        "statistics": {
            "total_patterns": len(patterns),
            "source": "prompt_effectiveness",
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    events = load_jsonl(args.jsonl)
    session_id = get_session_id(events)

    task_summary = extract_task_summary(events)
    solution_summary = extract_solution_summary(events)
    involved_agents = find_involved_agents(events)
    agent_prompts = load_agent_prompts(args.agents_dir, involved_agents)
    seed_rules = load_seed_rules(args.rules_dir)

    if not seed_rules and not agent_prompts:
        _write(args.output, {
            "session_id": session_id,
            "involved_agents": involved_agents,
            "error": "No seed rules or agent prompts found to analyze",
        })
        return

    prompt = build_prompt(task_summary, solution_summary, agent_prompts, seed_rules)

    if args.dry_run:
        print("=== DRY RUN — prompt sent to model ===")
        print(prompt)
        return

    analysis = call_api(prompt, args.model)

    if "error" in analysis:
        _write(args.output, {
            "session_id": session_id,
            "involved_agents": involved_agents,
            "task_summary": task_summary[:200],
            "error": analysis["error"],
        })
        return

    # Enrich with metadata not included in the model response
    analysis["session_id"] = session_id
    analysis["task_summary"] = task_summary[:200]
    analysis["involved_agents"] = involved_agents

    _write(args.output, analysis)

    # Write improvements file alongside output for rule-distiller
    improvements = extract_improvements_patterns(analysis)
    if improvements and args.output:
        imp_path = args.output.replace(".json", "_improvements.json")
        Path(imp_path).write_text(json.dumps(improvements, indent=2))


def _write(output_path: Optional[str], data: dict) -> None:
    text = json.dumps(data, indent=2)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
