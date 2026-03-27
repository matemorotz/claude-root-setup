#!/usr/bin/env python3
"""Quick test for HorizontalPlanSplitter"""

import sys
from pathlib import Path

# Add fractal to path
sys.path.insert(0, str(Path(__file__).parent))

from plan_splitter import HorizontalPlanSplitter, Boundary
from fractal_memory import FractalMemory


def test_boundary_detection():
    """Test boundary detection from seed rules"""
    print("Testing boundary detection...")

    # Mock seed rules
    seed_rules = {
        "project": "test",
        "patterns": {
            "authentication": {"files": ["app/auth.py"], "boundary": "auth_logic"},
            "database": {"files": ["app/models/"], "boundary": "db_schema"},
            "api_design": {"files": ["app/routes/"], "boundary": "api_routes"}
        },
        "conventions": {},
        "architecture": {}
    }

    # Mock sections
    sections = [
        {
            "section_id": "s1",
            "title": "Implement authentication logic",
            "metadata": {"estimated_steps": 5}
        },
        {
            "section_id": "s2",
            "title": "Create database models",
            "metadata": {"estimated_steps": 3}
        },
        {
            "section_id": "s3",
            "title": "Add API routes",
            "metadata": {"estimated_steps": 4}
        }
    ]

    # Create splitter (without fractal memory for now)
    class MockMemory:
        class opus_level:
            @staticmethod
            def get_seed_rules(project):
                return seed_rules

    splitter = HorizontalPlanSplitter(MockMemory())

    # Detect boundaries
    boundaries = splitter._detect_boundaries(sections, seed_rules)

    print(f"✓ Detected {len(boundaries)} boundaries:")
    for boundary in boundaries:
        print(f"  - {boundary.name}: {len(boundary.sections)} sections, complexity={boundary.complexity}")

    assert len(boundaries) == 3, f"Expected 3 boundaries, got {len(boundaries)}"
    print("✓ Boundary detection works!\n")


def test_seed_filtering():
    """Test seed rule filtering by boundary"""
    print("Testing seed rule filtering...")

    all_seed_rules = {
        "project": "test",
        "patterns": {
            "authentication": {"files": ["app/auth.py"], "boundary": "auth_logic"},
            "database": {"files": ["app/models/"], "boundary": "db_schema"},
            "api_design": {"files": ["app/routes/"], "boundary": "api_routes"}
        },
        "conventions": {
            "coding_style": ["Use type hints"],
            "testing": ["Write tests"]
        },
        "architecture": {
            "decisions": [],
            "patterns": [],
            "dependencies": []
        },
        "tech_stack": ["Python", "FastAPI"]
    }

    sections = [
        {"section_id": "s1", "title": "Auth", "steps": []}
    ]

    class MockMemory:
        class opus_level:
            @staticmethod
            def get_seed_rules(project):
                return all_seed_rules

    splitter = HorizontalPlanSplitter(MockMemory())

    # Filter for auth boundary
    filtered = splitter._filter_seeds_for_boundary(all_seed_rules, "auth_logic", sections)

    print(f"✓ Original patterns: {len(all_seed_rules['patterns'])}")
    print(f"✓ Filtered patterns: {len(filtered['patterns'])}")

    # Should only include auth pattern
    assert "authentication" in filtered["patterns"], "Auth pattern missing"
    assert len(filtered["patterns"]) <= len(all_seed_rules["patterns"]), "Filtered should be smaller"

    print("✓ Seed filtering works!\n")


def test_should_split():
    """Test split decision logic"""
    print("Testing split decision...")

    # Create plan that SHOULD split (with multiple boundaries!)
    plan_should_split = {
        "project": "test",
        "sections": [
            {"section_id": "s1", "metadata": {"estimated_steps": 5, "boundary": "auth_logic"}},
            {"section_id": "s2", "metadata": {"estimated_steps": 5, "boundary": "auth_logic"}},
            {"section_id": "s3", "metadata": {"estimated_steps": 5, "boundary": "db_schema"}},
            {"section_id": "s4", "metadata": {"estimated_steps": 5, "boundary": "api_routes"}},
            {"section_id": "s5", "metadata": {"estimated_steps": 5, "boundary": "api_routes"}},
        ]  # 5 sections, 25 total steps, 3 boundaries
    }

    # Create plan that should NOT split
    plan_no_split = {
        "project": "test",
        "sections": [
            {"section_id": "s1", "metadata": {"estimated_steps": 2}},
            {"section_id": "s2", "metadata": {"estimated_steps": 3}}
        ]  # Only 2 sections, 5 total steps
    }

    seed_rules = {
        "project": "test",
        "patterns": {
            "pattern1": {"boundary": "b1"},
            "pattern2": {"boundary": "b2"}
        }
    }

    class MockMemory:
        class opus_level:
            @staticmethod
            def get_seed_rules(project):
                return seed_rules

    splitter = HorizontalPlanSplitter(MockMemory())

    should_split_1 = splitter.should_split(plan_should_split)
    should_split_2 = splitter.should_split(plan_no_split)

    print(f"✓ Complex plan (5 sections, 25 steps): should_split={should_split_1}")
    print(f"✓ Simple plan (2 sections, 5 steps): should_split={should_split_2}")

    assert should_split_1 == True, "Complex plan should split"
    assert should_split_2 == False, "Simple plan should not split"

    print("✓ Split decision logic works!\n")


if __name__ == "__main__":
    print("=== Testing HorizontalPlanSplitter ===\n")

    test_boundary_detection()
    test_seed_filtering()
    test_should_split()

    print("=== All tests passed! ===")
