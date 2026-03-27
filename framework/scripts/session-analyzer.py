#!/usr/bin/env python3
"""
session-analyzer.py — Extract patterns from Claude Code session JSONL logs.

Reads a session JSONL file and produces pattern-adapter format output
compatible with rule-distiller.py.

Usage:
    session-analyzer.py <jsonl_file> [--output <path>] [--min-turns <N>]
"""

import json
import sys
import argparse
import re
from pathlib import Path
from collections import Counter
from typing import Optional


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract patterns from session JSONL")
    p.add_argument("jsonl", help="Path to session JSONL file")
    p.add_argument("--output", "-o", default=None, help="Output path (default: stdout)")
    p.add_argument("--min-turns", type=int, default=3,
                   help="Minimum turns to analyze (default: 3)")
    return p.parse_args()


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


def count_turns(events: list[dict]) -> int:
    return sum(1 for e in events if e.get("type") in ("user", "assistant"))


def extract_tool_calls(events: list[dict]) -> list[dict]:
    """Extract all tool_use blocks from assistant messages."""
    tool_calls = []
    for event in events:
        if event.get("type") != "assistant":
            continue
        content = event.get("message", {}).get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_calls.append({
                        "name": block.get("name", ""),
                        "input": block.get("input", {}),
                        "id": block.get("id", ""),
                        "timestamp": event.get("timestamp", ""),
                    })
    return tool_calls


def extract_tool_results(events: list[dict]) -> dict:
    """Map tool_use_id → {content, is_error}."""
    results: dict = {}

    def _check_content(content_list: list) -> None:
        for block in content_list:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                tid = block.get("tool_use_id", "")
                if tid:
                    results[tid] = {
                        "content": block.get("content", ""),
                        "is_error": block.get("is_error", False),
                    }

    for event in events:
        # Direct user messages (tool results arrive as user turn)
        if event.get("type") == "user":
            content = event.get("message", {}).get("content", [])
            if isinstance(content, list):
                _check_content(content)
        # Nested in progress/agent events
        data = event.get("data", {})
        if data.get("type") == "agent_progress":
            inner = data.get("message", {}).get("message", {}).get("content", [])
            if isinstance(inner, list):
                _check_content(inner)

    return results


# ── Pattern extractors ────────────────────────────────────────────────────────

