#!/usr/bin/env python3
"""Validate that all conditional edges have paths to END"""

import json
import sys
from typing import Dict, Any, Set


def can_reach_end(plan: Dict[str, Any], start_node: str, visited: Set[str] = None) -> bool:
    """Check if a node can reach END"""
    if visited is None:
        visited = set()

    if start_node == "END":
        return True

    if start_node in visited:
        return False  # Cycle detected

    visited.add(start_node)

    # Check direct edges
    for edge in plan.get("edges", []):
        if edge.get("from") == start_node:
            if can_reach_end(plan, edge.get("to"), visited.copy()):
                return True

    # Check conditional edges
    for edge in plan.get("conditional_edges", []):
        if edge.get("from") == start_node:
            destinations = edge.get("destinations", [])
            if any(can_reach_end(plan, dest, visited.copy()) for dest in destinations):
                return True

    return False


def validate_termination(plan: Dict[str, Any]) -> list[str]:
    """Validate all paths lead to END"""
    issues = []

    conditional_edges = plan.get("conditional_edges", [])
    if not conditional_edges:
        return issues  # No conditional edges to validate

    for edge in conditional_edges:
        source = edge.get("from")
        destinations = edge.get("destinations", [])

        # Check if END is directly reachable
        has_end_route = "END" in destinations

        # Check if all destinations can eventually reach END
        all_reach_end = all(can_reach_end(plan, dest) for dest in destinations)

        if not has_end_route and not all_reach_end:
            issues.append(
                f"ERROR: Conditional edge from '{source}' has no path to END. "
                f"Destinations: {destinations}"
            )
        elif not has_end_route:
            issues.append(
                f"WARNING: Conditional edge from '{source}' can reach END but not directly. "
                f"Consider adding END to destinations list."
            )

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_termination.py <plan.json>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)

        issues = validate_termination(plan)

        if not issues:
            print("✓ Termination validation PASSED - All paths lead to END")
            return 0
        else:
            for issue in issues:
                print(issue)
            return 1 if any("ERROR" in i for i in issues) else 0

    except Exception as e:
        print(f"ERROR: Failed to validate termination: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
