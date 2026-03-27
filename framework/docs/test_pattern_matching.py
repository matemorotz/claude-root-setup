#!/usr/bin/env python3
"""
Comprehensive Test Suite for Semantic Pattern Matching

Tests the three-layer matching strategy:
1. Direct keyword matching
2. Keyword-to-pattern mapping (semantic understanding)
3. Fuzzy string matching (variations and synonyms)

Target: 80%+ accuracy on 20 real-world task descriptions
"""

import sys
from typing import Dict, List, Tuple
from pattern_matcher import SemanticPatternMatcher
from context_distiller import TaskContextEngineer


# Test patterns (realistic project patterns)
TEST_PATTERNS = {
    "authentication": {
        "pattern": "JWT with bcrypt",
        "files": ["app/auth.py", "app/middleware/auth.py"],
        "conventions": ["Use @require_auth decorator", "Hash passwords with bcrypt"]
    },
    "database": {
        "pattern": "SQLAlchemy ORM",
        "files": ["app/models/user.py", "app/models/post.py"],
        "conventions": ["Use Alembic for migrations", "Define models with declarative base"]
    },
    "api_design": {
        "pattern": "FastAPI REST",
        "files": ["app/routes/user.py", "app/routes/posts.py"],
        "conventions": ["Use Pydantic for schemas", "Return proper HTTP status codes"]
    },
    "file_handling": {
        "pattern": "S3 storage with Pillow validation",
        "files": ["app/storage/s3.py", "app/utils/image.py"],
        "conventions": ["Validate file types before upload", "Generate unique filenames"]
    },
    "testing": {
        "pattern": "pytest with fixtures",
        "files": ["tests/conftest.py", "tests/test_api.py"],
        "conventions": ["Use pytest fixtures", "Aim for 80%+ coverage"]
    },
    "error_handling": {
        "pattern": "Structured logging with Sentry",
        "files": ["app/utils/logger.py", "app/middleware/error.py"],
        "conventions": ["Log all errors", "Use try-except blocks"]
    },
    "frontend": {
        "pattern": "React with TypeScript",
        "files": ["src/components/", "src/pages/"],
        "conventions": ["Use functional components", "TypeScript strict mode"]
    },
    "caching": {
        "pattern": "Redis for session and data cache",
        "files": ["app/cache/redis.py"],
        "conventions": ["Set TTL on all cached items"]
    },
}


# 20 real-world test cases with expected matches
TEST_CASES = [
    # Authentication-related tasks (should match "authentication")
    ("Add password reset endpoint", ["authentication", "api_design"]),
    ("Implement user login flow", ["authentication", "api_design"]),
    ("Create JWT token refresh mechanism", ["authentication"]),
    ("Add session management", ["authentication"]),
    ("Implement user logout functionality", ["authentication"]),

    # API-related tasks
    ("Create new REST endpoint for posts", ["api_design"]),
    ("Add POST /users endpoint", ["api_design"]),
    ("Implement GraphQL resolver", ["api_design"]),

    # Database-related tasks
    ("Add user model to database", ["database", "authentication"]),
    ("Create database migration for posts table", ["database"]),
    ("Implement ORM query optimization", ["database"]),
    ("Add SQL index on email field", ["database"]),

    # File handling tasks
    ("Implement image upload feature", ["file_handling", "api_design"]),
    ("Add PDF file processing", ["file_handling"]),
    ("Create S3 bucket integration", ["file_handling"]),

    # Testing tasks
    ("Write unit tests for authentication", ["testing", "authentication"]),
    ("Add integration tests", ["testing"]),
    ("Create pytest fixtures for database", ["testing", "database"]),

    # Mixed/complex tasks
    ("Build user profile page with image upload", ["frontend", "file_handling", "authentication"]),
    ("Implement error logging with Sentry", ["error_handling"]),
]


