#!/usr/bin/env python3
"""
Context Distillation Functions

Intelligent extraction of patterns and context engineering
for fractal memory system.

Each function distills context from one level to the next:
- User → Opus: Extract seed rules and patterns
- Opus → Sonnet: Engineer task-oriented context
- Sonnet → Haiku: Extract minimal step context
"""

import json
import re
from typing import Dict, List, Any, Optional

# Import pattern matcher (handle both module and standalone usage)
try:
    from .pattern_matcher import SemanticPatternMatcher
except ImportError:
    from pattern_matcher import SemanticPatternMatcher


class SeedRuleExtractor:
    """
    Extract seed rules from full project context

    User Level (Full) → Opus Level (Patterns)
    """

    @staticmethod
    def extract(full_context: Dict) -> List[Dict]:
        """
        Extract seed rules, patterns, and architectural decisions.

        Input: Full project context (unlimited tokens)
        Output: List of seed rule dicts in new schema (id, goal, grounding, rule, connected_seed_rules)
        """
        rules: List[Dict] = []

        # Extract patterns from files
        if "files" in full_context:
            rules.extend(SeedRuleExtractor._extract_patterns(full_context["files"]))

        # Extract conventions from CLAUDE.md
        if "claude_md" in full_context:
            rules.extend(SeedRuleExtractor._extract_conventions(full_context["claude_md"]))

        # Extract architecture from project.md
        if "project_md" in full_context:
            rules.extend(SeedRuleExtractor._extract_architecture(full_context["project_md"]))

        # Infer patterns from file structure
        if "file_structure" in full_context:
            rules.extend(SeedRuleExtractor._infer_file_patterns(full_context["file_structure"]))

        return rules

    @staticmethod
    def _extract_patterns(files: List[Dict]) -> List[Dict]:
        """Extract coding patterns from files, returning seed rule dicts."""
        rules: List[Dict] = []
        seen_patterns: set = set()

        for file_info in files:
            path = file_info.get("path", "")
            content = file_info.get("content", "")

            # Detect authentication patterns
            if "auth" in path.lower() or "authentication" in content.lower():
                pattern = SeedRuleExtractor._detect_auth_pattern(content)
                conventions = SeedRuleExtractor._extract_auth_conventions(content)
                rule_id = "authentication_pattern"
                if rule_id not in seen_patterns:
                    seen_patterns.add(rule_id)
                    conv_text = "; ".join(conventions) if conventions else ""
                    rule_text = f"Use {pattern} for authentication"
                    if conv_text:
                        rule_text = f"{rule_text}; {conv_text}"
                    rules.append({
                        "id": rule_id,
                        "goal": "Ensure all authentication code follows the established pattern to avoid inconsistent implementations",
                        "grounding": path,
                        "rule": rule_text,
                        "connected_seed_rules": {}
                    })

            # Detect database patterns
            if "model" in path.lower() or "database" in path.lower():
                pattern = SeedRuleExtractor._detect_db_pattern(content)
                if pattern != "Unknown":
                    rule_id = "database_pattern"
                    if rule_id not in seen_patterns:
                        seen_patterns.add(rule_id)
                        rules.append({
                            "id": rule_id,
                            "goal": "Ensure all database models and queries follow the established ORM pattern",
                            "grounding": path,
                            "rule": f"Use {pattern} for all database models and queries",
                            "connected_seed_rules": {}
                        })
                    else:
                        # Update grounding with additional file reference
                        for r in rules:
                            if r["id"] == rule_id and path not in r["grounding"]:
                                r["grounding"] = r["grounding"] + "," + path

            # Detect API patterns
            if "route" in path.lower() or "api" in path.lower():
                pattern = SeedRuleExtractor._detect_api_pattern(content)
                if pattern != "Unknown":
                    rule_id = "api_design_pattern"
                    if rule_id not in seen_patterns:
                        seen_patterns.add(rule_id)
                        rules.append({
                            "id": rule_id,
                            "goal": "Ensure all API endpoints follow the established framework pattern for consistency",
                            "grounding": path,
                            "rule": f"Use {pattern} for all API endpoints and routing",
                            "connected_seed_rules": {}
                        })

        return rules

    @staticmethod
    def _detect_auth_pattern(content: str) -> str:
        """Detect authentication pattern from code"""
        if "jwt" in content.lower() or "jsonwebtoken" in content.lower():
            return "JWT"
        elif "oauth" in content.lower():
            return "OAuth"
        elif "session" in content.lower():
            return "Session-based"
        return "Unknown"

    @staticmethod
    def _extract_auth_conventions(content: str) -> List[str]:
        """Extract auth conventions"""
        conventions = []
        if "@require_auth" in content or "@login_required" in content:
            conventions.append("Use decorator for protected routes")
        if "bcrypt" in content.lower():
            conventions.append("Use bcrypt for password hashing")
        if "token" in content.lower() and "expire" in content.lower():
            conventions.append("Tokens have expiration")
        return conventions

    @staticmethod
    def _detect_db_pattern(content: str) -> str:
        """Detect database pattern"""
        if "sqlalchemy" in content.lower():
            return "SQLAlchemy ORM"
        elif "mongoose" in content.lower():
            return "Mongoose ODM"
        elif "prisma" in content.lower():
            return "Prisma ORM"
        return "Unknown"

    @staticmethod
    def _detect_api_pattern(content: str) -> str:
        """Detect API design pattern"""
        if "fastapi" in content.lower():
            return "FastAPI REST"
        elif "express" in content.lower():
            return "Express.js REST"
        elif "graphql" in content.lower():
            return "GraphQL"
        return "Unknown"

    @staticmethod
    def _extract_conventions(claude_md: str) -> List[Dict]:
        """Extract conventions from CLAUDE.md, returning seed rule dicts."""
        rules: List[Dict] = []
        lines = claude_md.split("\n")
        current_section = None
        section_items: Dict[str, List[str]] = {
            "coding_style": [], "naming": [], "testing": [], "documentation": []
        }

        for line in lines:
            if "## Coding" in line or "## Code" in line:
                current_section = "coding_style"
            elif "## Naming" in line:
                current_section = "naming"
            elif "## Test" in line:
                current_section = "testing"
            elif "## Document" in line or "## Doc" in line:
                current_section = "documentation"
            elif line.strip().startswith("-") and current_section:
                section_items[current_section].append(line.strip("- ").strip())

        section_meta = {
            "coding_style": ("coding_style_convention", "Maintain consistent coding style for readability"),
            "naming": ("naming_convention", "Maintain consistent naming so agents can predict symbol names"),
            "testing": ("testing_convention", "Ensure all tests follow established structure"),
            "documentation": ("documentation_convention", "Maintain consistent documentation standards"),
        }

        for section, items in section_items.items():
            if items:
                rule_id, goal = section_meta[section]
                rule_text = "; ".join(items[:3])  # Cap at 3 items per one-liner
                rules.append({
                    "id": rule_id,
                    "goal": goal,
                    "grounding": "CLAUDE.md#" + section.replace("_", "-"),
                    "rule": rule_text,
                    "connected_seed_rules": {}
                })

        return rules

    @staticmethod
    def _extract_architecture(project_md: str) -> List[Dict]:
        """Extract architectural decisions from project.md, returning seed rule dicts."""
        rules: List[Dict] = []
        lines = project_md.split("\n")
        tech_stack_items: List[str] = []

        for i, line in enumerate(lines):
            if "## Tech" in line or "## Stack" in line:
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip().startswith("-"):
                        tech_stack_items.append(lines[j].strip("- ").strip())

        if tech_stack_items:
            rules.append({
                "id": "tech_stack_decision",
                "goal": "Ensure new code uses only the approved technology stack to avoid dependency sprawl",
                "grounding": "project.md#tech-stack",
                "rule": f"Use only the approved stack: {', '.join(tech_stack_items[:5])}",
                "connected_seed_rules": {}
            })

        return rules

    @staticmethod
    def _infer_file_patterns(file_structure: List[str]) -> List[Dict]:
        """Infer patterns from file structure, returning seed rule dicts."""
        rules: List[Dict] = []
        dirs = set()
        for path in file_structure:
            if "/" in path:
                dirs.add(path.split("/")[0])

        structure_facts = []
        if "src" in dirs:
            structure_facts.append("source files in src/")
        if "tests" in dirs or "test" in dirs:
            structure_facts.append("tests in tests/ or test/")
        if "docs" in dirs:
            structure_facts.append("documentation in docs/")
        if "app" in dirs:
            structure_facts.append("application code in app/")

        naming_facts = []
        if any("_test.py" in p for p in file_structure):
            naming_facts.append("Python test files use *_test.py suffix")
        if any(".test.js" in p for p in file_structure):
            naming_facts.append("JS test files use *.test.js suffix")

        if structure_facts:
            rules.append({
                "id": "directory_structure_convention",
                "goal": "Keep new files in established directories to maintain predictable project layout",
                "grounding": "pattern:DirectoryStructure",
                "rule": f"Place new files following the established structure: {'; '.join(structure_facts)}",
                "connected_seed_rules": {}
            })

        if naming_facts:
            rules.append({
                "id": "file_naming_convention",
                "goal": "Maintain consistent file naming so files are discoverable by pattern",
                "grounding": "pattern:FileNaming",
                "rule": "; ".join(naming_facts),
                "connected_seed_rules": {}
            })

        return rules


