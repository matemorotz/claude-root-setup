---
name: testing-workflows
description: Automated testing workflows with virtual environment validation and A/B testing. Use when testing code changes, validating implementations, or running test suites.
---

# Testing Workflows Skill

This skill automates testing procedures following the project's master rules for safe code validation and A/B testing approaches.

## Context Import

Reference project testing conventions:
@../../project.md

Follow master execution rules:
@../../CLAUDE_MASTER_RULES.md

## Testing Philosophy

### Core Principles (from CLAUDE_MASTER_RULES.md)
1. **Always use virtual environment**: `venv_linux`
2. **A/B Testing Approach**: Test new code alongside existing
3. **Dev Branch First**: Never test directly on main
4. **Validate Before Complete**: Tests must pass before marking tasks done

### Technology Stack
- Python 3.x with type hints
- pytest for testing
- Virtual environment: `/root/venv_linux`
- Branch strategy: `dev` → test → `main`

## Testing Workflow

### Phase 1: Pre-Testing Setup

1. **Verify Virtual Environment**
```bash
# Check venv exists
ls -la /root/venv_linux/

# Activate and verify
source /root/venv_linux/bin/activate
which python
# Should show: /root/venv_linux/bin/python
```

2. **Ensure Dev Branch**
```bash
# Check current branch
git branch --show-current

# Create/switch to dev branch if needed
git checkout -b dev || git checkout dev

# Verify not on main
if [ "$(git branch --show-current)" == "main" ]; then
    echo "ERROR: Cannot test on main branch!"
    exit 1
fi
```

3. **Check Existing Tests**
```bash
# Search for test files
find . -name "test_*.py" -o -name "*_test.py"

# Search for pytest.ini or setup.cfg
find . -name "pytest.ini" -o -name "setup.cfg"

# Check README for test commands
grep -i "test" README.md
```

### Phase 2: Test Execution

4. **Run Existing Test Suite**
```bash
# Using venv explicitly
/root/venv_linux/bin/pytest

# With verbose output
/root/venv_linux/bin/pytest -v

# With coverage
/root/venv_linux/bin/pytest --cov=. --cov-report=html

# Specific test file
/root/venv_linux/bin/pytest tests/test_specific.py

# Specific test function
/root/venv_linux/bin/pytest tests/test_specific.py::test_function_name
```

5. **A/B Testing Pattern** (for code changes)
```python
# Keep both implementations for comparison
# Example: Refactoring a function

# Original implementation (keep temporarily)
def process_data_original(data: list) -> list:
    """Original working implementation"""
    # ... existing code ...
    pass

# New implementation (test alongside)
def process_data_new(data: list) -> list:
    """New improved implementation"""
    # ... refactored code ...
    pass

# A/B Test
def test_ab_comparison():
    """Compare original vs new implementation"""
    test_data = [1, 2, 3, 4, 5]

    result_original = process_data_original(test_data)
    result_new = process_data_new(test_data)

    # Verify same behavior
    assert result_original == result_new, "Results differ!"

    # Verify correctness
    assert result_new == expected_output
```

6. **Integration Testing**
```bash
# Test CoreTeam multi-agent system
cd /root/CoreTeam/dev/
/root/venv_linux/bin/python -m pytest tests/

# Test Memory System MCP
cd /root/memory_system/
/root/venv_linux/bin/python -m pytest tests/

# Test with actual services running
# Start service in background
/root/venv_linux/bin/python server.py &
SERVICE_PID=$!

# Run integration tests
/root/venv_linux/bin/pytest tests/integration/

# Cleanup
kill $SERVICE_PID
```

### Phase 3: Validation

7. **Lint and Type Check**
```bash
# Run linting (if configured)
/root/venv_linux/bin/flake8 .
/root/venv_linux/bin/pylint **/*.py

# Type checking with mypy
/root/venv_linux/bin/mypy .

# Black formatting check
/root/venv_linux/bin/black --check .
```

8. **Validation Checklist**
   - [ ] All tests pass in venv
   - [ ] Type hints are correct
   - [ ] Linting passes (no errors)
   - [ ] Integration tests succeed
   - [ ] A/B tests show equivalence (if refactoring)
   - [ ] No unintended side effects
   - [ ] Error handling tested
   - [ ] Edge cases covered

### Phase 4: Documentation

9. **Test Documentation**
```python
def test_user_authentication():
    """
    Test user authentication workflow.

    Verifies:
    - Valid credentials authenticate successfully
    - Invalid credentials are rejected
    - Token is generated and valid
    - Error messages are appropriate

    Related to: project.md - Authentication section
    """
    # Test implementation
    pass
```

10. **Update Test README**
```markdown
# Testing Guide

## Running Tests

```bash
# All tests
/root/venv_linux/bin/pytest

# Specific module
/root/venv_linux/bin/pytest tests/test_agents.py

# With coverage
/root/venv_linux/bin/pytest --cov=src
```

## Test Structure
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for system workflows
- `tests/fixtures/` - Test data and fixtures

## Adding New Tests
1. Create test file: `test_<module_name>.py`
2. Follow existing patterns
3. Use descriptive test names
4. Include docstrings
5. Run tests before committing
```

## Testing Patterns

### Unit Testing Pattern
```python
import pytest
from typing import List

def test_agent_initialization():
    """Test agent initializes with correct state"""
    from agents.calendar_agent import CalendarAgent

    agent = CalendarAgent()

    assert agent.state is not None
    assert agent.llm_config is not None
    assert hasattr(agent, 'execute')

def test_agent_execution():
    """Test agent executes task correctly"""
    from agents.calendar_agent import CalendarAgent

    agent = CalendarAgent()
    result = agent.execute({"task": "get_events", "date": "2025-10-31"})

    assert result["status"] == "success"
    assert "events" in result
```

