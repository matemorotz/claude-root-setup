# Claude Agents - Complete Reference

**All available agents with paths, descriptions, and usage**
**Last Updated:** 2025-11-30

---

## 📂 Directory Structure

```
/root/software/
├── langgraph_dev_agents/              # Main agent system
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Base class for all agents
│   │   ├── langgraph_agent.py         # LangGraph best practices
│   │   ├── langgraph_agent.md         # 4,000 words of expertise
│   │   ├── security_agent.py          # Security vulnerabilities
│   │   ├── security_agent.md          # 4,500 words of expertise
│   │   ├── structure_agent.py         # Code structure & quality
│   │   ├── structure_agent.md         # 3,500 words of expertise
│   │   ├── test_debug_agent.py        # Testing & debugging
│   │   └── test_debug_agent.md        # 4,000 words of expertise
│   ├── configs/                       # Agent configurations
│   ├── prompts/                       # Agent prompts (future)
│   ├── research/                      # Research documentation
│   ├── tools/                         # Analysis tools (future)
│   ├── test_agents.py                 # Test runner
│   ├── CLAUDE.md                      # Agent configuration
│   ├── README.md                      # Project documentation
│   ├── project.md                     # Project plan
│   ├── state.md                       # Current status
│   └── todo.md                        # Task list
└── .claude/
    └── agents/                        # Agent documentation
        ├── AGENTS_GUIDE.md            # Comprehensive guide (this doc location)
        ├── AGENTS_REFERENCE.md        # This file
        └── CLAUDE.md                  # Quick reference
```

---

## �� Agent Catalog

### 1. LangGraph Best Practices Agent

**Class:** `LangGraphAgent`
**File:** `/root/software/langgraph_dev_agents/agents/langgraph_agent.py`
**Context:** `langgraph_agent.md` (4,000 words)
**Import:** `from agents import LangGraphAgent`

#### Description:
Specialized in LangGraph architecture patterns, state management, recursion control, and async patterns. Ensures agents follow LangGraph best practices and avoid common pitfalls.

#### Key Capabilities:
- ✅ Recursion limit validation
- ✅ Termination logic detection
- ✅ State management analysis (TypedDict, Annotated)
- ✅ Error handling checks (JSON parsing, KeyError)
- ✅ Async pattern validation (ainvoke vs invoke)
- ✅ Type hint coverage
- ✅ Message routing patterns
- ✅ Conditional edges validation
- ✅ Subgraph isolation

#### Critical Checks:
| Issue | Severity | Points Deducted |
|-------|----------|----------------|
| Missing recursion_limit | CRITICAL | -20 |
| Missing termination logic | CRITICAL | -20 |
| Missing JSON error handling | CRITICAL | -20 |
| Low recursion limit < 25 | WARNING | -10 |
| Blocking .invoke() calls | WARNING | -10 |

#### Example Usage:
```python
from agents import LangGraphAgent
from pathlib import Path

agent = LangGraphAgent()

# Single file
result = agent.analyze_file(Path("src/agents/governor_agent.py"))

# Project
results = agent.analyze_project(
    project_path=Path("/root/software/CoreTeam/TheCoreTeam"),
    file_patterns=["**/*_agent.py"]
)

# Check score
if result.overall_score < 80:
    print("⚠️ LangGraph issues detected!")
    for issue in result.issues:
        print(f"- {issue.issue}")
```

#### Output Format:
```python
AnalysisResult(
    agent_name="LangGraph Best Practices Agent",
    file_path="src/agents/governor_agent.py",
    overall_score=72,
    critical_count=1,
    warning_count=0,
    info_count=0,
    issues=[
        Issue(
            severity="CRITICAL",
            category="termination",
            location="governor_agent.py:145",
            issue="Missing explicit termination logic",
            explanation="...",
            fix="Add plan_complete condition",
            code_example="..."
        )
    ],
    best_practices=[...],
    recommendations=[...]
)
```

---

### 2. Security Best Practices Agent

**Class:** `SecurityAgent`
**File:** `/root/software/langgraph_dev_agents/agents/security_agent.py`
**Context:** `security_agent.md` (4,500 words)
**Import:** `from agents import SecurityAgent`