class TaskContextEngineer:
    """
    Engineer task-oriented context from seed rules

    Opus Level (Patterns) → Sonnet Level (Task Context)
    """

    # Initialize semantic pattern matcher (class-level, reused across calls)
    _pattern_matcher = SemanticPatternMatcher()

    @staticmethod
    def engineer(seed_rules: Any, task: Dict, token_limit: int = 10000) -> Dict:
        """
        Engineer task-specific context from seed rules.

        Input: seed_rules as List[Dict] (new format) or Dict (legacy)
        Output: Task context dict — rules injected as rule strings only
        """
        task_id = task.get("task_id")
        action = task.get("action", "")
        description = task.get("description", "")
        task_text = action + " " + description

        # Normalize to List[Dict]
        if isinstance(seed_rules, dict):
            # Legacy: convert patterns dict to list
            rules_list = [
                {"id": k, "goal": "", "grounding": ",".join(v.get("files", [])),
                 "rule": v.get("pattern", k), "connected_seed_rules": {}}
                for k, v in seed_rules.get("patterns", {}).items()
            ]
            conventions_list = [
                {"id": f"convention_{i}", "goal": "", "grounding": "",
                 "rule": item, "connected_seed_rules": {}}
                for items in seed_rules.get("conventions", {}).values()
                for i, item in enumerate(items)
            ]
            rules_list.extend(conventions_list)
        else:
            rules_list = seed_rules or []

        # Select relevant rules via semantic matching
        relevant_rules = TaskContextEngineer._select_relevant_rules(rules_list, task_text)

        # Extract file references from grounding fields
        relevant_files = TaskContextEngineer._select_relevant_files_from_rules(relevant_rules, task_text)

        # Build prompt-safe rule strings (rule field only)
        prompt_rules = [r.get("rule", "") for r in relevant_rules if r.get("rule")]

        engineered = {
            "task_id": task_id,
            "action": action,
            "prompt_rules": prompt_rules,
            "files_to_read": relevant_files,
            "inline_context": description,
            "validation": task.get("validation", [])
        }

        estimated_tokens = len(json.dumps(engineered)) // 4
        if estimated_tokens > token_limit:
            engineered = TaskContextEngineer._trim_to_limit(engineered, token_limit)

        return engineered

    @staticmethod
    def _select_relevant_rules(rules: List[Dict], task_text: str) -> List[Dict]:
        """
        Select rules relevant to the task using semantic matching.

        Matches against rule `id` (snake_case keywords) and `rule` text.
        Uses SemanticPatternMatcher for the id-based matching.
        """
        if not rules:
            return []

        # Build patterns dict for SemanticPatternMatcher (id → rule dict)
        patterns_dict = {r["id"]: r for r in rules}

        # Use semantic matcher on rule ids
        matched = TaskContextEngineer._pattern_matcher.get_relevant_patterns(
            task_description=task_text,
            available_patterns=patterns_dict,
            confidence_threshold=0.5
        )

        # Additionally include rules whose `rule` text directly mentions task keywords
        task_lower = task_text.lower()
        task_words = set(task_lower.split())
        for rule in rules:
            rule_id = rule.get("id", "")
            if rule_id in matched:
                continue
            rule_text = rule.get("rule", "").lower()
            # Include if any significant task word (>3 chars) appears in the rule text
            if any(word in rule_text for word in task_words if len(word) > 3):
                matched[rule_id] = rule

        return list(matched.values())

    @staticmethod
    def _select_relevant_files_from_rules(rules: List[Dict], task_text: str) -> List[Dict]:
        """Extract file references from rule grounding fields."""
        files = []
        seen_paths: set = set()
        task_lower = task_text.lower()

        for rule in rules:
            grounding = rule.get("grounding", "")
            rule_id = rule.get("id", "")

            # Parse grounding: comma-separated file:symbol or file references
            if not grounding or grounding.startswith("pattern:") or grounding.startswith("CLAUDE.md"):
                continue

            for ref in grounding.split(","):
                ref = ref.strip()
                # Extract file path (before : if present)
                file_path = ref.split(":")[0].strip()
                if file_path and file_path not in seen_paths:
                    seen_paths.add(file_path)
                    files.append({
                        "path": file_path,
                        "reason": f"Referenced in {rule_id}",
                        "load_full": False
                    })

        return files

    @staticmethod
    def _select_relevant_patterns(patterns: Dict, task_text: str) -> Dict:
        """
        Select patterns relevant to task using semantic matching.

        Uses three-layer strategy:
        1. Direct keyword match
        2. Keyword-to-pattern mapping (semantic understanding)
        3. Fuzzy string matching (variations)

        Improves accuracy from ~50% (keyword-only) to 80%+ (semantic).
        """
        # Use semantic pattern matcher for improved accuracy
        relevant = TaskContextEngineer._pattern_matcher.get_relevant_patterns(
            task_description=task_text,
            available_patterns=patterns,
            confidence_threshold=0.5  # Only include patterns with >50% confidence
        )

        return relevant

    @staticmethod
    def _select_relevant_files(patterns: Dict, task_text: str) -> List[Dict]:
        """Select files relevant to task"""
        files = []

        task_lower = task_text.lower()

        # Extract files from relevant patterns
        for pattern_name, pattern_data in patterns.items():
            if any(keyword in task_lower for keyword in pattern_name.lower().split("_")):
                if "files" in pattern_data:
                    for file_path in pattern_data["files"]:
                        files.append({
                            "path": file_path,
                            "reason": f"Related to {pattern_name}",
                            "load_full": False  # Agent should load specific sections
                        })

        return files

    @staticmethod
    def _select_relevant_conventions(conventions: Dict, task_text: str) -> List[str]:
        """Select conventions relevant to task"""
        relevant = []

        task_lower = task_text.lower()

        # Check each convention category
        for category, items in conventions.items():
            if any(keyword in task_lower for keyword in category.lower().split("_")):
                relevant.extend(items)

        return relevant

    @staticmethod
    def _trim_to_limit(context: Dict, token_limit: int) -> Dict:
        """Trim context to fit token limit."""
        trimmed = {
            "task_id": context["task_id"],
            "action": context["action"],
            "inline_context": context["inline_context"]
        }

        current_tokens = len(json.dumps(trimmed)) // 4

        if "files_to_read" in context and current_tokens < token_limit:
            trimmed["files_to_read"] = context["files_to_read"][:3]
            current_tokens = len(json.dumps(trimmed)) // 4

        if "prompt_rules" in context and current_tokens < token_limit:
            trimmed["prompt_rules"] = context["prompt_rules"][:5]
            current_tokens = len(json.dumps(trimmed)) // 4
        elif "relevant_seeds" in context and current_tokens < token_limit:
            # Legacy
            simplified_seeds = {}
            for name, data in context["relevant_seeds"].items():
                simplified_seeds[name] = {"pattern": data.get("pattern")}
            trimmed["relevant_seeds"] = simplified_seeds

        if "conventions" in context and current_tokens < token_limit:
            trimmed["conventions"] = context["conventions"][:5]

        return trimmed


