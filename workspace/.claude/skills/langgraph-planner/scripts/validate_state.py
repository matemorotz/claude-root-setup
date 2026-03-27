#!/usr/bin/env python3
"""Validate TypedDict state schema structure"""

import json
import sys
from typing import Dict, Any


def validate_state_schema(plan: Dict[str, Any]) -> list[str]:
    """Validate state schema has proper TypedDict structure"""
    issues = []

    state_schema = plan.get("state_schema", {})
    if not state_schema:
        issues.append("ERROR: No state_schema found in plan")
        return issues

    fields = state_schema.get("fields", [])
    if not fields:
        issues.append("ERROR: No fields defined in state_schema")
        return issues

    # Check for messages field with reducer
    has_messages = False
    for field in fields:
        if field.get("name") == "messages":
            has_messages = True
            if "Annotated" not in field.get("type", ""):
                issues.append("WARNING: messages field should use Annotated with add_messages reducer")
            break

    if not has_messages:
        issues.append("WARNING: No messages field found (common in LangGraph graphs)")

    # Check for type hints on all fields
    for field in fields:
        if not field.get("type"):
            issues.append(f"ERROR: Field '{field.get('name')}' missing type hint")

    # Check for state isolation if subgraphs exist
    if plan.get("subgraphs"):
        subgraph_states = [s for s in state_schema.get("subgraph_states", [])]
        if not subgraph_states:
            issues.append("WARNING: Subgraphs defined but no subgraph states specified")

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_state.py <plan.json>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)

        issues = validate_state_schema(plan)

        if not issues:
            print("✓ State schema validation PASSED")
            return 0
        else:
            for issue in issues:
                print(issue)
            return 1 if any("ERROR" in i for i in issues) else 0

    except Exception as e:
        print(f"ERROR: Failed to validate state schema: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
