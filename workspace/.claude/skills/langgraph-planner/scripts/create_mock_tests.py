#!/usr/bin/env python3
"""
Generate mock testing framework for planned graph

Why mock testing:
- Test graph logic without API dependencies
- Faster iteration (no network calls)
- Reproducible tests (deterministic responses)
- Safe experimentation (no real API costs/rate limits)

Design philosophy:
- Simple mocks for simple nodes (just return data)
- Complex mocks only where needed (e.g., LLM with variations)
- Modular - easy to swap mocks for real implementations later
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any


def generate_mock_state(plan: Dict[str, Any]) -> str:
    """
    Generate mock state fixtures
    
    Why: Provide realistic test data for state
    Design: Extract from state schema, create sensible defaults
    """
    state_schema = plan.get("state_schema", {})
    fields = state_schema.get("fields", [])
    
    mock_states = []
    
    # Scenario 1: Fresh start
    fresh_state = {"# Scenario: Fresh start": ""}
    for field in fields:
        name = field.get("name")
        field_type = field.get("type", "")
        
        # Generate sensible defaults based on type
        if "List" in field_type or "list" in field_type:
            if "message" in name.lower():
                fresh_state[name] = '[HumanMessage(content="Test request")]'
            else:
                fresh_state[name] = "[]"
        elif "int" in field_type.lower():
            fresh_state[name] = "0"
        elif "bool" in field_type.lower():
            fresh_state[name] = "False"
        elif "str" in field_type.lower():
            fresh_state[name] = '""'
        elif "Dict" in field_type or "dict" in field_type:
            fresh_state[name] = "{}"
        else:
            fresh_state[name] = "None"
    
    mock_states.append(fresh_state)
    
    # Scenario 2: Mid-execution (after some nodes)
    mid_state = fresh_state.copy()
    mid_state["# Scenario"] = "Mid-execution"
    if "iteration_count" in mid_state:
        mid_state["iteration_count"] = "2"
    if "context" in mid_state:
        mid_state["context"] = '["fact1", "fact2"]'
    
    mock_states.append(mid_state)
    
    # Scenario 3: Near completion
    complete_state = mid_state.copy()
    complete_state["# Scenario"] = "Near completion"
    if "task_complete" in complete_state:
        complete_state["task_complete"] = "True"
    if "iteration_count" in complete_state:
        complete_state["iteration_count"] = "5"
    
    mock_states.append(complete_state)
    
    return json.dumps(mock_states, indent=2)


def generate_mock_llm_responses(plan: Dict[str, Any]) -> str:
    """
    Generate mock LLM responses for each LLM node
    
    Why separate mocks per node: Different nodes expect different formats
    Design: Start simple (one response), add variations for edge cases
    """
    nodes = plan.get("nodes", [])
    llm_nodes = [n for n in nodes if "llm" in n.get("type", "").lower()]
    
    mocks = {}
    
    for node in llm_nodes:
        node_name = node.get("name")
        processing = node.get("processing", "")
        
        # Determine response format from processing description
        if "json" in processing.lower():
            # JSON response mock
            mocks[node_name] = {
                "success_response": '{"result": "success", "data": "mock data"}',
                "error_response": "Invalid JSON: {bad syntax",  # For testing validation
                "description": "Returns JSON. Test both valid and invalid responses."
            }
        else:
            # Text response mock
            mocks[node_name] = {
                "success_response": "Mock LLM response for testing",
                "description": "Returns plain text"
            }
    
    return json.dumps(mocks, indent=2)


def generate_mock_test_suite(plan: Dict[str, Any]) -> str:
    """
    Generate complete test suite template
    
    Why template: Give users a starting point, they customize for their domain
    Design: Pytest-based (standard), async-aware, simple structure
    """
    graph_name = plan.get("graph_name", "test_graph")
    
    test_code = f'''"""
Mock tests for {graph_name}

Why mock tests:
- Fast feedback loop (no API calls)
- Deterministic (same inputs → same outputs)
- Isolation (test graph logic independently)

How to run:
pytest test_{graph_name}_mock.py -v

