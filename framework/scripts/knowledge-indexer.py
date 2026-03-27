#!/usr/bin/env python3
"""
Knowledge Indexer - Autonomous Project Knowledge Discovery

Scans project files and extracts:
- Code patterns (classes, functions, imports)
- Architecture decisions
- Dependencies and relationships
- File structure patterns

Builds knowledge graph: Nodes (concepts, patterns, files) + Edges (relationships)

Usage:
    python knowledge-indexer.py /path/to/project
    python knowledge-indexer.py /path/to/project --output knowledge.json
"""

import os
import sys
import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
import hashlib


class KnowledgeNode:
    """Represents a knowledge node in the graph."""

    def __init__(
        self,
        node_id: str,
        node_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        self.id = node_id
        self.type = node_type  # pattern|concept|file|decision|dependency
        self.content = content
        self.metadata = metadata or {}
        self.relationships = []  # List of (target_id, relationship_type)

    def to_dict(self) -> Dict:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata,
            "relationships": [
                {"target_id": r[0], "type": r[1]}
                for r in self.relationships
            ]
        }

    def add_relationship(self, target_id: str, rel_type: str):
        """Add relationship to another node."""
        self.relationships.append((target_id, rel_type))


class KnowledgeGraph:
    """Knowledge graph builder and manager."""

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[Tuple[str, str, str]] = []  # (source, target, type)

    def add_node(self, node: KnowledgeNode):
        """Add node to graph."""
        self.nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str, edge_type: str):
        """Add edge between nodes."""
        if source_id in self.nodes and target_id in self.nodes:
            self.edges.append((source_id, target_id, edge_type))
            self.nodes[source_id].add_relationship(target_id, edge_type)

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def to_dict(self) -> Dict:
        """Convert graph to dictionary."""
        return {
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": [
                {"source": s, "target": t, "type": et}
                for s, t, et in self.edges
            ],
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_types": self._count_node_types(),
                "edge_types": self._count_edge_types()
            }
        }

    def _count_node_types(self) -> Dict[str, int]:
        """Count nodes by type."""
        counts = {}
        for node in self.nodes.values():
            counts[node.type] = counts.get(node.type, 0) + 1
        return counts

    def _count_edge_types(self) -> Dict[str, int]:
        """Count edges by type."""
        counts = {}
        for _, _, etype in self.edges:
            counts[etype] = counts.get(etype, 0) + 1
        return counts


