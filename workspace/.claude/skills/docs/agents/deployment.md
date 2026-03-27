# Agent Deployment Procedures

## Overview
Standard procedures for deploying new specialist agents into the CoreTeam multi-agent system.

## Deployment Checklist

### Pre-Deployment
- [ ] Agent purpose clearly defined
- [ ] State schema designed and documented
- [ ] Integration points identified
- [ ] Test plan created
- [ ] Development branch created

### Development
- [ ] Agent implementation follows architecture patterns
- [ ] Type hints included throughout
- [ ] Error handling comprehensive
- [ ] Logging configured
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing

### Integration
- [ ] Governor routing logic updated
- [ ] State handoff tested
- [ ] Multi-agent workflows validated
- [ ] Performance benchmarked
- [ ] Documentation updated

### Deployment
- [ ] Code review completed
- [ ] All tests passing in dev branch
- [ ] No regressions in existing agents
- [ ] Merged to main branch
- [ ] Deployed to production environment
- [ ] Monitoring configured

## Standard Deployment Process

### Step 1: Planning
```bash
# 1. Create feature branch
git checkout -b feature/new-agent-name

# 2. Document agent purpose
echo "Agent Purpose: Handle [domain] operations" >> docs/agents/new-agent.md

# 3. Design state schema
# Document in agent file
```

### Step 2: Implementation
```bash
# 1. Create agent file
cd /root/CoreTeam/dev/agents/
touch new_agent.py

# 2. Implement following template
# See: docs/agents/architecture.md

# 3. Create tests
cd /root/CoreTeam/dev/tests/
touch test_new_agent.py
```

### Step 3: Testing
```bash
# 1. Run unit tests
/root/venv_linux/bin/pytest tests/test_new_agent.py -vv

# 2. Run integration tests
/root/venv_linux/bin/pytest tests/integration/ -vv

# 3. Manual testing
/root/venv_linux/bin/python main.py --test-mode --agent=new_agent
```

### Step 4: Integration with Governor
```python
# Update main.py router logic
def route_to_agent(state):
    if "new_domain_keyword" in request:
        return "new_agent"
    # ... existing routing ...

# Add agent to workflow
workflow.add_node("new_agent", new_agent_execute)
workflow.add_edge("router", "new_agent")
workflow.add_edge("new_agent", "aggregator")
```

### Step 5: Validation
```bash
# 1. Full system test
/root/venv_linux/bin/pytest tests/ -vv

# 2. Check no regressions
git diff main -- tests/

# 3. Performance test
/root/venv_linux/bin/python benchmark_agent.py --agent=new_agent
```

### Step 6: Deployment
```bash
# 1. Merge to main
git checkout main
git merge feature/new-agent-name

# 2. Restart services
sudo systemctl restart coreteam-service

# 3. Verify deployment
curl -X POST http://localhost:8000/health
```

## Agent File Template

```python
"""
Agent Name: [Agent Name]
Purpose: [Brief description]
Domain: [Domain area]
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
import logging

logger = logging.getLogger(__name__)

# State Schema
class AgentState(TypedDict):
    """State schema for [Agent Name]"""
    messages: Annotated[list, operator.add]
    context: str
    plan: str
    # Domain-specific fields
    domain_data: dict

# Agent Functions
def update_context(state: AgentState) -> AgentState:
    """
    Analyze current situation and update context.

    Steps:
    1. Review incoming messages
    2. Gather necessary information
    3. Update context field
    """
    logger.info("Updating context")
    try:
        # Implementation
        state["context"] = "Analyzed context"
        return state
    except Exception as e:
        logger.error(f"Context update failed: {e}")
        raise

def update_plan(state: AgentState) -> AgentState:
    """
    Create execution plan based on context.

    Steps:
    1. Analyze context
    2. Determine necessary actions
    3. Create step-by-step plan
    """
    logger.info("Creating plan")
    try:
        # Implementation
        state["plan"] = "1. Step one\n2. Step two"
        return state
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        raise

def execute_plan(state: AgentState) -> AgentState:
    """
    Execute the planned actions.

    Steps:
    1. Parse plan
    2. Execute each step
    3. Aggregate results
    """
    logger.info("Executing plan")
    try:
        # Implementation
        state["domain_data"]["result"] = "Success"
        return state
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        raise

# Build Graph
def create_agent() -> StateGraph:
    """Create and compile agent workflow"""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("update_context", update_context)
    workflow.add_node("update_plan", update_plan)
    workflow.add_node("execute_plan", execute_plan)

    # Add edges
    workflow.set_entry_point("update_context")
    workflow.add_edge("update_context", "update_plan")
    workflow.add_edge("update_plan", "execute_plan")
    workflow.add_edge("execute_plan", END)

    return workflow.compile()

# Entry point
if __name__ == "__main__":
    # Test agent standalone
    agent = create_agent()
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Test request"}],
        "context": "",
        "plan": "",
        "domain_data": {}
    })
    print(result)
```

