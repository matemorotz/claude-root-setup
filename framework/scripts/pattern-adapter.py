#!/usr/bin/env python3
"""
Pattern Adapter - Bridge between pattern-extractor and rule-distiller.

Transforms the output format of pattern-extractor.py into the input format
expected by rule-distiller.py.

Usage:
    python pattern-adapter.py <extracted_patterns.json> [output.json]
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


# Frameworks detected via import patterns
FRAMEWORK_MAP = {
    "langgraph": ("LangGraph Agent Framework", "architectural"),
    "langchain": ("LangChain Framework", "architectural"),
    "fastapi": ("FastAPI REST Framework", "api_design"),
    "flask": ("Flask Web Framework", "api_design"),
    "express": ("Express.js Framework", "api_design"),
    "django": ("Django Framework", "api_design"),
    "react": ("React Frontend", "architectural"),
    "nextjs": ("Next.js Framework", "architectural"),
    "sqlalchemy": ("SQLAlchemy ORM", "architectural"),
    "prisma": ("Prisma ORM", "architectural"),
    "mongoose": ("Mongoose ODM", "architectural"),
}

# Language detection from file extensions
EXTENSION_TO_LANG = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".rb": "Ruby",
}


def adapt(extractor_output: Dict) -> Dict:
    """Transform pattern-extractor output to rule-distiller input format."""

    patterns = {
        "architectural": [],
        "coding": [],
        "testing": [],
        "api_design": [],
    }

    # 1. Map architecture_patterns (list of strings) → architectural
    arch_evidence = extractor_output.get("architecture_pattern_evidence", {})
    for name in extractor_output.get("architecture_patterns", []):
        patterns["architectural"].append({
            "name": name,
            "description": f"Detected architectural pattern: {name}",
            "confidence": 0.8,
            "coverage": 0.6,
            "consistency": 0.7,
            "evidence": arch_evidence.get(name, [])[:5],
        })

    # 2. Map naming_conventions → coding patterns
    naming = extractor_output.get("naming_conventions", {})
    convention = naming.get("convention", "")
    if convention:
        examples = []
        class_naming = naming.get("class_function_naming", {})
        for style, count in class_naming.items():
            if count > 0:
                examples.append(f"{style}: {count} occurrences")

        patterns["coding"].append({
            "name": "Naming Convention",
            "description": convention,
            "confidence": 0.9,
            "coverage": 0.8,
            "consistency": 0.9,
            "evidence": [],
            "metadata": {"examples": examples},
        })

    # 3. Map file_structure → coding patterns (directory organization)
    file_struct = extractor_output.get("file_structure", {})
    top_dirs = file_struct.get("top_directories", {})
    if top_dirs:
        standard_dirs = list(top_dirs.keys())
        patterns["coding"].append({
            "name": "File Organization",
            "description": f"Standard directories: {', '.join(standard_dirs[:8])}",
            "confidence": 0.85,
            "coverage": 0.7,
            "consistency": 0.8,
            "evidence": [],
            "metadata": {"standard_dirs": standard_dirs},
        })

    # Governor pattern detection
    if file_struct.get("governor_pattern"):
        patterns["architectural"].append({
            "name": "Fractal Governor Pattern",
            "description": f"Governor-based agent architecture ({file_struct.get('governor_dirs_found', 0)} governor dirs)",
            "confidence": 0.95,
            "coverage": 0.8,
            "consistency": 0.9,
            "evidence": [],
        })

    # 4. Map testing_patterns → testing
    testing = extractor_output.get("testing_patterns", {})
    if testing and testing.get("test_files", 0) > 0:
        framework = testing.get("framework", "unknown")
        patterns["testing"].append({
            "name": f"Testing with {framework}",
            "description": f"{testing.get('test_files', 0)} test files using {framework}",
            "confidence": 0.85,
            "coverage": 0.7,
            "consistency": 0.8,
            "evidence": testing.get("test_directories", []),
            "metadata": {"framework": framework, "mock_usage": testing.get("mock_usage", 0)},
        })

    # 5. Map import_patterns → detect frameworks
    imports = extractor_output.get("import_patterns", {})
    common_libs = imports.get("common_libraries", {})
    for lib_name, count in common_libs.items():
        lib_lower = lib_name.lower()
        if lib_lower in FRAMEWORK_MAP:
            display_name, category = FRAMEWORK_MAP[lib_lower]
            patterns[category].append({
                "name": display_name,
                "description": f"Uses {display_name} ({count} imports detected)",
                "confidence": 0.95,
                "coverage": 0.8,
                "consistency": 0.9,
                "evidence": [],
            })

    # 6. Infer languages from file extensions
    extensions = file_struct.get("file_extensions", {})
    for ext, count in extensions.items():
        if ext in EXTENSION_TO_LANG and count >= 3:
            lang = EXTENSION_TO_LANG[ext]
            already = any(p["name"] == f"{lang} Codebase" for p in patterns["coding"])
            if not already:
                patterns["coding"].append({
                    "name": f"{lang} Codebase",
                    "description": f"Primary language: {lang} ({count} files)",
                    "confidence": 0.95,
                    "coverage": count / max(sum(extensions.values()), 1),
                    "consistency": 0.9,
                    "evidence": [],
                })

    total = sum(len(v) for v in patterns.values())

    return {
        "patterns": patterns,
        "statistics": {"total_patterns": total},
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python pattern-adapter.py <extracted_patterns.json> [output.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "adapted_patterns.json"

    with open(input_path) as f:
        extractor_output = json.load(f)

    adapted = adapt(extractor_output)

    with open(output_path, "w") as f:
        json.dump(adapted, f, indent=2)

    total = adapted["statistics"]["total_patterns"]
    by_cat = {k: len(v) for k, v in adapted["patterns"].items() if v}
    print(f"Adapted {total} patterns: {by_cat}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