def analyze_file_patterns(tool_calls: list[dict]) -> dict:
    file_paths: list[str] = []
    extensions: Counter = Counter()
    directories: Counter = Counter()
    name_patterns = {"snake_case": 0, "camelCase": 0, "PascalCase": 0, "kebab-case": 0}

    for tc in tool_calls:
        if tc["name"] not in ("Write", "Edit"):
            continue
        fp = tc["input"].get("file_path") or tc["input"].get("path") or ""
        if not fp:
            continue
        file_paths.append(fp)
        p = Path(fp)
        ext = p.suffix.lower()
        if ext:
            extensions[ext] += 1
        parts = p.parts
        if len(parts) > 1:
            directories[parts[-2]] += 1
        name = p.stem
        if re.match(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$", name):
            name_patterns["snake_case"] += 1
        elif re.match(r"^[a-z][a-zA-Z0-9]+$", name):
            name_patterns["camelCase"] += 1
        elif re.match(r"^[A-Z][a-zA-Z0-9]+$", name):
            name_patterns["PascalCase"] += 1
        elif re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$", name):
            name_patterns["kebab-case"] += 1

    return {
        "file_paths": file_paths,
        "extensions": dict(extensions),
        "directories": dict(directories),
        "name_patterns": name_patterns,
    }


def analyze_bash_patterns(tool_calls: list[dict], tool_results: dict) -> dict:
    all_cmds: list[str] = []
    successful: list[str] = []
    failed: list[str] = []

    for tc in tool_calls:
        if tc["name"] != "Bash":
            continue
        cmd = tc["input"].get("command", "").strip()
        if not cmd:
            continue
        all_cmds.append(cmd)
        result = tool_results.get(tc["id"], {})
        if result.get("is_error"):
            failed.append(cmd)
        else:
            successful.append(cmd)

    base_cmds: Counter = Counter()
    for cmd in successful:
        base = cmd.split()[0] if cmd.split() else ""
        if base:
            base_cmds[base] += 1

    test_runner: Optional[str] = None
    for cmd in all_cmds:
        if "pytest" in cmd:
            test_runner = "pytest"
            break
        if "jest" in cmd:
            test_runner = "jest"
            break
        if re.search(r"\bnpm test\b|\byarn test\b", cmd):
            test_runner = "npm/yarn test"
            break

    pkg_manager: Optional[str] = None
    for cmd in all_cmds:
        first = cmd.split()[0] if cmd.split() else ""
        if first in ("pip", "pip3"):
            pkg_manager = "pip"
            break
        if first == "npm":
            pkg_manager = "npm"
            break
        if first == "yarn":
            pkg_manager = "yarn"
            break

    return {
        "total_commands": len(all_cmds),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "base_commands": dict(base_cmds.most_common(10)),
        "test_runner": test_runner,
        "package_manager": pkg_manager,
        "successful_samples": successful[:8],
    }


def analyze_agent_patterns(tool_calls: list[dict]) -> dict:
    subagent_types: Counter = Counter()
    task_samples: list[dict] = []

    for tc in tool_calls:
        if tc["name"] != "Agent":
            continue
        subtype = tc["input"].get("subagent_type", "general-purpose")
        subagent_types[subtype] += 1
        desc = tc["input"].get("description", "")
        if desc and len(task_samples) < 5:
            task_samples.append({"type": subtype, "description": desc})

    return {
        "subagent_types": dict(subagent_types),
        "total_agent_calls": sum(subagent_types.values()),
        "task_samples": task_samples,
    }


# ── Pattern → output builder ──────────────────────────────────────────────────

def _conf(count: int, max_count: int = 5) -> float:
    """Map occurrence count to confidence score."""
    if count >= 3:
        return 0.82
    if count >= 2:
        return 0.65
    return 0.45


def build_output(file_a: dict, bash_a: dict, agent_a: dict) -> dict:
    architectural: list = []
    coding: list = []
    testing: list = []
    tooling: list = []
    orchestration: list = []

    # Directory structure
    dirs = file_a["directories"]
    if dirs:
        top = sorted(dirs.items(), key=lambda x: x[1], reverse=True)[:5]
        architectural.append({
            "name": "directory_structure",
            "description": f"Top directories: {', '.join(d for d, _ in top)}",
            "confidence": _conf(sum(dirs.values()), 10),
            "evidence": [f"{d}/ ({c} files)" for d, c in top],
            "metadata": {"directories": dict(top)},
        })

    # File naming convention
    np = file_a["name_patterns"]
    dominant = max(np.items(), key=lambda x: x[1]) if any(np.values()) else None
    if dominant and dominant[1] > 0:
        coding.append({
            "name": "file_naming_convention",
            "description": f"Files use {dominant[0]} naming",
            "confidence": _conf(dominant[1]),
            "evidence": file_a["file_paths"][:5],
            "metadata": {"convention": dominant[0], "counts": np},
        })

    # Primary language (from extensions)
    exts = file_a["extensions"]
    if exts:
        top_exts = sorted(exts.items(), key=lambda x: x[1], reverse=True)[:3]
        lang_map = {
            ".py": "Python", ".ts": "TypeScript", ".js": "JavaScript",
            ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby",
            ".sh": "Shell", ".md": "Markdown",
        }
        primary = top_exts[0]
        lang = lang_map.get(primary[0], primary[0])
        architectural.append({
            "name": "primary_language",
            "description": f"Primary language: {lang}",
            "confidence": _conf(primary[1], 5),
            "evidence": [f"{ext}: {c} files" for ext, c in top_exts],
            "metadata": {"language": lang, "extensions": dict(top_exts)},
        })

    # Test runner
    if bash_a["test_runner"]:
        runner = bash_a["test_runner"]
        samples = [c for c in bash_a["successful_samples"] if runner.split()[0] in c][:3]
        testing.append({
            "name": "test_runner",
            "description": f"Testing uses {runner}",
            "confidence": 0.75,
            "evidence": samples,
            "metadata": {"framework": runner},
        })

    # Package manager
    if bash_a["package_manager"]:
        pm = bash_a["package_manager"]
        samples = [c for c in bash_a["successful_samples"] if c.startswith(pm)][:3]
        tooling.append({
            "name": "package_manager",
            "description": f"Package manager: {pm}",
            "confidence": 0.75,
            "evidence": samples,
            "metadata": {"manager": pm},
        })

    # Repeated bash commands (skip trivial ones)
    TRIVIAL = {"echo", "cat", "ls", "cd", "mkdir", "cp", "mv", "rm", "pwd", "set", "export"}
    for cmd, count in list(bash_a["base_commands"].items())[:6]:
        if cmd in TRIVIAL:
            continue
        samples = [c for c in bash_a["successful_samples"] if c.startswith(cmd)][:2]
        tooling.append({
            "name": f"tooling_{cmd}",
            "description": f"Uses {cmd} ({count}x)",
            "confidence": _conf(count),
            "evidence": samples,
            "metadata": {"command": cmd, "count": count},
        })

    # Agent orchestration
    if agent_a["subagent_types"]:
        desc = ", ".join(f"{t}({c}x)" for t, c in agent_a["subagent_types"].items())
        orchestration.append({
            "name": "agent_orchestration",
            "description": f"Agents: {desc}",
            "confidence": _conf(agent_a["total_agent_calls"]),
            "evidence": [t["description"] for t in agent_a["task_samples"]][:3],
            "metadata": {"subagent_types": agent_a["subagent_types"]},
        })

    total = len(architectural) + len(coding) + len(testing) + len(tooling) + len(orchestration)
    return {
        "patterns": {
            "architectural": architectural,
            "coding": coding,
            "testing": testing,
            "tooling": tooling,
            "orchestration": orchestration,
        },
        "statistics": {"total_patterns": total, "source": "session"},
    }


def main() -> None:
    args = parse_args()

    events = load_jsonl(args.jsonl)
    turns = count_turns(events)

    skipped_result = {
        "patterns": {k: [] for k in ("architectural", "coding", "testing", "tooling", "orchestration")},
        "statistics": {
            "total_patterns": 0,
            "session_turns": turns,
            "source": "session",
            "skipped": True,
            "reason": f"too few turns ({turns} < {args.min_turns})",
        },
    }

    if turns < args.min_turns:
        _write(args.output, skipped_result)
        return

    tool_calls = extract_tool_calls(events)
    tool_results = extract_tool_results(events)

    result = build_output(
        analyze_file_patterns(tool_calls),
        analyze_bash_patterns(tool_calls, tool_results),
        analyze_agent_patterns(tool_calls),
    )
    result["statistics"]["session_turns"] = turns
    result["statistics"]["total_tool_calls"] = len(tool_calls)

    _write(args.output, result)


def _write(output_path: Optional[str], data: dict) -> None:
    text = json.dumps(data, indent=2)
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
