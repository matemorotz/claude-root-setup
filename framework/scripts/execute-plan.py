#!/usr/bin/env python3
"""
Execution Engine - Execute orchestration plans with fractal memory

Loads execution plans and orchestrates agent execution using fractal
memory for intelligent context distribution.

Usage:
    python execute-plan.py <plan_file.json>
    python execute-plan.py <plan_file.json> --dry-run
    python execute-plan.py <plan_file.json> --strategy parallel

Architecture:
- Uses fractal memory for context engineering
- Executes steps via appropriate agents (simulated)
- Handles dependencies and parallel execution
- Tracks progress via SonnetTracker pattern
- Escalates errors to SonnetDebugger pattern
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

# Add fractal to path
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))

from fractal_memory import FractalMemory
from context_distiller import (
    distill_user_to_opus,
    distill_opus_to_sonnet,
    distill_sonnet_to_haiku
)
from plan_splitter import HorizontalPlanSplitter


@dataclass
class ExecutionResult:
    """Result from step execution"""
    step_id: str
    status: str  # success, error, timeout
    output: str
    error_message: Optional[str] = None
    execution_time: float = 0.0
    executed_by: str = ""
    executed_at: str = ""


class ExecutionEngine:
    """
    Execution Engine - Orchestrates plan execution with fractal memory

    Responsibilities:
    1. Load and validate execution plans
    2. Distribute context via fractal memory
    3. Execute steps with appropriate agents
    4. Handle dependencies and parallel execution
    5. Track progress and synthesize results
    6. Escalate errors for debugging
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.memory = FractalMemory()
        self.executed_steps: Set[str] = set()
        self.failed_steps: Set[str] = set()
        self.blocked_steps: Set[str] = set()

    def load_plan(self, plan_path: Path) -> Dict:
        """Load and validate execution plan"""
        print(f"📋 Loading execution plan: {plan_path}")

        with open(plan_path) as f:
            plan = json.load(f)

        # Validate required fields
        required = ["version", "plan_id", "project", "sections"]
        for field in required:
            if field not in plan:
                raise ValueError(f"Missing required field: {field}")

        print(f"✅ Loaded plan: {plan['plan_id']}")
        print(f"   Project: {plan['project']}")
        print(f"   Sections: {len(plan['sections'])}")

        total_steps = sum(len(s.get("steps", [])) for s in plan["sections"])
        print(f"   Total steps: {total_steps}")

        return plan

    def prepare_context(self, plan: Dict) -> Dict:
        """
        Prepare context using fractal memory

        Flow:
        1. Store full context at User level
        2. Extract seed rules at Opus level
        3. Engineer task contexts at Sonnet level
        4. Extract step contexts at Haiku level
        """
        print("\n🔧 Preparing fractal context...")

        project_name = plan["project"]
        if isinstance(project_name, dict):
            project_name = project_name.get("name", "unknown")

        # Build full context (User level)
        full_context = {
            "project": project_name,
            "plan_id": plan["plan_id"],
            "goal": plan.get("context_summary", {}).get("goal", ""),
            "sections": plan["sections"],
            "seed_rules_applied": plan.get("seed_rules_applied", []),
            "timestamp": datetime.now().isoformat()
        }

        # Store at User level
        self.memory.store_project(project_name, full_context)
        print(f"   ✅ Stored full context at User level")

        # Extract seed rules (Opus level)
        seed_rules = self.memory.distill_to_opus(project_name, distill_user_to_opus)
        print(f"   ✅ Extracted seed rules at Opus level")

        # Engineer task contexts for each section (Sonnet level)
        for section in plan["sections"]:
            section_task = {
                "task_id": section["section_id"],
                "action": section["title"],
                "description": section.get("description", "")
            }

            task_context = self.memory.distill_to_sonnet(
                project_name,
                section_task,
                distill_opus_to_sonnet
            )

            self.memory.sonnet_level.store_task_context(section["section_id"], task_context)

        print(f"   ✅ Engineered {len(plan['sections'])} task contexts at Sonnet level")

        return {
            "project": project_name,
            "seed_rules": seed_rules,
            "full_context": full_context
        }

    def can_execute_step(self, step: Dict, dependencies: Dict) -> bool:
        """Check if step can be executed (all dependencies met)"""
        step_id = step["step_id"]

        # Check if already executed or failed
        if step_id in self.executed_steps:
            return False
        if step_id in self.failed_steps:
            return False

        # Check dependencies
        step_deps = dependencies.get(step_id, [])
        for dep in step_deps:
            if dep not in self.executed_steps:
                return False  # Dependency not met
            if dep in self.failed_steps:
                self.blocked_steps.add(step_id)
                return False  # Dependency failed

        return True

    def execute_step(self, step: Dict, section_id: str, context: Dict) -> ExecutionResult:
        """
        Execute single step using appropriate agent

        Uses fractal memory to provide minimal context to execution agent.
        """
        step_id = step["step_id"]
        action = step["action"]
        agent_type = step.get("agent_type", "haiku-executor")

        print(f"\n⚙️  Executing step {step_id}: {action}")
        print(f"   Agent: {agent_type}")

        start_time = time.time()

        if self.dry_run:
            # Dry run - simulate execution
            print(f"   [DRY RUN] Would execute with {agent_type}")
            return ExecutionResult(
                step_id=step_id,
                status="success",
                output=f"[DRY RUN] Simulated execution of: {action}",
                execution_time=0.1,
                executed_by=agent_type,
                executed_at=datetime.now().isoformat()
            )

        try:
            # Get appropriate context for agent
            if agent_type == "haiku-executor":
                # Extract minimal step context (Haiku level)
                step_context = {
                    "step_id": step_id,
                    "action": action,
                    "inline_context": step.get("context", {}).get("inline_context", ""),
                    "expected_outcome": step.get("expected_outcome", ""),
                    "validation": step.get("validation", {})
                }

                # Store at Haiku level
                self.memory.haiku_level.store("step_contexts", step_id, step_context)

                # Simulate HaikuExecutor execution
                result = self._simulate_haiku_execution(step, step_context)

            elif agent_type == "sonnet-debugger":
                # Debugger gets task context + seed rules
                task_context = self.memory.sonnet_level.get_task_context(section_id)
                seed_rules = context["seed_rules"]

                # Simulate SonnetDebugger execution
                result = self._simulate_debugger_execution(step, task_context, seed_rules)

            elif agent_type == "sonnet-tracker":
                # Tracker synthesizes results
                result = self._simulate_tracker_execution(step, section_id)

            else:
                # Default: treat as haiku-executor
                result = ExecutionResult(
                    step_id=step_id,
                    status="success",
                    output=f"Executed: {action}",
                    execution_time=time.time() - start_time,
                    executed_by=agent_type,
                    executed_at=datetime.now().isoformat()
                )

            execution_time = time.time() - start_time
            result.execution_time = execution_time

            # Store result at appropriate level
            if agent_type == "haiku-executor":
                self.memory.haiku_level.store("step_results", step_id, {
                    "step_id": result.step_id,
                    "status": result.status,
                    "output": result.output,
                    "execution_time": result.execution_time
                })
            else:
                self.memory.sonnet_level.store("results", step_id, {
                    "step_id": result.step_id,
                    "status": result.status,
                    "output": result.output,
                    "execution_time": result.execution_time
                })

            print(f"   ✅ {result.status.upper()} ({result.execution_time:.2f}s)")

            return result

        except Exception as e:
            execution_time = time.time() - start_time

            print(f"   ❌ ERROR: {str(e)}")

            return ExecutionResult(
                step_id=step_id,
                status="error",
                output="",
                error_message=str(e),
                execution_time=execution_time,
                executed_by=agent_type,
                executed_at=datetime.now().isoformat()
            )

    def _simulate_haiku_execution(self, step: Dict, step_context: Dict) -> ExecutionResult:
        """Simulate HaikuExecutor execution"""
        # In real implementation, this would call actual HaikuExecutor
        # For now, simulate successful execution
        return ExecutionResult(
            step_id=step["step_id"],
            status="success",
            output=f"Completed: {step['action']}",
            executed_by="haiku-executor"
        )

    def _simulate_debugger_execution(self, step: Dict, task_context: Dict, seed_rules: Dict) -> ExecutionResult:
        """Simulate SonnetDebugger execution"""
        return ExecutionResult(
            step_id=step["step_id"],
            status="success",
            output=f"Debugged and resolved: {step['action']}",
            executed_by="sonnet-debugger"
        )

    def _simulate_tracker_execution(self, step: Dict, section_id: str) -> ExecutionResult:
        """Simulate SonnetTracker execution"""
        # Collect results from section
        # In real implementation, would synthesize actual results
        return ExecutionResult(
            step_id=step["step_id"],
            status="success",
            output=f"Tracked progress for section: {section_id}",
            executed_by="sonnet-tracker"
        )

    def find_executable_steps(self, sections: List[Dict], dependencies: Dict) -> List[tuple]:
        """
        Find all steps that can be executed now

        Returns list of (section, step) tuples ready for execution
        """
        executable = []

        for section in sections:
            section_id = section["section_id"]
            section_status = section.get("status", "pending")

            # Skip completed/blocked sections
            if section_status in ["completed", "blocked", "skipped"]:
                continue

            for step in section.get("steps", []):
                step_id = step["step_id"]
                step_status = step.get("status", "pending")

                # Skip non-pending steps
                if step_status != "pending":
                    continue

                # Check if can execute
                if self.can_execute_step(step, dependencies):
                    executable.append((section, step))

        return executable

    def execute_plan(self, plan: Dict, strategy: str = "balanced") -> Dict:
        """
        Execute plan with given strategy

        Now supports horizontal splitting for parallel sub-planners!

        Strategies:
        - sequential: Execute steps one by one in order
        - parallel: Execute independent steps simultaneously (simulated)
        - balanced: Mix of sequential and parallel
        - adaptive: Dynamically adjust based on progress
        - horizontal: Split plan and execute with parallel sub-planners (NEW!)
        """
        print(f"\n🚀 Executing plan with strategy: {strategy}")

        # NEW: Check if should split horizontally
        splitter = HorizontalPlanSplitter(self.memory)

        if splitter.should_split(plan):
            print("📊 Plan complexity detected - using horizontal splitting")
            return self._execute_horizontal(plan, splitter)
        else:
            print("📝 Plan simple enough - using vertical execution")
            return self._execute_vertical(plan, strategy)

    def _execute_horizontal(self, plan: Dict, splitter: HorizontalPlanSplitter) -> Dict:
        """
        Execute plan with horizontal splitting (parallel sub-planners)

        Creates sub-contexts for each boundary and spawns parallel OpusPlanner instances.
        Each sub-planner receives filtered seed rules for its boundary only.
        """
        print(f"\n{'='*70}")
        print(f"HORIZONTAL EXECUTION START")
        print(f"{'='*70}")

        # Step 1: Create sub-contexts using seed rules
        sub_contexts = splitter.create_sub_contexts(plan)
        print(f"\n📊 Created {len(sub_contexts)} sub-contexts:")
        for sc in sub_contexts:
            print(f"   - {sc.boundary}: {len(sc.sections)} sections, {sc.metadata['estimated_steps']} steps")

        # Step 2: Estimate token savings
        project_name = plan.get('project', {})
        if isinstance(project_name, dict):
            project_name = project_name.get('name', 'unknown')

        seed_rules = self.memory.opus_level.get_seed_rules(project_name)
        savings = splitter.estimate_token_savings(seed_rules, sub_contexts)
        print(f"\n💰 Token Savings Estimate:")
        print(f"   Without splitting: {savings['without_splitting']:,} tokens")
        print(f"   With splitting: {savings['with_splitting']:,} tokens")
        print(f"   Savings: {savings['savings_tokens']:,} tokens ({savings['savings_percent']}%)")

        if self.dry_run:
            print(f"\n[DRY RUN] Would spawn {len(sub_contexts)} parallel sub-planners")
            print(f"[DRY RUN] Simulating execution...")

            # Simulate sub-planner results
            results = []
            for sc in sub_contexts:
                results.append({
                    "sub_plan_id": sc.sub_plan_id,
                    "boundary": sc.boundary,
                    "status": "success",
                    "completed_steps": sc.metadata['estimated_steps'],
                    "dry_run": True
                })
        else:
            # Real execution would spawn Task agents here
            # For now, simulate (real implementation would use Task tool)
            print(f"\n⚠️  Note: Real sub-planner spawning not yet implemented")
            print(f"   Would spawn Task agents with OpusPlanner type")

            results = []
            for sc in sub_contexts:
                results.append({
                    "sub_plan_id": sc.sub_plan_id,
                    "boundary": sc.boundary,
                    "status": "simulated",
                    "completed_steps": sc.metadata['estimated_steps'],
                    "message": "Sub-planner spawning to be implemented"
                })

        # Step 3: Synthesize results
        synthesis = self._synthesize_horizontal_results(plan, sub_contexts, results)

        print(f"\n{'='*70}")
        print(f"HORIZONTAL EXECUTION COMPLETE")
        print(f"{'='*70}")

        return synthesis

    def _execute_vertical(self, plan: Dict, strategy: str = "balanced") -> Dict:
        """
        Execute plan with vertical distillation (existing sequential/parallel logic)

        This is the original execution logic, now extracted as a separate method.
        """
        print(f"\n{'='*70}")
        print(f"VERTICAL EXECUTION START")
        print(f"{'='*70}")

        # Prepare context
        context = self.prepare_context(plan)

        # Get dependencies
        dependencies = plan.get("dependencies", {})

        # Track execution
        total_steps = sum(len(s.get("steps", [])) for s in plan["sections"])
        completed_count = 0
        error_count = 0

        print(f"\n{'='*70}")
        print(f"EXECUTION START")
        print(f"{'='*70}")

        # Execute until all steps done
        while completed_count + error_count < total_steps:
            # Find executable steps
            executable = self.find_executable_steps(plan["sections"], dependencies)

            if not executable:
                # No more executable steps
                if self.blocked_steps:
                    print(f"\n⚠️  Execution blocked: {len(self.blocked_steps)} steps blocked by failures")
                break

            # Execute based on strategy
            if strategy == "sequential":
                # Execute first available step
                section, step = executable[0]
                result = self.execute_step(step, section["section_id"], context)

                if result.status == "success":
                    self.executed_steps.add(result.step_id)
                    completed_count += 1
                else:
                    self.failed_steps.add(result.step_id)
                    error_count += 1

            elif strategy in ["parallel", "balanced", "adaptive"]:
                # Execute all available steps (simulated parallel)
                # In real implementation, would use actual parallel execution
                for section, step in executable:
                    result = self.execute_step(step, section["section_id"], context)

                    if result.status == "success":
                        self.executed_steps.add(result.step_id)
                        completed_count += 1
                    else:
                        self.failed_steps.add(result.step_id)
                        error_count += 1

        print(f"\n{'='*70}")
        print(f"EXECUTION COMPLETE")
        print(f"{'='*70}")

        # Synthesize results (SonnetTracker pattern)
        synthesis = self.synthesize_results(plan, context)

        # Store synthesis
        self.memory.sonnet_level.store("synthesized_results", plan["plan_id"], synthesis)

        print(f"\n📊 Execution Summary:")
        print(f"   Total steps: {total_steps}")
        print(f"   Completed: {completed_count}")
        print(f"   Errors: {error_count}")
        print(f"   Blocked: {len(self.blocked_steps)}")
        print(f"   Success rate: {100 * completed_count / total_steps:.1f}%")

        return synthesis

    def _synthesize_horizontal_results(
        self,
        plan: Dict,
        sub_contexts: List,
        sub_results: List[Dict]
    ) -> Dict:
        """
        Synthesize results from parallel sub-planners (horizontal execution)

        Combines results from multiple Opus sub-planners into single synthesis.
        """
        print(f"\n🔄 Synthesizing horizontal results...")

        # Calculate totals
        total_sub_plans = len(sub_contexts)
        successful_sub_plans = sum(1 for r in sub_results if r.get("status") == "success")
        total_steps = sum(sc.metadata['estimated_steps'] for sc in sub_contexts)
        completed_steps = sum(r.get("completed_steps", 0) for r in sub_results)

        # Get project name
        project_name = plan.get('project', {})
        if isinstance(project_name, dict):
            project_name = project_name.get('name', 'unknown')

        synthesis = {
            "plan_id": plan["plan_id"],
            "project": project_name,
            "execution_strategy": "horizontal",
            "total_sub_plans": total_sub_plans,
            "successful_sub_plans": successful_sub_plans,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "success_rate": 100 * completed_steps / total_steps if total_steps > 0 else 0,
            "sub_plan_results": [
                {
                    "sub_plan_id": r["sub_plan_id"],
                    "boundary": r["boundary"],
                    "status": r["status"],
                    "completed_steps": r.get("completed_steps", 0)
                }
                for r in sub_results
            ],
            "executed_at": datetime.now().isoformat(),
            "dry_run": self.dry_run
        }

        # Store synthesis
        self.memory.sonnet_level.store("synthesized_results", plan["plan_id"], synthesis)

        print(f"   ✅ Horizontal synthesis complete")
        print(f"   Sub-plans: {successful_sub_plans}/{total_sub_plans} successful")
        print(f"   Total steps: {completed_steps}/{total_steps} completed")

        return synthesis

    def synthesize_results(self, plan: Dict, context: Dict) -> Dict:
        """
        Synthesize results from all executed steps (SonnetTracker pattern)
        """
        print(f"\n🔄 Synthesizing results...")

        total_steps = sum(len(s.get("steps", [])) for s in plan["sections"])

        synthesis = {
            "plan_id": plan["plan_id"],
            "project": context["project"],
            "execution_strategy": "balanced",  # Could be parameterized
            "total_steps": total_steps,
            "completed_steps": len(self.executed_steps),
            "failed_steps": len(self.failed_steps),
            "blocked_steps": len(self.blocked_steps),
            "success_rate": 100 * len(self.executed_steps) / total_steps if total_steps > 0 else 0,
            "executed_at": datetime.now().isoformat(),
            "dry_run": self.dry_run
        }

        print(f"   ✅ Results synthesized")

        return synthesis


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Execute orchestration plans")
    parser.add_argument("plan", type=Path, help="Path to execution plan JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without actually running")
    parser.add_argument("--strategy", choices=["sequential", "parallel", "balanced", "adaptive"],
                       default="balanced", help="Execution strategy")

    args = parser.parse_args()

    # Validate plan exists
    if not args.plan.exists():
        print(f"❌ Plan file not found: {args.plan}")
        return 1

    # Create engine
    engine = ExecutionEngine(dry_run=args.dry_run)

    # Load plan
    try:
        plan = engine.load_plan(args.plan)
    except Exception as e:
        print(f"❌ Failed to load plan: {e}")
        return 1

    # Execute plan
    try:
        synthesis = engine.execute_plan(plan, strategy=args.strategy)

        # Print results
        print(f"\n✅ Execution complete")
        print(f"   Success rate: {synthesis['success_rate']:.1f}%")

        if synthesis["failed_steps"] > 0 or synthesis["blocked_steps"] > 0:
            return 1

        return 0

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
