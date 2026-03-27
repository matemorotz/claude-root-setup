#!/usr/bin/env python3
"""
Knowledge Query Engine - Query the knowledge graph

Query capabilities:
- Find nodes by type (pattern, concept, file, decision, dependency)
- Search by keyword with fuzzy matching
- Find nodes by relationship
- Get node by ID
- List all patterns/concepts/files
- Get related nodes

Usage:
    python knowledge-query.py --type pattern
    python knowledge-query.py --keyword "authentication"
    python knowledge-query.py --node-id <id>
    python knowledge-query.py --related <node-id>
    python knowledge-query.py --file <path> --format json
    python knowledge-query.py --stats
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from difflib import SequenceMatcher
from collections import defaultdict


class KnowledgeNode:
    """Represents a knowledge node in the graph."""

    def __init__(self, data: Dict):
        """Initialize node from dictionary."""
        self.id = data["id"]
        self.type = data["type"]
        self.content = data["content"]
        self.metadata = data.get("metadata", {})
        self.relationships = data.get("relationships", [])

    def to_dict(self) -> Dict:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata,
            "relationships": self.relationships
        }

    def matches_keyword(self, keyword: str, threshold: float = 0.6) -> float:
        """Check if node matches keyword (fuzzy). Returns similarity score."""
        keyword_lower = keyword.lower()

        # Check content
        content_sim = SequenceMatcher(None, keyword_lower, self.content.lower()).ratio()

        # Check metadata values
        metadata_sim = 0.0
        for value in self.metadata.values():
            if isinstance(value, str):
                sim = SequenceMatcher(None, keyword_lower, value.lower()).ratio()
                metadata_sim = max(metadata_sim, sim)

        # Return best match
        max_sim = max(content_sim, metadata_sim)
        return max_sim if max_sim >= threshold else 0.0

    def __str__(self) -> str:
        """String representation."""
        return f"[{self.type}] {self.content} (id: {self.id[:8]}...)"


class KnowledgeGraph:
    """Knowledge graph query interface."""

    def __init__(self, data: Dict):
        """Initialize graph from dictionary."""
        self.nodes: Dict[str, KnowledgeNode] = {
            nid: KnowledgeNode(ndata)
            for nid, ndata in data["nodes"].items()
        }
        self.edges: List[Dict] = data.get("edges", [])
        self.stats: Dict = data.get("stats", {})

        # Build reverse index for relationships
        self._build_reverse_index()

    def _build_reverse_index(self):
        """Build reverse index for quick lookups."""
        self.nodes_by_type: Dict[str, List[KnowledgeNode]] = defaultdict(list)
        self.incoming_edges: Dict[str, List[Dict]] = defaultdict(list)
        self.outgoing_edges: Dict[str, List[Dict]] = defaultdict(list)

        # Index nodes by type
        for node in self.nodes.values():
            self.nodes_by_type[node.type].append(node)

        # Index edges
        for edge in self.edges:
            source = edge["source"]
            target = edge["target"]
            self.outgoing_edges[source].append(edge)
            self.incoming_edges[target].append(edge)

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_nodes_by_type(self, node_type: str) -> List[KnowledgeNode]:
        """Get all nodes of a specific type."""
        return self.nodes_by_type.get(node_type, [])

    def search_by_keyword(
        self,
        keyword: str,
        threshold: float = 0.6,
        node_type: Optional[str] = None
    ) -> List[Tuple[KnowledgeNode, float]]:
        """
        Search nodes by keyword with fuzzy matching.

        Args:
            keyword: Search term
            threshold: Minimum similarity score (0.0-1.0)
            node_type: Optional type filter

        Returns:
            List of (node, similarity_score) tuples, sorted by score desc
        """
        results = []

        nodes_to_search = (
            self.nodes_by_type.get(node_type, [])
            if node_type
            else self.nodes.values()
        )

        for node in nodes_to_search:
            score = node.matches_keyword(keyword, threshold)
            if score > 0:
                results.append((node, score))

        # Sort by similarity score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def get_related_nodes(
        self,
        node_id: str,
        direction: str = "both",
        edge_type: Optional[str] = None
    ) -> List[Tuple[KnowledgeNode, str, str]]:
        """
        Get nodes related to the given node.

        Args:
            node_id: Source node ID
            direction: "incoming", "outgoing", or "both"
            edge_type: Optional edge type filter

        Returns:
            List of (related_node, relationship_type, direction) tuples
        """
        results = []

        # Get outgoing relationships
        if direction in ("outgoing", "both"):
            for edge in self.outgoing_edges.get(node_id, []):
                if edge_type and edge["type"] != edge_type:
                    continue
                target_node = self.nodes.get(edge["target"])
                if target_node:
                    results.append((target_node, edge["type"], "outgoing"))

        # Get incoming relationships
        if direction in ("incoming", "both"):
            for edge in self.incoming_edges.get(node_id, []):
                if edge_type and edge["type"] != edge_type:
                    continue
                source_node = self.nodes.get(edge["source"])
                if source_node:
                    results.append((source_node, edge["type"], "incoming"))

        return results

    def get_nodes_by_relationship(
        self,
        edge_type: str,
        source_type: Optional[str] = None,
        target_type: Optional[str] = None
    ) -> List[Tuple[KnowledgeNode, KnowledgeNode, str]]:
        """
        Find nodes connected by specific relationship type.

        Args:
            edge_type: Relationship type (e.g., "found_in", "imports")
            source_type: Optional source node type filter
            target_type: Optional target node type filter

        Returns:
            List of (source_node, target_node, edge_type) tuples
        """
        results = []

        for edge in self.edges:
            if edge["type"] != edge_type:
                continue

            source_node = self.nodes.get(edge["source"])
            target_node = self.nodes.get(edge["target"])

            if not source_node or not target_node:
                continue

            # Apply type filters
            if source_type and source_node.type != source_type:
                continue
            if target_type and target_node.type != target_type:
                continue

            results.append((source_node, target_node, edge["type"]))

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": {
                ntype: len(nodes)
                for ntype, nodes in self.nodes_by_type.items()
            },
            "edge_types": self.stats.get("edge_types", {}),
            "stored_stats": self.stats
        }


class QueryFormatter:
    """Format query results for different output types."""

    @staticmethod
    def format_json(data: Any) -> str:
        """Format as JSON."""
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_table(nodes: List[KnowledgeNode], show_metadata: bool = False) -> str:
        """Format nodes as table."""
        if not nodes:
            return "No results found."

        lines = []
        lines.append("-" * 100)
        lines.append(f"{'Type':<15} {'ID':<18} {'Content':<50} {'Relationships':<15}")
        lines.append("-" * 100)

        for node in nodes:
            node_id = node.id[:16]
            content = node.content[:47] + "..." if len(node.content) > 50 else node.content
            rel_count = len(node.relationships)

            lines.append(f"{node.type:<15} {node_id:<18} {content:<50} {rel_count:<15}")

            if show_metadata and node.metadata:
                for key, value in node.metadata.items():
                    value_str = str(value)[:60]
                    lines.append(f"  └─ {key}: {value_str}")

        lines.append("-" * 100)
        lines.append(f"Total: {len(nodes)} nodes")
        return "\n".join(lines)

    @staticmethod
    def format_summary(nodes: List[KnowledgeNode]) -> str:
        """Format as summary."""
        if not nodes:
            return "No results found."

        lines = []
        lines.append(f"Found {len(nodes)} nodes:\n")

        # Group by type
        by_type = defaultdict(list)
        for node in nodes:
            by_type[node.type].append(node)

        for node_type, type_nodes in sorted(by_type.items()):
            lines.append(f"\n{node_type.upper()} ({len(type_nodes)}):")
            for node in type_nodes[:10]:  # Show max 10 per type
                lines.append(f"  • {node.content} (id: {node.id[:8]}...)")
            if len(type_nodes) > 10:
                lines.append(f"  ... and {len(type_nodes) - 10} more")

        return "\n".join(lines)

    @staticmethod
    def format_relationships(
        results: List[Tuple[KnowledgeNode, str, str]]
    ) -> str:
        """Format relationship results."""
        if not results:
            return "No related nodes found."

        lines = []
        lines.append(f"Found {len(results)} related nodes:\n")

        # Group by relationship type and direction
        by_rel = defaultdict(lambda: defaultdict(list))
        for node, rel_type, direction in results:
            by_rel[rel_type][direction].append(node)

        for rel_type in sorted(by_rel.keys()):
            lines.append(f"\n{rel_type.upper()}:")

            for direction in ["outgoing", "incoming"]:
                if direction in by_rel[rel_type]:
                    nodes = by_rel[rel_type][direction]
                    lines.append(f"  {direction} ({len(nodes)}):")
                    for node in nodes[:10]:
                        lines.append(f"    • [{node.type}] {node.content}")
                    if len(nodes) > 10:
                        lines.append(f"    ... and {len(nodes) - 10} more")

        return "\n".join(lines)


def load_knowledge_graph(file_path: str) -> KnowledgeGraph:
    """Load knowledge graph from JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return KnowledgeGraph(data)


