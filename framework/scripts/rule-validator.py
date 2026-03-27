#!/usr/bin/env python3
"""
Rule Validator - Track Seed Rule Effectiveness and Detect Conflicts

Monitors seed rule usage, tracks effectiveness metrics, detects conflicts,
and prunes ineffective rules from the fractal memory system.

Usage:
    python rule-validator.py --project myproject --stats
    python rule-validator.py --project myproject --find-ineffective --threshold 0.5
    python rule-validator.py --project myproject --find-conflicts
    python rule-validator.py --project myproject --prune --threshold 0.6

Features:
- Track rule usage and success/failure counts
- Calculate effectiveness (success rate)
- Detect conflicting rules
- Prune ineffective or stale rules
- Adjust rule confidence based on performance
- Generate effectiveness reports
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict


@dataclass
class RuleMetrics:
    """Metrics for a single seed rule."""
    rule_id: str
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    original_confidence: float = 0.0
    adjusted_confidence: float = 0.0
    first_used: Optional[str] = None
    last_used: Optional[str] = None
    last_updated: Optional[str] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0-1.0)."""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count

    @property
    def is_effective(self) -> bool:
        """Check if rule is effective (>50% success rate after 20 uses)."""
        if self.usage_count < 20:
            return True  # Not enough data yet
        return self.success_rate >= 0.5

    @property
    def is_stale(self) -> bool:
        """Check if rule is stale (not used in 30 days)."""
        if not self.last_used:
            return False

        last_used_dt = datetime.fromisoformat(self.last_used.replace('Z', '+00:00'))
        days_since_use = (datetime.now(last_used_dt.tzinfo) - last_used_dt).days
        return self.usage_count < 5 and days_since_use > 30

    def record_usage(self, success: bool):
        """Record rule usage."""
        now = datetime.utcnow().isoformat() + "Z"

        self.usage_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        if not self.first_used:
            self.first_used = now
        self.last_used = now

        # Adjust confidence based on success rate (after 10+ uses)
        if self.usage_count >= 10:
            self.adjusted_confidence = self.success_rate
        else:
            # Blend original and current success rate
            weight = self.usage_count / 10.0
            self.adjusted_confidence = (
                self.original_confidence * (1 - weight) +
                self.success_rate * weight
            )

        self.last_updated = now


@dataclass
class ConflictReport:
    """Report of conflicting rules."""
    rule_id_1: str
    rule_id_2: str
    conflict_type: str  # contradictory|overlapping|incompatible
    description: str
    confidence_1: float
    confidence_2: float
    coverage_1: float
    coverage_2: float
    recommendation: str