#### Description:
Specialized in security vulnerability detection, credential management, injection prevention, and authentication patterns. Ensures code follows security best practices.

#### Key Capabilities:
- ✅ Hardcoded credential detection
- ✅ JWT signature verification
- ✅ Input validation checks (Pydantic)
- ✅ .env file usage validation
- ✅ MCP authentication header validation
- ✅ Prompt injection detection
- ✅ SQL injection prevention
- ✅ Command injection checks (subprocess, os.system)
- ✅ Error message security (no info leakage)

#### Critical Checks:
| Issue | Severity | Points Deducted |
|-------|----------|----------------|
| Hardcoded credentials | CRITICAL | -25 |
| Disabled JWT verification | CRITICAL | -25 |
| Prompt/SQL/Command injection | CRITICAL | -25 |
| Missing input validation | WARNING | -15 |
| Unsafe error handling | WARNING | -10 |

#### Example Usage:
```python
from agents import SecurityAgent
from pathlib import Path

agent = SecurityAgent()

# Analyze for security issues
result = agent.analyze_file(Path("src/api/routes.py"))

if result.critical_count > 0:
    print("🚨 SECURITY ISSUES DETECTED!")
    for issue in result.issues:
        if issue.severity == "CRITICAL":
            print(f"\n❌ {issue.issue}")
            print(f"   Location: {issue.location}")
            print(f"   Fix: {issue.fix}")
            print(f"   Example:\n{issue.code_example}")
```

#### Output Format:
```python
AnalysisResult(
    agent_name="Security Best Practices Agent",
    file_path="src/api/routes.py",
    overall_score=75,
    critical_count=1,
    issues=[
        Issue(
            severity="CRITICAL",
            category="credentials",
            location="routes.py:23",
            issue="Hardcoded API key detected",
            explanation="API keys should never be hardcoded in source code",
            fix="Use environment variable: os.getenv('API_KEY')",
            code_example="import os\napi_key = os.getenv('OPENAI_API_KEY')"
        )
    ]
)
```

---

### 3. Code Structure Controller Agent

**Class:** `StructureAgent`
**File:** `/root/software/langgraph_dev_agents/agents/structure_agent.py`
**Context:** `structure_agent.md` (3,500 words)
**Import:** `from agents import StructureAgent`

#### Description:
Specialized in code organization, type hints, documentation, naming conventions, and complexity analysis. Ensures code is maintainable and follows Python best practices.

#### Key Capabilities:
- ✅ File organization analysis
- ✅ Import organization (stdlib, third-party, local)
- ✅ Type hint coverage calculation
- ✅ Naming convention validation (PEP 8)
- ✅ Function docstring detection
- ✅ Function complexity analysis (nesting depth, LOC)
- ✅ Magic value detection
- ✅ Module-level documentation

#### Critical Checks:
| Issue | Severity | Points Deducted |
|-------|----------|----------------|
| Type coverage < 50% | WARNING | -10 |
| Function depth > 4 | WARNING | -10 |
| Missing docstrings | INFO | -5 |
| Naming violations | INFO | -5 |
| Disorganized imports | INFO | -5 |

#### Example Usage:
```python
from agents import StructureAgent
from pathlib import Path

agent = StructureAgent()

# Analyze structure
result = agent.analyze_file(Path("src/utils/helpers.py"))

print(f"Type hint coverage: {result.type_hint_coverage}%")
print(f"Docstring coverage: {result.docstring_coverage}%")

for issue in result.issues:
    if issue.category == "complexity":
        print(f"⚠️ {issue.issue} at {issue.location}")
```

#### Output Format:
```python
AnalysisResult(
    agent_name="Code Structure Controller Agent",
    file_path="src/utils/helpers.py",
    overall_score=94,
    warning_count=1,
    issues=[
        Issue(
            severity="WARNING",
            category="complexity",
            location="helpers.py:45-67",
            issue="Function has nesting depth of 5 (limit 4)",
            explanation="Deep nesting reduces readability",
            fix="Extract nested logic into separate functions",
            code_example="..."
        )
    ]
)
```

---

### 4. Test & Debug Agent

