# Orchestrator Pattern

**Source:** ORCHESTRATOR_SEPARATION_PRINCIPLE.md
**Section:** Orchestration Workflow Pattern

---

## Orchestration Workflow Pattern

### Verification → Execution → Verification Loop

```python
class OpusPlannerAgent:
    def orchestrate(self, user_request):
        # 1. INITIAL PLANNING (lightweight)
        long_term_goal = self.define_goal(user_request)  # 500 tokens
        plan_phases = self.create_plan_phases(long_term_goal)  # 2K tokens

        # Store plan in memory (OpusPlanner does NOT keep it)
        memory.opus_level.store_plan(plan_id, plan_phases)

        # 2. DELEGATE CONTEXT ENGINEERING (spawn & forget)
        context_task = Task(
            subagent_type="context-engineer",
            prompt=f"Engineer contexts for plan: {plan_id}",
            run_in_background=True
        )

        # OpusPlanner continues (does NOT wait)

        # 3. EXECUTION LOOP (lightweight control)
        for phase in plan_phases:
            # VERIFICATION (check if ready)
            if not self.verify_phase_ready(phase):
                self.handle_blocker(phase)
                continue

            # EXECUTION (delegate to specialists)
            results = self.execute_phase_parallel(phase)

            # VERIFICATION (check results)
            verification = self.verify_results(results, phase.expected_outcomes)

            if verification.status == "failed":
                # PROBLEM-SOLVING (spawn debugger)
                self.spawn_debugger(phase, verification.issues)

                # VERIFICATION (check if fixed)
                retry_results = self.retry_phase(phase)
                verification = self.verify_results(retry_results, phase.expected_outcomes)

            if verification.status == "success":
                # Update progress (lightweight)
                self.mark_phase_complete(phase)
            else:
                # Escalate to user
                user_decision = self.escalate(phase, verification)
                self.apply_decision(user_decision)

        # 4. FINAL VERIFICATION
        return self.verify_long_term_goal_achieved(long_term_goal)

    def verify_phase_ready(self, phase):
        """Lightweight check - no context loading"""
        dependencies_met = all(
            memory.opus_level.is_phase_complete(dep)
            for dep in phase.dependencies
        )
        return dependencies_met

    def execute_phase_parallel(self, phase):
        """Spawn agents, get lightweight summaries back"""
        task_ids = []
        for task in phase.tasks:
            # Spawn agent (agent reads context from memory)
            task_id = Task(
                subagent_type=task.agent_type,
                prompt=f"Execute task {task.id} (context in memory)",
                run_in_background=True
            )
            task_ids.append(task_id)

        # Collect lightweight summaries (NOT full results)
        summaries = [
            TaskOutput(tid, block=True).get_summary()
            for tid in task_ids
        ]

        return summaries  # Lightweight: 100-500 tokens per task

    def verify_results(self, results, expected_outcomes):
        """Lightweight verification - just pass/fail + issues"""
        verification = {
            "status": "success",
            "issues": []
        }

        for result, expected in zip(results, expected_outcomes):
            if not self.matches_expectation(result.summary, expected):
                verification["status"] = "failed"
                verification["issues"].append({
                    "task_id": result.task_id,
                    "expected": expected,
                    "got": result.summary
                })

        return verification

    def spawn_debugger(self, phase, issues):
        """Problem-solving coordination"""
        Task(
            subagent_type="sonnet-debugger",
            prompt=f"Debug phase {phase.id}, issues: {issues}",
            run_in_background=True
        )
```

---



---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: ORCHESTRATOR_SEPARATION_PRINCIPLE.md](../ORCHESTRATOR_SEPARATION_PRINCIPLE.md)
