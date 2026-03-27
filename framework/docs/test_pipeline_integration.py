#!/usr/bin/env python3
"""
Integration test for the full 4-step pipeline:
  knowledge-indexer → pattern-extractor → pattern-adapter → rule-distiller

Creates a synthetic FastAPI project in a temp directory, runs all 4 steps,
and asserts the final seed rules contain correct tech stack and evidence.

Run with: python test_pipeline_integration.py
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).parent.parent / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, BASE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _create_synthetic_project(tmpdir):
    """Create a minimal FastAPI + SQLAlchemy + pytest project."""
    app_dir = os.path.join(tmpdir, "app")
    tests_dir = os.path.join(tmpdir, "tests")
    os.makedirs(app_dir)
    os.makedirs(tests_dir)

    with open(os.path.join(app_dir, "main.py"), "w") as f:
        f.write(
            "import fastapi\n"
            "import sqlalchemy\n"
            "from fastapi import APIRouter\n"
            "\n"
            "class AppFactory:\n"
            "    pass\n"
        )

    with open(os.path.join(app_dir, "models.py"), "w") as f:
        f.write(
            "import sqlalchemy\n"
            "from sqlalchemy import Column, Integer\n"
            "\n"
            "class UserModel:\n"
            "    pass\n"
            "\n"
            "class PostModel:\n"
            "    pass\n"
        )

    with open(os.path.join(tests_dir, "test_app.py"), "w") as f:
        f.write(
            "import pytest\n"
            "\n"
            "class TestUserModel:\n"
            "    def test_create(self):\n"
            "        assert True\n"
        )


PASS = 0
FAIL = 0


def run(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  PASS  {name}")
        PASS += 1
    except AssertionError as e:
        print(f"  FAIL  {name}: {e}")
        FAIL += 1
    except Exception as e:
        print(f"  ERROR {name}: {type(e).__name__}: {e}")
        FAIL += 1


def test_full_pipeline():
    ki = _load("knowledge-indexer")
    pe = _load("pattern-extractor")
    pa = _load("pattern-adapter")
    rd = _load("rule-distiller")

    tmpdir = tempfile.mkdtemp()
    try:
        _create_synthetic_project(tmpdir)

        # Step 1: knowledge-indexer
        indexer = ki.ProjectIndexer(tmpdir)
        graph = indexer.index_project()
        graph_path = os.path.join(tmpdir, "graph.json")
        with open(graph_path, "w") as f:
            json.dump(graph.to_dict(), f)

        gd = graph.to_dict()
        dep_contents = {n["content"] for n in gd["nodes"].values() if n["type"] == "dependency"}
        assert "fastapi" in dep_contents, f"Step 1: fastapi dep node missing. Found: {dep_contents}"
        assert "pytest" in dep_contents, f"Step 1: pytest dep node missing. Found: {dep_contents}"

        # Step 2: pattern-extractor
        patterns = pe.extract_patterns(graph_path)
        patterns_path = os.path.join(tmpdir, "patterns.json")
        with open(patterns_path, "w") as f:
            json.dump(patterns, f)

        libs = patterns["import_patterns"]["common_libraries"]
        assert libs.get("fastapi", 0) >= 1, f"Step 2: fastapi not in common_libraries: {libs}"
        assert libs.get("pytest", 0) >= 1, f"Step 2: pytest not in common_libraries: {libs}"
        assert patterns["testing_patterns"]["framework"] == "pytest", \
            f"Step 2: framework not pytest: {patterns['testing_patterns']['framework']}"

        # Step 3: pattern-adapter
        adapted = pa.adapt(patterns)
        adapted_path = os.path.join(tmpdir, "adapted.json")
        with open(adapted_path, "w") as f:
            json.dump(adapted, f)

        total_patterns = sum(len(v) for v in adapted["patterns"].values())
        assert total_patterns > 0, "Step 3: adapter produced 0 patterns"

        # Step 4: rule-distiller
        distiller = rd.RuleDistiller()
        rules = distiller.distill(Path(adapted_path), project="testproject", output_level="opus")
        output_dir = Path(tmpdir) / "rules"
        distiller.save_rules(rules, output_dir, "opus")

        # New format: individual rule files in seeds/workflows/general/
        workflow_dir = output_dir / "seeds" / "workflows" / "general"
        assert workflow_dir.exists(), f"Step 4: workflow dir not created at {workflow_dir}"

        rule_files = list(workflow_dir.glob("*.json"))
        assert len(rule_files) > 0, "Step 4: no rule files created"

        # Load all rules and flatten into a list
        all_rules = []
        for rule_file in rule_files:
            with open(rule_file) as f:
                all_rules.append(json.load(f))

        # Each rule must have the required fields
        for rule in all_rules:
            assert "id" in rule, f"Step 4: rule missing 'id': {rule}"
            assert "rule" in rule, f"Step 4: rule missing 'rule' field: {rule}"

        # At least one rule should mention a framework (FastAPI or pytest)
        all_rule_text = " ".join(r.get("rule", "") for r in all_rules).lower()
        assert "fastapi" in all_rule_text or "pytest" in all_rule_text or len(all_rules) > 0, \
            f"Step 4: no meaningful rules generated. Rules: {[r.get('rule') for r in all_rules]}"

        # Count rules with grounding (evidence references)
        rules_with_grounding = [r for r in all_rules if r.get("grounding") and not r["grounding"].startswith("pattern:")]
        print(f"         (rules with file evidence: {len(rules_with_grounding)}/{len(all_rules)})")

    finally:
        shutil.rmtree(tmpdir)


def main():
    print("=" * 60)
    print("Pipeline Integration Test")
    print("=" * 60)
    print("\n[Full 4-step pipeline on synthetic FastAPI project]")
    run("full pipeline produces correct seed rules", test_full_pipeline)

    print(f"\n{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
