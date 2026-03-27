#!/usr/bin/env python3
"""
Horizontal Plan Splitter - Extend Fractal System with Parallel Sub-Planners

Adds horizontal splitting dimension to existing vertical fractal distillation.
Uses existing seed rules to detect natural boundaries and create sub-contexts.

Architecture:
    User Level (Full Context)
         ↓ distill_to_opus()
    Opus Level (Seed Rules)
         ↓
    ╔════╬════╗  ← HORIZONTAL SPLIT (this module)
    ↓    ↓    ↓
  Opus₁ Opus₂ Opus₃  (parallel sub-planners)
    ↓    ↓    ↓
  Sonnet → Haiku (existing vertical distillation)

Key Principle: Use seed rule boundaries to avoid context duplication.
Each sub-planner gets ONLY the seed rules relevant to its boundary.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import networkx as nx


@dataclass
class Boundary:
    """Natural split boundary detected from seed rules"""
    name: str
    sections: List[Dict] = field(default_factory=list)
    complexity: int = 0
    parallelizable: bool = True
    dependencies: Set[str] = field(default_factory=set)

    def add_section(self, section: Dict):
        """Add section to this boundary"""
        self.sections.append(section)
        self.complexity += section.get('metadata', {}).get('estimated_steps', 1)

        # Check if any section in this boundary has dependencies
        deps = section.get('metadata', {}).get('dependencies', [])
        if deps:
            self.parallelizable = False
            for dep in deps:
                self.dependencies.add(dep)


@dataclass
class SubContext:
    """Sub-context package for horizontal sub-planner"""
    sub_plan_id: str
    boundary: str
    sections: List[Dict]
    seed_rules: Dict
    coordination: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


class HorizontalPlanSplitter:
    """
    Split execution plans horizontally into parallel sub-contexts.

    Uses existing seed rules from OpusLevelMemory to:
    1. Detect natural boundaries (auth, database, API, etc.)
    2. Group sections by boundary
    3. Filter seed rules per boundary
    4. Create independent sub-contexts

    Integrates with existing ExecutionEngine for parallel execution.
    """

    def __init__(self, fractal_memory):
        """
        Initialize splitter with fractal memory access.

        Args:
            fractal_memory: FractalMemory instance (provides access to seed rules)
        """
        self.memory = fractal_memory
        self.complexity_threshold = 8  # Split if section has >8 steps
        self.min_sections_for_split = 4  # Need at least 4 sections to split

    def should_split(self, plan: Dict) -> bool:
        """
        Decide if plan should be split horizontally.

        Uses heuristics:
        1. Plan has >4 sections (min_sections_for_split)
        2. Multiple boundaries detected in seed rules
        3. Sections can run in parallel (low dependencies)
        4. Total complexity warrants splitting

        Args:
            plan: Execution plan dictionary

        Returns:
            True if plan should be split, False otherwise
        """
        sections = plan.get('sections', [])

        # Check 1: Enough sections?
        if len(sections) < self.min_sections_for_split:
            return False

        # Check 2: Get seed rules for project
        project_name = plan.get('project', {})
        if isinstance(project_name, dict):
            project_name = project_name.get('name', 'unknown')

        seed_rules = self.memory.opus_level.get_seed_rules(project_name)
        if not seed_rules:
            return False  # No seed rules = can't split

        # Check 3: Multiple boundaries?
        boundaries = self._detect_boundaries(sections, seed_rules)
        if len(boundaries) < 2:
            return False  # Need at least 2 boundaries to split

        # Check 4: Total complexity high enough?
        total_steps = sum(
            s.get('metadata', {}).get('estimated_steps', 1)
            for s in sections
        )
        if total_steps < self.complexity_threshold * 2:
            return False  # Not complex enough to warrant splitting

        return True

    def create_sub_contexts(self, plan: Dict) -> List[SubContext]:
        """
        Create sub-context packages for horizontal splitting.

        Process:
        1. Detect boundaries from seed rules
        2. Group sections by boundary
        3. Filter seed rules per boundary (KEY: avoid duplication!)
        4. Create sub-context with coordination info

        Args:
            plan: Execution plan dictionary

        Returns:
            List of SubContext objects for parallel execution
        """
        project_name = plan.get('project', {})
        if isinstance(project_name, dict):
            project_name = project_name.get('name', 'unknown')

        seed_rules = self.memory.opus_level.get_seed_rules(project_name)
        sections = plan.get('sections', [])

        # Step 1: Detect boundaries
        boundaries = self._detect_boundaries(sections, seed_rules)

        # Step 2: Build dependency graph
        dependency_graph = self._build_dependency_graph(sections)

        # Step 3: Create sub-contexts
        sub_contexts = []
        for boundary in boundaries:
            # Filter seed rules for this boundary only
            filtered_seeds = self._filter_seeds_for_boundary(
                seed_rules,
                boundary.name,
                boundary.sections
            )

            # Detect cross-boundary dependencies
            cross_deps = self._find_cross_boundary_dependencies(
                boundary,
                dependency_graph,
                boundaries
            )

            # Create sub-context
            sub_ctx = SubContext(
                sub_plan_id=f"sp-{project_name}-{boundary.name}",
                boundary=boundary.name,
                sections=boundary.sections,
                seed_rules=filtered_seeds,
                coordination={
                    "can_run_parallel": boundary.parallelizable and not cross_deps,
                    "dependencies": list(cross_deps),
                    "parent_plan_id": plan.get('plan_id', 'unknown')
                },
                metadata={
                    "complexity": boundary.complexity,
                    "estimated_steps": sum(
                        s.get('metadata', {}).get('estimated_steps', 1)
                        for s in boundary.sections
                    ),
                    "section_count": len(boundary.sections)
                }
            )
            sub_contexts.append(sub_ctx)

        return sub_contexts

    def _detect_boundaries(
        self,
        sections: List[Dict],
        seed_rules: Dict
    ) -> List[Boundary]:
        """
        Detect natural boundaries from sections and seed rules.

        Strategy:
        1. Extract boundary tags from section metadata
        2. Use seed rule patterns to infer boundaries
        3. Group sections by boundary
        4. Handle "default" boundary for untagged sections

        Args:
            sections: List of plan sections
            seed_rules: Seed rules from OpusLevelMemory

        Returns:
            List of Boundary objects
        """
        # Group sections by boundary tag
        boundary_map = defaultdict(lambda: Boundary(name="default"))

        for section in sections:
            # Get boundary from section metadata
            boundary_name = section.get('metadata', {}).get('boundary')

            # If no explicit boundary, infer from seed rules
            if not boundary_name:
                boundary_name = self._infer_boundary_from_seed_rules(
                    section,
                    seed_rules
                )

            # Add section to boundary
            if boundary_name not in boundary_map:
                boundary_map[boundary_name] = Boundary(name=boundary_name)

            boundary_map[boundary_name].add_section(section)

        # Convert to list and filter out empty boundaries
        boundaries = [b for b in boundary_map.values() if b.sections]

        return boundaries

    def _infer_boundary_from_seed_rules(
        self,
        section: Dict,
        seed_rules: Dict
    ) -> str:
        """
        Infer boundary by matching section title/description to seed rule patterns.

        Args:
            section: Plan section
            seed_rules: Project seed rules

        Returns:
            Inferred boundary name or "default"
        """
        title = section.get('title', '').lower()
        description = section.get('description', '').lower()
        section_text = f"{title} {description}"

        # Check seed rule patterns for matches
        patterns = seed_rules.get('patterns', {})

        for pattern_name, pattern_data in patterns.items():
            # Check if pattern keywords appear in section text
            if pattern_name.lower() in section_text:
                # Return boundary from pattern, or pattern name as boundary
                return pattern_data.get('boundary', pattern_name)

        # Check conventions
        conventions = seed_rules.get('conventions', {})
        for conv_type, conv_list in conventions.items():
            if any(conv.lower() in section_text for conv in conv_list):
                return conv_type

        return "default"

    def _filter_seeds_for_boundary(
        self,
        all_seed_rules: Dict,
        boundary: str,
        sections: List[Dict]
    ) -> Dict:
        """
        Filter seed rules to include ONLY relevant rules for this boundary.

        This is CRITICAL for avoiding context bloat!

        Example:
            all_seed_rules: 50K tokens (all patterns, conventions, architecture)
            auth_boundary: 15K tokens (auth patterns + related conventions only)

        Args:
            all_seed_rules: Complete seed rules from OpusLevelMemory
            boundary: Boundary name (e.g., "auth_logic", "database")
            sections: Sections in this boundary

        Returns:
            Filtered seed rules dict (much smaller!)
        """
        filtered = {
            "project": all_seed_rules.get("project"),
            "patterns": {},
            "conventions": {
                "coding_style": [],
                "naming": [],
                "testing": [],
                "documentation": []
            },
            "architecture": {
                "decisions": [],
                "patterns": [],
                "dependencies": []
            },
            "tech_stack": all_seed_rules.get("tech_stack", []),
            "file_patterns": {}
        }

        # Filter patterns by boundary
        patterns = all_seed_rules.get("patterns", {})
        for pattern_name, pattern_data in patterns.items():
            # Include if pattern matches boundary
            pattern_boundary = pattern_data.get('boundary', pattern_name)
            if pattern_boundary == boundary or pattern_name.lower() in boundary.lower():
                filtered["patterns"][pattern_name] = pattern_data

        # Include relevant conventions (all for now - could be more selective)
        filtered["conventions"] = all_seed_rules.get("conventions", {})

        # Filter architecture by relevance to sections
        section_files = set()
        for section in sections:
            for step in section.get('steps', []):
                action = step.get('action', '')
                # Extract file references from action
                if 'app/' in action or 'src/' in action:
                    section_files.add(action.split()[-1])

        # Include architecture decisions related to section files
        arch = all_seed_rules.get("architecture", {})
        for decision in arch.get("decisions", []):
            # Simple relevance check
            if any(f in str(decision) for f in section_files):
                filtered["architecture"]["decisions"].append(decision)

        # Copy architecture patterns (usually small)
        filtered["architecture"]["patterns"] = arch.get("patterns", [])
        filtered["architecture"]["dependencies"] = arch.get("dependencies", [])

        # Copy file patterns
        filtered["file_patterns"] = all_seed_rules.get("file_patterns", {})

        return filtered

    def _build_dependency_graph(self, sections: List[Dict]) -> nx.DiGraph:
        """
        Build directed dependency graph from sections.

        Args:
            sections: List of plan sections

        Returns:
            NetworkX DiGraph with section dependencies
        """
        graph = nx.DiGraph()

        for section in sections:
            section_id = section['section_id']
            graph.add_node(section_id, **section.get('metadata', {}))

            # Add edges for dependencies
            deps = section.get('metadata', {}).get('dependencies', [])
            for dep in deps:
                graph.add_edge(dep, section_id)  # dep → section

        return graph

    def _find_cross_boundary_dependencies(
        self,
        boundary: Boundary,
        dependency_graph: nx.DiGraph,
        all_boundaries: List[Boundary]
    ) -> Set[str]:
        """
        Find dependencies that cross boundary boundaries.

        These require coordination between sub-planners.

        Args:
            boundary: Current boundary
            dependency_graph: Full dependency graph
            all_boundaries: All boundaries in plan

        Returns:
            Set of cross-boundary dependencies
        """
        cross_deps = set()
        boundary_section_ids = {s['section_id'] for s in boundary.sections}

        for section in boundary.sections:
            section_id = section['section_id']

            # Check incoming dependencies
            if section_id in dependency_graph:
                for dep in dependency_graph.predecessors(section_id):
                    # If dependency is NOT in this boundary, it's cross-boundary
                    if dep not in boundary_section_ids:
                        cross_deps.add(dep)

        return cross_deps

    def estimate_token_savings(
        self,
        all_seed_rules: Dict,
        sub_contexts: List[SubContext]
    ) -> Dict:
        """
        Estimate token savings from horizontal splitting.

        Args:
            all_seed_rules: Complete seed rules
            sub_contexts: Created sub-contexts

        Returns:
            Dict with token estimates
        """
        # Rough estimate: JSON length / 4
        all_tokens = len(str(all_seed_rules)) // 4

        # Without splitting: all_tokens × num_contexts
        without_split = all_tokens * len(sub_contexts)

        # With splitting: sum of filtered tokens
        with_split = sum(
            len(str(sc.seed_rules)) // 4
            for sc in sub_contexts
        )

        savings_pct = ((without_split - with_split) / without_split * 100) if without_split > 0 else 0

        return {
            "all_seed_rules_tokens": all_tokens,
            "without_splitting": without_split,
            "with_splitting": with_split,
            "savings_tokens": without_split - with_split,
            "savings_percent": round(savings_pct, 1)
        }
