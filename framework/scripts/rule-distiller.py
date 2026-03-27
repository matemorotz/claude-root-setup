#!/usr/bin/env python3
"""
Rule Distiller - Convert Patterns to Hierarchical Seed Rules

Transforms patterns extracted from knowledge graphs into hierarchical seed rules
for the fractal memory system (User/Opus/Sonnet/Haiku levels).

Usage:
    python rule-distiller.py patterns.json --project myproject
    python rule-distiller.py patterns.json --project myproject --workflow auth_workflow --output-dir /path/to/project
    python rule-distiller.py patterns.json --project myproject --level user --output-dir .claude/memory/user_level/projects/
    python rule-distiller.py patterns.json --update --project myproject --workflow general

Features:
- Converts patterns to seed rule format (id, goal, grounding, rule, connected_seed_rules)
- Opus level: one JSON file per rule in seeds/workflows/{workflow}/
- Organizes rules by fractal level (User/Opus/Sonnet/Haiku)
- Confidence-based rule creation (threshold: 0.6)
- Evidence linking from pattern files
- Token estimation for each rule
- Update mode for existing rules
- Hierarchical categorization
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class SeedRule:
    """Individual seed rule as a reusable context block."""
    id: str
    goal: str
    grounding: str
    rule: str
    connected_seed_rules: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "grounding": self.grounding,
            "rule": self.rule,
            "connected_seed_rules": self.connected_seed_rules
        }


@dataclass
class HierarchicalRules:
    """Hierarchical seed rules organized by fractal level."""
    project: str
    timestamp: str
    user_level: Dict[str, Any] = field(default_factory=dict)
    opus_level: List[Any] = field(default_factory=list)
    sonnet_level: Dict[str, Any] = field(default_factory=dict)
    haiku_level: Dict[str, Any] = field(default_factory=dict)


class RuleDistiller:
    """Convert extracted patterns into hierarchical seed rules."""

    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize RuleDistiller.

        Args:
            confidence_threshold: Minimum confidence for rule creation (default: 0.6)
        """
        self.confidence_threshold = confidence_threshold
        self.stats = {
            "total_patterns": 0,
            "rules_created": 0,
            "rules_skipped": 0,
            "by_level": {"user": 0, "opus": 0, "sonnet": 0, "haiku": 0},
            "by_category": {}
        }

    def distill(
        self,
        patterns_file: Path,
        project: str,
        output_level: str = "opus"
    ) -> HierarchicalRules:
        """
        Distill patterns into hierarchical seed rules.

        Args:
            patterns_file: Path to patterns.json from pattern-extractor.py
            project: Project name
            output_level: Target fractal level (user|opus|sonnet|haiku)

        Returns:
            HierarchicalRules object with rules at all levels
        """
        # Load patterns
        with open(patterns_file, 'r') as f:
            data = json.load(f)

        patterns = data.get("patterns", {})
        self.stats["total_patterns"] = data.get("statistics", {}).get("total_patterns", 0)

        # Initialize hierarchical rules
        rules = HierarchicalRules(
            project=project,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        # Process patterns by category
        if output_level in ["user", "opus"]:
            # User/Opus levels need comprehensive rules
            rules.user_level = self._create_user_level_rules(patterns, project)
            rules.opus_level = self._create_opus_level_rules(patterns, project)

        if output_level in ["sonnet", "haiku"]:
            # Sonnet/Haiku levels need task-specific templates
            rules.sonnet_level = self._create_sonnet_level_rules(patterns, project)
            rules.haiku_level = self._create_haiku_level_rules(patterns, project)

        return rules

    def _make_id(self, name: str, suffix: str) -> str:
        """Generate snake_case rule ID from name and suffix."""
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        words = clean.split()
        base = '_'.join(words)
        return f"{base}_{suffix}"

    def _create_user_level_rules(self, patterns: Dict, project: str) -> Dict[str, Any]:
        """
        Create User-level rules (unlimited context, project overview).

        User level contains:
        - Project architecture overview
        - Complete tech stack
        - All major patterns
        - Full dependencies list
        """
        user_rules = {
            "project": project,
            "level": "user",
            "architecture": {},
            "tech_stack": {},
            "patterns": {},
            "file_structure": {}
        }

        # Extract tech stack from architectural patterns
        tech_stack = self._extract_tech_stack(patterns)
        if tech_stack:
            user_rules["tech_stack"] = tech_stack

        # Extract architecture from architectural patterns
        arch_patterns = patterns.get("architectural", [])
        for pattern in arch_patterns:
            if pattern["confidence"] >= self.confidence_threshold:
                user_rules["architecture"][pattern["name"].lower().replace(" ", "_")] = {
                    "pattern": pattern["name"],
                    "description": pattern["description"],
                    "confidence": pattern["confidence"],
                    "coverage": pattern["coverage"],
                    "evidence": pattern["evidence"][:5]  # Top 5 evidence files
                }
                self.stats["rules_created"] += 1
                self.stats["by_level"]["user"] += 1

        return user_rules

    def _create_opus_level_rules(self, patterns: Dict, project: str) -> List[SeedRule]:
        """
        Create Opus-level rules as individual reusable context blocks.

        Each rule has: id, goal, grounding, rule, connected_seed_rules.
        Only the `rule` field is injected into agent prompts at runtime.
        """
        rules: List[SeedRule] = []
        rule_ids_by_category: Dict[str, List[str]] = defaultdict(list)

        # Process architectural patterns
        for pattern in patterns.get("architectural", []):
            if pattern["confidence"] < self.confidence_threshold:
                self.stats["rules_skipped"] += 1
                continue
            rule_id = self._make_id(pattern["name"], "pattern")
            evidence = pattern.get("evidence", [])
            grounding = ",".join(evidence[:3]) if evidence else f"pattern:{pattern['name']}"
            goal = f"Ensure new code follows the established {pattern['name']} to maintain architectural consistency"
            new_rules = self._expand_compound_rule(rule_id, goal, grounding, pattern["description"])
            rules.extend(new_rules)
            rule_ids_by_category["architectural"].extend(r.id for r in new_rules)
            self.stats["rules_created"] += len(new_rules)
            self.stats["by_level"]["opus"] += len(new_rules)
            self._update_category_stats("architectural")

        # Process coding patterns
        for pattern in patterns.get("coding", []):
            if pattern["confidence"] < self.confidence_threshold:
                self.stats["rules_skipped"] += 1
                continue
            name_lower = pattern["name"].lower()
            suffix = "convention" if "naming" in name_lower or "style" in name_lower else "pattern"
            rule_id = self._make_id(pattern["name"], suffix)
            evidence = pattern.get("evidence", [])
            grounding = ",".join(evidence[:3]) if evidence else f"pattern:{pattern['name']}"
            goal = f"Maintain consistent {pattern['name'].lower()} so code is predictable and readable"
            new_rules = self._expand_compound_rule(rule_id, goal, grounding, pattern["description"])
            rules.extend(new_rules)
            rule_ids_by_category["coding"].extend(r.id for r in new_rules)
            self.stats["rules_created"] += len(new_rules)
            self.stats["by_level"]["opus"] += len(new_rules)
            self._update_category_stats("coding")

        # Process testing patterns
        for pattern in patterns.get("testing", []):
            if pattern["confidence"] < self.confidence_threshold:
                self.stats["rules_skipped"] += 1
                continue
            rule_id = self._make_id(pattern["name"], "convention")
            evidence = pattern.get("evidence", [])
            grounding = ",".join(evidence[:3]) if evidence else f"pattern:{pattern['name']}"
            metadata = pattern.get("metadata", {})
            framework = metadata.get("framework", "")
            rule_text = pattern["description"]
            if framework:
                rule_text = f"{rule_text}; use {framework} framework"
            goal = "Ensure all tests follow the established structure for consistent verification"
            new_rules = self._expand_compound_rule(rule_id, goal, grounding, rule_text)
            rules.extend(new_rules)
            rule_ids_by_category["testing"].extend(r.id for r in new_rules)
            self.stats["rules_created"] += len(new_rules)
            self.stats["by_level"]["opus"] += len(new_rules)
            self._update_category_stats("testing")

        # Process API design patterns
        for pattern in patterns.get("api_design", []):
            if pattern["confidence"] < self.confidence_threshold:
                self.stats["rules_skipped"] += 1
                continue
            rule_id = self._make_id(pattern["name"], "pattern")
            evidence = pattern.get("evidence", [])
            grounding = ",".join(evidence[:3]) if evidence else f"pattern:{pattern['name']}"
            goal = f"Ensure all API endpoints follow the established {pattern['name']} for consistency"
            new_rules = self._expand_compound_rule(rule_id, goal, grounding, pattern["description"])
            rules.extend(new_rules)
            rule_ids_by_category["api_design"].extend(r.id for r in new_rules)
            self.stats["rules_created"] += len(new_rules)
            self.stats["by_level"]["opus"] += len(new_rules)
            self._update_category_stats("api_design")

        # Wire up connected_seed_rules based on category relationships
        for rule in rules:
            my_category = next(
                (cat for cat, ids in rule_ids_by_category.items() if rule.id in ids),
                None
            )
            connected: Dict[str, List[str]] = {}

            if my_category:
                # Same-category rules → workflow connections (named after category)
                peers = [rid for rid in rule_ids_by_category[my_category] if rid != rule.id]
                if peers:
                    connected[f"{my_category}_workflow"] = peers

            # API patterns have architectural patterns as prerequisites
            if my_category == "api_design" and rule_ids_by_category["architectural"]:
                connected["prerequisite"] = rule_ids_by_category["architectural"]

            # Testing conventions related to coding conventions
            if my_category == "testing" and rule_ids_by_category["coding"]:
                connected["coding_workflow"] = rule_ids_by_category["coding"]

            # Coding conventions related to architectural patterns
            if my_category == "coding" and rule_ids_by_category["architectural"]:
                connected["architecture_workflow"] = rule_ids_by_category["architectural"]

            rule.connected_seed_rules = connected

        return rules

    def _create_sonnet_level_rules(self, patterns: Dict, project: str) -> Dict[str, Any]:
        """
        Create Sonnet-level rules (task-specific templates).

        Sonnet level contains:
        - Task type templates
        - File location patterns
        - Required imports
        - Conventions for specific tasks
        """
        sonnet_rules = {
            "project": project,
            "level": "sonnet",
            "task_templates": {}
        }

        # Create templates based on detected patterns
        api_patterns = patterns.get("api_design", [])
        if api_patterns:
            template = self._create_api_endpoint_template(api_patterns)
            if template:
                sonnet_rules["task_templates"]["add_api_endpoint"] = template
                self.stats["by_level"]["sonnet"] += 1

        # Create model creation template from architectural patterns
        arch_patterns = patterns.get("architectural", [])
        for pattern in arch_patterns:
            if "repository" in pattern["name"].lower() or "orm" in pattern["description"].lower():
                template = self._create_model_template(pattern)
                if template:
                    sonnet_rules["task_templates"]["create_model"] = template
                    self.stats["by_level"]["sonnet"] += 1
                    break

        return sonnet_rules

    def _create_haiku_level_rules(self, patterns: Dict, project: str) -> Dict[str, Any]:
        """
        Create Haiku-level rules (step-by-step instructions).

        Haiku level contains:
        - Atomic step instructions
        - File creation templates
        - Validation commands
        - Specific code snippets
        """
        haiku_rules = {
            "project": project,
            "level": "haiku",
            "step_instructions": {}
        }

        # Extract step-level instructions from coding patterns
        coding_patterns = patterns.get("coding", [])
        for pattern in coding_patterns:
            if "naming" in pattern["name"].lower():
                haiku_rules["step_instructions"]["naming_convention"] = {
                    "description": pattern["description"],
                    "examples": pattern.get("metadata", {}).get("examples", [])
                }
                self.stats["by_level"]["haiku"] += 1
                break

        # Add file organization steps
        for pattern in coding_patterns:
            if "file organization" in pattern["name"].lower():
                haiku_rules["step_instructions"]["create_file"] = {
                    "description": "Follow standard directory structure",
                    "structure": pattern.get("metadata", {}).get("standard_dirs", [])
                }
                self.stats["by_level"]["haiku"] += 1
                break

        return haiku_rules

    def _extract_tech_stack(self, patterns: Dict) -> Dict[str, List[str]]:
        """Extract technology stack from patterns."""
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "libraries": [],
            "databases": [],
            "dependencies": []
        }

        # Extract from architectural patterns
        for pattern in patterns.get("architectural", []):
            name_lower = pattern["name"].lower()
            description_lower = pattern["description"].lower()

            # Frameworks
            if "mvc" in name_lower:
                tech_stack["patterns"] = ["MVC Architecture"]

            # Databases/ORMs
            if "repository" in name_lower:
                # Try to extract ORM from description
                if "sqlalchemy" in description_lower:
                    tech_stack["libraries"].append("SQLAlchemy")
                elif "mongoose" in description_lower:
                    tech_stack["libraries"].append("Mongoose")
                elif "prisma" in description_lower:
                    tech_stack["frameworks"].append("Prisma")

        # Extract from API patterns
        for pattern in patterns.get("api_design", []):
            name_lower = pattern["name"].lower()

            if "rest" in name_lower:
                if "fastapi" in name_lower:
                    tech_stack["frameworks"].append("FastAPI")
                    tech_stack["languages"].append("Python")
                elif "express" in name_lower:
                    tech_stack["frameworks"].append("Express")
                    tech_stack["languages"].append("JavaScript")

        # Extract from testing patterns
        for pattern in patterns.get("testing", []):
            metadata = pattern.get("metadata", {})
            framework = metadata.get("framework")
            if framework:
                tech_stack["libraries"].append(framework)

        # Deduplicate
        for key in tech_stack:
            tech_stack[key] = list(set(tech_stack[key]))

        return tech_stack

    def _extract_naming_conventions(self, pattern: Dict) -> List[str]:
        """Extract naming conventions from pattern."""
        conventions = []
        metadata = pattern.get("metadata", {})

        # Extract from metadata examples
        examples = metadata.get("examples", [])
        convention_map = {
            "PascalCase": "Classes use PascalCase",
            "snake_case": "Functions/variables use snake_case",
            "camelCase": "Variables use camelCase"
        }

        for example in examples:
            for style, convention in convention_map.items():
                if style in example and convention not in conventions:
                    conventions.append(convention)

        return conventions

    def _create_api_endpoint_template(self, api_patterns: List[Dict]) -> Optional[Dict]:
        """Create API endpoint template from patterns."""
        for pattern in api_patterns:
            if pattern["confidence"] >= self.confidence_threshold:
                return {
                    "file_template": "app/routes/{resource}.py",
                    "pattern": pattern["name"],
                    "conventions": [pattern["description"]],
                    "example_files": pattern["evidence"][:2]
                }
        return None

    def _create_model_template(self, pattern: Dict) -> Optional[Dict]:
        """Create model creation template from pattern."""
        if pattern["confidence"] >= self.confidence_threshold:
            return {
                "file_template": "app/models/{resource}.py",
                "pattern": pattern["name"],
                "conventions": [pattern["description"]],
                "example_files": pattern["evidence"][:2]
            }
        return None

    def _estimate_tokens(self, seed_rules: Dict) -> int:
        """Estimate token count for seed rules."""
        # Rough estimate: JSON length / 4 (average token length)
        json_str = json.dumps(seed_rules)
        return len(json_str) // 4

    def _expand_compound_rule(
        self,
        rule_id: str,
        goal: str,
        grounding: str,
        rule_text: str
    ) -> List["SeedRule"]:
        """
        Split a semicolon-separated compound rule into individual SeedRules.

        Each clause becomes its own rule. Single-clause rules are returned as-is
        with the original ID. Multi-clause rules get numeric suffixes (_1, _2, ...).
        """
        clauses = [c.strip() for c in rule_text.split(";") if c.strip()]
        if len(clauses) <= 1:
            return [SeedRule(id=rule_id, goal=goal, grounding=grounding, rule=rule_text.strip())]

        return [
            SeedRule(id=f"{rule_id}_{i}", goal=goal, grounding=grounding, rule=clause)
            for i, clause in enumerate(clauses, 1)
        ]

    def _update_category_stats(self, category: str):
        """Update statistics for category."""
        if category not in self.stats["by_category"]:
            self.stats["by_category"][category] = 0
        self.stats["by_category"][category] += 1

    def save_rules(
        self,
        rules: "HierarchicalRules",
        output_dir: Path,
        level: str = "opus",
        workflow: str = "general"
    ) -> List[Path]:
        """
        Save seed rules to disk.

        For opus level: writes one JSON file per rule into
        {output_dir}/seeds/workflows/{workflow}/{rule_id}.json

        For other levels: writes a single JSON file as before.

        Args:
            rules: HierarchicalRules object
            output_dir: Project root (for opus) or target directory (for other levels)
            level: Fractal level to save (user|opus|sonnet|haiku)
            workflow: Workflow name for opus level (default: "general")

        Returns:
            List of written file paths
        """
        output_dir = Path(output_dir)
        written: List[Path] = []

        if level == "opus":
            # New behaviour: one file per rule in seeds/workflows/{workflow}/
            workflow_dir = output_dir / "seeds" / "workflows" / workflow
            workflow_dir.mkdir(parents=True, exist_ok=True)
            for seed_rule in rules.opus_level:
                filepath = workflow_dir / f"{seed_rule.id}.json"
                with open(filepath, 'w') as f:
                    json.dump(seed_rule.to_dict(), f, indent=2)
                written.append(filepath)
        else:
            # Legacy behaviour for user/sonnet/haiku levels
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{rules.project}.json"
            filepath = output_dir / filename
            if level == "user":
                data = rules.user_level
            elif level == "sonnet":
                data = rules.sonnet_level
            elif level == "haiku":
                data = rules.haiku_level
            else:
                raise ValueError(f"Invalid level: {level}")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            written.append(filepath)

        return written

    def update_rules(
        self,
        patterns_file: Path,
        existing_rules_dir: Path,
        project: str,
        workflow: str = "general"
    ) -> List[SeedRule]:
        """
        Update existing seed rules with new patterns.

        Args:
            patterns_file: New patterns.json
            existing_rules_dir: Project root (seeds/workflows/{workflow}/ will be scanned)
            project: Project name
            workflow: Workflow name

        Returns:
            Updated list of SeedRule objects (merged)
        """
        # Load existing rules from workflow dir
        workflow_dir = Path(existing_rules_dir) / "seeds" / "workflows" / workflow
        existing_rules: Dict[str, SeedRule] = {}
        if workflow_dir.exists():
            for rule_file in workflow_dir.glob("*.json"):
                with open(rule_file, 'r') as f:
                    data = json.load(f)
                existing_rules[data["id"]] = SeedRule(
                    id=data["id"],
                    goal=data.get("goal", ""),
                    grounding=data.get("grounding", ""),
                    rule=data.get("rule", ""),
                    connected_seed_rules=data.get("connected_seed_rules", {})
                )

        # Create new rules from patterns
        new_rules_obj = self.distill(patterns_file, project, output_level="opus")

        # Merge: new rules override existing by id
        for seed_rule in new_rules_obj.opus_level:
            existing_rules[seed_rule.id] = seed_rule

        return list(existing_rules.values())

    def print_stats(self):
        """Print distillation statistics."""
        print("\n=== Rule Distillation Statistics ===")
        print(f"Total patterns analyzed: {self.stats['total_patterns']}")
        print(f"Rules created: {self.stats['rules_created']}")
        print(f"Rules skipped (low confidence): {self.stats['rules_skipped']}")
        print(f"\nBy fractal level:")
        for level, count in self.stats['by_level'].items():
            if count > 0:
                print(f"  {level.capitalize()}: {count}")
        print(f"\nBy category:")
        for category, count in self.stats['by_category'].items():
            print(f"  {category}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert extracted patterns to hierarchical seed rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create seed rules for the 'general' workflow (project root = current dir)
  python rule-distiller.py patterns.json --project myproject

  # Create seed rules for a specific workflow
  python rule-distiller.py patterns.json --project myproject --workflow auth_workflow --output-dir /path/to/project

  # Create User-level rules (legacy single-file output)
  python rule-distiller.py patterns.json --project myproject --level user --output-dir .claude/memory/user_level/projects/

  # Update existing seed rules
  python rule-distiller.py patterns.json --update --project myproject --workflow general

  # Set confidence threshold
  python rule-distiller.py patterns.json --project myproject --confidence 0.7
        """
    )

    parser.add_argument(
        "patterns_file",
        type=Path,
        help="Path to patterns.json from pattern-extractor.py"
    )

    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Project name"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Project root directory for opus level (seeds/workflows/{workflow}/ will be created here). "
             "For other levels, the direct output directory. (default: .)"
    )

    parser.add_argument(
        "--workflow",
        type=str,
        default="general",
        help="Workflow name for opus-level output (default: general)"
    )

    parser.add_argument(
        "--level",
        choices=["user", "opus", "sonnet", "haiku"],
        default="opus",
        help="Target fractal level (default: opus)"
    )

    parser.add_argument(
        "--confidence",
        type=float,
        default=0.6,
        help="Minimum confidence threshold for rule creation (default: 0.6)"
    )

    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing rules instead of creating new"
    )

    parser.add_argument(
        "--existing-rules",
        type=Path,
        help="Project root containing existing rules (required with --update)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.patterns_file.exists():
        print(f"Error: Patterns file not found: {args.patterns_file}")
        return 1

    if args.update and not args.existing_rules:
        print("Error: --existing-rules required with --update")
        return 1

    if args.update and not args.existing_rules.exists():
        print(f"Error: Existing rules directory not found: {args.existing_rules}")
        return 1

    # Create distiller
    distiller = RuleDistiller(confidence_threshold=args.confidence)

    if args.verbose:
        print(f"Loading patterns from: {args.patterns_file}")
        print(f"Project: {args.project}")
        print(f"Confidence threshold: {args.confidence}")
        print(f"Target level: {args.level}")
        if args.level == "opus":
            print(f"Workflow: {args.workflow}")

    # Distill or update rules
    if args.update:
        if args.verbose:
            print(f"Updating existing rules in: {args.existing_rules}")

        updated_rules = distiller.update_rules(
            args.patterns_file,
            args.existing_rules,
            args.project,
            workflow=args.workflow
        )

        # Build a minimal HierarchicalRules wrapper to reuse save_rules
        rules = HierarchicalRules(
            project=args.project,
            timestamp=datetime.utcnow().isoformat() + "Z",
            opus_level=updated_rules
        )
        written = distiller.save_rules(rules, args.existing_rules, level="opus", workflow=args.workflow)

        if args.verbose:
            print(f"\n✓ Updated {len(written)} seed rules in: {args.existing_rules / 'seeds' / 'workflows' / args.workflow}")
            distiller.print_stats()
        else:
            print(f"Updated: {len(written)} rules in seeds/workflows/{args.workflow}/")

    else:
        # Create new rules
        if args.verbose:
            print("Distilling patterns into seed rules...")

        rules = distiller.distill(
            args.patterns_file,
            args.project,
            output_level=args.level
        )

        # Save rules
        written = distiller.save_rules(rules, args.output_dir, level=args.level, workflow=args.workflow)

        if args.verbose:
            if args.level == "opus":
                workflow_dir = args.output_dir / "seeds" / "workflows" / args.workflow
                print(f"\n✓ {len(written)} seed rules written to: {workflow_dir}")
            else:
                print(f"\n✓ Seed rules created: {written[0] if written else 'none'}")
            distiller.print_stats()
        else:
            if args.level == "opus":
                print(f"Created: {len(written)} rules in seeds/workflows/{args.workflow}/")
            else:
                print(f"Created: {written[0] if written else 'none'}")

    return 0


if __name__ == "__main__":
    exit(main())