def run_test_case(
    matcher: SemanticPatternMatcher,
    task: str,
    expected_patterns: List[str]
) -> Tuple[bool, Dict]:
    """
    Run a single test case and return pass/fail status.

    Returns:
        Tuple of (passed: bool, match_details: Dict)
    """
    # Get pattern matches
    matches = matcher.match_patterns(task, TEST_PATTERNS)
    matched_patterns = list(matches.keys())

    # Check if all expected patterns were matched
    expected_set = set(expected_patterns)
    matched_set = set(matched_patterns)

    # Calculate metrics
    true_positives = len(expected_set & matched_set)
    false_positives = len(matched_set - expected_set)
    false_negatives = len(expected_set - matched_set)

    # Pass if we got all expected patterns (false negatives = 0)
    # Allow some false positives (they're often useful extra context)
    passed = false_negatives == 0 and false_positives <= 1

    return passed, {
        "task": task,
        "expected": expected_patterns,
        "matched": matched_patterns,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "match_details": matches
    }


def run_all_tests() -> Tuple[int, int, List[Dict]]:
    """
    Run all test cases and return results.

    Returns:
        Tuple of (passed_count, total_count, detailed_results)
    """
    matcher = SemanticPatternMatcher()

    passed = 0
    total = len(TEST_CASES)
    results = []

    print("=" * 80)
    print("SEMANTIC PATTERN MATCHING TEST SUITE")
    print("=" * 80)
    print(f"Running {total} test cases...")
    print()

    for i, (task, expected) in enumerate(TEST_CASES, 1):
        test_passed, details = run_test_case(matcher, task, expected)
        results.append(details)

        if test_passed:
            passed += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"Test {i:2d}/{total}: {status}")
        print(f"  Task: {task}")
        print(f"  Expected: {expected}")
        print(f"  Matched:  {details['matched']}")

        if not test_passed:
            if details['false_negatives'] > 0:
                print(f"  MISSING: {list(set(expected) - set(details['matched']))}")
            if details['false_positives'] > 1:
                print(f"  EXTRA: {list(set(details['matched']) - set(expected))}")

        print()

    return passed, total, results


def calculate_accuracy_metrics(results: List[Dict]) -> Dict:
    """Calculate detailed accuracy metrics."""
    total_tp = sum(r['true_positives'] for r in results)
    total_fp = sum(r['false_positives'] for r in results)
    total_fn = sum(r['false_negatives'] for r in results)

    # Precision: TP / (TP + FP)
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0

    # Recall: TP / (TP + FN)
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0

    # F1 score: 2 * (Precision * Recall) / (Precision + Recall)
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn
    }


def main():
    """Run test suite and report results."""
    # Run all tests
    passed, total, results = run_all_tests()

    # Calculate metrics
    metrics = calculate_accuracy_metrics(results)

    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Passed:  {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Tests Failed:  {total-passed}/{total}")
    print()

    print("ACCURACY METRICS:")
    print(f"  Precision: {metrics['precision']:.2%} (how many matched patterns were correct)")
    print(f"  Recall:    {metrics['recall']:.2%} (how many expected patterns were found)")
    print(f"  F1 Score:  {metrics['f1_score']:.2%} (harmonic mean of precision & recall)")
    print()

    print("CONFUSION MATRIX:")
    print(f"  True Positives:  {metrics['true_positives']} (correct matches)")
    print(f"  False Positives: {metrics['false_positives']} (extra matches)")
    print(f"  False Negatives: {metrics['false_negatives']} (missed matches)")
    print()

    # Determine overall result
    accuracy = passed / total
    target_accuracy = 0.80

    if accuracy >= target_accuracy:
        print(f"✓ SUCCESS: Achieved {accuracy:.1%} accuracy (target: {target_accuracy:.0%})")
        print("  Semantic pattern matching is PRODUCTION READY")
        return 0
    else:
        print(f"✗ FAILED: Achieved {accuracy:.1%} accuracy (target: {target_accuracy:.0%})")
        print("  Need to improve pattern matching")
        return 1


if __name__ == "__main__":
    sys.exit(main())
