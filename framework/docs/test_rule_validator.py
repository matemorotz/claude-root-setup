#!/usr/bin/env python3
"""
Unit tests for rule-validator.py — RuleValidator and RuleMetrics.

Tests are standalone (no pytest required). Run with: python test_rule_validator.py
"""

import importlib.util
import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent / "scripts"


def _load_validator():
    spec = importlib.util.spec_from_file_location("rule-validator", BASE / "rule-validator.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


# ─── Test 1: record_rule_usage creates rule_metrics.json ──────────────────────

def test_record_usage_creates_metrics():
    rv = _load_validator()
    tmpdir = tempfile.mkdtemp()
    try:
        validator = rv.RuleValidator(memory_dir=Path(tmpdir))
        validator.record_rule_usage("myproj:auth", success=True, original_confidence=0.9)

        metrics_file = Path(tmpdir) / "rule_metrics.json"
        assert metrics_file.exists(), "rule_metrics.json was not created"

        with open(metrics_file) as f:
            data = json.load(f)

        assert "myproj:auth" in data, f"myproj:auth not in saved metrics: {list(data.keys())}"
        assert data["myproj:auth"]["usage_count"] == 1, \
            f"usage_count expected 1, got {data['myproj:auth']['usage_count']}"
        assert data["myproj:auth"]["success_count"] == 1, \
            f"success_count expected 1, got {data['myproj:auth']['success_count']}"
        assert data["myproj:auth"]["failure_count"] == 0, \
            f"failure_count expected 0, got {data['myproj:auth']['failure_count']}"

        # Record a failure and verify
        validator.record_rule_usage("myproj:auth", success=False)
        metrics = validator.get_rule_metrics("myproj:auth")
        assert metrics.usage_count == 2, f"usage_count expected 2, got {metrics.usage_count}"
        assert metrics.failure_count == 1, f"failure_count expected 1, got {metrics.failure_count}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 2: confidence adjustment algorithm ──────────────────────────────────

def test_confidence_adjustment():
    rv = _load_validator()

    # After 10 successes with original_confidence=0.5: adjusted should equal success_rate = 1.0
    tmpdir = tempfile.mkdtemp()
    try:
        validator = rv.RuleValidator(memory_dir=Path(tmpdir))
        for _ in range(10):
            validator.record_rule_usage("proj:rule1", success=True, original_confidence=0.5)
        m = validator.get_rule_metrics("proj:rule1")
        assert m.adjusted_confidence == 1.0, \
            f"After 10 successes: adjusted_confidence expected 1.0, got {m.adjusted_confidence}"
        assert m.success_rate == 1.0, f"success_rate expected 1.0, got {m.success_rate}"
    finally:
        shutil.rmtree(tmpdir)

    # After 1 success with original_confidence=0.5:
    # weight = 1/10 = 0.1; blended = 0.5*(1-0.1) + 1.0*0.1 = 0.45 + 0.1 = 0.55
    tmpdir = tempfile.mkdtemp()
    try:
        validator = rv.RuleValidator(memory_dir=Path(tmpdir))
        validator.record_rule_usage("proj:rule2", success=True, original_confidence=0.5)
        m = validator.get_rule_metrics("proj:rule2")
        expected = 0.5 * 0.9 + 1.0 * 0.1  # = 0.55
        assert abs(m.adjusted_confidence - expected) < 0.001, \
            f"Blended confidence: expected {expected:.3f}, got {m.adjusted_confidence:.3f}"
    finally:
        shutil.rmtree(tmpdir)

    # Mixed: 5 uses, 3 successes, original=0.8
    # weight = 5/10 = 0.5; success_rate = 3/5 = 0.6
    # adjusted = 0.8*0.5 + 0.6*0.5 = 0.4 + 0.3 = 0.70
    tmpdir = tempfile.mkdtemp()
    try:
        validator = rv.RuleValidator(memory_dir=Path(tmpdir))
        for i in range(5):
            validator.record_rule_usage("proj:rule3", success=(i < 3), original_confidence=0.8)
        m = validator.get_rule_metrics("proj:rule3")
        expected = 0.8 * 0.5 + 0.6 * 0.5  # = 0.70
        assert abs(m.adjusted_confidence - expected) < 0.001, \
            f"Mixed blended: expected {expected:.3f}, got {m.adjusted_confidence:.3f}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Test 3: stale detection ──────────────────────────────────────────────────

def test_stale_detection():
    rv = _load_validator()

    # No last_used → never stale
    m = rv.RuleMetrics(rule_id="proj:r1")
    assert not m.is_stale, "Rule with no last_used should not be stale"

    # Recent usage → not stale (used now, usage_count=1)
    m2 = rv.RuleMetrics(rule_id="proj:r2")
    m2.record_usage(True)
    assert not m2.is_stale, "Rule used just now should not be stale"

    # usage_count=2, last_used 40 days ago → stale (< 5 uses AND > 30 days)
    old_date = (
        datetime.now(timezone.utc) - timedelta(days=40)
    ).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    m3 = rv.RuleMetrics(
        rule_id="proj:r3",
        usage_count=2,
        success_count=1,
        failure_count=1,
        last_used=old_date,
        first_used=old_date,
    )
    assert m3.is_stale, "Rule with 2 uses and last_used 40 days ago should be stale"

    # usage_count=6, last_used 40 days ago → NOT stale (>= 5 uses)
    m4 = rv.RuleMetrics(
        rule_id="proj:r4",
        usage_count=6,
        success_count=4,
        failure_count=2,
        last_used=old_date,
        first_used=old_date,
    )
    assert not m4.is_stale, "Rule with 6 uses should not be stale (usage_count >= 5)"


# ─── Test 4: generate_report produces meaningful output with data ─────────────

def test_generate_report_with_data():
    rv = _load_validator()
    tmpdir = tempfile.mkdtemp()
    try:
        validator = rv.RuleValidator(memory_dir=Path(tmpdir))

        # Record 3 rules: 2 successes, 1 failure
        validator.record_rule_usage("myproj/rule0", success=True, original_confidence=0.9)
        validator.record_rule_usage("myproj/rule1", success=True, original_confidence=0.8)
        validator.record_rule_usage("myproj/rule2", success=False, original_confidence=0.7)

        report = validator.generate_report("myproj")

        assert "Seed Rule Effectiveness Report" in report, \
            f"Report header missing: {report[:200]}"
        assert "myproj" in report, "Project name not in report"
        assert "Total Rules: 3" in report, \
            f"Expected 'Total Rules: 3' in report: {report}"
        assert "Total Usage: 3" in report, \
            f"Expected 'Total Usage: 3' in report: {report}"
        # Overall success rate should be 2/3 = 66.7%
        assert "66.7%" in report or "67.0%" in report or "66.6%" in report, \
            f"Expected ~66% success rate in report: {report}"
    finally:
        shutil.rmtree(tmpdir)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Rule Validator Unit Tests")
    print("=" * 60)

    print("\n[rule-validator.py — RuleValidator & RuleMetrics]")
    run("record_rule_usage creates rule_metrics.json", test_record_usage_creates_metrics)
    run("confidence adjustment algorithm", test_confidence_adjustment)
    run("stale detection", test_stale_detection)
    run("generate_report with data", test_generate_report_with_data)

    print(f"\n{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print("=" * 60)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
