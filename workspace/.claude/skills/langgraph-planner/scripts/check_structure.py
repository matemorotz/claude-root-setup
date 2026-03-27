#!/usr/bin/env python3
"""
Final structure check: Verify graph completeness and consistency

Why this solution:
- Comprehensive validation before implementation saves debugging time
- Catches architectural issues early when they're cheap to fix
- Simple checks first, complex analysis only if needed (efficiency)
"""

import json
import sys
from typing import Dict, Any, Set, List


def check_structure(plan: Dict[str, Any]) -> List[str]:
    """
    Perform comprehensive structure validation
    
    Why comprehensive: Better to catch issues now than during runtime
    """
    issues = []
    
    # 1. Basic Completeness Check (SIMPLE - do first)
    required_keys = ["graph_name", "state_schema", "nodes", "edges"]
    for key in required_keys:
        if key not in plan:
            issues.append(f"ERROR: Missing required key '{key}' in plan")
    
    if issues:
        return issues  # Stop early if basic structure missing
    
    # 2. Node Completeness (SIMPLE)
    nodes = plan.get("nodes", [])
    node_names = {node.get("name") for node in nodes}
    
    for node in nodes:
        if not node.get("name"):
            issues.append("ERROR: Node missing 'name' field")
        if not node.get("type"):
            issues.append(f"WARNING: Node '{node.get('name')}' missing 'type' field")
        if not node.get("inputs"):
            issues.append(f"WARNING: Node '{node.get('name')}' missing 'inputs' specification")
        if not node.get("outputs"):
            issues.append(f"WARNING: Node '{node.get('name')}' missing 'outputs' specification")
    
    # 3. Edge Consistency (MODERATE - reference checking)
    # Why: Prevents broken connections that cause runtime failures
    all_edges = plan.get("edges", []) + plan.get("conditional_edges", [])
    for edge in all_edges:
        source = edge.get("from")
        
        # Check source exists
        if source and source != "START" and source not in node_names:
            issues.append(f"ERROR: Edge from unknown node '{source}'")
        
        # Check destinations exist
        if "to" in edge:  # Direct edge
            dest = edge.get("to")
            if dest and dest != "END" and dest not in node_names:
                issues.append(f"ERROR: Edge to unknown node '{dest}'")
        elif "destinations" in edge:  # Conditional edge
            for dest in edge.get("destinations", []):
                if dest and dest != "END" and dest not in node_names:
                    issues.append(f"ERROR: Conditional edge to unknown node '{dest}'")
    
    # 4. State Field Consistency (COMPLEX - only if above passed)
    # Why complexity justified: Prevents subtle state bugs that are hard to debug
    if not any("ERROR" in i for i in issues):
        state_fields = {field.get("name") for field in plan.get("state_schema", {}).get("fields", [])}
        
        for node in nodes:
            # Check inputs reference valid state fields
            for inp in node.get("inputs", []):
                if inp not in state_fields and inp != "messages":
                    issues.append(f"WARNING: Node '{node.get('name')}' input '{inp}' not in state schema")
            
            # Check outputs reference valid state fields
            for out in node.get("outputs", []):
                if out not in state_fields and out != "messages":
                    issues.append(f"WARNING: Node '{node.get('name')}' output '{out}' not in state schema")
    
    # 5. Subgraph Isolation Check (COMPLEX - architecture validation)
    # Why: Prevents state pollution bugs in subgraphs
    if plan.get("subgraphs"):
        parent_fields = {f.get("name") for f in plan.get("state_schema", {}).get("fields", [])}
        
        for subgraph in plan.get("subgraphs", []):
            subgraph_state = plan.get("state_schema", {}).get(f"{subgraph}_state")
            if subgraph_state:
                local_fields = {f.get("name") for f in subgraph_state.get("local_fields", [])}
                
                # Check no local fields leak to parent
                if local_fields & parent_fields:
                    overlap = local_fields & parent_fields
                    issues.append(
                        f"ERROR: Subgraph '{subgraph}' local fields overlap with parent: {overlap}"
                    )
    
    return issues