class StepContextExtractor:
    """
    Extract minimal step context from task context

    Sonnet Level (Task) → Haiku Level (Step)
    """

    @staticmethod
    def extract(task_context: Dict, step: Dict, token_limit: int = 2000) -> Dict:
        """
        Extract minimal context for single step

        Input: Task context (5-15K tokens) + Step description
        Output: Step context (<2K tokens)
        """
        step_id = step.get("step_id")
        action = step.get("action", "")
        description = step.get("description", "")

        # Build minimal context
        minimal = {
            "step_id": step_id,
            "action": action,
            "task": description,
            "requirements": step.get("requirements", []),
            "validation": step.get("validation", [])
        }

        # Add single most relevant file reference if exists
        if "files_to_read" in task_context and task_context["files_to_read"]:
            minimal["reference_file"] = task_context["files_to_read"][0]["path"]

        # Add location hint if creating new file
        if "create" in action.lower() or "add" in action.lower():
            minimal["location"] = step.get("location", "")

        # Ensure under token limit
        estimated_tokens = len(json.dumps(minimal)) // 4
        if estimated_tokens > token_limit:
            # Remove requirements if needed
            if "requirements" in minimal:
                minimal["requirements"] = minimal["requirements"][:3]

        return minimal


def build_system_prompt_rules(rules: List[Dict]) -> str:
    """
    Build the runtime system prompt fragment from a list of seed rules.

    ONLY the `rule` field from each seed is included.
    goal, grounding, and connected_seed_rules are NEVER injected into prompts.

    Args:
        rules: List of seed rule dicts (new schema)

    Returns:
        Newline-joined rule strings ready for system prompt injection
    """
    lines = []
    for rule in rules:
        rule_text = rule.get("rule", "").strip()
        if rule_text:
            lines.append(rule_text)
    return "\n".join(lines)


# Convenience functions
def distill_user_to_opus(full_context: Dict) -> List[Dict]:
    """User → Opus: Extract seed rules (returns List[Dict])"""
    return SeedRuleExtractor.extract(full_context)


def distill_opus_to_sonnet(seed_rules: Any, task: Dict) -> Dict:
    """Opus → Sonnet: Engineer task context (accepts List[Dict] or legacy Dict)"""
    return TaskContextEngineer.engineer(seed_rules, task)


def distill_sonnet_to_haiku(task_context: Dict, step: Dict) -> Dict:
    """Sonnet → Haiku: Extract step context"""
    return StepContextExtractor.extract(task_context, step)


if __name__ == "__main__":
    print("Context Distiller - Fractal Memory System")
    print("\nDistillation Functions:")
    print("  distill_user_to_opus(full_context)")
    print("  distill_opus_to_sonnet(seed_rules, task)")
    print("  distill_sonnet_to_haiku(task_context, step)")
    print("\nUse with FractalMemory for intelligent context engineering")
