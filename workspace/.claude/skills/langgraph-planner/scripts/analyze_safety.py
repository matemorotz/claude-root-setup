#!/usr/bin/env python3
"""
Safety analysis: Identify potential runtime risks

Why this matters:
- Production graphs must be resilient to failures
- Safety issues cause customer-facing failures
- Prevention is cheaper than debugging in production

Design philosophy:
- Start with critical safety checks (fast to compute)
- Add defensive layers only where needed (avoid over-engineering)
- Fail safe, not fail secure (graceful degradation over hard failures)
"""

import json
import sys
from typing import Dict, Any, List, Set


def check_termination_safety(plan: Dict[str, Any]) -> List[str]:
    """
    Verify multiple layers of termination protection
    
    Why multiple layers: Single point of failure is risky
    Why this approach: Defense in depth (security principle)
    """
    issues = []
    
    # Layer 1: Explicit termination flags in state
    state_fields = {f.get("name") for f in plan.get("state_schema", {}).get("fields", [])}
    termination_flags = {"task_complete", "plan_complete", "done", "finished"}
    
    has_completion_flag = bool(state_fields & termination_flags)
    if not has_completion_flag:
        issues.append(
            "WARNING: No explicit completion flag in state. "
            "Recommended: Add 'task_complete' or 'plan_complete' field."
        )
    
    # Layer 2: Safety counters
    safety_counters = {"iteration_count", "retry_count", "error_count", "loop_count"}
    has_safety_counter = bool(state_fields & safety_counters)
    
    if not has_safety_counter:
        issues.append(
            "ERROR: No safety counter in state. "
            "CRITICAL: Add 'iteration_count' to prevent infinite loops."
        )
    
    # Layer 3: Error tracking
    error_fields = {"error_count", "error_message", "errors", "failed_count"}
    has_error_tracking = bool(state_fields & error_fields)
    
    if not has_error_tracking:
        issues.append(
            "WARNING: No error tracking in state. "
            "Recommended: Add 'error_count' to handle cascading failures."
        )
    
    # Layer 4: Check conditional edges use safety counters
    for edge in plan.get("conditional_edges", []):
        logic = edge.get("logic", "").lower()
        uses_counter = any(counter in logic for counter in safety_counters)
        
        if not uses_counter:
            issues.append(
                f"WARNING: Conditional edge from '{edge.get('from')}' "
                f"doesn't check safety counters in routing logic."
            )
    
    return issues


def check_error_handling(plan: Dict[str, Any]) -> List[str]:
    """
    Verify error handling strategy exists
    
    Why: Unhandled errors crash graphs and lose user data
    Design: Check for error handling at each layer (node, edge, graph)
    """
    issues = []
    
    nodes = plan.get("nodes", [])
    
    # Check LLM nodes have error handling
    llm_nodes = [n for n in nodes if "llm" in n.get("type", "").lower()]
    
    for node in llm_nodes:
        error_handling = node.get("error_handling", "")
        if not error_handling or "none" in error_handling.lower():
            issues.append(
                f"WARNING: LLM node '{node.get('name')}' missing error handling strategy. "
                f"LLM calls can fail - add try/except wrapper."
            )
    
    # Check for circuit breaker or retry logic
    has_retry = any("retry" in n.get("error_handling", "").lower() for n in nodes)
    has_circuit_breaker = any("circuit" in str(plan).lower() or "breaker" in str(plan).lower())
    
    if not has_retry:
        issues.append(
            "INFO: No retry logic detected. "
            "Consider adding retry for transient failures."
        )
    
    return issues


def check_resource_safety(plan: Dict[str, Any]) -> List[str]:
    """
    Check for resource exhaustion risks
    
    Why: Prevent memory leaks, token overflow, rate limit violations
    Simple solution: Check for obvious risks, don't overengineer
    """
    issues = []
    
    # Check 1: Message history accumulation (COMMON PROBLEM)
    # Why: Unbounded message list causes context overflow
    state_fields = plan.get("state_schema", {}).get("fields", [])
    messages_field = next((f for f in state_fields if f.get("name") == "messages"), None)
    
    if messages_field:
        # Check if any node mentions pruning/windowing
        has_pruning = any(
            "prune" in n.get("processing", "").lower() or
            "window" in n.get("processing", "").lower() or
            "limit" in n.get("processing", "").lower()
            for n in plan.get("nodes", [])
        )
        
        if not has_pruning:
            issues.append(
                "WARNING: Messages field exists but no conversation windowing detected. "
                "For long conversations, add message pruning (keep last N messages)."
            )
    
    # Check 2: Parallel processing limits
    parallel_nodes = [n for n in plan.get("nodes", []) if "parallel" in n.get("type", "").lower()]
    
    for node in parallel_nodes:
        processing = node.get("processing", "")
        has_limit = "semaphore" in processing.lower() or "limit" in processing.lower()
        
        if not has_limit:
            issues.append(
                f"WARNING: Parallel node '{node.get('name')}' missing concurrency limit. "
                f"Add Semaphore to prevent resource exhaustion."
            )
    
    # Check 3: Large data accumulation
    # Why: Unbounded lists in state cause memory issues
    for field in state_fields:
        field_type = field.get("type", "")
        if "List" in field_type or "list" in field_type:
            field_name = field.get("name")
            if field_name != "messages":  # Messages already checked
                issues.append(
                    f"INFO: State field '{field_name}' is a list. "
                    f"If unbounded, consider adding size limit or periodic cleanup."
                )
    
    return issues


