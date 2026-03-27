#!/usr/bin/env python3
"""
Knowledge Graph Generator - Visualize Documentation Structure

Parses markdown files, extracts cross-references, generates graph visualizations.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter
import json


class KnowledgeGraph:
    """Documentation knowledge graph"""

    def __init__(self, docs_dir: str = ".claude/docs"):
        self.docs_dir = Path(docs_dir)
        self.nodes = {}  # file_path -> metadata
        self.edges = []  # (source, target, type)
        self.graph = defaultdict(list)  # adjacency list

    def build(self):
        """Build graph from documentation files"""
        print(f"Building knowledge graph from {self.docs_dir}...")

        # Discover all markdown files
        for md_file in self.docs_dir.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue

            rel_path = str(md_file.relative_to(self.docs_dir))
            self.nodes[rel_path] = self._analyze_file(md_file)

        print(f"  Found {len(self.nodes)} documentation nodes")

        # Extract links
        for md_file in self.docs_dir.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue

            source = str(md_file.relative_to(self.docs_dir))
            links = self._extract_links(md_file)

            for link_text, link_target, link_type in links:
                # Resolve relative link
                try:
                    target_path = (md_file.parent / link_target).relative_to(self.docs_dir)
                    target = str(target_path)

                    if target in self.nodes:
                        self.edges.append((source, target, link_type))
                        self.graph[source].append(target)
                except ValueError:
                    # Link outside docs dir
                    pass

        print(f"  Extracted {len(self.edges)} cross-references")

    def _analyze_file(self, file_path: Path) -> dict:
        """Analyze file metadata"""
        with open(file_path) as f:
            content = f.read()

        # Extract level from content
        level = "unknown"
        if "Level:** WHAT" in content:
            level = "WHAT"
        elif "Level:** HOW" in content:
            level = "HOW"
        elif "Level:** DETAILS" in content or "Level:** IMPL" in content:
            level = "DETAILS"
        elif "Level:** REFERENCE" in content or "Level:** API" in content:
            level = "REFERENCE"
        elif "INDEX.md" in file_path.name:
            level = "INDEX"

        # Estimate size
        words = len(content.split())
        tokens = words * 1.3  # Rough estimate

        # Extract category
        parts = file_path.relative_to(self.docs_dir).parts
        category = parts[0] if len(parts) > 1 else "root"

        return {
            "level": level,
            "words": words,
            "tokens": int(tokens),
            "category": category,
            "name": file_path.stem
        }

    def _extract_links(self, file_path: Path) -> list:
        """Extract markdown links with classification"""
        with open(file_path) as f:
            content = f.read()

        links = []

        # Pattern: [text](link.md)
        pattern = r'\[([^\]]+)\]\(([^\)]+\.md)\)'
        matches = re.findall(pattern, content)

        for text, link in matches:
            # Classify link type
            link_type = "related"

            if "↑" in text or "Up:" in text or "Back to:" in text:
                link_type = "up"
            elif "↓" in text or "Down:" in text or "Learn more:" in text:
                link_type = "down"
            elif "INDEX" in text or "Index" in text or "Home" in text:
                link_type = "index"
            elif "Related:" in text or "See also:" in text:
                link_type = "related"
            elif "implements" in text.lower() or "example" in text.lower():
                link_type = "implementation"

            links.append((text, link, link_type))

        return links

    def generate_stats(self) -> dict:
        """Calculate graph statistics"""
        stats = {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "avg_out_degree": len(self.edges) / len(self.nodes) if self.nodes else 0,
            "categories": len(set(n["category"] for n in self.nodes.values())),
            "levels": Counter(n["level"] for n in self.nodes.values()),
            "edge_types": Counter(e[2] for e in self.edges),
            "largest_hubs": self._find_hubs(5),
            "orphans": self._find_orphans()
        }

        return stats

    def _find_hubs(self, n: int = 5) -> list:
        """Find nodes with most outgoing links"""
        out_degrees = Counter()
        for source, targets in self.graph.items():
            out_degrees[source] = len(targets)

        return out_degrees.most_common(n)

    def _find_orphans(self) -> list:
        """Find nodes with no incoming or outgoing links"""
        all_nodes = set(self.nodes.keys())
        has_out = set(self.graph.keys())
        has_in = set(target for targets in self.graph.values() for target in targets)

        connected = has_out | has_in
        orphans = all_nodes - connected

        return list(orphans)

    def generate_mermaid(self, output_file: str = None) -> str:
        """Generate Mermaid graph syntax"""
        lines = ["graph TD"]

        # Add nodes with categories
        categories = {}
        for node_path, metadata in self.nodes.items():
            node_id = node_path.replace("/", "_").replace(".md", "").replace("-", "_")
            category = metadata["category"]

            if category not in categories:
                categories[category] = []
            categories[category].append(node_id)

            # Node label
            label = metadata["name"].replace("_", " ")

            # Style by level
            if metadata["level"] == "INDEX":
                lines.append(f'    {node_id}["{label}"]:::index')
            elif metadata["level"] == "WHAT":
                lines.append(f'    {node_id}["{label}"]:::what')
            elif metadata["level"] == "HOW":
                lines.append(f'    {node_id}["{label}"]:::how')
            else:
                lines.append(f'    {node_id}["{label}"]')

        # Add edges
        for source, target, link_type in self.edges:
            source_id = source.replace("/", "_").replace(".md", "").replace("-", "_")
            target_id = target.replace("/", "_").replace(".md", "").replace("-", "_")

            # Style by type
            if link_type == "up":
                lines.append(f'    {source_id} -.up.-> {target_id}')
            elif link_type == "down":
                lines.append(f'    {source_id} -->|down| {target_id}')
            elif link_type == "index":
                lines.append(f'    {source_id} --> {target_id}')
            else:
                lines.append(f'    {source_id} -.-> {target_id}')

        # Add styles
        lines.append("")
        lines.append("    classDef index fill:#e1f5ff,stroke:#01579b")
        lines.append("    classDef what fill:#fff9c4,stroke:#f57f17")
        lines.append("    classDef how fill:#c8e6c9,stroke:#2e7d32")

        mermaid = "\n".join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(mermaid)

        return mermaid

    def generate_dot(self, output_file: str = None) -> str:
        """Generate Graphviz DOT syntax"""
        lines = ['digraph knowledge_graph {']
        lines.append('    rankdir=TB;')
        lines.append('    node [shape=box, style=rounded];')
        lines.append('')

        # Nodes
        for node_path, metadata in self.nodes.items():
            node_id = node_path.replace("/", "_").replace(".md", "").replace("-", "_")
            label = metadata["name"].replace("_", " ")

            # Color by level
            if metadata["level"] == "INDEX":
                color = "lightblue"
            elif metadata["level"] == "WHAT":
                color = "lightyellow"
            elif metadata["level"] == "HOW":
                color = "lightgreen"
            else:
                color = "white"

            lines.append(f'    {node_id} [label="{label}", fillcolor={color}, style="filled,rounded"];')

        lines.append('')

        # Edges
        for source, target, link_type in self.edges:
            source_id = source.replace("/", "_").replace(".md", "").replace("-", "_")
            target_id = target.replace("/", "_").replace(".md", "").replace("-", "_")

            if link_type == "up":
                lines.append(f'    {source_id} -> {target_id} [style=dashed, label="up"];')
            elif link_type == "down":
                lines.append(f'    {source_id} -> {target_id} [label="down"];')
            else:
                lines.append(f'    {source_id} -> {target_id};')

        lines.append('}')

        dot = "\n".join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(dot)

        return dot


def main():
    """Main entry point"""
    import sys

    graph = KnowledgeGraph()
    graph.build()

    # Generate statistics
    stats = graph.generate_stats()

    print("\n" + "="*60)
    print("KNOWLEDGE GRAPH STATISTICS")
    print("="*60)
    print(f"Nodes (files):        {stats['nodes']}")
    print(f"Edges (links):        {stats['edges']}")
    print(f"Categories:           {stats['categories']}")
    print(f"Avg out-degree:       {stats['avg_out_degree']:.1f}")
    print(f"\nLevels:")
    for level, count in stats['levels'].items():
        print(f"  {level:15s} {count:3d}")
    print(f"\nEdge types:")
    for edge_type, count in stats['edge_types'].items():
        print(f"  {edge_type:15s} {count:3d}")
    print(f"\nTop hubs (most outgoing links):")
    for node, degree in stats['largest_hubs']:
        print(f"  {node:40s} → {degree}")

    if stats['orphans']:
        print(f"\n⚠️  Orphan nodes (no links): {len(stats['orphans'])}")
        for orphan in stats['orphans']:
            print(f"  - {orphan}")

    print("="*60)

    # Generate visualizations
    if len(sys.argv) > 1:
        output_format = sys.argv[1]

        if output_format == "mermaid":
            mermaid = graph.generate_mermaid(".claude/docs/graph.mmd")
            print(f"\n✅ Mermaid graph: .claude/docs/graph.mmd")

        elif output_format == "dot":
            dot = graph.generate_dot(".claude/docs/graph.dot")
            print(f"\n✅ DOT graph: .claude/docs/graph.dot")
            print(f"   Generate PNG: dot -Tpng .claude/docs/graph.dot -o graph.png")

        elif output_format == "json":
            with open(".claude/docs/graph.json", 'w') as f:
                json.dump({
                    "nodes": graph.nodes,
                    "edges": [(s, t, type) for s, t, type in graph.edges],
                    "stats": stats
                }, f, indent=2)
            print(f"\n✅ JSON graph: .claude/docs/graph.json")


if __name__ == "__main__":
    main()