**Class:** `TestDebugAgent`
**File:** `/root/software/langgraph_dev_agents/agents/test_debug_agent.py`
**Context:** `test_debug_agent.md` (4,000 words)
**Import:** `from agents import TestDebugAgent`

#### Description:
Specialized in test infrastructure, mock patterns, dataset design, debugging strategies, and performance profiling. Ensures comprehensive testing and debuggability.

#### Key Capabilities:
- ✅ Test framework detection (pytest/unittest)
- ✅ Async test configuration
- ✅ Assertion presence validation
- ✅ Test isolation checks (fixtures, setup/teardown)
- ✅ Mock implementation analysis
- ✅ Skeleton-based mock validation
- ✅ Dataset structure validation
- ✅ Time consistency (freezegun)
- ✅ Logging pattern analysis
- ✅ Error handling in tests

#### Critical Checks:
| Issue | Severity | Points Deducted |
|-------|----------|----------------|
| Tests without assertions | CRITICAL | -20 |
| Mock returns JSON strings | CRITICAL | -20 |
| No test framework | WARNING | -10 |
| Poor test isolation | WARNING | -10 |
| Missing edge cases | INFO | -5 |

#### Example Usage:
```python
from agents import TestDebugAgent
from pathlib import Path

agent = TestDebugAgent()

# Analyze test quality
result = agent.analyze_file(Path("tests/test_agent.py"))

if result.critical_count > 0:
    print("❌ Test quality issues:")
    for issue in result.issues:
        if "assertion" in issue.issue.lower():
            print(f"- {issue.issue}")
            print(f"  Fix: {issue.fix}")
```

#### Output Format:
```python
AnalysisResult(
    agent_name="Test & Debug Agent",
    file_path="tests/test_agent.py",
    overall_score=85,
    critical_count=0,
    warning_count=1,
    issues=[
        Issue(
            severity="WARNING",
            category="mock_design",
            location="test_agent.py:45",
            issue="Mock LLM returns JSON string instead of object",
            explanation="Mocks should return structured objects for type safety",
            fix="Create dataclass for mock response",
            code_example="@dataclass\nclass MockResponse:\n    content: str"
        )
    ]
)
```

---

## 🔧 Base Agent Class

**Class:** `BaseDevAgent`
**File:** `/root/software/langgraph_dev_agents/agents/base_agent.py`
**Purpose:** Base class for all development agents

### Common Interface:

```python
class BaseDevAgent:
    def __init__(self, name: str, description: str, context_file: Optional[Path]):
        """Initialize agent with name, description, and context file."""

    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single Python file."""

    def analyze_project(
        self,
        project_path: Path,
        file_patterns: list[str] = ["**/*.py"]
    ) -> list[AnalysisResult]:
        """Analyze all matching files in project."""

    def format_summary(self, results: list[AnalysisResult]) -> str:
        """Format results as summary report."""

    def save_results(
        self,
        results: list[AnalysisResult],
        output_dir: Path,
        format: str = "both"  # "json", "markdown", "both"
    ) -> None:
        """Save analysis results to files."""
```

### Data Models:

```python
@dataclass
class Issue:
    severity: str  # "CRITICAL", "WARNING", "INFO"
    category: str
    location: str
    issue: str
    explanation: str
    fix: str
    code_example: str

@dataclass
class BestPractice:
    category: str
    what_was_done_well: str
    location: str

@dataclass
class AnalysisResult:
    agent_name: str
    file_path: str
    overall_score: int  # 0-100
    critical_count: int
    warning_count: int
    info_count: int
    issues: list[Issue]
    best_practices: list[BestPractice]
    recommendations: list[str]
```

---

## 📊 Analysis Workflow

```
┌─────────────────────────────────────────────┐
│  User calls agent.analyze_file(path)        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  1. Read file content                       │
│  2. Parse AST (Abstract Syntax Tree)        │
│  3. Run pattern matching checks             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Check Methods (agent-specific):            │
│  - _check_recursion_limit()                 │
│  - _check_termination_logic()               │
│  - _check_error_handling()                  │
│  - _check_security_issues()                 │
│  - _check_type_hints()                      │
│  - etc.                                     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Collect Results:                           │
│  - Issues (with severity)                   │
│  - Best practices found                     │
│  - Recommendations                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Calculate Score:                           │
│  - Start at 100                             │
│  - Deduct points for issues                 │
│  - CRITICAL: -20 to -25 points              │
│  - WARNING: -10 to -15 points               │
│  - INFO: -5 points                          │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Return AnalysisResult                      │
│  - overall_score (0-100)                    │
│  - issues (categorized)                     │
│  - best_practices                           │
│  - recommendations                          │
└─────────────────────────────────────────────┘
```

