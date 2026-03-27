# Prompt Engineering for LangGraph Nodes

Guide for designing effective prompts for LLM nodes in LangGraph architectures.

---

## External Prompt File Pattern

### File Structure

Store prompts in `.prompt` files with placeholder substitution:

```
prompts/
├── builder.prompt          # Plan generation
├── reviewer.prompt         # Validation/review
├── router.prompt           # Routing decisions
├── analyzer.prompt         # Analysis tasks
└── formatter.prompt        # Output formatting
```

### Template Syntax

Use `$placeholder_name` for dynamic substitution:

```
File: builder.prompt

You are an expert $role_name working in the $workflow workflow.

Available resources:
$available_resources

Keywords for special actions:
- $user_key_word: Request user input
- $cancel_key_word: User cancellation
- $terminate_key_word: Task completion

Current context:
$context

Your task:
$task_description
```

### Loading with Substitution

```python
from string import Template
from pathlib import Path

def read_system_prompt(
    node_name: str,
    sub_dir: str = None,
    placeholders: Dict[str, str] = None
) -> str:
    """Load prompt file with placeholder substitution"""
    prompt_dir = Path("src/agents")
    if sub_dir:
        prompt_dir = prompt_dir / sub_dir

    prompt_path = prompt_dir / f"{node_name}.prompt"

    with open(prompt_path, 'r') as f:
        content = f.read()

    if placeholders:
        return Template(content).safe_substitute(placeholders)
    return content
```

---

## System Prompt Templates by Node Type

### 1. Builder Node (Generation)

**Purpose:** Generate structured outputs (plans, analyses, summaries)

```
You are an expert [ROLE] responsible for [PRIMARY_TASK].

**Your Responsibilities:**
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

**Output Format (STRICT JSON):**
{
  "field1": "description",
  "field2": ["list", "of", "items"],
  "field3": {"nested": "object"}
}

**Constraints:**
- Must be valid JSON (no comments, trailing commas, or syntax errors)
- All required fields must be present
- Follow the exact structure above

**Available Context:**
- Current conversation: [Will be injected from state.messages]
- Accumulated facts: [Will be injected from state.context]
- Previous plan: [Will be injected from state.plan]

**Special Keywords:**
- "$user_key_word" - Use when you need additional information from user
- "$cancel_key_word" - Use when user wants to cancel the operation
- "$terminate_key_word" - Use when the task is complete

**Examples:**
[Include 2-3 example inputs and outputs]
```

### 2. Validator Node Prompt (for Builder)

**Purpose:** Guide LLM to produce validatable output

```
IMPORTANT: Your response must be PURE JSON with no additional text.

Do NOT include:
- Explanations before or after the JSON
- Markdown code fences (```json)
- Comments within the JSON
- Any text outside the JSON structure

CORRECT Response:
{"steps": [{"agent": "booking_agent", "task": "Search flights", "done": false}]}

INCORRECT Responses:
Here's the plan: {"steps": [...]}  ❌ (has text before JSON)
```json\n{"steps": [...]}```  ❌ (has markdown)
{"steps": [...]} // This is the plan  ❌ (has comments)

If you need to explain your reasoning, include it in a dedicated field:
{"steps": [...], "reasoning": "Explanation here"}
```

### 3. Reviewer Node (Validation)

**Purpose:** Validate outputs from builder nodes

```
You are a strict reviewer for [NODE_TYPE] outputs. Your role is to ensure quality and correctness.

**Review Criteria:**
1. **Structural Validity:** Check JSON structure is correct
2. **Completeness:** Verify all required fields are present
3. **Logic:** Ensure the plan/output makes sense for the given task
4. **Specificity:** Confirm tasks are concrete and actionable

**Response Format:**
If APPROVED: "[APPROVED]"
If REJECTED: "[REJECTED] Reason: [specific error description]"

**What to Check:**
- [ ] Valid JSON syntax
- [ ] All required fields present
- [ ] Field types match schema
- [ ] Tasks are specific and actionable
- [ ] Agents are assigned correctly
- [ ] Logic flows correctly

**Previous Output to Review:**
[Will be injected from state.node_messages]

Be thorough but fair. Only reject if there are real problems.
```

### 4. Router Node (Decision Making)

**Purpose:** Decide next node based on state analysis

```
You are a routing decision maker. Analyze the current state and decide the next action.

**Your Task:**
Based on the conversation and current state, decide where to route next.

**Available Routes:**
$available_routes

**Decision Criteria:**
- If [CONDITION_1], route to [DESTINATION_1]
- If [CONDITION_2], route to [DESTINATION_2]
- Default: [DEFAULT_DESTINATION]

**Response Format (STRICT JSON):**
{
  "next_agent": "agent_name or END",
  "reason": "Brief explanation of routing decision"
}

**Current State:**
- Conversation: [From state.messages]
- Context: [From state.context]
- Plan: [From state.plan]
- Progress: [From state tracking fields]

