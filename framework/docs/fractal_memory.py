#!/usr/bin/env python3
"""
Fractal Memory System - Hierarchical Context Distillation

Mirrors agent hierarchy with 4 memory levels:
1. User Level: Full project context (unlimited)
2. Opus Level: Seed rules and patterns (10-50K tokens)
3. Sonnet Level: Task-oriented context (5-15K tokens)
4. Haiku Level: Minimal step context (<2K tokens)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class MemoryLayer:
    """Base class for memory layers"""

    def __init__(self, base_path: str, layer_name: str):
        self.base_path = Path(base_path)
        self.layer_name = layer_name
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, key: str) -> Path:
        """Get file path for a memory entry"""
        category_path = self.base_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        return category_path / f"{key}.json"

    def store(self, category: str, key: str, data: Dict) -> None:
        """Store data in this layer"""
        path = self._get_path(category, key)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def retrieve(self, category: str, key: str) -> Optional[Dict]:
        """Retrieve data from this layer"""
        path = self._get_path(category, key)
        if not path.exists():
            return None
        with open(path, 'r') as f:
            return json.load(f)

    def list_keys(self, category: str) -> List[str]:
        """List all keys in a category"""
        category_path = self.base_path / category
        if not category_path.exists():
            return []
        return [f.stem for f in category_path.glob("*.json")]

    def exists(self, category: str, key: str) -> bool:
        """Check if entry exists"""
        return self._get_path(category, key).exists()


class UserLevelMemory(MemoryLayer):
    """
    User Level Memory - Infinite Context

    Stores complete project knowledge:
    - Full file contents
    - Complete history
    - All patterns
    - External dependencies

    No token limits - this is the source of truth
    """

    def __init__(self, base_path: str):
        super().__init__(base_path, "user_level")

    def store_project_context(self, project: str, context: Dict) -> None:
        """Store complete project context"""
        self.store("projects", project, {
            "project": project,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "full_context": context
        })

    def get_full_context(self, project: str) -> Optional[Dict]:
        """Retrieve complete project context"""
        data = self.retrieve("projects", project)
        return data["full_context"] if data else None

    def store_research(self, topic: str, findings: Dict) -> None:
        """Store research findings"""
        self.store("research", topic, {
            "topic": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings": findings
        })

    def get_research(self, topic: str) -> Optional[Dict]:
        """Retrieve research findings"""
        data = self.retrieve("research", topic)
        return data["findings"] if data else None


class OpusLevelMemory(MemoryLayer):
    """
    Opus Level Memory - Orchestration Context (10-50K tokens)

    Stores distilled knowledge:
    - Seed rules
    - Architectural patterns
    - Cross-cutting concerns
    - Project conventions

    Read by: OpusPlanner
    Written by: OpusPlanner (distilled from User level)
    """

    def __init__(self, base_path: str, project_root: Optional[str] = None):
        super().__init__(base_path, "opus_level")
        self.project_root = Path(project_root) if project_root else None

    def store_seed_rules(
        self,
        project: str,
        seed_rules: Any,
        workflow: str = "general",
        project_root: Optional[Path] = None
    ) -> None:
        """
        Store project seed rules.

        New behaviour: writes one JSON file per rule into
        {project_root}/seeds/workflows/{workflow}/{rule_id}.json

        Legacy behaviour (if seed_rules is a Dict and no project_root):
        writes a single JSON file at seed_rules/{project}.json
        """
        root = project_root or self.project_root

        if root is not None and isinstance(seed_rules, list):
            # New format: list of rule dicts → individual files per workflow
            workflow_dir = root / "seeds" / "workflows" / workflow
            workflow_dir.mkdir(parents=True, exist_ok=True)
            for rule in seed_rules:
                rule_id = rule.get("id") if isinstance(rule, dict) else rule.id
                rule_data = rule if isinstance(rule, dict) else rule.to_dict()
                filepath = workflow_dir / f"{rule_id}.json"
                with open(filepath, 'w') as f:
                    json.dump(rule_data, f, indent=2)
        else:
            # Legacy format: single dict → one project JSON file
            self.store("seed_rules", project, {
                "project": project,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "seed_rules": seed_rules,
                "token_estimate": self._estimate_tokens(seed_rules) if isinstance(seed_rules, dict) else 0
            })

    def get_seed_rules(
        self,
        project: str,
        workflow: str = "general",
        project_root: Optional[Path] = None
    ) -> Optional[List[Dict]]:
        """
        Retrieve project seed rules.

        Reads from {project_root}/seeds/workflows/{workflow}/*.json if available.
        Falls back to legacy .claude/memory/opus_level/seed_rules/{project}.json.
        Returns List[Dict] in both cases.
        """
        root = project_root or self.project_root

        # Try new workflow-scoped format first
        if root is not None:
            workflow_dir = root / "seeds" / "workflows" / workflow
            if workflow_dir.exists():
                rules = []
                for rule_file in sorted(workflow_dir.glob("*.json")):
                    with open(rule_file, 'r') as f:
                        rules.append(json.load(f))
                if rules:
                    return rules

        # Backward-compat: load old single-file format and reshape
        data = self.retrieve("seed_rules", project)
        if data:
            old_rules = data.get("seed_rules", {})
            return self._convert_legacy_rules(old_rules)

        return None

    def _convert_legacy_rules(self, old_rules: Dict) -> List[Dict]:
        """Convert legacy nested-dict seed rules to new List[Dict] format."""
        result = []
        patterns = old_rules.get("patterns", {})
        for pattern_key, pattern_data in patterns.items():
            rule_id = pattern_key.lower().replace(" ", "_").replace("-", "_")
            rule_text = pattern_data.get("pattern", pattern_key)
            files = pattern_data.get("files", [])
            grounding = ",".join(files[:3]) if files else f"pattern:{pattern_key}"
            result.append({
                "id": rule_id,
                "goal": f"Maintain the established {pattern_key} pattern",
                "grounding": grounding,
                "rule": rule_text,
                "connected_seed_rules": {}
            })
        return result

    def assemble_prompt_rules(
        self,
        workflow: str,
        project_root: Optional[Path] = None,
        project: Optional[str] = None
    ) -> str:
        """
        Assemble the runtime system prompt fragment from a workflow's seed chain.

        Walks connected_seed_rules[workflow] to build the full ordered chain,
        deduplicates, and returns only the `rule` one-liners joined by newlines.

        Only `rule` fields are returned — goal/grounding/connected_seed_rules
        are NEVER included in the runtime prompt.
        """
        root = project_root or self.project_root
        rules = self.get_seed_rules(project or "unknown", workflow=workflow, project_root=root)
        if not rules:
            return ""

        # Build lookup by id
        rules_by_id: Dict[str, Dict] = {r["id"]: r for r in rules}

        # Walk the seed chain: start with all rules in workflow dir,
        # then expand connected_seed_rules[workflow] entries (depth 1)
        seen: set = set()
        ordered: List[str] = []

        def add_rule(rule_id: str):
            if rule_id in seen or rule_id not in rules_by_id:
                return
            seen.add(rule_id)
            rule = rules_by_id[rule_id]
            rule_text = rule.get("rule", "").strip()
            if rule_text:
                ordered.append(rule_text)
            # Expand workflow connections (depth 1 only)
            connected = rule.get("connected_seed_rules", {})
            for connected_id in connected.get(workflow, []):
                if connected_id not in seen and connected_id in rules_by_id:
                    seen.add(connected_id)
                    connected_rule = rules_by_id[connected_id]
                    connected_text = connected_rule.get("rule", "").strip()
                    if connected_text:
                        ordered.append(connected_text)

        for rule in rules:
            add_rule(rule["id"])

        return "\n".join(ordered)

    def store_pattern(self, pattern_name: str, pattern: Dict) -> None:
        """Store reusable pattern"""
        self.store("patterns", pattern_name, {
            "pattern_name": pattern_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pattern": pattern
        })

    def get_pattern(self, pattern_name: str) -> Optional[Dict]:
        """Retrieve pattern"""
        data = self.retrieve("patterns", pattern_name)
        return data["pattern"] if data else None

    def store_architecture_decision(self, project: str, decision: Dict) -> None:
        """Store architectural decision"""
        decisions_data = self.retrieve("architecture", project) or {
            "project": project,
            "decisions": []
        }
        decisions_data["decisions"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **decision
        })
        self.store("architecture", project, decisions_data)

    def get_architecture_decisions(self, project: str) -> List[Dict]:
        """Retrieve all architectural decisions"""
        data = self.retrieve("architecture", project)
        return data["decisions"] if data else []

    def _estimate_tokens(self, data: Dict) -> int:
        """Rough token estimate (1 token ≈ 4 characters)"""
        json_str = json.dumps(data)
        return len(json_str) // 4


class SonnetLevelMemory(MemoryLayer):
    """
    Sonnet Level Memory - Execution Context (5-15K tokens)

    Stores task-specific knowledge:
    - Task contexts (engineered by OpusPlanner)
    - Working memory (current task state)
    - Task results

    Read by: SonnetCoder, SonnetDebugger
    Written by: OpusPlanner (engineered contexts), SonnetCoder (results)
    """

    def __init__(self, base_path: str):
        super().__init__(base_path, "sonnet_level")

    def store_task_context(self, task_id: str, context: Dict) -> None:
        """Store engineered task context (from OpusPlanner)"""
        self.store("task_contexts", task_id, {
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engineered_context": context,
            "token_estimate": self._estimate_tokens(context)
        })

    def get_task_context(self, task_id: str) -> Optional[Dict]:
        """Retrieve task context"""
        data = self.retrieve("task_contexts", task_id)
        return data["engineered_context"] if data else None

    def store_working_memory(self, agent: str, state: Dict) -> None:
        """Store current working state for agent"""
        self.store("working_memory", agent, {
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": state
        })

    def get_working_memory(self, agent: str) -> Optional[Dict]:
        """Retrieve agent's working state"""
        data = self.retrieve("working_memory", agent)
        return data["state"] if data else None

    def store_task_result(self, task_id: str, result: Dict) -> None:
        """Store task execution result"""
        self.store("results", task_id, {
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result
        })

    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Retrieve task result"""
        data = self.retrieve("results", task_id)
        return data["result"] if data else None

    def get_all_results(self) -> List[Dict]:
        """Retrieve all task results"""
        task_ids = self.list_keys("results")
        return [self.get_task_result(tid) for tid in task_ids]

    def _estimate_tokens(self, data: Dict) -> int:
        """Rough token estimate"""
        json_str = json.dumps(data)
        return len(json_str) // 4


class HaikuLevelMemory(MemoryLayer):
    """
    Haiku Level Memory - Minimal Step Context (<2K tokens)

    Stores absolute minimum for single steps:
    - Step contexts (inline instructions only)
    - Step results

    Read by: HaikuExecutor
    Written by: OpusPlanner or SonnetCoder (step decomposition)
    """

    def __init__(self, base_path: str):
        super().__init__(base_path, "haiku_level")

    def store_step_context(self, step_id: str, context: Dict) -> None:
        """Store minimal step context"""
        token_count = self._estimate_tokens(context)
        if token_count > 2000:
            print(f"WARNING: Step context {step_id} exceeds 2K tokens ({token_count})")

        self.store("step_contexts", step_id, {
            "step_id": step_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "minimal_context": context,
            "token_estimate": token_count
        })

    def get_step_context(self, step_id: str) -> Optional[Dict]:
        """Retrieve step context"""
        data = self.retrieve("step_contexts", step_id)
        return data["minimal_context"] if data else None

    def store_step_result(self, step_id: str, result: Dict) -> None:
        """Store step execution result"""
        self.store("step_results", step_id, {
            "step_id": step_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result
        })

    def get_step_result(self, step_id: str) -> Optional[Dict]:
        """Retrieve step result"""
        data = self.retrieve("step_results", step_id)
        return data["result"] if data else None

    def get_all_results(self) -> List[Dict]:
        """Retrieve all step results"""
        step_ids = self.list_keys("step_results")
        return [self.get_step_result(sid) for sid in step_ids]

    def _estimate_tokens(self, data: Dict) -> int:
        """Rough token estimate"""
        json_str = json.dumps(data)
        return len(json_str) // 4


class FractalMemory:
    """
    Fractal Memory System - Main Interface

    Provides hierarchical memory with automatic context distillation.
    Each level mirrors the agent hierarchy:

    User → Opus → Sonnet → Haiku
    (Full) (Patterns) (Task) (Step)
    """

    def __init__(self, base_path: str = ".claude/memory", project_root: Optional[str] = None):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Resolve project root: explicit > inferred from base_path > None
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Infer: if base_path is .claude/memory, project root is ../..
            inferred = self.base_path.parent.parent
            self.project_root = inferred if (inferred / "seeds").exists() or inferred.exists() else None

        # Initialize all memory layers
        self.user_level = UserLevelMemory(str(self.base_path / "user_level"))
        self.opus_level = OpusLevelMemory(
            str(self.base_path / "opus_level"),
            project_root=str(self.project_root) if self.project_root else None
        )
        self.sonnet_level = SonnetLevelMemory(str(self.base_path / "sonnet_level"))
        self.haiku_level = HaikuLevelMemory(str(self.base_path / "haiku_level"))

    def store_project(self, project: str, full_context: Dict) -> None:
        """
        Store project at User level (full context)

        This is the entry point - all distillation flows from here
        """
        self.user_level.store_project_context(project, full_context)

    def distill_to_opus(self, project: str, distiller_func=None, workflow: str = "general") -> Any:
        """
        Distill User context to Opus level (seed rules)
        """
        full_context = self.user_level.get_full_context(project)
        if not full_context:
            raise ValueError(f"No full context found for project: {project}")

        if distiller_func:
            seed_rules = distiller_func(full_context)
        else:
            seed_rules = self._default_seed_extraction(full_context)

        self.opus_level.store_seed_rules(project, seed_rules, workflow=workflow, project_root=self.project_root)

        return seed_rules

    def distill_to_sonnet(self, project: str, task: Dict, engineer_func=None) -> Dict:
        """
        Engineer Sonnet context from Opus level

        OpusPlanner calls this to create task-oriented context
        """
        seed_rules = self.opus_level.get_seed_rules(project)
        if not seed_rules:
            raise ValueError(f"No seed rules found for project: {project}")

        # Use provided engineer or default
        if engineer_func:
            task_context = engineer_func(seed_rules, task)
        else:
            task_context = self._default_task_engineering(seed_rules, task)

        # Store at Sonnet level
        self.sonnet_level.store_task_context(task["task_id"], task_context)

        return task_context

    def distill_to_haiku(self, task_id: str, step: Dict, extract_func=None) -> Dict:
        """
        Extract Haiku context from Sonnet level

        SonnetCoder calls this when decomposing complex tasks
        """
        task_context = self.sonnet_level.get_task_context(task_id)
        if not task_context:
            raise ValueError(f"No task context found: {task_id}")

        # Use provided extractor or default
        if extract_func:
            step_context = extract_func(task_context, step)
        else:
            step_context = self._default_step_extraction(task_context, step)

        # Store at Haiku level
        self.haiku_level.store_step_context(step["step_id"], step_context)

        return step_context

    def _default_seed_extraction(self, full_context: Dict) -> List[Dict]:
        """Default seed rule extraction — returns new List[Dict] format."""
        return [{
            "id": "project_overview_pattern",
            "goal": "Provide baseline context about this project's structure",
            "grounding": f"pattern:{full_context.get('project', 'unknown')}",
            "rule": f"This is the {full_context.get('project', 'unknown')} project; follow existing patterns",
            "connected_seed_rules": {}
        }]

    def _default_task_engineering(self, seed_rules: Any, task: Dict) -> Dict:
        """Default task context engineering."""
        # Extract rule strings from new format or old format
        if isinstance(seed_rules, list):
            rules_text = [r.get("rule", "") for r in seed_rules if r.get("rule")]
        else:
            rules_text = []

        return {
            "task_id": task.get("task_id"),
            "action": task.get("action"),
            "inline_rules": rules_text,
            "inline_context": task.get("description", ""),
            "note": "Default engineering - implement custom engineer for better results"
        }

    def _default_step_extraction(self, task_context: Dict, step: Dict) -> Dict:
        """Default step context extraction (placeholder)"""
        return {
            "step_id": step.get("step_id"),
            "action": step.get("action"),
            "minimal_context": step.get("description", ""),
            "note": "Default extraction - implement custom extractor for better results"
        }

    def get_context_for_agent(self, agent_type: str, context_id: str) -> Optional[Dict]:
        """
        Retrieve appropriate context for agent type

        Automatically selects the right memory level:
        - opus-planner → Opus level (seed rules)
        - sonnet-coder/sonnet-debugger → Sonnet level (task context)
        - haiku-executor → Haiku level (step context)
        """
        if agent_type == "opus-planner":
            return self.opus_level.get_seed_rules(context_id)
        elif agent_type in ["sonnet-coder", "sonnet-debugger", "sonnet-tracker"]:
            return self.sonnet_level.get_task_context(context_id)
        elif agent_type == "haiku-executor":
            return self.haiku_level.get_step_context(context_id)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    def get_statistics(self) -> Dict:
        """Get memory usage statistics across all levels"""
        return {
            "user_level": {
                "projects": len(self.user_level.list_keys("projects")),
                "research": len(self.user_level.list_keys("research"))
            },
            "opus_level": {
                "seed_rules": len(self.opus_level.list_keys("seed_rules")),
                "patterns": len(self.opus_level.list_keys("patterns")),
                "architecture": len(self.opus_level.list_keys("architecture"))
            },
            "sonnet_level": {
                "task_contexts": len(self.sonnet_level.list_keys("task_contexts")),
                "results": len(self.sonnet_level.list_keys("results"))
            },
            "haiku_level": {
                "step_contexts": len(self.haiku_level.list_keys("step_contexts")),
                "step_results": len(self.haiku_level.list_keys("step_results"))
            }
        }


# CLI for testing
if __name__ == "__main__":
    import sys

    memory = FractalMemory()

    if len(sys.argv) < 2:
        print("Fractal Memory System")
        print("\nUsage:")
        print("  python fractal_memory.py stats")
        print("  python fractal_memory.py test")
        sys.exit(0)

    command = sys.argv[1]

    if command == "stats":
        stats = memory.get_statistics()
        print(json.dumps(stats, indent=2))

    elif command == "test":
        print("Running fractal memory test...")

        # Test: Store full project context
        test_project = "test_project"
        test_context = {
            "project": test_project,
            "files": ["app/main.py", "app/auth.py"],
            "patterns": {"auth": "JWT"},
            "tech_stack": ["Python", "FastAPI"]
        }

        print("\n1. Storing full context at User level...")
        memory.store_project(test_project, test_context)

        print("2. Distilling to Opus level (seed rules)...")
        seed_rules = memory.distill_to_opus(test_project)
        print(f"   Seed rules: {json.dumps(seed_rules, indent=2)}")

        print("\n3. Engineering Sonnet context for task...")
        task = {"task_id": "t1", "action": "Add auth", "description": "Add JWT auth"}
        task_context = memory.distill_to_sonnet(test_project, task)
        print(f"   Task context: {json.dumps(task_context, indent=2)}")

        print("\n4. Extracting Haiku context for step...")
        step = {"step_id": "s1", "action": "Create route", "description": "Create auth route"}
        step_context = memory.distill_to_haiku("t1", step)
        print(f"   Step context: {json.dumps(step_context, indent=2)}")

        print("\n5. Statistics:")
        stats = memory.get_statistics()
        print(json.dumps(stats, indent=2))

        print("\n✅ Fractal memory test complete!")