def check_data_validation(plan: Dict[str, Any]) -> List[str]:
    """
    Verify inputs are validated before use
    
    Why: Invalid data causes crashes or incorrect behavior
    Design choice: Check for validation patterns, suggest where missing
    """
    issues = []
    
    nodes = plan.get("nodes", [])
    
    # Check for validation nodes
    validation_nodes = [n for n in nodes if "validation" in n.get("type", "").lower()]
    
    # Check LLM nodes that generate JSON have validation
    llm_nodes = [n for n in nodes if "llm" in n.get("type", "").lower()]
    json_nodes = [n for n in llm_nodes if "json" in n.get("processing", "").lower()]
    
    if json_nodes and not validation_nodes:
        issues.append(
            "WARNING: LLM nodes generate JSON but no validation nodes found. "
            "Add syntax checker to validate JSON before use."
        )
    
    # Check for Pydantic models
    has_pydantic = "pydantic" in str(plan).lower() or "BaseModel" in str(plan)
    
    if json_nodes and not has_pydantic:
        issues.append(
            "INFO: No Pydantic models detected. "
            "Consider adding schema validation for type safety."
        )
    
    return issues


def check_secrets_and_credentials(plan: Dict[str, Any]) -> List[str]:
    """
    Check for security risks in plan
    
    Why: Leaked credentials are critical security issues
    Simple approach: Pattern matching for common mistakes
    """
    issues = []
    
    plan_str = json.dumps(plan).lower()
    
    # Check for hardcoded secrets (SIMPLE pattern matching)
    # Why simple: Comprehensive secret scanning is complex, this catches obvious mistakes
    secret_patterns = ["api_key", "password", "secret", "token", "credential"]
    
    for pattern in secret_patterns:
        if f'"{pattern}":' in plan_str or f"'{pattern}':" in plan_str:
            # Check if it mentions environment variable or config
            if "env" not in plan_str and "config" not in plan_str:
                issues.append(
                    f"WARNING: Found '{pattern}' in plan. "
                    f"Ensure secrets are loaded from environment variables, not hardcoded."
                )
                break
    
    return issues


def generate_safety_score(all_issues: List[str]) -> Dict[str, Any]:
    """
    Calculate overall safety score
    
    Why: Give users a quick sense of risk level
    Design: Simple scoring, clear thresholds
    """
    errors = len([i for i in all_issues if "ERROR" in i])
    warnings = len([i for i in all_issues if "WARNING" in i])
    
    # Scoring (SIMPLE formula)
    # Why: Easy to understand, penalizes errors more than warnings
    max_score = 100
    score = max_score - (errors * 25) - (warnings * 5)
    score = max(0, score)  # Floor at 0
    
    if score >= 90:
        rating = "EXCELLENT"
        color = "🟢"
    elif score >= 70:
        rating = "GOOD"
        color = "🟡"
    elif score >= 50:
        rating = "NEEDS IMPROVEMENT"
        color = "🟠"
    else:
        rating = "CRITICAL ISSUES"
        color = "🔴"
    
    return {
        "score": score,
        "rating": rating,
        "color": color,
        "errors": errors,
        "warnings": warnings
    }


def main():
    """
    Safety analysis workflow
    
    Order matters:
    1. Termination (most critical - prevents stuck graphs)
    2. Error handling (critical - prevents crashes)
    3. Resource safety (important - prevents exhaustion)
    4. Data validation (important - prevents corruption)
    5. Security (critical but separate concern)
    """
    if len(sys.argv) < 2:
        print("Usage: python analyze_safety.py <plan.json>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)
        
        print("=" * 60)
        print("SAFETY ANALYSIS")
        print("=" * 60)
        
        all_issues = []
        
        # 1. Termination Safety (CRITICAL)
        print("\n🛑 Termination Safety:")
        termination_issues = check_termination_safety(plan)
        if termination_issues:
            for issue in termination_issues:
                print(f"  {issue}")
            all_issues.extend(termination_issues)
        else:
            print("  ✓ Termination safety checks passed")
        
        # 2. Error Handling (CRITICAL)
        print("\n⚠️  Error Handling:")
        error_issues = check_error_handling(plan)
        if error_issues:
            for issue in error_issues:
                print(f"  {issue}")
            all_issues.extend(error_issues)
        else:
            print("  ✓ Error handling checks passed")
        
        # 3. Resource Safety (IMPORTANT)
        print("\n💾 Resource Safety:")
        resource_issues = check_resource_safety(plan)
        if resource_issues:
            for issue in resource_issues:
                print(f"  {issue}")
            all_issues.extend(resource_issues)
        else:
            print("  ✓ Resource safety checks passed")
        
        # 4. Data Validation (IMPORTANT)
        print("\n✅ Data Validation:")
        validation_issues = check_data_validation(plan)
        if validation_issues:
            for issue in validation_issues:
                print(f"  {issue}")
            all_issues.extend(validation_issues)
        else:
            print("  ✓ Data validation checks passed")
        
        # 5. Security (CRITICAL)
        print("\n🔒 Security:")
        security_issues = check_secrets_and_credentials(plan)
        if security_issues:
            for issue in security_issues:
                print(f"  {issue}")
            all_issues.extend(security_issues)
        else:
            print("  ✓ Security checks passed")
        
        # Overall Safety Score
        safety_score = generate_safety_score(all_issues)
        print("\n" + "=" * 60)
        print(f"{safety_score['color']} SAFETY SCORE: {safety_score['score']}/100 - {safety_score['rating']}")
        print("=" * 60)
        print(f"Errors: {safety_score['errors']}, Warnings: {safety_score['warnings']}")
        
        # Return code based on errors
        return 1 if safety_score['errors'] > 0 else 0
    
    except Exception as e:
        print(f"ERROR: Failed safety analysis: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
