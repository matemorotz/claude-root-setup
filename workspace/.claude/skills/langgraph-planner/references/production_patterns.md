# LangGraph Production Patterns

Real-world implementation patterns extracted from production codebases: CoreTeam, Fly Achensee, PETI, and Email Solver.

---

## Table of Contents

1. [Governor-Specialist Pattern (CoreTeam)](#governor-specialist-pattern-coreteam)
2. [Enhanced Governor with Dynamic Children (Fly Achensee)](#enhanced-governor-with-dynamic-children-fly-achensee)
3. [RAG Pipeline with Refinement Loop (PETI)](#rag-pipeline-with-refinement-loop-peti)
4. [Parallel Processing with Error Isolation (Email Solver)](#parallel-processing-with-error-isolation-email-solver)
5. [MCP Integration Patterns](#mcp-integration-patterns)
6. [Prompt Management Patterns](#prompt-management-patterns)
7. [Error Handling Strategies](#error-handling-strategies)

---

## Governor-Specialist Pattern (CoreTeam)

**Use When:** Multi-agent orchestration with centralized planning and context management

### Architecture

```
Team Graph (Root)
└── Governor Agent (Orchestrator)
    ├── Plan Node (Subgraph)
    │   ├── builder → syntax_check → reviewer → output
    │   └── Validates plan JSON structure
    ├── Context Node (Subgraph)
    │   └── Updates context with facts from specialist results
    ├── Next Node (Routing)
    │   └── Decides which specialist to call or END
    └── Specialist Agents (Children)
        ├── Booking Agent (ReAct with MCP tools)
        ├── Gmail Agent (ReAct with MCP tools)
        ├── Calendar Agent (ReAct with MCP tools)
        └── etc.
```

### State Schema Pattern

**Governor State (Parent):**
```python
from typing_extensions import TypedDict, Annotated
from typing import List, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class GovernorState(TypedDict):
    """Parent state - only messages visible to children"""
    messages: Annotated[List[AnyMessage], add_messages]
    context: List[Any]  # Facts extracted from conversation
    plan: str  # JSON string of execution plan
    last_context_message: int  # Pointer for context updates
```

**Plan Node State (Subgraph):**
```python
class PlanNodeState(TypedDict):
    # Inherited from parent
    messages: Annotated[List[AnyMessage], add_messages]
    context: List[Any]
    plan: str
    last_context_message: int

    # Local to this subgraph (isolated)
    node_messages: List[AnyMessage]  # Isolated conversation thread
    wrong_syntax_counter: int  # Retry tracking
    failed_review_counter: int  # Validation tracking
```

### Node Implementations

**Builder Node Pattern (LLM Generation):**
```python
async def _builder_node(self, state: PlanNodeState) -> Dict[str, Any]:
    """Generate plan using LLM"""
    model_context_window: List[AnyMessage] = [
        SystemMessage(content=self._builder_system_prompt),
        SystemMessage(content=now_message()),  # Timestamp for context
    ] + state['node_messages']

    response = await self._builder_model.ainvoke(model_context_window)
    return {"node_messages": state['node_messages'] + [response]}
```

**Syntax Check Node Pattern (Deterministic Validation):**
```python
def _syntax_check_node(self, state: PlanNodeState) -> Dict[str, Any]:
    """Validate JSON structure with error recovery"""
    def handle_error(content: str) -> Dict[str, Any]:
        if state["wrong_syntax_counter"] <= self._MAX_SYNTAX_ERRORS:
            return {
                "node_messages": state['node_messages'] +
                    [AIMessage(content=f"{self._REJECTED_TOKEN} {content}")],
                "wrong_syntax_counter": state["wrong_syntax_counter"] + 1
            }
        else:
            raise AgentException("Too many syntax errors in plan builder output.")

    try:
        # Validate JSON structure
        plan_obj = json.loads(state['node_messages'][-1].content)
        validated_plan = _planModel(plan_obj)  # Pydantic validation
        return {"node_messages": state['node_messages'] +
                [AIMessage(content=self._APPROVED_TOKEN)]}
    except json.JSONDecodeError as e:
        return handle_error(f"Your output is not valid JSON: {str(e)}")
    except ValidationError as e:
        return handle_error(f"Schema validation failed: {str(e)}")
```

**Output Node Pattern (State Extraction):**
```python
def _output_node(self, state: PlanNodeState) -> Dict[str, Any]:
    """Extract validated result to parent state"""
    # Last message approved by reviewer is at index -3
    # (message before [APPROVED] and reviewer decision)
    return {"plan": state['node_messages'][-3].content}
```

### Edge Configurations

**Approval Gate Pattern:**
```python
def _approved_edge(self, approved: str, rejected: str) -> Callable:
    """Create conditional edge based on approval token"""
    def edge_fn(state: PlanNodeState) -> str:
        last_message = state['node_messages'][-1].content
        return approved if self._APPROVED_TOKEN in last_message else rejected
    return edge_fn

# Usage in graph building
workflow.add_conditional_edges(
    self._SYNTAX_CHECK_NODE_NAME,
    self._approved_edge(self._REVIEWER_NODE_NAME, self._BUILDER_NODE_NAME)
)
```

**Routing to Children or END:**
```python
def _route_next(self, state: GovernorState) -> str:
    """Route to specialist agent or END"""
    agent_name, message = decode_next_from_state(state)

    if agent_name == "END":
        return "END"
    elif agent_name == "context":
        return "context"  # Update context before ending
    elif agent_name in self._children:
        return agent_name  # Route to specialist
    else:
        # Fallback: update context
        return "context"
```

### Compilation Pattern

```python
class GovernorAgent:
    def __init__(self, model, children: Dict[str, BaseCoreTeamAgent]):
        self.name = "governor_agent"
        self._children = children

        # Initialize subgraphs
        self._plan_node = PlanNode(model)
        self._context_node = ContextNode(model)

        # Build graph
        self.agent = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(GovernorState)

        # Add subgraph nodes
        workflow.add_node("plan", self._plan_node.node)
        workflow.add_node("context", self._context_node.node)
        workflow.add_node("next", self._next_node)

        # Add specialist children
        for child_name, child_agent in self._children.items():
            workflow.add_node(child_name, child_agent)

        # Edges
        workflow.add_edge(START, "init_state")
        workflow.add_edge("init_state", "plan")
        workflow.add_edge("plan", "next")

        # Conditional routing to children or context
        workflow.add_conditional_edges(
            "next",
            self._route_next,
            {
                **{name: name for name in self._children.keys()},
                "context": "context",
                "END": END
            }
        )

        # Context can either loop back to next or END
        workflow.add_conditional_edges("context", self._context_edge)

        return workflow.compile(name=self.name, checkpointer=True)
```

---

## Enhanced Governor with Dynamic Children (Fly Achensee)

**Enhancements over CoreTeam:**
1. Dynamic child registration (not hardcoded)
2. Improved logging and error handling
3. Minimal prompt support for token optimization
4. JSON extraction with markdown handling

### Dynamic Child Registration

```python
async def get_mcp_agents_for_governor(
    workflow: str,
    mcp_clients: Dict[str, BaseMCPClient]
) -> Dict[str, BaseCoreTeamAgent]:
    """Initialize agents dynamically based on available MCP tools"""
    agents = await initialize_mcp_agents(workflow, mcp_clients)

    return {
        agent_name: agent
        for agent_name, agent in agents.items()
        if agent is not None  # Only include successfully initialized agents
    }

# Usage
children = await get_mcp_agents_for_governor("customer_communication", mcp_clients)
governor = GovernorAgent(model, children=children)
```

### Enhanced JSON Extraction

**Handles markdown-wrapped JSON:**
```python
def extract_json_from_response(content: str) -> str:
    """Extract JSON from markdown code blocks or raw JSON"""
    # Try to extract from markdown code block
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # Try to find raw JSON object
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        return json_match.group(0)

    # Return as-is if no extraction succeeded
    return content

# Usage in syntax check
def _syntax_check_node(self, state: PlanNodeState) -> Dict[str, Any]:
    last_message_content = state['node_messages'][-1].content
    extracted_json = extract_json_from_response(last_message_content)

    try:
        plan_obj = json.loads(extracted_json)
        # ... validation
    except json.JSONDecodeError as e:
        # ... error handling
```

### Minimal Prompt Support

**Token optimization through prompt variants:**
```python
def load_prompt(
    node_name: str,
    workflow: str,
    use_minimal: bool = False,
    sub_dir: str = None,
    placeholders: Dict[str, str] = None
) -> str:
    """Load prompt with optional minimal variant"""
    base_name = f"{node_name}_minimal" if use_minimal else node_name
    prompt_path = Path(f"prompts/{workflow}/{sub_dir}/{base_name}.prompt")

    with open(prompt_path, 'r') as f:
        content = f.read()

    if placeholders:
        return Template(content).safe_substitute(placeholders)
    return content
```

---

## RAG Pipeline with Refinement Loop (PETI)

**Use When:** Question answering with document search and iterative refinement

### Architecture

```
START
  ↓
init_state
  ↓
load_kb_metadata  # Load knowledge base overview
  ↓
routing_node  # Decide: SEARCH or DIRECT
  ├─ DIRECT → answer_node → context_expander → END
  └─ SEARCH → search_documents
              ↓
          evaluate_results  # Check if sufficient
              ├─ SUFFICIENT → answer_node → context_expander → END
              └─ REFINE → search_documents  # Loop back (max 2 iterations)
```

### State Schema with Nested Metadata

```python
from typing import NotRequired

class ConversationState(TypedDict):
    """Complex state with nested structures"""
    # Core conversation
    messages: Annotated[List[AnyMessage], add_messages]

    # Knowledge base metadata (cached)
    kb_metadata: NotRequired[Dict[str, Any]]  # Loaded once, reused

    # Search context (accumulated)
    retrieved_docs: NotRequired[List[str]]
    expanded_context: NotRequired[str]

    # Routing decisions
    routing_decision: NotRequired[str]  # "SEARCH" or "DIRECT"

    # Quality metrics
    confidence_score: NotRequired[float]
    search_iteration: NotRequired[int]  # Track refinement loops

    # Token tracking (cumulative)
    tokens_used_this_turn: NotRequired[int]
    tokens_used_session: NotRequired[int]

    # Hidden state (internal tracking)
    _last_expansion_quality: NotRequired[float]
```

### Routing Pattern with Embedded JSON

**LLM generates routing decision in JSON within response:**
```python
async def routing_node(state: ConversationState) -> Dict[str, Any]:
    """Decide whether to search or answer directly"""
    prompt = f"""
Analyze the question and decide if document search is needed.

Response format:
ROUTING_DECISION: {{"decision": "SEARCH" or "DIRECT", "reason": "..."}}

Question: {state['messages'][-1].content}
KB Overview: {state.get('kb_metadata', {}).get('overview', '')}
"""

    response = await model.ainvoke([SystemMessage(content=prompt)])

    # Extract JSON from response
    decision_match = re.search(r'ROUTING_DECISION:\s*({.*?})', response.content, re.DOTALL)
    if decision_match:
        decision_obj = json.loads(decision_match.group(1))
        routing_decision = decision_obj['decision']
    else:
        routing_decision = "SEARCH"  # Fallback

    return {
        "messages": [response],
        "routing_decision": routing_decision
    }

# Conditional edge based on routing decision
def route_question_edge(state: ConversationState) -> Literal["search_documents", "answer_node"]:
    if state.get("routing_decision") == "SEARCH":
        return "search_documents"
    return "answer_node"
```

### Refinement Loop with Iteration Limit

```python
async def evaluate_results(state: ConversationState) -> Dict[str, Any]:
    """Evaluate if search results are sufficient"""
    docs = state.get('retrieved_docs', [])
    iteration = state.get('search_iteration', 0)

    # Max 2 refinement iterations
    if iteration >= 2:
        return {"routing_decision": "SUFFICIENT"}

    # LLM evaluates document quality
    prompt = f"""
Evaluate if these documents answer the question sufficiently.

Question: {state['messages'][-1].content}
Documents: {docs}

Response: {{"sufficient": true/false, "reason": "..."}}
"""

    response = await model.ainvoke([SystemMessage(content=prompt)])
    eval_obj = json.loads(extract_json_from_response(response.content))

    if eval_obj['sufficient']:
        return {"routing_decision": "SUFFICIENT"}
    else:
        return {
            "routing_decision": "REFINE",
            "search_iteration": iteration + 1
        }

# Conditional edge for refinement loop
def evaluate_results_edge(state: ConversationState) -> Literal["answer_node", "search_documents"]:
    if state.get("routing_decision") == "SUFFICIENT":
        return "answer_node"
    return "search_documents"  # Refine search
```

### Token Optimization Strategies

**1. KB Overview Caching (OPT 1.1):**
```python
async def load_kb_metadata(state: ConversationState) -> Dict[str, Any]:
    """Load once per session, reuse across turns"""
    if 'kb_metadata' in state and state['kb_metadata']:
        return {}  # Already loaded, no update

    # Fetch compressed KB overview
    overview = await fetch_kb_overview()  # ~500-800 tokens
    return {"kb_metadata": {"overview": overview}}
```

**2. Conversation History Windowing (OPT 1.3):**
```python
def get_conversation_window(messages: List[AnyMessage], window_size: int = 11) -> List[AnyMessage]:
    """Keep system message + last N messages"""
    if len(messages) <= window_size:
        return messages

    # System message + last (window_size - 1) messages
    return [messages[0]] + messages[-(window_size - 1):]

# Usage in nodes
async def answer_node(state: ConversationState) -> Dict[str, Any]:
    windowed_messages = get_conversation_window(state['messages'])
    response = await model.ainvoke(windowed_messages)
    return {"messages": [response]}
```

**3. Conditional Context Expansion (OPT 2.1):**
```python
async def context_expander(state: ConversationState) -> Dict[str, Any]:
    """Only expand on first turn or if quality is low"""
    if state.get('_last_expansion_quality', 0) > 0.8:
        return {}  # Skip expansion, quality is good

    # Expand context (expensive: ~2000 tokens)
    expanded = await expand_context(state)
    return {
        "expanded_context": expanded,
        "_last_expansion_quality": calculate_quality(expanded)
    }
```

---

## Parallel Processing with Error Isolation (Email Solver)

**Use When:** Processing multiple independent items where one failure shouldn't crash others

### Architecture

```python
import asyncio
from typing import List, Dict, Any

async def process_emails_parallel(
    emails: List[Dict],
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """Process emails in parallel with error isolation"""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(email: Dict) -> Dict[str, Any]:
        async with semaphore:
            try:
                result = await process_single_email(email)
                return {"email_id": email['id'], "status": "success", "result": result}
            except Exception as e:
                # Isolate error - log but don't propagate
                logger.error(f"Failed to process email {email['id']}: {e}")
                return {"email_id": email['id'], "status": "error", "error": str(e)}

    # Process all in parallel
    results = await asyncio.gather(
        *[process_one(email) for email in emails],
        return_exceptions=False  # Errors are handled inside process_one
    )

    return results
```

### State Extension Pattern

**Using a "bus" object for state extension:**
```python
class EmailProcessingBus:
    """Extends state without modifying LangGraph state schema"""
    def __init__(self):
        self.results: List[Dict] = []
        self.failed_count: int = 0
        self.success_count: int = 0

    def record_result(self, result: Dict):
        self.results.append(result)
        if result['status'] == 'success':
            self.success_count += 1
        else:
            self.failed_count += 1

    def get_summary(self) -> str:
        return f"Processed {self.success_count + self.failed_count} emails: {self.success_count} succeeded, {self.failed_count} failed"

# Usage in graph
async def process_emails_node(state: AgentState) -> Dict[str, Any]:
    bus = EmailProcessingBus()

    # Extract email list from state
    emails = extract_emails_from_messages(state['messages'])

    # Process in parallel
    results = await process_emails_parallel(emails)

    # Record in bus
    for result in results:
        bus.record_result(result)

    # Return summary to state
    summary_message = AIMessage(content=bus.get_summary())
    return {"messages": [summary_message]}
```

---

## MCP Integration Patterns

### Token Acquisition Pattern (Fly Achensee)

**Acquire tokens before agent initialization:**
```python
async def initialize_mcp_agents(
    workflow: str,
    mcp_clients: Dict[str, BaseMCPClient]
) -> Dict[str, BaseCoreTeamAgent]:
    """Initialize agents with pre-acquired MCP tokens"""

    # Acquire tokens first
    tokens = {}
    for client_name, client in mcp_clients.items():
        try:
            token = await client.acquire_token()
            tokens[client_name] = token
        except Exception as e:
            logger.error(f"Failed to acquire token for {client_name}: {e}")
            tokens[client_name] = None

    # Initialize agents with tokens
    agents = {}
    if tokens.get('tandemfligen'):
        agents['booking_agent'] = BookingAgent(
            model=model,
            tandemfligen_tools=await discover_tools(mcp_clients['tandemfligen'])
        )

    if tokens.get('gmail'):
        agents['gmail_agent'] = GmailAgent(
            model=model,
            gmail_tools=await discover_tools(mcp_clients['gmail'])
        )

    return agents
```

### Tool Discovery at Startup

**Discover MCP tools once, not per call:**
```python
async def discover_tools(mcp_client: BaseMCPClient) -> List[BaseTool]:
    """Discover available tools from MCP server"""
    tools_response = await mcp_client.call("tools/list", {})

    # Convert MCP tool definitions to LangChain tools
    tools = []
    for tool_def in tools_response['tools']:
        tool = create_tool_from_mcp_definition(tool_def)
        tools.append(tool)

    return tools

# Usage
booking_tools = await discover_tools(mcp_clients['tandemfligen'])
booking_agent = BookingAgent(model, booking_tools)
```

### ReAct Agent with MCP Tools

```python
from langgraph.prebuilt import create_react_agent

class BookingAgent(BaseCoreTeamAgent):
    def __init__(self, model: BaseChatModel, tandemfligen_tools: List[BaseTool]):
        super().__init__(agent_name="booking_agent", description="Handles flight bookings")

        system_prompt = read_system_prompt(self.agent_name)

        def _callable_prompt(state: CoreTeamState, config) -> List[AnyMessage]:
            return [SystemMessage(content=system_prompt)] + state["messages"]

        # Context window management hooks
        pre_model_hook, post_model_hook = cut_context_window_for_tool_agent(self.agent_name)

        self.agent = create_react_agent(
            model=model,
            name=self.agent_name,
            prompt=_callable_prompt,
            tools=tandemfligen_tools,
            pre_model_hook=pre_model_hook,
            post_model_hook=post_model_hook,
            version="v2"
        )
```

---

## Prompt Management Patterns

### External Prompt Files with Placeholders

**Prompt file structure:**
```
File: prompts/governor_graph/builder.prompt

You are an expert task planner for the $workflow workflow.

Your role:
- Analyze user requests
- Create execution plans in JSON format
- Assign tasks to appropriate agents

Available Agents:
$participants

Keywords:
- Use "$user_key_word" when you need user input
- Use "$cancel_key_word" when user wants to cancel
- Use "$terminate_key_word" when task is complete

Output Format (STRICT JSON):
{
  "steps": [
    {"agent": "agent_name", "task": "description", "done": false}
  ]
}

Current Context:
(will be injected from state.context)

Current Plan:
(will be injected from state.plan)
```

**Loading with substitution:**
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

# Usage
placeholders = {
    "workflow": "customer_communication",
    "participants": "\n".join([f"- {name}: {desc}" for name, desc in agents.items()]),
    "user_key_word": "[USER]",
    "cancel_key_word": "[CANCEL]",
    "terminate_key_word": "[TERMINATE]"
}

builder_prompt = read_system_prompt(
    "builder",
    sub_dir="governor_graph",
    placeholders=placeholders
)
```

### Approval/Rejection Token Pattern

**Tokens in prompts:**
```
If the plan is valid, respond with: [APPROVED]
If the plan is invalid, respond with: [REJECTED] followed by specific error details.
```

**Token checking in edges:**
```python
APPROVED_TOKEN = "[APPROVED]"
REJECTED_TOKEN = "[REJECTED]"

def _approved_edge(approved_dest: str, rejected_dest: str) -> Callable:
    def edge_fn(state: State) -> str:
        last_content = state['node_messages'][-1].content
        return approved_dest if APPROVED_TOKEN in last_content else rejected_dest
    return edge_fn
```

---

## Error Handling Strategies

### Retry Counter Pattern

**Max attempts with escalation:**
```python
def _validation_node(self, state: State) -> Dict[str, Any]:
    MAX_RETRIES = 3

    try:
        # Attempt validation
        validated = validate(state['node_messages'][-1].content)
        return {"node_messages": [..., AIMessage(content="[APPROVED]")]}

    except ValidationError as e:
        if state["retry_count"] < MAX_RETRIES:
            # Retry with feedback
            return {
                "node_messages": [..., AIMessage(content=f"[REJECTED] {e}")],
                "retry_count": state["retry_count"] + 1
            }
        else:
            # Escalate to parent
            raise AgentException(f"Max retries exceeded: {e}")
```

### Graceful Degradation

**Fallback paths:**
```python
async def llm_node_with_fallback(state: State) -> Dict[str, Any]:
    try:
        # Try primary model (powerful but expensive)
        response = await primary_model.ainvoke(messages)
        return {"messages": [response]}

    except Exception as e:
        logger.warning(f"Primary model failed: {e}, using fallback")

        try:
            # Fallback to secondary model (fast but less capable)
            response = await fallback_model.ainvoke(messages)
            return {"messages": [response]}

        except Exception as e2:
            logger.error(f"Both models failed: {e2}")
            # Return safe error message
            error_msg = AIMessage(content="I encountered an error processing your request. Please try again.")
            return {
                "messages": [error_msg],
                "error_count": state.get("error_count", 0) + 1
            }
```

### Error Isolation in Subgraphs

**Errors contained within subgraph:**
```python
class PlanNode:
    def build_graph(self):
        workflow = StateGraph(PlanNodeState)
        # ... add nodes ...

        # Wrap compilation with error handling
        try:
            compiled_graph = workflow.compile(name="plan_node")
            return compiled_graph
        except Exception as e:
            logger.error(f"Failed to compile plan_node: {e}")
            # Return dummy graph that returns error state
            return self._create_error_graph()

    def _create_error_graph(self):
        """Fallback graph that immediately returns error"""
        def error_node(state):
            return {
                "plan": "ERROR",
                "node_messages": [AIMessage(content="Plan generation unavailable")]
            }

        workflow = StateGraph(PlanNodeState)
        workflow.add_node("error", error_node)
        workflow.add_edge(START, "error")
        workflow.add_edge("error", END)
        return workflow.compile()
```

---

## Summary

These production patterns demonstrate:

1. **Governor-Specialist** - Centralized orchestration with subgraph isolation (CoreTeam)
2. **Dynamic Registration** - Runtime agent initialization based on available resources (Fly Achensee)
3. **RAG with Refinement** - Iterative search improvement with quality gates (PETI)
4. **Parallel Processing** - Error-isolated concurrent execution (Email Solver)
5. **MCP Integration** - Token acquisition, tool discovery, ReAct agents
6. **Prompt Externalization** - Template files with dynamic substitution
7. **Error Handling** - Retry counters, graceful degradation, error isolation

Use these patterns as starting points for your LangGraph implementations.