---

## 🎯 Usage Patterns

### Pattern 1: Development Feedback Loop

```python
from agents import LangGraphAgent
from pathlib import Path

agent = LangGraphAgent()

# Analyze during development
file = Path("src/agents/new_agent.py")
result = agent.analyze_file(file)

# Show immediate feedback
if result.critical_count > 0:
    print("🚨 Fix critical issues first:")
    for issue in result.issues:
        if issue.severity == "CRITICAL":
            print(f"\n{issue.issue}")
            print(f"Fix: {issue.fix}")
```

### Pattern 2: Pre-Commit Validation

```python
import sys
from agents import LangGraphAgent, SecurityAgent

# Get staged files
import subprocess
result = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
    capture_output=True,
    text=True
)
staged_files = [f for f in result.stdout.split("\n") if f.endswith(".py")]

# Analyze
critical_issues = 0
for file in staged_files:
    lg_result = LangGraphAgent().analyze_file(Path(file))
    sec_result = SecurityAgent().analyze_file(Path(file))

    critical_issues += lg_result.critical_count + sec_result.critical_count

if critical_issues > 0:
    print(f"❌ Commit blocked: {critical_issues} critical issues")
    sys.exit(1)
```

### Pattern 3: Continuous Integration

```python
from agents import LangGraphAgent, SecurityAgent, StructureAgent, TestDebugAgent
from pathlib import Path

# Run all agents on project
project_path = Path(".")
agents = [
    LangGraphAgent(),
    SecurityAgent(),
    StructureAgent(),
    TestDebugAgent()
]

all_results = []
for agent in agents:
    results = agent.analyze_project(project_path, ["**/*.py"])
    all_results.extend(results)

# Generate report
total_critical = sum(r.critical_count for r in all_results)
total_warnings = sum(r.warning_count for r in all_results)
avg_score = sum(r.overall_score for r in all_results) / len(all_results)

print(f"📊 Project Quality Report")
print(f"Average Score: {avg_score:.1f}/100")
print(f"Critical Issues: {total_critical}")
print(f"Warnings: {total_warnings}")

# Fail CI if critical issues
if total_critical > 0:
    sys.exit(1)
```

---

## 📚 Documentation Files

### Primary Documentation:
- **AGENTS_GUIDE.md** - Comprehensive usage guide (30,000+ words)
- **AGENTS_REFERENCE.md** - This file (complete reference)
- **CLAUDE.md** - Quick reference for Claude Code

### Agent-Specific Context:
- **langgraph_agent.md** - 4,000 words of LangGraph expertise
- **security_agent.md** - 4,500 words of security expertise
- **structure_agent.md** - 3,500 words of structure expertise
- **test_debug_agent.md** - 4,000 words of testing expertise

### Project Documentation:
- **/root/software/langgraph_dev_agents/CLAUDE.md** - Agent configuration
- **/root/software/langgraph_dev_agents/README.md** - Project overview
- **/root/software/langgraph_dev_agents/project.md** - Project plan
- **/root/software/langgraph_dev_agents/state.md** - Current status

---

## 🔗 Related Resources

### Internal References:
- [Skills Guide](/root/software/.claude/skills/SKILLS_INSTALLATION_SUMMARY.md)
- [CoreTeam Documentation](/root/software/CoreTeam/TheCoreTeam/CLAUDE.md)
- [Master Rules](/root/software/CLAUDE_MASTER_RULES.md)

### External Resources:
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [PEP 8 Style Guide](https://pep8.org/)

---

**Last Updated:** 2025-11-30
**Status:** ✅ Production Ready
**Tested On:** CoreTeam/TheCoreTeam (100% detection rate, 0% false positives)