How to expand:
1. Add more scenarios to test_scenarios
2. Create variations for edge cases
3. Add failure scenario tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

# Import your graph implementation
# from agents.{graph_name}_graph.{graph_name}_agent import {graph_name.title()}Agent


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_model():
    """
    Mock LLM model
    
    Why AsyncMock: LLM calls are async in production
    Design: Return configurable responses for different test scenarios
    """
    model = AsyncMock()
    
    # Default response (simple case)
    model.ainvoke.return_value = MagicMock(
        content='{{"result": "success", "data": "test"}}',
        name="assistant"
    )
    
    return model


@pytest.fixture
def mock_tools():
    """
    Mock MCP/API tools
    
    Why: Test without external dependencies
    Design: Simple success responses, add failures as needed
    """
    return []


# ============================================================================
# TEST SCENARIOS
# ============================================================================

@pytest.mark.asyncio
async def test_simple_success_path(mock_model, mock_tools):
    """
    Test: Happy path from START to END
    
    Why test this: Validates basic graph connectivity
    Expectation: Graph completes successfully
    """
    # Arrange
    # graph = {graph_name.title()}Agent(model=mock_model, children={{}})
    input_state = {{
        "messages": [],  # Add test message
        "iteration_count": 0
    }}
    
    # Act
    # result = await graph.agent.ainvoke(input_state)
    
    # Assert
    # assert result.get("task_complete") is True
    # assert result.get("iteration_count") > 0
    
    # TODO: Replace with actual implementation
    assert True, "Implement test with real graph"


