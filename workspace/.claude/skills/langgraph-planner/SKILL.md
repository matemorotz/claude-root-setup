---
name: langgraph-planner
description: Interactive LangGraph planning assistant for rigorous graph architecture design. Use when planning new LangGraph agents, multi-agent systems, or complex workflows. Supports governor-specialist pattern, standalone workflows, and custom archetypes. Guides through 11-phase workflow with progressive disclosure for token efficiency. Enforces LangGraph best practices, simplicity-first principle, safety analysis, and mock testing.
---

# LangGraph Planner

**Rigorous, interactive planning for LangGraph agent architectures with progressive disclosure**

## When to Use This Skill

Use this skill when:
- **Planning new LangGraph graphs** (governor-specialist, standalone, custom)
- **Designing multi-agent systems** with orchestration and specialists
- **Building reusable archetypes** for similar future projects
- **Generating production-ready code** with validation and testing

**Note:** This skill uses progressive disclosure - load phase-specific references as you work through each phase for optimal token efficiency.

---

## How It Works: 11-Phase Workflow

Each phase builds on the previous. Load the detailed reference file when starting each phase.

| Phase | Name | Goal | Load Reference |
|-------|------|------|----------------|
| 1 | **Complexity Analysis** | Understand purpose, scope, architecture type | `@references/phase1_complexity_analysis.md` |
| 2 | **Nodes/Edges/State** | Define graph structure with node types, flow, state schema | `@references/phase2_nodes_edges_state.md` |
| 3 | **Node I/O** | Specify precise inputs/outputs for every node | `@references/phase3_node_io.md` |
| 4 | **Conditional Edges** | Design routing logic with termination validation | `@references/phase4_conditional_edges.md` |
| 5 | **LLM Prompts** | Plan all system and user prompts in execution order | `@references/phase5_llm_prompts.md` |
| 6 | **State Evolution** | Trace state changes through example scenario | `@references/phase6_state_evolution.md` |
| 7 | **Archetype Generation** | Extract and save reusable graph pattern | `@references/phase7_archetypes.md` |
| 8 | **Code Generation** | Generate production-ready, well-structured code | `@references/phase8_code_generation.md` |
| 9 | **Structure Check** | Verify completeness, complexity, logic control | `@references/phase9_structure_check.md` |
| 10 | **Safety Analysis** | Analyze termination, errors, resources, security | `@references/phase10_safety_analysis.md` |
| 11 | **Mock Testing** | Generate test framework with mock API responses | `@references/phase11_mock_testing.md` |

**Workflow:** Start Phase 1 → Load its reference → Complete phase → Move to next → Load next reference

---

## Supported Architectures

### 1. Governor-Specialist Pattern
**From:** CoreTeam, Fly Achensee (production)
**Use When:** Multi-agent orchestration with centralized planning

**Structure:**
```
Governor (Orchestrator)
├── Plan Subgraph - Generate/validate execution plans
├── Context Subgraph - Accumulate facts and learnings
├── Next Subgraph - Route to appropriate specialist
└── Specialist Agents - Domain-specific tasks (email, booking, etc.)
```

**Details:** `@references/production_patterns.md` (Governor-Specialist section)

### 2. Standalone Workflow Pattern
**From:** PETI, general-purpose workflows
**Use When:** Focused single-purpose tasks, no orchestration

**Structure:** Linear or branching flow (START → init → process → validate → END)

**Details:** `@references/production_patterns.md` (Standalone Workflow section)

### 3. RAG Pipeline Pattern
**From:** PETI 9-node conversation graph
**Use When:** Question answering with document search and refinement

**Structure:** Router → Search/Direct → Evaluate → (Refine loop) → Answer

**Details:** `@references/production_patterns.md` (RAG Pipeline section)

### 4. Parallel Processor Pattern
**From:** Email Solver (production)
**Use When:** Batch processing with error isolation

**Structure:** Init → Parallel Processing (semaphore-controlled) → Summarize

**Details:** `@references/production_patterns.md` (Parallel Processor section)

### 5. Custom Archetypes
**Load saved patterns from archetype library**
- See: `@assets/archetypes/` for available patterns
- Can build and save new archetypes (Phase 7)

---

## Enforcement Features

**Automatically enforced during planning:**
- ✓ **Termination patterns** - Every conditional path routes to END
- ✓ **JSON I/O strictness** - TypedDict + Pydantic validation
- ✓ **State isolation** - Parent routing, subgraph working state
- ✓ **Error handling** - Retry counters, max iteration limits
- ✓ **Async patterns** - LLM nodes use `await`, validation is sync
- ✓ **Prompt externalization** - `.prompt` files with placeholders
- ✓ **Message reducers** - `Annotated[list, add_messages]` pattern
- ✓ **Safety analysis** - 5-dimension scoring (termination, errors, resources, validation, security)
- ✓ **Mock testing** - Test framework generated before production

---

## Knowledge Base

Load these references as needed during planning:

**Core LangGraph Theory:**
- `@references/LANGGRAPH_KNOWLEDGE_BASE.md` - Complete LangGraph patterns (1,165 lines)
  - Core concepts, state management, subgraphs, termination
  - Common pitfalls, performance optimization

**Production Patterns:**
- `@references/production_patterns.md` - Real implementations
  - CoreTeam governor pattern
  - Fly Achensee enhancements
  - PETI RAG pipeline
  - Email Solver parallel processing

**Specialized Guides:**
- `@references/prompt_engineering.md` - Prompt design templates
- `@references/validation_patterns.md` - Validation strategies

**Phase-Specific (load sequentially):**
- `@references/phase1_complexity_analysis.md` through `phase11_mock_testing.md`

---

## Archetypes Library

