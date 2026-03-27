#!/usr/bin/env python3
"""
Unit tests for the knowledge-indexer, pattern-extractor, and pattern-adapter pipeline scripts.

Tests are standalone (no pytest required). Run with: python test_pipeline_unit.py
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
    """Load a hyphenated script as a module."""
    spec = importlib.util.spec_from_file_location(name, BASE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_graph(nodes, edges):
    """Build a minimal graph dict for use as extractor input."""
    return {"nodes": nodes, "edges": edges, "stats": {}}


def _write_graph(graph, tmpdir):
    """Write graph dict to a temp JSON file, return path."""
    path = os.path.join(tmpdir, "graph.json")
    with open(path, "w") as f:
        json.dump(graph, f)
    return path


# ─── Test runners ────────────────────────────────────────────────────────────

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


# ─── Test 1: indexer extracts imports ────────────────────────────────────────

def test_indexer_extracts_imports():
    ki = _load("knowledge-indexer")
    tmpdir = tempfile.mkdtemp()
    try:
        py_file = os.path.join(tmpdir, "main.py")
        with open(py_file, "w") as f:
            f.write("import fastapi\nimport sqlalchemy\n")

        indexer = ki.ProjectIndexer(tmpdir)
        graph = indexer.index_project()
        gd = graph.to_dict()

        dep_contents = {
            n["content"] for n in gd["nodes"].values() if n["type"] == "dependency"
        }
        assert "fastapi" in dep_contents, f"fastapi not in dependency nodes: {dep_contents}"
        assert "sqlalchemy" in dep_contents, f"sqlalchemy not in dependency nodes: {dep_contents}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 2: indexer detects classes ─────────────────────────────────────────

def test_indexer_detects_classes():
    ki = _load("knowledge-indexer")
    tmpdir = tempfile.mkdtemp()
    try:
        py_file = os.path.join(tmpdir, "models.py")
        with open(py_file, "w") as f:
            f.write("class MyModel:\n    pass\n")

        indexer = ki.ProjectIndexer(tmpdir)
        graph = indexer.index_project()
        gd = graph.to_dict()

        pattern_names = {
            n["metadata"].get("name")
            for n in gd["nodes"].values()
            if n["type"] == "pattern"
        }
        assert "MyModel" in pattern_names, f"MyModel not in patterns: {pattern_names}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 3: indexer creates found_in edges ───────────────────────────────────

def test_indexer_found_in_edges():
    ki = _load("knowledge-indexer")
    tmpdir = tempfile.mkdtemp()
    try:
        py_file = os.path.join(tmpdir, "services.py")
        with open(py_file, "w") as f:
            f.write("class UserService:\n    pass\n")

        indexer = ki.ProjectIndexer(tmpdir)
        graph = indexer.index_project()
        gd = graph.to_dict()

        edge_types = {e["type"] for e in gd["edges"]}
        assert "found_in" in edge_types, f"No found_in edges in graph. Edge types: {edge_types}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 4: extractor detects all tracked imports ────────────────────────────

def test_extractor_import_detection():
    pe = _load("pattern-extractor")
    tmpdir = tempfile.mkdtemp()
    try:
        graph = _make_graph(
            nodes={
                "f1": {"id": "f1", "type": "file", "content": "app/main.py", "metadata": {}, "relationships": []},
                "d_fastapi": {"id": "d_fastapi", "type": "dependency", "content": "fastapi", "metadata": {}, "relationships": []},
                "d_langgraph": {"id": "d_langgraph", "type": "dependency", "content": "langgraph", "metadata": {}, "relationships": []},
                "d_pytest": {"id": "d_pytest", "type": "dependency", "content": "pytest", "metadata": {}, "relationships": []},
                "d_sqlalchemy": {"id": "d_sqlalchemy", "type": "dependency", "content": "sqlalchemy.orm", "metadata": {}, "relationships": []},
            },
            edges=[
                {"source": "f1", "target": "d_fastapi", "type": "imports"},
                {"source": "f1", "target": "d_langgraph", "type": "imports"},
                {"source": "f1", "target": "d_pytest", "type": "imports"},
                {"source": "f1", "target": "d_sqlalchemy", "type": "imports"},
            ],
        )
        graph_path = _write_graph(graph, tmpdir)
        result = pe.extract_patterns(graph_path)

        libs = result["import_patterns"]["common_libraries"]
        assert libs.get("fastapi", 0) >= 1, f"fastapi not detected: {libs}"
        assert libs.get("langgraph", 0) >= 1, f"langgraph not detected: {libs}"
        assert libs.get("pytest", 0) >= 1, f"pytest not detected: {libs}"
        assert libs.get("sqlalchemy", 0) >= 1, f"sqlalchemy (from sqlalchemy.orm) not detected: {libs}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 5: extractor populates evidence file paths ─────────────────────────

def test_extractor_evidence_populated():
    pe = _load("pattern-extractor")
    tmpdir = tempfile.mkdtemp()
    try:
        graph = _make_graph(
            nodes={
                "f1": {"id": "f1", "type": "file", "content": "app/workflows/graph.py", "metadata": {}, "relationships": []},
                "p1": {
                    "id": "p1", "type": "pattern",
                    "content": "function: stategraph_builder",
                    "metadata": {"pattern_type": "function", "name": "stategraph_builder", "confidence": 0.9},
                    "relationships": [{"target_id": "f1", "type": "found_in"}],
                },
            },
            edges=[
                {"source": "p1", "target": "f1", "type": "found_in"},
            ],
        )
        graph_path = _write_graph(graph, tmpdir)
        result = pe.extract_patterns(graph_path)

        evidence = result.get("architecture_pattern_evidence", {})
        assert "LangGraph StateGraph" in evidence, \
            f"LangGraph StateGraph not in evidence keys: {list(evidence.keys())}"
        assert "app/workflows/graph.py" in evidence["LangGraph StateGraph"], \
            f"Expected file path missing from evidence: {evidence['LangGraph StateGraph']}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 6: extractor detects testing framework from imports ─────────────────

def test_extractor_framework_detection():
    pe = _load("pattern-extractor")

    # Case A: pytest import → should detect pytest
    tmpdir = tempfile.mkdtemp()
    try:
        graph = _make_graph(
            nodes={
                "f1": {"id": "f1", "type": "file", "content": "tests/test_app.py", "metadata": {}, "relationships": []},
                "d1": {"id": "d1", "type": "dependency", "content": "pytest", "metadata": {}, "relationships": []},
            },
            edges=[{"source": "f1", "target": "d1", "type": "imports"}],
        )
        result = pe.extract_patterns(_write_graph(graph, tmpdir))
        assert result["testing_patterns"]["framework"] == "pytest", \
            f"Expected pytest, got: {result['testing_patterns']['framework']}"
    finally:
        shutil.rmtree(tmpdir)

    # Case B: .test.js file + no imports → should detect jest
    tmpdir = tempfile.mkdtemp()
    try:
        graph = _make_graph(
            nodes={
                "f1": {"id": "f1", "type": "file", "content": "src/app.test.js", "metadata": {}, "relationships": []},
            },
            edges=[],
        )
        result = pe.extract_patterns(_write_graph(graph, tmpdir))
        assert result["testing_patterns"]["framework"] == "jest", \
            f"Expected jest for .test.js file, got: {result['testing_patterns']['framework']}"
    finally:
        shutil.rmtree(tmpdir)

    # Case C: no test indicators → unknown
    tmpdir = tempfile.mkdtemp()
    try:
        graph = _make_graph(
            nodes={
                "f1": {"id": "f1", "type": "file", "content": "main.py", "metadata": {}, "relationships": []},
            },
            edges=[],
        )
        result = pe.extract_patterns(_write_graph(graph, tmpdir))
        assert result["testing_patterns"]["framework"] == "unknown", \
            f"Expected unknown, got: {result['testing_patterns']['framework']}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 7: adapter passes evidence through ─────────────────────────────────

def test_adapter_evidence_passthrough():
    pa = _load("pattern-adapter")

    extractor_output = {
        "architecture_patterns": ["LangGraph StateGraph", "Fractal Governor"],
        "architecture_pattern_evidence": {
            "LangGraph StateGraph": ["app/state.py", "app/graph.py"],
            "Fractal Governor": [],
        },
        "naming_conventions": {},
        "file_structure": {},
        "testing_patterns": {"framework": "pytest", "test_files": 0, "test_directories": [], "mock_usage": 0},
        "import_patterns": {"total_imports": 0, "common_libraries": {}},
        "key_concepts": [],
    }

    result = pa.adapt(extractor_output)
    arch = result["patterns"]["architectural"]

    lg_pat = next((p for p in arch if p["name"] == "LangGraph StateGraph"), None)
    assert lg_pat is not None, "LangGraph StateGraph pattern not found in output"
    assert lg_pat["evidence"] == ["app/state.py", "app/graph.py"], \
        f"Evidence not passed through: {lg_pat['evidence']}"

    gov_pat = next((p for p in arch if p["name"] == "Fractal Governor"), None)
    assert gov_pat is not None, "Fractal Governor pattern not found in output"
    assert gov_pat["evidence"] == [], \
        f"Empty evidence should remain empty: {gov_pat['evidence']}"


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Pipeline Unit Tests")
    print("=" * 60)

    print("\n[knowledge-indexer.py]")
    run("indexer extracts imports", test_indexer_extracts_imports)
    run("indexer detects classes", test_indexer_detects_classes)
    run("indexer creates found_in edges", test_indexer_found_in_edges)

    print("\n[pattern-extractor.py]")
    run("extractor detects all tracked imports", test_extractor_import_detection)
    run("extractor populates evidence file paths", test_extractor_evidence_populated)
    run("extractor detects testing framework", test_extractor_framework_detection)

    print("\n[pattern-adapter.py]")
    run("adapter passes evidence through", test_adapter_evidence_passthrough)

    print(f"\n{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