**Special Cases:**
- If task is complete: {"next_agent": "END", "reason": "Task completed"}
- If need user input: {"next_agent": "END", "reason": "Awaiting user response"}
- If error occurred: {"next_agent": "context", "reason": "Error recovery"}
```

### 5. Analyzer Node (Extraction/Analysis)

**Purpose:** Extract information or analyze content

```
You are a [DOMAIN] analyst. Extract key information from the conversation.

**Your Task:**
Analyze the conversation and extract [SPECIFIC_INFO].

**Output Format (STRICT JSON):**
{
  "extracted_facts": ["fact1", "fact2", "fact3"],
  "key_entities": {"entity_type": ["entity1", "entity2"]},
  "intent": "primary user intent",
  "confidence": 0.0-1.0
}

**Analysis Guidelines:**
1. Focus on factual information, not assumptions
2. Extract entities with their types (person, place, date, etc.)
3. Identify primary user intent
4. Rate your confidence in the analysis

**Conversation to Analyze:**
[Will be injected from state.messages]

Be precise and comprehensive in your extraction.
```

### 6. Context Update Node

**Purpose:** Maintain accumulated facts/knowledge

```
You are a context manager. Your role is to update accumulated knowledge based on new information.

**Current Context:**
$current_context

**New Information:**
[From recent agent responses/actions]

**Your Task:**
1. Review new information
2. Extract new facts/insights
3. Update context by:
   - Adding new facts
   - Updating outdated facts
   - Removing contradictions

**Output Format (STRICT JSON):**
{
  "new_facts": ["new fact 1", "new fact 2"],
  "updated_facts": {"old_fact": "updated_fact"},
  "removed_facts": ["outdated fact"],
  "summary": "Brief summary of changes"
}

Keep context concise - focus on actionable facts.
```

---

## User Prompt Template Patterns

### Message History Injection

```python
async def llm_node(state: AgentState) -> Dict[str, Any]:
    """LLM node with proper message injection"""

    # Build context window
    system_prompt = read_system_prompt("node_name")
    context_window = [
        SystemMessage(content=system_prompt),
        SystemMessage(content=now_message()),  # Timestamp
    ] + state['messages']  # Conversation history

    response = await model.ainvoke(context_window)
    return {"messages": [response]}
```

### State Field Injection

```python
async def planning_node(state: AgentState) -> Dict[str, Any]:
    """Inject state fields into prompt"""

    # Build user prompt with state injection
    user_prompt = f"""
Current Context:
{json.dumps(state.get('context', []), indent=2)}

Previous Plan:
{state.get('plan', 'No plan yet')}

Latest Request:
{state['messages'][-1].content}

Generate updated plan based on the above.
"""

    context_window = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = await model.ainvoke(context_window)
    return {"messages": [response]}
```

### Conversation Window Management

```python
def get_conversation_window(
    messages: List[AnyMessage],
    window_size: int = 11,
    keep_system: bool = True
) -> List[AnyMessage]:
    """Maintain conversation window to prevent context overflow"""
    if len(messages) <= window_size:
        return messages

    if keep_system:
        # Keep first message (system) + last N messages
        return [messages[0]] + messages[-(window_size - 1):]
    else:
        # Just keep last N messages
        return messages[-window_size:]

# Usage
async def node_with_windowing(state: AgentState) -> Dict[str, Any]:
    windowed = get_conversation_window(state['messages'], window_size=11)

    context_window = [
        SystemMessage(content=system_prompt)
    ] + windowed

    response = await model.ainvoke(context_window)
    return {"messages": [response]}
```

---

## Approval/Rejection Token Pattern

### Token Definitions

```python
APPROVED_TOKEN = "[APPROVED]"
REJECTED_TOKEN = "[REJECTED]"
```

### In Prompts

```
**Review Decision:**
- If valid: Respond with exactly "[APPROVED]"
- If invalid: Respond with "[REJECTED] Reason: [specific error]"

Do not add any other text to your response.
```

### In Conditional Edges

```python
def approval_edge(approved_dest: str, rejected_dest: str) -> Callable:
    """Create conditional edge based on approval token"""
    def edge_fn(state: NodeState) -> str:
        last_message = state['node_messages'][-1].content
        return approved_dest if APPROVED_TOKEN in last_message else rejected_dest
    return edge_fn

# Usage
workflow.add_conditional_edges(
    "validator",
    approval_edge("output_node", "builder_node")
)
```

---

## Model Selection Guidelines

### Temperature Settings

```python
# Deterministic tasks (validation, routing, extraction)
deterministic_model = model.with_config(temperature=0.0)

# Creative tasks (generation, brainstorming)
creative_model = model.with_config(temperature=0.7)

# Balanced (most tasks)
balanced_model = model.with_config(temperature=0.3)
```

### Model Tiers

```python
# Fast model for simple tasks
fast_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
# Routing decisions, simple validations, extraction