class RuleValidator:
    """Validate seed rules and track effectiveness."""

    def __init__(self, memory_dir: Path = Path(".claude/memory")):
        """
        Initialize RuleValidator.

        Args:
            memory_dir: Base memory directory containing seed rules
        """
        self.memory_dir = Path(memory_dir)
        self.metrics_file = self.memory_dir / "rule_metrics.json"
        self.metrics: Dict[str, RuleMetrics] = {}

        # Load existing metrics
        self._load_metrics()

    def _load_metrics(self):
        """Load existing rule metrics from disk."""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                for rule_id, metrics_dict in data.items():
                    self.metrics[rule_id] = RuleMetrics(**metrics_dict)

    def _save_metrics(self):
        """Save rule metrics to disk."""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            rule_id: asdict(metrics)
            for rule_id, metrics in self.metrics.items()
        }
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_rule_usage(
        self,
        rule_id: str,
        success: bool,
        original_confidence: float = None
    ):
        """
        Record rule usage.

        Args:
            rule_id: Unique rule identifier (e.g., "myproject/general/jwt_authentication_pattern")
            success: Whether the task using this rule succeeded
            original_confidence: Original rule confidence (for new rules)
        """
        if rule_id not in self.metrics:
            # Create new metrics entry
            self.metrics[rule_id] = RuleMetrics(
                rule_id=rule_id,
                original_confidence=original_confidence or 0.8
            )

        # Record usage
        self.metrics[rule_id].record_usage(success)

        # Save updated metrics
        self._save_metrics()

    def get_rule_metrics(self, rule_id: str) -> Optional[RuleMetrics]:
        """Get metrics for a specific rule."""
        return self.metrics.get(rule_id)

    def get_project_stats(self, project: str) -> Dict[str, Any]:
        """
        Get statistics for all rules in a project.

        Args:
            project: Project name

        Returns:
            Dictionary with project statistics
        """
        project_metrics = [
            m for rule_id, m in self.metrics.items()
            if rule_id.startswith(f"{project}/")
        ]

        if not project_metrics:
            return {
                "project": project,
                "total_rules": 0,
                "tracked_rules": 0,
                "message": "No metrics found for this project"
            }

        total_usage = sum(m.usage_count for m in project_metrics)
        total_success = sum(m.success_count for m in project_metrics)
        total_failure = sum(m.failure_count for m in project_metrics)

        effective_rules = [m for m in project_metrics if m.is_effective]
        ineffective_rules = [m for m in project_metrics if not m.is_effective]
        stale_rules = [m for m in project_metrics if m.is_stale]

        return {
            "project": project,
            "total_rules": len(project_metrics),
            "tracked_rules": len([m for m in project_metrics if m.usage_count > 0]),
            "total_usage": total_usage,
            "total_success": total_success,
            "total_failure": total_failure,
            "overall_success_rate": total_success / total_usage if total_usage > 0 else 0.0,
            "effective_rules": len(effective_rules),
            "ineffective_rules": len(ineffective_rules),
            "stale_rules": len(stale_rules),
            "average_confidence": sum(m.adjusted_confidence for m in project_metrics) / len(project_metrics),
            "rules_with_high_confidence": len([m for m in project_metrics if m.adjusted_confidence > 0.8]),
            "rules_with_low_confidence": len([m for m in project_metrics if m.adjusted_confidence < 0.6])
        }

    def find_ineffective_rules(
        self,
        project: str,
        threshold: float = 0.5
    ) -> List[RuleMetrics]:
        """
        Find ineffective rules.

        Args:
            project: Project name
            threshold: Minimum success rate threshold

        Returns:
            List of ineffective rule metrics
        """
        ineffective = []

        for rule_id, metrics in self.metrics.items():
            if not rule_id.startswith(f"{project}/"):
                continue

            # Rule is ineffective if:
            # 1. Success rate < threshold after 20+ uses
            # 2. Stale (< 5 uses in 30 days)
            if metrics.usage_count >= 20 and metrics.success_rate < threshold:
                ineffective.append(metrics)
            elif metrics.is_stale:
                ineffective.append(metrics)

        return ineffective

    def find_conflicts(self, project: str) -> List[ConflictReport]:
        """
        Find conflicting rules by scanning seeds/workflows/ directories.

        Scans {memory_dir}/../../seeds/workflows/ (project root inferred from memory_dir).
        Falls back to legacy .claude/memory/opus_level/seed_rules/{project}.json.
        """
        conflicts = []

        # Try new workflow-scoped format
        # memory_dir is typically {project}/.claude/memory, so project root = ../..
        project_root = self.memory_dir.parent.parent
        workflows_dir = project_root / "seeds" / "workflows"

        all_rules: List[Dict] = []
        if workflows_dir.exists():
            for workflow_dir in workflows_dir.iterdir():
                if workflow_dir.is_dir():
                    for rule_file in workflow_dir.glob("*.json"):
                        try:
                            with open(rule_file, 'r') as f:
                                all_rules.append(json.load(f))
                        except (json.JSONDecodeError, OSError):
                            pass
        else:
            # Legacy fallback
            rules_file = self.memory_dir / "opus_level" / "seed_rules" / f"{project}.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    data = json.load(f)
                seed_rules = data.get("seed_rules", {})
                patterns = seed_rules.get("patterns", {})
                all_rules = [{"id": k, "rule": v.get("pattern", k)} for k, v in patterns.items()]
                conventions = seed_rules.get("conventions", {})
                naming = conventions.get("naming", [])
                all_rules.extend([{"id": f"naming_{i}", "rule": n} for i, n in enumerate(naming)])

        if not all_rules:
            return conflicts

        conflicts.extend(self._find_rule_conflicts(all_rules, project))
        return conflicts

    def _find_rule_conflicts(self, rules: List[Dict], project: str) -> List[ConflictReport]:
        """Detect conflicts in a flat list of seed rule dicts."""
        conflicts = []

        # Detect multiple authentication approaches
        auth_rules = [r for r in rules if "auth" in r.get("id", "").lower() or "authentication" in r.get("rule", "").lower()]
        auth_patterns = set()
        for r in auth_rules:
            rule_text = r.get("rule", "").lower()
            if "jwt" in rule_text:
                auth_patterns.add("JWT")
            if "oauth" in rule_text:
                auth_patterns.add("OAuth")
            if "session" in rule_text:
                auth_patterns.add("Session")

        if len(auth_patterns) > 1:
            auth_ids = [r["id"] for r in auth_rules]
            conflicts.append(ConflictReport(
                rule_id_1=f"{project}/{auth_ids[0]}" if auth_ids else f"{project}/auth_1",
                rule_id_2=f"{project}/{auth_ids[1]}" if len(auth_ids) > 1 else f"{project}/auth_2",
                conflict_type="incompatible",
                description=f"Multiple authentication patterns: {', '.join(auth_patterns)}",
                confidence_1=0.8,
                confidence_2=0.8,
                coverage_1=0.5,
                coverage_2=0.5,
                recommendation="Choose one authentication pattern based on usage metrics"
            ))

        # Detect contradictory naming conventions
        all_rule_text = " ".join(r.get("rule", "").lower() for r in rules)
        has_snake = "snake_case" in all_rule_text
        has_camel = "camelcase" in all_rule_text
        has_pascal = "pascalcase" in all_rule_text

        if sum([has_snake, has_camel, has_pascal]) > 1:
            # Only flag if they're applying to the same entity type (not class vs function)
            if has_snake and has_camel:
                conflicts.append(ConflictReport(
                    rule_id_1=f"{project}/naming_convention_1",
                    rule_id_2=f"{project}/naming_convention_2",
                    conflict_type="contradictory",
                    description="Mixed naming conventions: snake_case and camelCase both present",
                    confidence_1=0.7,
                    confidence_2=0.7,
                    coverage_1=0.5,
                    coverage_2=0.5,
                    recommendation="Unify naming: snake_case for Python (functions/vars), PascalCase for classes only"
                ))

        return conflicts

    def _find_pattern_conflicts(
        self,
        patterns: Dict[str, Any],
        project: str
    ) -> List[ConflictReport]:
        """Find conflicts in patterns (legacy method, kept for backward compatibility)."""
        conflicts = []

        # Check authentication patterns
        auth_patterns = {
            k: v for k, v in patterns.items()
            if "auth" in k.lower()
        }

        if len(auth_patterns) > 1:
            pattern_names = [v.get("pattern", "") for v in auth_patterns.values()]
            if len(set(pattern_names)) > 1:
                keys = list(auth_patterns.keys())
                conflicts.append(ConflictReport(
                    rule_id_1=f"{project}/{keys[0]}",
                    rule_id_2=f"{project}/{keys[1]}",
                    conflict_type="incompatible",
                    description=f"Multiple authentication patterns: {', '.join(pattern_names)}",
                    confidence_1=0.8,
                    confidence_2=0.8,
                    coverage_1=0.5,
                    coverage_2=0.5,
                    recommendation="Choose one authentication pattern based on usage metrics"
                ))

        return conflicts

    def _find_convention_conflicts(
        self,
        conventions: Dict[str, List[str]],
        project: str
    ) -> List[ConflictReport]:
        """Find conflicts in conventions (legacy method, kept for backward compatibility)."""
        conflicts = []

        naming = conventions.get("naming", [])
        if naming:
            has_snake = any("snake_case" in n.lower() for n in naming)
            has_camel = any("camelcase" in n.lower() for n in naming)
            has_pascal = any("pascalcase" in n.lower() for n in naming)

            if sum([has_snake, has_camel, has_pascal]) > 1:
                conflicts.append(ConflictReport(
                    rule_id_1=f"{project}/naming_convention_1",
                    rule_id_2=f"{project}/naming_convention_2",
                    conflict_type="contradictory",
                    description="Multiple naming conventions for same entity type",
                    confidence_1=0.7,
                    confidence_2=0.7,
                    coverage_1=0.5,
                    coverage_2=0.5,
                    recommendation="Unify naming convention or specify context (e.g., snake_case for functions, PascalCase for classes)"
                ))

        return conflicts

    def prune_rules(
        self,
        project: str,
        threshold: float = 0.6,
        dry_run: bool = False
    ) -> Tuple[List[str], List[str]]:
        """
        Prune ineffective and stale rules.

        Args:
            project: Project name
            threshold: Minimum success rate threshold
            dry_run: If True, don't actually prune, just report

        Returns:
            Tuple of (pruned_rule_ids, stale_rule_ids)
        """
        # Find rules to prune
        ineffective = self.find_ineffective_rules(project, threshold)

        pruned = []
        stale = []

        for metrics in ineffective:
            if metrics.is_stale:
                stale.append(metrics.rule_id)
            else:
                pruned.append(metrics.rule_id)

        if not dry_run:
            # Remove from metrics
            for rule_id in pruned + stale:
                if rule_id in self.metrics:
                    del self.metrics[rule_id]
            self._save_metrics()

            # Also delete the actual rule files from seeds/workflows/
            project_root = self.memory_dir.parent.parent
            workflows_dir = project_root / "seeds" / "workflows"
            if workflows_dir.exists():
                for rule_id in pruned + stale:
                    # rule_id format: {project}/{workflow}/{bare_id} or {project}/{bare_id}
                    parts = rule_id.split("/")
                    bare_id = parts[-1]
                    for rule_file in workflows_dir.rglob(f"{bare_id}.json"):
                        rule_file.unlink(missing_ok=True)

        return pruned, stale

    def generate_report(self, project: str) -> str:
        """
        Generate effectiveness report for a project.

        Args:
            project: Project name

        Returns:
            Formatted report string
        """
        stats = self.get_project_stats(project)

        report = []
        report.append(f"=== Seed Rule Effectiveness Report ===")
        report.append(f"Project: {project}")
        report.append(f"Generated: {datetime.utcnow().isoformat()}Z\n")

        if stats["total_rules"] == 0:
            report.append("No metrics found for this project.")
            return "\n".join(report)

        report.append(f"Total Rules: {stats['total_rules']}")
        report.append(f"Tracked Rules: {stats['tracked_rules']}")
        report.append(f"Total Usage: {stats['total_usage']}")
        report.append(f"Overall Success Rate: {stats['overall_success_rate']:.1%}\n")

        report.append("Rule Quality:")
        report.append(f"  Effective: {stats['effective_rules']}")
        report.append(f"  Ineffective: {stats['ineffective_rules']}")
        report.append(f"  Stale: {stats['stale_rules']}\n")

        report.append("Confidence Distribution:")
        report.append(f"  High (>0.8): {stats['rules_with_high_confidence']}")
        report.append(f"  Medium (0.6-0.8): {stats['total_rules'] - stats['rules_with_high_confidence'] - stats['rules_with_low_confidence']}")
        report.append(f"  Low (<0.6): {stats['rules_with_low_confidence']}\n")

        # Find conflicts
        conflicts = self.find_conflicts(project)
        if conflicts:
            report.append(f"Conflicts Detected: {len(conflicts)}")
            for conflict in conflicts:
                report.append(f"  - {conflict.description}")
                report.append(f"    Recommendation: {conflict.recommendation}\n")

        # Top performing rules
        project_metrics = sorted(
            [m for rule_id, m in self.metrics.items() if rule_id.startswith(f"{project}/")],
            key=lambda m: m.success_rate,
            reverse=True
        )

        if project_metrics:
            report.append("Top Performing Rules:")
            for metrics in project_metrics[:5]:
                if metrics.usage_count > 0:
                    report.append(
                        f"  {metrics.rule_id}: "
                        f"{metrics.success_rate:.1%} success "
                        f"({metrics.success_count}/{metrics.usage_count} uses)"
                    )

        # Ineffective rules
        ineffective = [m for m in project_metrics if not m.is_effective]
        if ineffective:
            report.append("\nIneffective Rules (should be reviewed):")
            for metrics in ineffective:
                report.append(
                    f"  {metrics.rule_id}: "
                    f"{metrics.success_rate:.1%} success "
                    f"({metrics.success_count}/{metrics.usage_count} uses)"
                )

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Validate seed rules and track effectiveness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show project statistics
  python rule-validator.py --project myproject --stats

  # Find ineffective rules
  python rule-validator.py --project myproject --find-ineffective --threshold 0.5

  # Find conflicts
  python rule-validator.py --project myproject --find-conflicts

  # Prune ineffective rules (dry run)
  python rule-validator.py --project myproject --prune --dry-run

  # Prune ineffective rules (for real)
  python rule-validator.py --project myproject --prune --threshold 0.6

  # Generate full report
  python rule-validator.py --project myproject --report
        """
    )

    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Project name"
    )

    parser.add_argument(
        "--memory-dir",
        type=Path,
        default=Path(".claude/memory"),
        help="Base memory directory (default: .claude/memory)"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show project statistics"
    )

    parser.add_argument(
        "--find-ineffective",
        action="store_true",
        help="Find ineffective rules"
    )

    parser.add_argument(
        "--find-conflicts",
        action="store_true",
        help="Find conflicting rules"
    )

    parser.add_argument(
        "--prune",
        action="store_true",
        help="Prune ineffective and stale rules"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate full effectiveness report"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Minimum success rate threshold (default: 0.5)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (don't actually prune)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Create validator
    validator = RuleValidator(memory_dir=args.memory_dir)

    # Execute requested operation
    if args.stats:
        stats = validator.get_project_stats(args.project)
        print(json.dumps(stats, indent=2))

    elif args.find_ineffective:
        ineffective = validator.find_ineffective_rules(args.project, args.threshold)
        if ineffective:
            print(f"Found {len(ineffective)} ineffective rules:")
            for metrics in ineffective:
                reason = "stale" if metrics.is_stale else f"low success rate ({metrics.success_rate:.1%})"
                print(f"  {metrics.rule_id}: {reason} ({metrics.usage_count} uses)")
        else:
            print("No ineffective rules found.")

    elif args.find_conflicts:
        conflicts = validator.find_conflicts(args.project)
        if conflicts:
            print(f"Found {len(conflicts)} conflicts:")
            for conflict in conflicts:
                print(f"\n  {conflict.conflict_type.upper()}: {conflict.description}")
                print(f"  Rules: {conflict.rule_id_1} vs {conflict.rule_id_2}")
                print(f"  Recommendation: {conflict.recommendation}")
        else:
            print("No conflicts detected.")

    elif args.prune:
        pruned, stale = validator.prune_rules(
            args.project,
            args.threshold,
            dry_run=args.dry_run
        )

        if args.dry_run:
            print("DRY RUN - No changes made")

        if pruned or stale:
            print(f"Pruned {len(pruned)} ineffective rules:")
            for rule_id in pruned:
                print(f"  {rule_id}")

            print(f"\nRemoved {len(stale)} stale rules:")
            for rule_id in stale:
                print(f"  {rule_id}")
        else:
            print("No rules to prune.")

    elif args.report:
        report = validator.generate_report(args.project)
        print(report)

    else:
        # Default: show stats
        stats = validator.get_project_stats(args.project)
        print(json.dumps(stats, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
