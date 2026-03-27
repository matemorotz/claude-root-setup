---
name: deploying-agents
description: Deploy new agents following LangGraph multi-agent architecture patterns. Use when creating new specialist agents for the CoreTeam system.
---

# Agent Deployment Skill

This skill automates the deployment of new specialist agents following the project's LangGraph-based multi-agent architecture.

## Context Import

Reference project conventions:
@../../project.md

Follow master execution rules:
@../../CLAUDE_MASTER_RULES.md

## Agent Architecture Patterns

### LangGraph Multi-Agent Structure
- **Governor Agent**: Orchestrates specialist agents
- **Specialist Agents**: Domain-specific tasks (email, booking, calendar, etc.)
- **State Management**: LangGraph native persistent state
- **Context Flow**: Chain of thought (update_context → update_plan → execute_plan)

### Technology Stack
- Python 3.x with type hints
- LangGraph for agent workflows
- Azure OpenAI for LLM
- Virtual environment: `venv_linux`

## Deployment Workflow

### Phase 1: Planning
1. **Clarify Agent Purpose**
   - What domain does this agent handle?
   - What specific tasks will it perform?
   - How does it integrate with existing agents?

2. **Review Existing Agents**
   - Check `/root/CoreTeam/dev/` for similar agents
   - Identify reusable patterns
   - Understand state schema requirements

### Phase 2: Implementation
3. **Create Agent File**
   - Location: `/root/CoreTeam/dev/agents/`
   - Naming: `{domain}_agent.py` (e.g., `calendar_agent.py`)
   - Follow existing agent structure

4. **Agent Template Structure**
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

# State Schema
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    context: str
    plan: str
    # Add domain-specific fields

# Agent Functions
def update_context(state: AgentState) -> AgentState:
    """Analyze current situation and update context"""
    pass

def update_plan(state: AgentState) -> AgentState:
    """Create execution plan based on context"""
    pass

def execute_plan(state: AgentState) -> AgentState:
    """Execute the planned actions"""
    pass

# Build Graph
def create_agent():
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
```

5. **Integrate with Governor**
   - Update governor agent to route to new specialist
   - Add domain detection logic
   - Test handoff mechanism

### Phase 3: Testing
6. **Development Branch Testing**
   - Work in `dev` branch per master rules
   - Use virtual environment: `venv_linux/bin/python`
   - Test agent in isolation first
   - Test integration with governor

7. **Validation Checklist**
   - [ ] Agent follows LangGraph patterns
   - [ ] Uses correct virtual environment
   - [ ] Includes type hints
   - [ ] Error handling implemented
   - [ ] State schema compatible
   - [ ] Integrates with governor
   - [ ] Tests pass

### Phase 4: Deployment
8. **Code Review**
   - Verify against project.md conventions
   - Check CLAUDE_MASTER_RULES.md compliance
   - A/B test if modifying existing code

9. **Integration**
   - Merge to main after approval
   - Update documentation
   - Monitor initial executions

## Common Agent Types

### Email Agent
- Domain: Email operations
- Tasks: Send, read, search emails
- Integration: Email service APIs

### Booking Agent
- Domain: Reservation management
- Tasks: Create, modify, cancel bookings
- Integration: Booking systems

### Calendar Agent
- Domain: Schedule management
- Tasks: Create events, check availability
- Integration: Calendar APIs

## Best Practices

### Do's
✓ Follow existing agent patterns in CoreTeam
✓ Use venv_linux virtual environment
✓ Include comprehensive type hints
✓ Test in dev branch first
✓ Handle errors appropriately
✓ Document agent capabilities

### Don'ts
✗ Don't skip validation checklist
✗ Don't modify main branch directly
✗ Don't hardcode credentials
✗ Don't skip error handling
✗ Don't bypass virtual environment

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure using `venv_linux/bin/python`
2. **State Conflicts**: Verify state schema matches governor
3. **Integration Failures**: Check handoff logic in governor
4. **Environment Issues**: Activate correct virtual environment

## Examples

### Creating a Calendar Agent
```bash
# 1. Create agent file
cd /root/CoreTeam/dev/agents/
touch calendar_agent.py

# 2. Implement using template above
# 3. Test in isolation
venv_linux/bin/python test_calendar_agent.py

# 4. Integrate with governor
# 5. Run full system test
```

## References

See also:
- `/root/CoreTeam/dev/main.py` - Governor implementation
- `/root/CoreTeam/dev/main_alt.py` - Alternative entry point
- `project.md` - Full architecture documentation
- `CLAUDE_MASTER_RULES.md` - Execution principles