def find_graph_file(input_path: Optional[str] = None) -> str:
    """Find knowledge graph JSON file."""
    if input_path:
        return input_path

    # Look in default location
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir.parent / "knowledge" / "graph"

    if knowledge_dir.exists():
        # Find most recent graph file
        json_files = list(knowledge_dir.glob("*_nodes.json"))
        if json_files:
            # Sort by modification time
            json_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return str(json_files[0])

    raise FileNotFoundError(
        "No knowledge graph file found. "
        "Run knowledge-indexer.py first or specify --file path."
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input
    parser.add_argument("--file", help="Path to knowledge graph JSON file")

    # Query types
    parser.add_argument("--type", help="Filter by node type")
    parser.add_argument("--keyword", help="Search by keyword (fuzzy matching)")
    parser.add_argument("--node-id", help="Get specific node by ID")
    parser.add_argument("--related", help="Get nodes related to this node ID")
    parser.add_argument("--relationship", help="Find nodes by relationship type")
    parser.add_argument("--stats", action="store_true", help="Show graph statistics")

    # Filters
    parser.add_argument("--source-type", help="Filter source node type")
    parser.add_argument("--target-type", help="Filter target node type")
    parser.add_argument("--threshold", type=float, default=0.6, help="Fuzzy match threshold (0.0-1.0)")

    # Output
    parser.add_argument("--format", choices=["json", "table", "summary"], default="table", help="Output format")
    parser.add_argument("--metadata", action="store_true", help="Show metadata (table format)")
    parser.add_argument("--limit", type=int, help="Limit number of results")

    args = parser.parse_args()

    try:
        # Find and load graph
        graph_file = find_graph_file(args.file)
        graph = load_knowledge_graph(graph_file)
        formatter = QueryFormatter()

        # Execute query
        if args.stats:
            stats = graph.get_statistics()
            if args.format == "json":
                print(formatter.format_json(stats))
            else:
                print(f"Total Nodes: {stats['total_nodes']}")
                print(f"Total Edges: {stats['total_edges']}")
        elif args.keyword:
            results = graph.search_by_keyword(args.keyword, args.threshold, args.type)
            if args.limit:
                results = results[:args.limit]
            nodes = [n for n, _ in results]
            if args.format == "json":
                print(formatter.format_json([{"node": n.to_dict(), "score": s} for n, s in results]))
            elif args.format == "summary":
                print(formatter.format_summary(nodes))
            else:
                print(formatter.format_table(nodes, args.metadata))
        elif args.type:
            nodes = graph.get_nodes_by_type(args.type)
            if args.limit:
                nodes = nodes[:args.limit]
            if args.format == "json":
                print(formatter.format_json([n.to_dict() for n in nodes]))
            else:
                print(formatter.format_table(nodes, args.metadata))
        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