# Balanced model for most tasks
balanced_model = ChatOpenAI(model="gpt-4o", temperature=0.3)
# Plan generation, analysis, context updates

# Powerful model for complex reasoning
powerful_model = ChatOpenAI(model="gpt-4o", temperature=0.7)
# Complex planning, multi-step reasoning
```

### Model Selection by Node Type

| Node Type | Recommended Model | Temperature | Reasoning |
|-----------|------------------|-------------|-----------|
| Builder | gpt-4o | 0.3-0.5 | Needs creativity + structure |
| Validator | gpt-4o-mini | 0.0 | Deterministic checking |
| Reviewer | gpt-4o | 0.0 | Accurate evaluation |
| Router | gpt-4o-mini | 0.0 | Simple decision making |
| Analyzer | gpt-4o | 0.0 | Precise extraction |
| Context Update | gpt-4o-mini | 0.0 | Factual updates |

---

## JSON Output Format Enforcement

### In Prompts

```
**CRITICAL: JSON Output Requirements**

Your response MUST be valid JSON. Follow these rules:

✓ CORRECT:
{"key": "value", "list": [1, 2, 3], "nested": {"inner": "value"}}

✗ INCORRECT:
- {"key": "value",}  // Trailing comma
- {"key": 'value'}  // Single quotes
- {key: "value"}  // Unquoted keys
- {"key": "value"} // Extra text here
- ```json {"key": "value"}```  // Markdown wrapper

If you need to include explanations, use a dedicated field:
{"result": "...", "explanation": "Your reasoning here"}
```

### Pydantic Models for Validation

```python
from pydantic import BaseModel, Field
from typing import List

class PlanStep(BaseModel):
    """Single step in execution plan"""
    agent: str = Field(..., description="Agent name")
    task: str = Field(..., min_length=10, description="Task description")
    done: bool = Field(default=False)

class PlanOutput(BaseModel):
    """Complete plan structure"""
    steps: List[PlanStep] = Field(..., min_items=1)
    reasoning: str = Field(default="", description="Optional reasoning")

# Usage in validation node
def validate_plan(content: str) -> PlanOutput:
    """Validate and parse plan JSON"""
    plan_obj = json.loads(content)
    return PlanOutput(**plan_obj)  # Raises ValidationError if invalid
```

---

## Error Message Templates

### Syntax Errors

```
[REJECTED] Invalid JSON syntax: {error_details}

Your response must be pure JSON. Common mistakes:
- Trailing commas: {"key": "value",} ❌
- Single quotes: {'key': 'value'} ❌
- Unquoted keys: {key: "value"} ❌

Please try again with valid JSON.
```

### Missing Fields

```
[REJECTED] Missing required fields: {missing_fields}

Required structure:
{
  "steps": [...],  // REQUIRED
  "reasoning": "..."  // OPTIONAL
}

Please include all required fields and try again.
```

### Business Logic Errors

```
[REJECTED] Logic error: {specific_issue}

Example:
- Task assigned to non-existent agent "unknown_agent"
- Available agents: booking_agent, gmail_agent, calendar_agent

Please fix the error and resubmit.
```

---

## Complete Example: Plan Builder Node

```
File: prompts/plan_builder.prompt

You are an expert task planning assistant for multi-agent orchestration.

**Your Role:**
Break down user requests into actionable steps, assigning each step to the appropriate specialist agent.

**Available Specialist Agents:**
$available_agents

**Output Format (STRICT JSON):**
{
  "steps": [
    {
      "agent": "agent_name",
      "task": "specific, actionable task description",
      "done": false
    }
  ]
}

**Requirements:**
1. Each step must be assigned to an available agent
2. Tasks must be specific and actionable
3. Steps should be in logical execution order
4. Output must be valid JSON (no comments, trailing commas, or markdown)

**Special Keywords:**
- "$user_key_word" - Use when you need more information from user
- "$cancel_key_word" - Detect when user wants to cancel
- "$terminate_key_word" - Detect when task is complete

**Current Context:**
Conversation: [From state.messages]
Previous Plan: $previous_plan
Accumulated Facts: $context

**Example:**
User: "Book me a flight to Paris and send confirmation email"
Output:
{
  "steps": [
    {"agent": "booking_agent", "task": "Search and book flight to Paris", "done": false},
    {"agent": "gmail_agent", "task": "Send booking confirmation email to user", "done": false}
  ]
}

Generate the plan now based on the conversation.
```

---

## Summary

**Key Principles:**
1. ✓ External `.prompt` files for maintainability
2. ✓ Placeholder substitution for reusability
3. ✓ Clear output format specifications
4. ✓ Approval/rejection tokens for validation
5. ✓ Model selection based on task complexity
6. ✓ JSON strictness enforcement
7. ✓ Helpful error messages for recovery

Use these templates as starting points, customizing for your specific graph requirements.