@pytest.mark.asyncio
async def test_validation_retry():
    """
    Test: Validation fails, retries, then succeeds
    
    Why test this: Ensures retry logic works
    Expectation: Graph recovers from validation failure
    """
    # Arrange - mock returns invalid JSON first, then valid
    call_count = 0
    
    async def mock_ainvoke(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return MagicMock(content="Invalid JSON: {{bad")
        else:
            return MagicMock(content='{{"result": "success"}}')
    
    # TODO: Implement test with retry logic
    assert True, "Implement validation retry test"


@pytest.mark.asyncio
async def test_max_iterations_safety():
    """
    Test: Graph terminates at iteration limit
    
    Why test this: Critical safety - prevents infinite loops
    Expectation: Graph stops at max iterations even if not complete
    """
    # TODO: Implement with iteration counter check
    assert True, "Implement safety limit test"


@pytest.mark.asyncio
async def test_error_handling():
    """
    Test: LLM call fails, graph handles gracefully
    
    Why test this: Production resilience
    Expectation: Error logged, graph continues or terminates safely
    """
    # Arrange - mock raises exception
    error_model = AsyncMock()
    error_model.ainvoke.side_effect = Exception("API Error")
    
    # TODO: Implement error handling test
    assert True, "Implement error handling test"


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.asyncio
async def test_empty_input():
    """Edge case: Empty input data"""
    # TODO: How should graph handle empty input?
    assert True, "Implement empty input test"


@pytest.mark.asyncio
async def test_large_conversation():
    """Edge case: Very long conversation history"""
    # TODO: Test message windowing/pruning
    assert True, "Implement large conversation test"


# ============================================================================
# INTEGRATION TESTS (with mock responses)
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow_scenario_1():
    """
    Integration test: Realistic user scenario
    
    Scenario: [Describe realistic use case]
    Steps:
    1. User provides input
    2. Graph processes through nodes
    3. Graph returns expected output
    
    Why separate from unit tests: Tests complete workflow
    """
    # TODO: Implement realistic scenario
    assert True, "Implement integration test"


# ============================================================================
# PERFORMANCE TESTS (optional)
# ============================================================================

@pytest.mark.asyncio
async def test_response_time():
    """
    Performance test: Graph completes within acceptable time
    
    Why: Ensure graph doesn't get stuck or take too long
    Design: With mocks, should be fast (<1s)
    """
    import time
    
    start = time.time()
    # TODO: Run graph
    elapsed = time.time() - start
    
    assert elapsed < 1.0, f"Graph took {{elapsed}}s (expected <1s with mocks)"
    assert True, "Implement performance test"
'''
    
    return test_code


def generate_mock_data_fixtures(plan: Dict[str, Any]) -> str:
    """
    Generate test data fixtures file
    
    Why separate file: Keep tests clean, reuse fixtures
    Design: JSON format for easy editing
    """
    fixtures = {
        "test_scenarios": [
            {
                "name": "simple_request",
                "description": "Basic request that should succeed",
                "input": {
                    "user_message": "Test request",
                    "context": []
                },
                "expected_outcome": "success"
            },
            {
                "name": "complex_request",
                "description": "Multi-step request requiring multiple nodes",
                "input": {
                    "user_message": "Complex multi-step request",
                    "context": ["prior fact"]
                },
                "expected_outcome": "success_after_iterations"
            },
            {
                "name": "edge_case_empty",
                "description": "Empty input - how should graph handle?",
                "input": {
                    "user_message": "",
                    "context": []
                },
                "expected_outcome": "error_or_request_clarification"
            }
        ],
        "mock_llm_responses": {},  # Populated from generate_mock_llm_responses
        "mock_api_responses": {
            "description": "Add mock responses for external APIs/MCP tools",
            "example_api_call": {
                "success": {"status": "ok", "data": "mock data"},
                "failure": {"status": "error", "message": "API unavailable"}
            }
        }
    }
    
    return json.dumps(fixtures, indent=2)


def main():
    """
    Generate complete mock testing framework
    
    Creates:
    1. test_mock.py - Test suite template
    2. mock_fixtures.json - Test data
    3. mock_states.json - State scenarios
    4. mock_responses.json - LLM/API mock responses
    
    Why separate files:
    - Test code separate from test data (SOLID principles)
    - Easy to edit fixtures without touching code
    - Reusable across test files
    """
    if len(sys.argv) < 2:
        print("Usage: python create_mock_tests.py <plan.json>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            plan = json.load(f)
        
        graph_name = plan.get("graph_name", "test_graph")
        output_dir = Path(f"tests_{graph_name}")
        output_dir.mkdir(exist_ok=True)
        
        print("=" * 60)
        print(f"GENERATING MOCK TESTING FRAMEWORK: {graph_name}")
        print("=" * 60)
        
        # 1. Generate test suite
        test_code = generate_mock_test_suite(plan)
        test_file = output_dir / f"test_{graph_name}_mock.py"
        with open(test_file, 'w') as f:
            f.write(test_code)
        print(f"\n✓ Created: {test_file}")
        
        # 2. Generate mock states
        mock_states = generate_mock_state(plan)
        states_file = output_dir / "mock_states.json"
        with open(states_file, 'w') as f:
            f.write(mock_states)
        print(f"✓ Created: {states_file}")
        
        # 3. Generate mock LLM responses
        mock_responses = generate_mock_llm_responses(plan)
        responses_file = output_dir / "mock_llm_responses.json"
        with open(responses_file, 'w') as f:
            f.write(mock_responses)
        print(f"✓ Created: {responses_file}")
        
        # 4. Generate test data fixtures
        fixtures = generate_mock_data_fixtures(plan)
        fixtures_file = output_dir / "test_fixtures.json"
        with open(fixtures_file, 'w') as f:
            f.write(fixtures)
        print(f"✓ Created: {fixtures_file}")
        
        print("\n" + "=" * 60)
        print("MOCK TESTING FRAMEWORK READY")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"1. Review generated tests in {output_dir}/")
        print(f"2. Customize mock responses in mock_llm_responses.json")
        print(f"3. Add domain-specific test scenarios")
        print(f"4. Run tests: pytest {test_file} -v")
        print(f"5. Iterate: Add tests for edge cases and failures")
        
        print(f"\n💡 Testing philosophy:")
        print(f"  - Start simple: Test basic connectivity first")
        print(f"  - Add complexity gradually: Edge cases, failures, performance")
        print(f"  - Keep mocks simple: Complex mocks = complex tests = maintenance burden")
        print(f"  - Mock what you must: Use real implementations when possible")
        
        return 0
    
    except Exception as e:
        print(f"ERROR: Failed to generate mock tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
