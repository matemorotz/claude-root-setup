#!/usr/bin/env python3
"""Detect potential infinite loops in graph"""

import json
import sys
from typing import Dict, Any, List, Set, Tuple


def find_cycles(plan: Dict[str, Any]) -> List[List[str]]:
    """Find all cycles in the graph"""
    cycles = []
    visited = set()

    def dfs(node: str, path: List[str]) -> None:
        if node in path:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:]
            if cycle not in cycles:
                cycles.append(cycle)
            return

        if node in visited:
            return

        path.append(node)

        # Follow direct edges
        for edge in plan.get("edges", []):
            if edge.get("from") == node:
                dfs(edge.get("to"), path.copy())

        # Follow conditional edges
        for edge in plan.get("conditional_edges", []):
            if edge.get("from") == node:
                for dest in edge.get("destinations", []):
                    if dest != "END":
                        dfs(dest, path.copy())

        visited.add(node)

    # Start DFS from all nodes
    all_nodes = set()
    for edge in plan.get("edges", []) + plan.get("conditional_edges", []):
        all_nodes.add(edge.get("from"))

    for node in all_nodes:
        if node not in visited:
            dfs(node, [])

    return cycles


def check_loop_safety(plan: Dict[str, Any], cycle: List[str]) -> Tuple[bool, str]:
    """Check if a cycle has termination safeguards"""
    # Check state schema for iteration counter
    state_schema = plan.get("state_schema", {})
    fields = state_schema.get("fields", [])

    has_iteration_counter = any(
        "iteration" in field.get("name", "").lower() or
        "retry" in field.get("name", "").lower() or
        "count" in field.get("name", "").lower()
        for field in fields
    )

    # Check conditional edges for END route
    for node in cycle:
        for edge in plan.get("conditional_edges", []):
            if edge.get("from") == node and "END" in edge.get("destinations", []):
                return True, "Has END route in loop"

    if has_iteration_counter:
        return True, "Has iteration counter in state"

    return False, "No termination safeguards found"


def check_loops(plan: Dict[str, Any]) -> list[str]:
    """Check for infinite loop risks"""
    issues = []

    cycles = find_cycles(plan)

    if not cycles:
        return issues  # No cycles found

    for cycle in cycles:
        is_safe, reason = check_loop_safety(plan, cycle)

        if not is_safe:
            issues.append(
                f"ERROR: Potential infinite loop detected: {' → '.join(cycle)} → {cycle[0]}. "
                f"Add iteration counter or END route in conditional edge."
            )
        else:
            issues.append(
                f"INFO: Loop detected: {' → '.join(cycle)} → {cycle[0]}. "
                f"Safety: {reason}"
            )

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_loops.py <plan.json>")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)

        issues = check_loops(plan)

        if not issues:
            print("✓ Loop check PASSED - No cycles detected")
            return 0
        else:
            for issue in issues:
                print(issue)
            return 1 if any("ERROR" in i for i in issues) else 0

    except Exception as e:
        print(f"ERROR: Failed to check loops: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
