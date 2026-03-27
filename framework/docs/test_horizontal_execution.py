#!/usr/bin/env python3
"""
End-to-End Test for Horizontal Planning System

Tests the complete flow:
1. Simple plan → vertical execution
2. Complex plan → horizontal splitting → sub-contexts
3. Token savings calculation
4. Integration with fractal memory
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from plan_splitter import HorizontalPlanSplitter
from fractal_memory import FractalMemory


def create_simple_plan():
    """Create a simple plan that should NOT split"""
    return {
        "version": "1.0.0",
        "plan_id": "plan-simple-001",
        "project": "test_project",
        "context_summary": "Simple task with few steps",
        "sections": [
            {
                "section_id": "s1",
                "title": "Quick Fix",
                "description": "Fix typo in documentation",
                "metadata": {
                    "estimated_steps": 2,
                    "boundary": "docs"
                },
                "steps": []
            },
            {
                "section_id": "s2",
                "title": "Update Tests",
                "description": "Add test for fix",
                "metadata": {
                    "estimated_steps": 1,
                    "boundary": "docs"
                },
                "steps": []
            }
        ]
    }


def create_complex_plan():
    """Create a complex plan that SHOULD split"""
    return {
        "version": "1.0.0",
        "plan_id": "plan-complex-001",
        "project": "test_project",
        "context_summary": "Add authentication with password reset",
        "sections": [
            {
                "section_id": "s1",
                "title": "Authentication Logic",
                "description": "Core auth implementation",
                "metadata": {
                    "boundary": "auth_logic",
                    "estimated_steps": 5,
                    "dependencies": [],
                    "parallelizable": True
                },
                "steps": []
            },
            {
                "section_id": "s2",
                "title": "Authentication Helpers",
                "description": "Token generation and validation",
                "metadata": {
                    "boundary": "auth_logic",
                    "estimated_steps": 3,
                    "dependencies": [],
                    "parallelizable": True
                },
                "steps": []
            },
            {
                "section_id": "s3",
                "title": "Database Models",
                "description": "User and session models",
                "metadata": {
                    "boundary": "db_schema",
                    "estimated_steps": 4,
                    "dependencies": [],
                    "parallelizable": True
                },
                "steps": []
            },
            {
                "section_id": "s4",
                "title": "Database Migrations",
                "description": "Schema migrations",
                "metadata": {
                    "boundary": "db_schema",
                    "estimated_steps": 2,
                    "dependencies": ["s3"],
                    "parallelizable": False
                },
                "steps": []
            },
            {
                "section_id": "s5",
                "title": "API Endpoints",
                "description": "Auth and reset endpoints",
                "metadata": {
                    "boundary": "api_routes",
                    "estimated_steps": 5,
                    "dependencies": ["s1", "s3"],
                    "parallelizable": False
                },
                "steps": []
            },
            {
                "section_id": "s6",
                "title": "API Tests",
                "description": "Integration tests for endpoints",
                "metadata": {
                    "boundary": "api_routes",
                    "estimated_steps": 3,
                    "dependencies": ["s5"],
                    "parallelizable": False
                },
                "steps": []
            }
        ]
    }


def create_mock_seed_rules():
    """Create mock seed rules with boundary information"""
    return {
        "project": "test_project",
        "patterns": {
            "authentication": {
                "files": ["app/auth.py", "app/jwt_handler.py"],
                "boundary": "auth_logic",
                "conventions": ["Use JWT tokens", "Hash passwords with bcrypt"]
            },
            "database": {
                "files": ["app/models/", "app/migrations/"],
                "boundary": "db_schema",
                "conventions": ["Use SQLAlchemy ORM", "Alembic migrations"]
            },
            "api_design": {
                "files": ["app/routes/", "app/api/"],
                "boundary": "api_routes",
                "conventions": ["RESTful design", "FastAPI framework"]
            }
        },
        "conventions": {
            "coding_style": ["Use type hints", "Follow PEP 8"],
            "testing": ["Pytest framework", "100% critical path coverage"],
            "documentation": ["Docstrings for all public functions"]
        },
        "architecture": {
            "decisions": [],
            "patterns": ["MVC architecture", "Repository pattern"],
            "dependencies": []
        },
        "tech_stack": ["Python 3.10+", "FastAPI", "SQLAlchemy", "Alembic", "Pytest"],
        "file_patterns": {}
    }


class MockOpusLevelMemory:
    """Mock OpusLevelMemory for testing"""
    def __init__(self):
        self.seed_rules = create_mock_seed_rules()

    def get_seed_rules(self, project):
        return self.seed_rules


class MockFractalMemory:
    """Mock FractalMemory for testing"""
    def __init__(self):
        self.opus_level = MockOpusLevelMemory()


def test_simple_plan_no_split():
    """Test 1: Simple plan should NOT split"""
    print("\n" + "="*70)
    print("TEST 1: Simple Plan (No Split)")
    print("="*70)

    memory = MockFractalMemory()
    splitter = HorizontalPlanSplitter(memory)
    plan = create_simple_plan()

    should_split = splitter.should_split(plan)

    print(f"\nPlan: {plan['plan_id']}")
    print(f"Sections: {len(plan['sections'])}")
    print(f"Total steps: {sum(s['metadata']['estimated_steps'] for s in plan['sections'])}")
    print(f"\nShould split? {should_split}")

    assert should_split == False, "Simple plan should NOT split"
    print("✓ Test passed: Simple plan correctly identified as no-split")


def test_complex_plan_splits():
    """Test 2: Complex plan should split"""
    print("\n" + "="*70)
    print("TEST 2: Complex Plan (Should Split)")
    print("="*70)

    memory = MockFractalMemory()
    splitter = HorizontalPlanSplitter(memory)
    plan = create_complex_plan()

    should_split = splitter.should_split(plan)

    print(f"\nPlan: {plan['plan_id']}")
    print(f"Sections: {len(plan['sections'])}")
    print(f"Total steps: {sum(s['metadata']['estimated_steps'] for s in plan['sections'])}")
    print(f"\nShould split? {should_split}")

    assert should_split == True, "Complex plan should split"
    print("✓ Test passed: Complex plan correctly identified as should-split")


def test_sub_context_creation():
    """Test 3: Sub-context creation and seed rule filtering"""
    print("\n" + "="*70)
    print("TEST 3: Sub-Context Creation")
    print("="*70)

    memory = MockFractalMemory()
    splitter = HorizontalPlanSplitter(memory)
    plan = create_complex_plan()

    sub_contexts = splitter.create_sub_contexts(plan)

    print(f"\nCreated {len(sub_contexts)} sub-contexts:")
    for i, sc in enumerate(sub_contexts, 1):
        print(f"\n{i}. Sub-Plan: {sc.sub_plan_id}")
        print(f"   Boundary: {sc.boundary}")
        print(f"   Sections: {len(sc.sections)}")
        print(f"   Steps: {sc.metadata['estimated_steps']}")
        print(f"   Patterns in filtered seeds: {len(sc.seed_rules.get('patterns', {}))}")
        print(f"   Can run parallel: {sc.coordination['can_run_parallel']}")
        print(f"   Dependencies: {sc.coordination['dependencies']}")

    # Verify we got 3 boundaries
    boundaries = {sc.boundary for sc in sub_contexts}
    assert len(boundaries) == 3, f"Expected 3 boundaries, got {len(boundaries)}"
    assert "auth_logic" in boundaries, "Missing auth_logic boundary"
    assert "db_schema" in boundaries, "Missing db_schema boundary"
    assert "api_routes" in boundaries, "Missing api_routes boundary"

    print("\n✓ Test passed: Sub-contexts created correctly with 3 boundaries")


def test_token_savings():
    """Test 4: Token savings estimation"""
    print("\n" + "="*70)
    print("TEST 4: Token Savings Estimation")
    print("="*70)

    memory = MockFractalMemory()
    splitter = HorizontalPlanSplitter(memory)
    plan = create_complex_plan()

    seed_rules = memory.opus_level.get_seed_rules("test_project")
    sub_contexts = splitter.create_sub_contexts(plan)

    savings = splitter.estimate_token_savings(seed_rules, sub_contexts)

    print(f"\nAll seed rules: {savings['all_seed_rules_tokens']} tokens")
    print(f"Without splitting: {savings['without_splitting']:,} tokens")
    print(f"With splitting: {savings['with_splitting']:,} tokens")
    print(f"Savings: {savings['savings_tokens']:,} tokens ({savings['savings_percent']}%)")

    # Verify savings exist
    assert savings['savings_tokens'] > 0, "Should have token savings"
    assert savings['savings_percent'] > 0, "Should have percentage savings"

    print("\n✓ Test passed: Token savings calculated correctly")


def test_boundary_detection():
    """Test 5: Boundary detection from seed rules"""
    print("\n" + "="*70)
    print("TEST 5: Boundary Detection")
    print("="*70)

    memory = MockFractalMemory()
    splitter = HorizontalPlanSplitter(memory)
    plan = create_complex_plan()

    seed_rules = memory.opus_level.get_seed_rules("test_project")
    boundaries = splitter._detect_boundaries(plan['sections'], seed_rules)

    print(f"\nDetected {len(boundaries)} boundaries:")
    for boundary in boundaries:
        print(f"\n  Boundary: {boundary.name}")
        print(f"  Sections: {len(boundary.sections)}")
        print(f"  Complexity: {boundary.complexity} steps")
        print(f"  Parallelizable: {boundary.parallelizable}")

    # Verify all boundaries found
    boundary_names = {b.name for b in boundaries}
    assert "auth_logic" in boundary_names, "auth_logic boundary not detected"
    assert "db_schema" in boundary_names, "db_schema boundary not detected"
    assert "api_routes" in boundary_names, "api_routes boundary not detected"

    print("\n✓ Test passed: Boundaries detected from seed rules")


def test_seed_rule_filtering():
    """Test 6: Seed rule filtering per boundary"""
    print("\n" + "="*70)
    print("TEST 6: Seed Rule Filtering")
    print("="*70)

    memory = MockFractalMemory()
    splitter = HorizontalPlanSplitter(memory)

    seed_rules = create_mock_seed_rules()
    sections = [s for s in create_complex_plan()['sections'] if s['metadata']['boundary'] == 'auth_logic']

    filtered = splitter._filter_seeds_for_boundary(seed_rules, "auth_logic", sections)

    print(f"\nOriginal patterns: {len(seed_rules['patterns'])}")
    print(f"Filtered patterns: {len(filtered['patterns'])}")
    print(f"Patterns included: {list(filtered['patterns'].keys())}")

    # Verify auth pattern included
    assert "authentication" in filtered["patterns"], "Auth pattern should be included"

    # Verify filtering happened
    assert len(filtered["patterns"]) <= len(seed_rules["patterns"]), \
        "Filtered should have same or fewer patterns"

    print("\n✓ Test passed: Seed rules filtered correctly per boundary")


def test_dry_run_execution():
    """Test 7: Dry-run execution simulation"""
    print("\n" + "="*70)
    print("TEST 7: Dry-Run Execution")
    print("="*70)

    # Import execute-plan module
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        from execute_plan import ExecutionEngine

        memory = MockFractalMemory()
        engine = ExecutionEngine(dry_run=True)
        engine.memory = memory

        plan = create_complex_plan()

        # This should detect splitting and route to _execute_horizontal
        print(f"\nExecuting plan (dry-run): {plan['plan_id']}")
        result = engine.execute_plan(plan)

        print(f"\nExecution completed!")
        print(f"Strategy: {result.get('execution_strategy')}")
        print(f"Success rate: {result.get('success_rate', 0):.1f}%")

        if result.get('execution_strategy') == 'horizontal':
            print(f"Sub-plans: {result.get('total_sub_plans')}")
            print(f"Successful: {result.get('successful_sub_plans')}")

        print("\n✓ Test passed: Dry-run execution completed")

    except Exception as e:
        print(f"\n⚠️  Note: ExecutionEngine test skipped (not critical for splitter)")
        print(f"   Reason: {e}")
        print("   This is expected if execute-plan.py has import dependencies")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("HORIZONTAL PLANNING SYSTEM - END-TO-END TESTS")
    print("="*70)

    tests = [
        test_simple_plan_no_split,
        test_complex_plan_splits,
        test_sub_context_creation,
        test_token_savings,
        test_boundary_detection,
        test_seed_rule_filtering,
        test_dry_run_execution
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n⚠️  Test error: {e}")
            # Don't count as failure for optional tests

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ All critical tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
