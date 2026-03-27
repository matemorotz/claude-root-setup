#!/usr/bin/env python3
"""
Dynamic Re-planning Module - Detect blockers and coordinate re-planning

Part of fractal orchestration system.
Used by execute-plan.py to handle stuck tasks adaptively.
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional


class ReplanningCoordinator:
    """Lightweight blocker detection and re-planning coordination"""

    def __init__(self, plan_id: str, project_name: str):
        self.plan_id = plan_id
        self.project_name = project_name
        self.state_dir = Path(".claude/state/agents")
        self.log_file = Path(".claude/memory/opus_level/re-planning-log.jsonl")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def detect_blockers(self, timeout_minutes: int = 5) -> List[Dict]:
        """
        Detect stuck tasks by checking state files (lightweight)

        Returns list of blocked tasks:
        [{"task_id": "1.1", "agent_type": "haiku-executor", "stuck_duration_seconds": 350}]
        """
        blockers = []

        if not self.state_dir.exists():
            return blockers

        # Check all .start files
        start_files = list(self.state_dir.glob("*/*.start"))

        for start_file in start_files:
            try:
                with open(start_file) as f:
                    state = json.load(f)

                started = datetime.fromisoformat(state["started_at"])
                elapsed = datetime.now(timezone.utc) - started

                # Blocker if stuck >timeout_minutes
                if elapsed > timedelta(minutes=timeout_minutes):
                    blockers.append({
                        "task_id": state["task_id"],
                        "agent_type": state["agent_type"],
                        "project": state.get("project", "unknown"),
                        "stuck_duration_seconds": elapsed.total_seconds(),
                        "started_at": state["started_at"]
                    })
            except Exception as e:
                print(f"   Warning: Could not read {start_file}: {e}")

        return blockers

    def handle_blockers(self, blockers: List[Dict], current_section: Optional[Dict] = None):
        """
        Handle detected blockers (lightweight coordination)

        Strategy:
        1. Log blocker event
        2. Clean up stuck task state files
        3. Optionally trigger section re-planning (future enhancement)
        """
        if not blockers:
            return

        print(f"\n🔄 Handling {len(blockers)} blocked task(s)...")

        for blocker in blockers:
            # Log blocker event
            self._log_blocker(blocker, current_section)

            # Clean up stuck task
            self._cleanup_stuck_task(blocker)

            print(f"   ⏱️  Task {blocker['task_id']} stuck for {blocker['stuck_duration_seconds']:.0f}s - cleaned up")

        print(f"   ✅ Blockers handled\n")

    def _log_blocker(self, blocker: Dict, current_section: Optional[Dict]):
        """Log blocker event to re-planning log"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan_id": self.plan_id,
            "section": current_section.get("section_id") if current_section else None,
            "task_id": blocker["task_id"],
            "agent_type": blocker["agent_type"],
            "project": blocker.get("project", self.project_name),
            "reason": "task_timeout",
            "stuck_duration_seconds": blocker["stuck_duration_seconds"],
            "started_at": blocker["started_at"]
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _cleanup_stuck_task(self, blocker: Dict):
        """Remove stuck task state file"""
        state_file = self.state_dir / blocker["agent_type"] / f"{blocker['task_id']}.start"

        if state_file.exists():
            state_file.unlink()

    def get_replanning_history(self) -> List[Dict]:
        """Read re-planning log (lightweight - just file read)"""
        if not self.log_file.exists():
            return []

        history = []
        with open(self.log_file) as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))

        return history

    def suggest_section_regeneration(self, failed_tasks: List[str]) -> Optional[str]:
        """
        Analyze failed tasks and suggest which section to re-plan

        Returns section_id if re-planning recommended, None otherwise
        """
        # Simple heuristic: if >50% of section tasks failed, re-plan entire section
        # (Future enhancement: actual OpusPlanner delegation)

        # For now, just return None (no automatic re-planning yet)
        return None


# CLI for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Re-planning Coordinator Test")
        print("\nUsage:")
        print("  python replanning.py detect <plan_id>")
        print("  python replanning.py history <plan_id>")
        sys.exit(0)

    command = sys.argv[1]

    if command == "detect":
        plan_id = sys.argv[2] if len(sys.argv) > 2 else "test-plan"
        coordinator = ReplanningCoordinator(plan_id, "test_project")

        blockers = coordinator.detect_blockers(timeout_minutes=1)  # 1min for testing

        if blockers:
            print(f"Found {len(blockers)} blocker(s):")
            for blocker in blockers:
                print(f"  - {blocker['task_id']} ({blocker['agent_type']}) stuck for {blocker['stuck_duration_seconds']:.0f}s")
        else:
            print("No blockers detected")

    elif command == "history":
        plan_id = sys.argv[2] if len(sys.argv) > 2 else "test-plan"
        coordinator = ReplanningCoordinator(plan_id, "test_project")

        history = coordinator.get_replanning_history()

        if history:
            print(f"Re-planning history ({len(history)} events):")
            for event in history:
                print(f"  - {event['timestamp']}: {event['task_id']} ({event['reason']})")
        else:
            print("No re-planning history")