class ProjectIndexer:
    """Indexes project files and extracts knowledge."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.graph = KnowledgeGraph()
        self.patterns: Dict[str, List[str]] = {}  # pattern_type -> [examples]
        self.file_index: Dict[str, Dict] = {}  # file_path -> metadata

        # Ignore patterns
        self.ignore_patterns = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'dist', 'build', '.egg-info'
        }

    def index_project(self) -> KnowledgeGraph:
        """Main indexing entry point."""
        print(f"Indexing project: {self.project_path}")

        # Scan project structure
        files = self._scan_directory()
        print(f"Found {len(files)} files to analyze")

        # Analyze files by type
        for file_path in files:
            self._analyze_file(file_path)

        # Extract patterns
        self._extract_global_patterns()

        # Build relationships
        self._build_relationships()

        return self.graph

    def _scan_directory(self) -> List[Path]:
        """Scan directory and return list of files to analyze."""
        files = []

        for root, dirs, filenames in os.walk(self.project_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]

            for filename in filenames:
                file_path = Path(root) / filename

                # Only analyze code and documentation files
                if self._should_analyze(file_path):
                    files.append(file_path)

        return files

    def _should_analyze(self, file_path: Path) -> bool:
        """Check if file should be analyzed."""
        extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.json', '.yaml', '.yml'}
        return file_path.suffix in extensions

    def _analyze_file(self, file_path: Path):
        """Analyze a single file and extract knowledge."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Create file node
            file_id = self._generate_id(f"file:{file_path.relative_to(self.project_path)}")
            file_node = KnowledgeNode(
                node_id=file_id,
                node_type="file",
                content=str(file_path.relative_to(self.project_path)),
                metadata={
                    "size": len(content),
                    "lines": content.count('\n'),
                    "extension": file_path.suffix,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
            )
            self.graph.add_node(file_node)

            # Store in file index
            self.file_index[str(file_path)] = {
                "id": file_id,
                "path": str(file_path.relative_to(self.project_path)),
                "type": file_path.suffix
            }

            # Analyze based on file type
            if file_path.suffix == '.py':
                self._analyze_python_file(file_path, content, file_id)
            elif file_path.suffix in {'.js', '.ts', '.tsx', '.jsx'}:
                self._analyze_javascript_file(file_path, content, file_id)
            elif file_path.suffix == '.md':
                self._analyze_markdown_file(file_path, content, file_id)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _analyze_python_file(self, file_path: Path, content: str, file_id: str):
        """Extract patterns from Python file."""
        try:
            tree = ast.parse(content)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._record_dependency(file_id, alias.name, "imports")

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._record_dependency(file_id, node.module, "imports")

                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    self._record_pattern("class", node.name, file_id)

                # Extract function definitions
                elif isinstance(node, ast.FunctionDef):
                    self._record_pattern("function", node.name, file_id)

        except SyntaxError:
            pass  # Skip files with syntax errors

    def _analyze_javascript_file(self, file_path: Path, content: str, file_id: str):
        """Extract patterns from JavaScript/TypeScript file."""
        # Simple regex-based extraction (can be enhanced with proper parser)

        # Extract imports
        import_pattern = r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            module = match.group(1)
            self._record_dependency(file_id, module, "imports")

        # Extract class definitions
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            self._record_pattern("class", class_name, file_id)

        # Extract function definitions
        function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\()'
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1) or match.group(2)
            if func_name:
                self._record_pattern("function", func_name, file_id)

    def _analyze_markdown_file(self, file_path: Path, content: str, file_id: str):
        """Extract concepts from markdown documentation."""
        # Extract headers as concepts
        header_pattern = r'^#{1,3}\s+(.+)$'
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            concept = match.group(1).strip()
            self._record_concept(concept, file_id)

    def _record_pattern(self, pattern_type: str, name: str, file_id: str):
        """Record a code pattern."""
        pattern_id = self._generate_id(f"pattern:{pattern_type}:{name}")

        if pattern_id not in self.graph.nodes:
            node = KnowledgeNode(
                node_id=pattern_id,
                node_type="pattern",
                content=f"{pattern_type}: {name}",
                metadata={"pattern_type": pattern_type, "name": name, "confidence": 0.9}
            )
            self.graph.add_node(node)

            # Track pattern
            if pattern_type not in self.patterns:
                self.patterns[pattern_type] = []
            self.patterns[pattern_type].append(name)

        # Link pattern to file
        self.graph.add_edge(pattern_id, file_id, "found_in")

    def _record_concept(self, concept: str, file_id: str):
        """Record a concept from documentation."""
        concept_id = self._generate_id(f"concept:{concept}")

        if concept_id not in self.graph.nodes:
            node = KnowledgeNode(
                node_id=concept_id,
                node_type="concept",
                content=concept,
                metadata={"confidence": 0.8}
            )
            self.graph.add_node(node)

        # Link concept to file
        self.graph.add_edge(concept_id, file_id, "documented_in")

    def _record_dependency(self, file_id: str, dependency: str, dep_type: str):
        """Record a dependency."""
        dep_id = self._generate_id(f"dependency:{dependency}")

        if dep_id not in self.graph.nodes:
            node = KnowledgeNode(
                node_id=dep_id,
                node_type="dependency",
                content=dependency,
                metadata={"dependency_type": dep_type}
            )
            self.graph.add_node(node)

        # Link file to dependency
        self.graph.add_edge(file_id, dep_id, dep_type)

    def _extract_global_patterns(self):
        """Extract high-level patterns from collected data."""
        # Detect common architectural patterns
        if "class" in self.patterns:
            # Check for MVC pattern
            model_classes = [c for c in self.patterns["class"] if "model" in c.lower()]
            if model_classes:
                self._add_architectural_decision("MVC pattern detected", model_classes)

        # Detect testing patterns
        test_files = [f for f in self.file_index.values() if "test" in f["path"].lower()]
        if test_files:
            self._add_architectural_decision("Testing infrastructure present", [f["path"] for f in test_files])

    def _add_architectural_decision(self, decision: str, evidence: List[str]):
        """Record an architectural decision."""
        decision_id = self._generate_id(f"decision:{decision}")

        node = KnowledgeNode(
            node_id=decision_id,
            node_type="decision",
            content=decision,
            metadata={"evidence": evidence, "confidence": 0.85}
        )
        self.graph.add_node(node)

    def _build_relationships(self):
        """Build additional relationships between nodes using token similarity."""
        pattern_nodes = [(nid, n) for nid, n in self.graph.nodes.items() if n.type == 'pattern']
        concept_nodes = [(nid, n) for nid, n in self.graph.nodes.items() if n.type == 'concept']

        # Link patterns that share a significant name token (>= 4 chars)
        # e.g. UserModel + UserService both have "user" → related_to
        for i, (id1, n1) in enumerate(pattern_nodes):
            tokens1 = {t for t in re.split(r'[_\-\s]', n1.metadata.get('name', '').lower()) if len(t) >= 4}
            if not tokens1:
                continue
            for id2, n2 in pattern_nodes[i + 1:]:
                tokens2 = {t for t in re.split(r'[_\-\s]', n2.metadata.get('name', '').lower()) if len(t) >= 4}
                if tokens1 & tokens2:
                    self.graph.add_edge(id1, id2, 'related_to')

        # Link concepts to patterns that share a keyword
        for cid, cn in concept_nodes:
            words = {w.lower() for w in re.split(r'\s+', cn.content) if len(w) >= 4}
            for pid, pn in pattern_nodes:
                if any(w in pn.metadata.get('name', '').lower() for w in words):
                    self.graph.add_edge(cid, pid, 'related_to')

    def _generate_id(self, key: str) -> str:
        """Generate unique ID for node."""
        return hashlib.md5(key.encode()).hexdigest()[:16]


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python knowledge-indexer.py <project_path> [--output <file>]")
        sys.exit(1)

    project_path = sys.argv[1]
    output_file = None

    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output")
        if output_idx + 1 < len(sys.argv):
            output_file = sys.argv[output_idx + 1]

    # Index project
    indexer = ProjectIndexer(project_path)
    graph = indexer.index_project()

    # Convert to dict and save
    graph_data = graph.to_dict()

    print("\n" + "=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)
    print(f"Total nodes: {graph_data['stats']['total_nodes']}")
    print(f"Total edges: {graph_data['stats']['total_edges']}")
    print("\nNode types:")
    for ntype, count in graph_data['stats']['node_types'].items():
        print(f"  {ntype}: {count}")
    print("\nEdge types:")
    for etype, count in graph_data['stats']['edge_types'].items():
        print(f"  {etype}: {count}")

    # Save to file
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        print(f"\nKnowledge graph saved to: {output_file}")
    else:
        # Save to default location
        knowledge_dir = Path(__file__).parent.parent / "knowledge" / "graph"
        knowledge_dir.mkdir(parents=True, exist_ok=True)

        project_name = Path(project_path).name
        output_path = knowledge_dir / f"{project_name}_nodes.json"

        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        print(f"\nKnowledge graph saved to: {output_path}")


if __name__ == "__main__":
    main()
