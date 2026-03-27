#!/usr/bin/env python3
"""
Pattern Extractor - Extract project patterns from knowledge graph

Analyzes knowledge graph and extracts:
- Naming conventions
- Architecture patterns
- File structure patterns
- Testing patterns
- Import patterns
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


# Libraries to track in import analysis (mirrors FRAMEWORK_MAP in pattern-adapter.py + common extras)
TRACKED_LIBRARIES = {
    'langgraph', 'langchain', 'fastapi', 'flask', 'express', 'django',
    'react', 'nextjs', 'sqlalchemy', 'prisma', 'mongoose',
    'pydantic', 'pytest', 'numpy', 'pandas', 'redis', 'celery',
    'asyncio', 'requests', 'aiohttp', 'httpx', 'boto3', 'jwt', 'bcrypt',
    'unittest', 'jest', 'vitest', 'mocha', 'playwright', 'cypress',
    'starlette', 'uvicorn', 'gunicorn', 'alembic', 'psycopg2',
    'motor', 'pymongo', 'elasticsearch', 'kafka', 'grpc', 'graphql',
    'torch', 'tensorflow', 'sklearn', 'scipy',
}


def extract_patterns(graph_path: str) -> Dict:
    """Extract patterns from knowledge graph."""

    with open(graph_path) as f:
        graph = json.load(f)

    nodes = graph['nodes']
    edges = graph['edges']

    arch_list, arch_evidence = _extract_architecture_patterns_with_evidence(nodes, edges)

    patterns = {
        'naming_conventions': extract_naming_conventions(nodes),
        'architecture_patterns': arch_list,
        'architecture_pattern_evidence': arch_evidence,
        'file_structure': extract_file_structure(nodes),
        'testing_patterns': extract_testing_patterns(nodes, edges),
        'import_patterns': extract_import_patterns(nodes, edges),
        'key_concepts': extract_key_concepts(nodes),
    }

    return patterns


def extract_naming_conventions(nodes: Dict) -> Dict:
    """Extract naming conventions from file and concept nodes."""

    file_nodes = [n for n in nodes.values() if n['type'] == 'file']
    concept_nodes = [n for n in nodes.values() if n['type'] == 'concept']

    # Analyze file naming
    file_patterns = {
        'snake_case_files': 0,
        'dot_prefixed': 0,
        'test_files': 0,
        'config_files': 0,
    }

    for node in file_nodes:
        filename = Path(node['content']).name

        if re.match(r'^[a-z_]+\.py$', filename):
            file_patterns['snake_case_files'] += 1
        if filename.startswith('.'):
            file_patterns['dot_prefixed'] += 1
        if 'test' in filename.lower():
            file_patterns['test_files'] += 1
        if 'config' in filename.lower() or filename.endswith(('.yaml', '.json', '.toml')):
            file_patterns['config_files'] += 1

    # Analyze class/function naming from concepts
    class_patterns = defaultdict(int)
    for node in concept_nodes:
        content = node['content']
        if re.match(r'^[A-Z][a-zA-Z]+$', content):
            class_patterns['PascalCase'] += 1
        elif re.match(r'^[a-z_]+$', content):
            class_patterns['snake_case'] += 1

    return {
        'file_naming': file_patterns,
        'class_function_naming': dict(class_patterns),
        'convention': 'snake_case files, PascalCase classes'
    }


def _extract_architecture_patterns_with_evidence(
    nodes: Dict, edges: List
) -> Tuple[List[str], Dict[str, List[str]]]:
    """Extract architecture patterns and their evidence file paths.

    Returns:
        (pattern_names_list, {pattern_name: [file_paths]})
    """
    pattern_nodes = [n for n in nodes.values() if n['type'] == 'pattern']

    # Build map: pattern_node_id -> list of file paths via found_in edges
    found_in_edges = [e for e in edges if e['type'] == 'found_in']
    pattern_to_files: Dict[str, List[str]] = {}
    for edge in found_in_edges:
        file_node = nodes.get(edge['target'])
        if file_node and file_node['type'] == 'file':
            pattern_to_files.setdefault(edge['source'], []).append(file_node['content'])

    # Count pattern occurrences and accumulate evidence
    pattern_counts = Counter()
    pattern_evidence: Dict[str, List[str]] = {}

    for node in pattern_nodes:
        content = node['content'].lower()
        node_id = node['id']
        files = pattern_to_files.get(node_id, [])

        # Detect which named pattern this node matches
        matched_key = None
        if 'langgraph' in content or 'stategraph' in content:
            matched_key = 'LangGraph StateGraph'
        elif 'governor' in content:
            matched_key = 'Fractal Governor'
        elif 'agent' in content and 'factory' in content:
            matched_key = 'Agent Factory'
        elif 'mcp' in content or 'tool' in content:
            matched_key = 'MCP Tools'
        elif '.governor' in content:
            matched_key = 'Filesystem-driven agents'
        elif 'rate' in content and 'limit' in content:
            matched_key = 'Rate Limiting'
        elif 'checkpoint' in content or 'state' in content:
            matched_key = 'State Persistence'

        if matched_key:
            pattern_counts[matched_key] += 1
            pattern_evidence.setdefault(matched_key, []).extend(files)

    # Deduplicate evidence files per pattern while preserving order
    for key in pattern_evidence:
        pattern_evidence[key] = list(dict.fromkeys(pattern_evidence[key]))

    top_patterns = [p for p, _ in pattern_counts.most_common(10)]
    # Only include evidence for patterns that have files
    evidence = {k: v for k, v in pattern_evidence.items() if v}

    return top_patterns, evidence


def extract_file_structure(nodes: Dict) -> Dict:
    """Extract file structure patterns."""

    file_nodes = [n for n in nodes.values() if n['type'] == 'file']

    # Analyze directory structure
    directories = defaultdict(int)
    file_extensions = Counter()

    for node in file_nodes:
        path = Path(node['content'])

        # Count directories
        if path.parent != Path('.'):
            directories[str(path.parent)] += 1

        # Count extensions
        if path.suffix:
            file_extensions[path.suffix] += 1

    # Find common directory patterns
    top_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)[:10]

    # Detect .governor/ pattern
    governor_dirs = [d for d, _ in top_dirs if '.governor' in d]

    return {
        'top_directories': dict(top_dirs),
        'file_extensions': dict(file_extensions.most_common(10)),
        'governor_pattern': len(governor_dirs) > 0,
        'governor_dirs_found': len(governor_dirs)
    }


def extract_testing_patterns(nodes: Dict, edges: List) -> Dict:
    """Extract testing patterns, including framework detection from actual imports."""

    file_nodes = [n for n in nodes.values() if n['type'] == 'file']

    # Detect testing framework from imported dependency nodes
    dep_nodes = {n['id']: n for n in nodes.values() if n['type'] == 'dependency'}
    import_edges = [e for e in edges if e['type'] == 'imports']
    imported_modules = {
        dep_nodes[e['target']]['content'].lower().split('.')[0]
        for e in import_edges
        if e['target'] in dep_nodes
    }

    has_test_js = any(
        n['content'].endswith(('.test.js', '.test.ts', '.spec.js', '.spec.ts'))
        for n in file_nodes
    )

    if 'pytest' in imported_modules:
        detected_framework = 'pytest'
    elif 'unittest' in imported_modules:
        detected_framework = 'unittest'
    elif 'jest' in imported_modules or has_test_js:
        detected_framework = 'jest'
    elif 'vitest' in imported_modules:
        detected_framework = 'vitest'
    elif 'mocha' in imported_modules:
        detected_framework = 'mocha'
    elif 'playwright' in imported_modules:
        detected_framework = 'playwright'
    else:
        detected_framework = 'unknown'

    test_patterns = {
        'framework': detected_framework,
        'test_files': 0,
        'test_directories': set(),
        'mock_usage': 0,
    }

    for node in file_nodes:
        path = Path(node['content'])

        if 'test' in str(path).lower():
            test_patterns['test_files'] += 1
            test_patterns['test_directories'].add(str(path.parent))

        if 'mock' in str(path).lower():
            test_patterns['mock_usage'] += 1

    test_patterns['test_directories'] = list(test_patterns['test_directories'])

    return test_patterns


def extract_import_patterns(nodes: Dict, edges: List) -> Dict:
    """Extract import patterns from edges."""

    import_edges = [e for e in edges if e['type'] == 'imports']

    # Count imports using the tracked libraries set
    import_counts = Counter()

    for edge in import_edges[:1000]:  # Sample to avoid processing too many
        target_node = nodes.get(edge['target'])

        if target_node:
            top_module = target_node['content'].lower().split('.')[0]
            if top_module in TRACKED_LIBRARIES:
                import_counts[top_module] += 1

    return {
        'total_imports': len(import_edges),
        'common_libraries': dict(import_counts.most_common(10))
    }


def extract_key_concepts(nodes: Dict) -> List[str]:
    """Extract key concepts from concept nodes."""

    concept_nodes = [n for n in nodes.values() if n['type'] == 'concept']

    # Count concept occurrences
    concept_counts = Counter(node['content'] for node in concept_nodes)

    # Return top concepts
    return [concept for concept, _ in concept_counts.most_common(20)]


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extract_patterns.py <knowledge_graph.json>")
        sys.exit(1)

    graph_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'extracted_patterns.json'

    print(f"Extracting patterns from: {graph_path}")
    patterns = extract_patterns(graph_path)

    # Save patterns
    with open(output_path, 'w') as f:
        json.dump(patterns, f, indent=2)

    print(f"\n{'='*80}")
    print("PATTERN EXTRACTION COMPLETE")
    print('='*80)

    print(f"\nNaming Conventions:")
    print(f"  Convention: {patterns['naming_conventions']['convention']}")
    print(f"  Snake case files: {patterns['naming_conventions']['file_naming']['snake_case_files']}")

    print(f"\nArchitecture Patterns:")
    for i, pattern in enumerate(patterns['architecture_patterns'][:5], 1):
        evidence = patterns['architecture_pattern_evidence'].get(pattern, [])
        print(f"  {i}. {pattern} ({len(evidence)} evidence files)")

    print(f"\nFile Structure:")
    print(f"  Governor pattern: {patterns['file_structure']['governor_pattern']}")
    print(f"  Governor dirs: {patterns['file_structure']['governor_dirs_found']}")

    print(f"\nTesting:")
    print(f"  Framework: {patterns['testing_patterns']['framework']}")
    print(f"  Test files: {patterns['testing_patterns']['test_files']}")

    print(f"\nImports (top 10):")
    for lib, count in list(patterns['import_patterns']['common_libraries'].items())[:10]:
        print(f"  {lib}: {count}")

    print(f"\nKey Concepts (top 10):")
    for i, concept in enumerate(patterns['key_concepts'][:10], 1):
        print(f"  {i}. {concept}")

    print(f"\nPatterns saved to: {output_path}")


if __name__ == "__main__":
    main()
