#!/usr/bin/env python3
"""Validate strict JSON I/O enforcement"""

import json
import sys
from typing import Dict, Any


def validate_json_io(plan: Dict[str, Any]) -> list[str]:
    """Validate JSON I/O strictness"""
    issues = []

    nodes = plan.get("nodes", [])
    if not nodes:
        issues.append("ERROR: No nodes defined in plan")
        return issues

    # Check LLM nodes for JSON output specifications
    for node in nodes:
        node_type = node.get("type", "")
        if "llm" in node_type.lower():
            processing = node.get("processing", "")
            outputs = node.get("outputs", [])

            # Check if JSON is mentioned in processing
            has_json_spec = "json" in processing.lower() or "JSON" in processing

            if not has_json_spec and "json" in str(outputs).lower():
                issues.append(
                    f"WARNING: Node '{node.get('name')}' outputs JSON but no format specification in processing"
                )

    # Check for Pydantic models or validation
    has_validation = (
        "validation" in str(plan).lower() or
        "pydantic" in str(plan).lower()
    )

    if not has_validation:
        issues.append(
            "WARNING: No Pydantic validation models detected. "
            "Consider adding validation for strict JSON enforcement."
        )

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_json.py <plan.json>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)

        issues = validate_json_io(plan)

        if not issues:
            print("✓ JSON I/O validation PASSED")
            return 0
        else:
            for issue in issues:
                print(issue)
            return 0  # Warnings only, not errors

    except Exception as e:
        print(f"ERROR: Failed to validate JSON I/O: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