**Pre-built patterns ready to use:**
- `@assets/archetypes/governor_specialist.json` - Multi-agent orchestrator
- `@assets/archetypes/standalone_workflow.json` - Simple linear/branching flow
- `@assets/archetypes/rag_pipeline.json` - Search → Evaluate → Refine
- `@assets/archetypes/parallel_processor.json` - Concurrent batch processing

**How to use:**
1. Load archetype JSON in Phase 1 when selecting architecture
2. Customize for your specific use case in Phases 2-6
3. Save your customized pattern as new archetype in Phase 7

---

## Validation Scripts

**Run after code generation (Phase 8):**

```bash
# Navigate to skill directory
cd /root/software/.claude/skills/langgraph-planner

# Validate state schema structure
python scripts/validate_state.py <your_plan.json>

# Check termination paths (CRITICAL)
python scripts/validate_termination.py <your_plan.json>

# Detect potential infinite loops
python scripts/check_loops.py <your_plan.json>

# Enforce JSON I/O consistency
python scripts/validate_json.py <your_plan.json>

# Comprehensive structure check (Phase 9)
python scripts/check_structure.py <your_plan.json>

# Safety analysis (Phase 10)
python scripts/analyze_safety.py <your_plan.json>

# Generate mock tests (Phase 11)
python scripts/create_mock_tests.py <your_plan.json>
```

**Pass all validations before deploying to production.**

---

## Code Generation Output

**Generated structure (Phase 8):**
```
src/agents/{graph_name}_graph/
├── common.py              # State TypedDict schemas
├── {graph_name}_agent.py  # Main graph class with _build_graph()
├── {node}_node.py         # Node/subgraph implementations
├── routing.py             # Conditional edge routing functions
├── validation.py          # Pydantic models for JSON validation
└── prompts/               # External .prompt files for LLM nodes
    ├── builder.prompt
    ├── reviewer.prompt
    └── router.prompt
```

**Code characteristics:**
- Human-readable with clear structure
- Type hints throughout (Python)
- TODOs mark customization points
- Comments explain solution choices
- Production patterns from real agents
- Ready to run after prompt customization

---

## Best Practices Enforced

**From LangGraph documentation + production implementations:**

**State Management:**
- Parent state for routing decisions
- Subgraph local state for working memory
- Reducers for list accumulation (`add_messages`)
- NotRequired for optional conditional fields

**Termination:**
- Multi-layer checks (completion flags, iteration counters, error limits)
- Every conditional edge has route to END
- Safety limits prevent infinite loops
- Graceful degradation on errors

**Performance:**
- Async LLM calls (`ainvoke` not `invoke`)
- Simple routing functions (no heavy computation)
- Message pruning for context window management
- External prompts for easy iteration

**Error Handling:**
- Try/except wrappers in LLM nodes
- Retry logic with max attempt limits
- Error count tracking in state
- Fallback strategies for validation failures

---

## Example Session (Condensed)

```
User: I need a graph for email triage and auto-response

Skill: Starting Phase 1: Complexity Analysis
       Load: @references/phase1_complexity_analysis.md

       Questions:
       1. Primary purpose? → Auto-triage incoming emails by urgency
       2. Main tasks? → Extract info, classify priority, draft responses
       3. Architecture type? → Standalone workflow (no orchestration needed)
       4. External systems? → Gmail API (MCP tool)
       5. Complexity? → Medium (5-7 nodes)

       Recommendation: Standalone Workflow Pattern
       Archetype: Use rag_pipeline.json as template (analyze → classify → route)

Phase 2-6: [Design nodes, I/O, edges, prompts, trace state changes]

Phase 7: Archetype Generation
         Saved: email_triage_standalone.json
         Can reuse for similar email processing tasks

Phase 8: Code Generation
         Generated: src/agents/email_triage_graph/
         Files: common.py, email_triage_agent.py, analyze_node.py,
                classify_node.py, routing.py, validation.py, prompts/

Phase 9-11: [Structure check, safety analysis, mock tests generated]

Result: ✓ Production-ready code
        ✓ All validations passed
        ✓ Mock tests created
        ✓ Archetype saved for reuse

Next: Customize prompts in prompts/ directory, run mock tests
```

---

## Progressive Disclosure Benefits

**Token Efficiency:**
- Initial load: ~10K tokens (this SKILL.md overview)
- Per-phase load: ~2-5K tokens (only active phase details)
- **50-60% reduction** vs loading all 11 phases at once

**User Experience:**
- Clear "what to load when" instructions
- No cognitive overload from seeing all phases
- Sequential flow matches mental model

**Maintainability:**
- Easy to update individual phases
- Add new phases without bloating main file
- Each phase file self-contained and testable

---

## Quick Start

1. **Load Phase 1:** `@references/phase1_complexity_analysis.md`
2. **Answer questions** about your graph purpose and scope
3. **Follow sequential workflow** through phases 2-11
4. **Load each phase reference** when starting that phase
5. **Run validations** after code generation (phases 8-11)
6. **Customize prompts** in generated `prompts/` directory
7. **Test with mocks** before production deployment

---

## Integration Points

**Load these for deeper understanding:**
- **LangGraph theory:** `@references/LANGGRAPH_KNOWLEDGE_BASE.md`
- **Production examples:** `@references/production_patterns.md`
- **Prompt design:** `@references/prompt_engineering.md`
- **Validation strategies:** `@references/validation_patterns.md`

**Phase-specific details:**
- Load `@references/phaseN_*.md` when starting Phase N
- Each phase file includes: goal, process, templates, pitfalls, checklist
- Navigation links guide you to next phase

---

**Ready to plan a new LangGraph agent? Start with Phase 1!**
`@references/phase1_complexity_analysis.md`