def check_logic_control(plan: Dict[str, Any]) -> List[str]:
    """
    Verify routing logic is sound and complete
    
    Why separate function: Logic control is distinct concern from structure
    Why this approach: Catches logic errors that lead to stuck graphs
    """
    issues = []
    
    conditional_edges = plan.get("conditional_edges", [])
    if not conditional_edges:
        return issues  # No conditional routing to check
    
    for edge in conditional_edges:
        source = edge.get("from")
        destinations = edge.get("destinations", [])
        logic = edge.get("logic", "")
        
        # 1. Check END is reachable (CRITICAL)
        # Why: Prevents graphs that never terminate
        if "END" not in destinations:
            issues.append(
                f"WARNING: Conditional edge from '{source}' doesn't list END as destination. "
                f"Ensure END is reachable through other paths."
            )
        
        # 2. Check logic describes all destinations (IMPORTANT)
        # Why: Prevents undefined behavior when conditions don't match expectations
        for dest in destinations:
            if dest != "END" and dest.lower() not in logic.lower():
                issues.append(
                    f"WARNING: Destination '{dest}' not mentioned in routing logic for '{source}'"
                )
        
        # 3. Check for termination conditions (CRITICAL)
        # Why: Primary cause of infinite loops
        termination_keywords = ["complete", "iteration", "error", "count", "END"]
        has_termination = any(kw in logic for kw in termination_keywords)
        
        if not has_termination:
            issues.append(
                f"ERROR: Conditional edge from '{source}' missing termination conditions. "
                f"Add iteration counter or completion flag check."
            )
    
    return issues


def analyze_complexity(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze graph complexity to recommend simplifications
    
    Why this exists: Enforce "simpler solutions are better" principle
    Design choice: Suggest simplifications but don't enforce (user knows their domain)
    """
    analysis = {
        "node_count": len(plan.get("nodes", [])),
        "conditional_edges_count": len(plan.get("conditional_edges", [])),
        "subgraph_count": len(plan.get("subgraphs", [])),
        "complexity_score": 0,
        "recommendations": []
    }
    
    # Calculate complexity score (SIMPLE heuristic)
    # Why: Quick estimate of maintenance burden
    analysis["complexity_score"] = (
        analysis["node_count"] * 1 +
        analysis["conditional_edges_count"] * 2 +
        analysis["subgraph_count"] * 3
    )
    
    # Recommend simplifications (SIMPLE rules)
    # Why: Guide users toward maintainable designs
    
    if analysis["node_count"] > 10:
        analysis["recommendations"].append(
            f"Consider splitting into multiple graphs. Current: {analysis['node_count']} nodes (>10)."
        )
    
    if analysis["conditional_edges_count"] > 5:
        analysis["recommendations"].append(
            f"Many conditional branches ({analysis['conditional_edges_count']}). "
            f"Consider using routing table pattern or state machine."
        )
    
    if analysis["subgraph_count"] > 4:
        analysis["recommendations"].append(
            f"Many subgraphs ({analysis['subgraph_count']}). "
            f"Verify each subgraph is necessary vs. simple nodes."
        )
    
    # Check for unnecessary complexity (PATTERN DETECTION)
    # Why: Common anti-pattern - overengineering
    nodes = plan.get("nodes", [])
    simple_passthrough = [n for n in nodes if "passthrough" in n.get("processing", "").lower()]
    
    if simple_passthrough:
        analysis["recommendations"].append(
            f"Found {len(simple_passthrough)} potential passthrough nodes. "
            f"Consider removing if they don't add value."
        )
    
    return analysis


def main():
    """
    Main validation workflow
    
    Why this order:
    1. Structure first (fast, catches basic errors)
    2. Logic second (moderate, catches routing errors)
    3. Complexity last (informational, helps future maintenance)
    """
    if len(sys.argv) < 2:
        print("Usage: python check_structure.py <plan.json>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)
        
        print("=" * 60)
        print("FINAL STRUCTURE CHECK")
        print("=" * 60)
        
        # Phase 1: Structure validation
        structure_issues = check_structure(plan)
        if structure_issues:
            print("\n📋 Structure Issues:")
            for issue in structure_issues:
                print(f"  {issue}")
        else:
            print("\n✓ Structure validation PASSED")
        
        # Phase 2: Logic control validation
        logic_issues = check_logic_control(plan)
        if logic_issues:
            print("\n🧠 Logic Control Issues:")
            for issue in logic_issues:
                print(f"  {issue}")
        else:
            print("\n✓ Logic control validation PASSED")
        
        # Phase 3: Complexity analysis
        complexity = analyze_complexity(plan)
        print(f"\n📊 Complexity Analysis:")
        print(f"  Nodes: {complexity['node_count']}")
        print(f"  Conditional Edges: {complexity['conditional_edges_count']}")
        print(f"  Subgraphs: {complexity['subgraph_count']}")
        print(f"  Complexity Score: {complexity['complexity_score']}/100")
        
        if complexity['recommendations']:
            print(f"\n💡 Simplification Recommendations:")
            for rec in complexity['recommendations']:
                print(f"  • {rec}")
        else:
            print(f"\n✓ Complexity is reasonable")
        
        # Return code
        has_errors = any("ERROR" in i for i in structure_issues + logic_issues)
        return 1 if has_errors else 0
    
    except Exception as e:
        print(f"ERROR: Failed to check structure: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