### Integration Testing Pattern
```python
import pytest
import requests

@pytest.fixture
def mcp_server():
    """Start MCP server for testing"""
    import subprocess
    process = subprocess.Popen([
        "/root/venv_linux/bin/python",
        "/root/memory_system/server.py"
    ])
    yield process
    process.kill()

def test_mcp_integration(mcp_server):
    """Test MCP server integration"""
    import time
    time.sleep(2)  # Wait for server start

    response = requests.post(
        "http://localhost:8001/tools/search_memory",
        json={"query": "test"},
        headers={"Authorization": "Menycibu"}
    )

    assert response.status_code == 200
    assert "results" in response.json()
```

### Mock Testing Pattern
```python
from unittest.mock import Mock, patch

def test_external_api_call():
    """Test function with external API dependency"""
    with patch('requests.post') as mock_post:
        # Configure mock
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": "test"}

        # Test function that uses requests.post
        from services.api_client import fetch_data
        result = fetch_data("endpoint")

        # Verify
        assert result == {"data": "test"}
        mock_post.assert_called_once()
```

### Parametrized Testing Pattern
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("Test", "TEST"),
    ("", ""),
])
def test_uppercase_conversion(input, expected):
    """Test uppercase conversion with multiple inputs"""
    from utils.text import to_uppercase
    assert to_uppercase(input) == expected
```

## Project-Specific Testing

### CoreTeam Agent Testing
```bash
# Test specific agent
cd /root/CoreTeam/dev/
/root/venv_linux/bin/pytest tests/test_calendar_agent.py

# Test agent integration with governor
/root/venv_linux/bin/pytest tests/test_governor.py

# Test full workflow
/root/venv_linux/bin/python main.py --test-mode
```

### Memory System Testing
```bash
# Test memory CRUD operations
cd /root/memory_system/
/root/venv_linux/bin/pytest tests/test_memory_crud.py

# Test vector search
/root/venv_linux/bin/pytest tests/test_vector_search.py

# Test timeline tracking
/root/venv_linux/bin/pytest tests/test_timeline.py
```

### MCP Server Testing
```bash
# Test MCP endpoints
/root/venv_linux/bin/pytest tests/test_mcp_endpoints.py

# Test authentication
/root/venv_linux/bin/pytest tests/test_auth.py

# Test with actual MCP client
/root/venv_linux/bin/python test_mcp_client.py
```

## Continuous Testing Workflow

### Before Committing
```bash
# 1. Run all tests
/root/venv_linux/bin/pytest

# 2. Check types
/root/venv_linux/bin/mypy .

# 3. Lint code
/root/venv_linux/bin/flake8 .

# 4. Format check
/root/venv_linux/bin/black --check .

# 5. If all pass, ready to commit
```

### After Code Changes
```bash
# 1. Run affected tests
/root/venv_linux/bin/pytest tests/test_modified_module.py

# 2. Run integration tests
/root/venv_linux/bin/pytest tests/integration/

# 3. Run full suite
/root/venv_linux/bin/pytest

# 4. Verify no regressions
git diff main dev -- tests/
```

## Troubleshooting

### Virtual Environment Issues
```bash
# Problem: Tests fail with import errors
# Solution: Ensure using correct venv
which python  # Should show /root/venv_linux/bin/python

# Problem: Package not found
# Solution: Install in venv
/root/venv_linux/bin/pip install <package>

# Problem: Wrong Python version
# Solution: Recreate venv
python3 -m venv /root/venv_linux
```

### Test Failures
```bash
# Run with verbose output
/root/venv_linux/bin/pytest -vv

# Run with print statements visible
/root/venv_linux/bin/pytest -s

# Run specific failing test
/root/venv_linux/bin/pytest tests/test_file.py::test_function -vv

# Run with debugger on failure
/root/venv_linux/bin/pytest --pdb
```

### Coverage Issues
```bash
# Generate detailed coverage report
/root/venv_linux/bin/pytest --cov=. --cov-report=html

# View report
firefox htmlcov/index.html

# Find untested code
/root/venv_linux/bin/pytest --cov=. --cov-report=term-missing
```

## Best Practices

### Do's
✓ Always use `/root/venv_linux/bin/python` or `/root/venv_linux/bin/pytest`
✓ Test on dev branch first
✓ Use A/B testing for refactoring
✓ Write descriptive test names
✓ Include test documentation
✓ Run full suite before merging
✓ Verify tests pass before marking tasks complete

### Don'ts
✗ Never test directly on main branch
✗ Don't skip virtual environment
✗ Don't delete old code before new tests pass
✗ Don't commit with failing tests
✗ Don't skip integration tests
✗ Don't assume tests work without running them

## Quick Reference

```bash
# Standard test command
/root/venv_linux/bin/pytest

# Verbose with coverage
/root/venv_linux/bin/pytest -vv --cov=. --cov-report=term-missing

# Specific test
/root/venv_linux/bin/pytest tests/test_file.py::test_name

# Type check
/root/venv_linux/bin/mypy .

# Lint
/root/venv_linux/bin/flake8 .

# Format
/root/venv_linux/bin/black .
```

## References

See also:
- `CLAUDE_MASTER_RULES.md` - Testing priorities and safe code practices
- `project.md` - Testing conventions and infrastructure
- `/root/CoreTeam/dev/tests/` - Example test implementations
- pytest documentation: https://docs.pytest.org