## Common Deployment Issues

### Issue: Import Errors
**Symptom**: `ModuleNotFoundError` or `ImportError`
**Solution**:
```bash
# Ensure using correct venv
/root/venv_linux/bin/python -c "import sys; print(sys.path)"

# Install missing packages
/root/venv_linux/bin/pip install <package>
```

### Issue: State Schema Mismatch
**Symptom**: `KeyError` or `TypeError` in state access
**Solution**:
```python
# Ensure all agents use compatible state schema
# Add optional fields with defaults
state.get("field", default_value)
```

### Issue: Governor Routing Fails
**Symptom**: Agent not receiving requests
**Solution**:
```python
# Debug routing logic
logger.debug(f"Routing decision for: {request}")
logger.debug(f"Selected agent: {agent_name}")

# Verify keywords in routing logic match agent domain
```

### Issue: Integration Tests Fail
**Symptom**: Agent works standalone but fails in multi-agent
**Solution**:
```bash
# Test state handoff
/root/venv_linux/bin/pytest tests/test_state_handoff.py -vv

# Verify state persistence between agents
```

## Rollback Procedure

### If Deployment Fails
```bash
# 1. Identify issue
tail -f /var/log/coreteam.log

# 2. Quick rollback
git checkout main
git revert HEAD

# 3. Restart services
sudo systemctl restart coreteam-service

# 4. Verify system operational
curl http://localhost:8000/health
```

### If Issue Found Post-Deployment
```bash
# 1. Create hotfix branch
git checkout -b hotfix/agent-issue

# 2. Fix issue
# ... make changes ...

# 3. Test thoroughly
/root/venv_linux/bin/pytest tests/ -vv

# 4. Deploy hotfix
git checkout main
git merge hotfix/agent-issue
sudo systemctl restart coreteam-service
```

## Monitoring New Agents

### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log key events
logger.info(f"Agent started: {agent_name}")
logger.info(f"Processing request: {request_id}")
logger.error(f"Agent failed: {error_message}")
```

### Metrics
```python
# Track agent performance
metrics = {
    "agent_name": "new_agent",
    "requests_handled": 0,
    "success_rate": 0.0,
    "avg_response_time": 0.0,
    "errors": 0
}

# Update metrics after each execution
```

### Health Checks
```python
@app.get("/health/agent/new_agent")
async def agent_health():
    """Health check for new agent"""
    try:
        # Verify agent operational
        agent.test_connection()
        return {"status": "healthy", "agent": "new_agent"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Best Practices

### Deployment
✓ Always deploy to dev environment first
✓ Run full test suite before merging
✓ Use feature branches for development
✓ Document all changes in commit messages
✓ Monitor logs during initial deployment

### Testing
✓ Write tests before implementation (TDD)
✓ Include both unit and integration tests
✓ Test error handling paths
✓ Verify state persistence
✓ Benchmark performance

### Documentation
✓ Update architecture docs
✓ Document agent purpose and capabilities
✓ Include usage examples
✓ Note any limitations or constraints
✓ Keep changelog updated

## References

See also:
- `docs/agents/architecture.md` - Agent architecture patterns
- `docs/testing/workflows.md` - Testing procedures
- `CLAUDE_MASTER_RULES.md` - Deployment rules
- `/root/CoreTeam/dev/` - Agent implementations
