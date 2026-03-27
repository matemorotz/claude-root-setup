#!/usr/bin/env python3
"""
Assemble runtime prompt rules from workflow seed files.

Reads seeds/workflows/{workflow}/*.json and outputs only the `rule` one-liners.
Only `rule` fields are included — goal/grounding/connected_seed_rules stay in files.

Usage:
    python assemble-prompt.py --project-dir /path/to/project --workflow general
    python assemble-prompt.py --project-dir /path/to/project --workflow auth_workflow --json
"""

import json
import argparse
from pathlib import Path
import sys


def assemble_rules(project_dir: Path, workflow: str) -> list:
    """Read all seed rule files for a workflow, return only the `rule` strings."""
    workflow_dir = project_dir / "seeds" / "workflows" / workflow
    if not workflow_dir.exists():
        return []

    rules = []
    for rule_file in sorted(workflow_dir.glob("*.json")):
        try:
            with open(rule_file) as f:
                data = json.load(f)
            rule_text = data.get("rule", "").strip()
            if rule_text:
                rules.append(rule_text)
        except (json.JSONDecodeError, OSError):
            continue

    return rules


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble seed rules into agent prompt fragment"
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        required=True,
        help="Project root directory (seeds/workflows/{workflow}/ must exist here)"
    )
    parser.add_argument(
        "--workflow",
        type=str,
        default="general",
        help="Workflow name (default: general)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON array instead of newline-separated text"
    )
    args = parser.parse_args()

    rules = assemble_rules(args.project_dir, args.workflow)

    if args.json:
        print(json.dumps(rules))
    else:
        print("\n".join(rules))

    return 0


if __name__ == "__main__":
    sys.exit(main())
