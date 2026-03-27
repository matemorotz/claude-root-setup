# Claude Code JSON Schemas

**Version:** 1.0.0
**Purpose:** Standardized JSON structures for fractal orchestration system

---

## Overview

These schemas define the data structures used for communication between agents, hooks, and scripts in the fractal orchestration system.

### Schema Files

1. **context-analysis-output.schema.json** - Output from `analyze-context.py`
2. **execution-plan.schema.json** - Structured execution plans with haiku-optimized steps
3. **agent-communication.schema.json** - Inter-agent message protocol
4. **research-output.schema.json** - Research findings from ResearchAgent

---

## Usage

### In Python Scripts

```python
import json
import jsonschema

# Load schema
with open('.claude/schemas/context-analysis-output.schema.json') as f:
    schema = json.load(f)

# Validate data
data = {...}  # Your data
jsonschema.validate(instance=data, schema=schema)
```

### In Bash Hooks

```bash
# Validate JSON output using jq
cat output.json | jq --schema-file .claude/schemas/context-analysis-output.schema.json .
```

### In Agents

Agents receive and send messages conforming to these schemas. The `agent-communication.schema.json` defines the standard message envelope.

---

## Schema Versioning

All schemas include a `version` field following semantic versioning (MAJOR.MINOR.PATCH).

**Current Version:** 1.0.0

### Compatibility Rules

- **Patch updates (1.0.x):** Backward compatible bug fixes
- **Minor updates (1.x.0):** Backward compatible new features (optional fields)
- **Major updates (x.0.0):** Breaking changes (required field changes, removed fields)

---

## Adaptive Structures

These schemas support "adaptive" input/output by using:

1. **Optional Fields:** Most fields beyond required ones are optional
2. **Flexible Types:** Union types and `oneOf` for variant structures
3. **Extensible Metadata:** `metadata` objects allow custom fields
4. **Version Detection:** Schemas can evolve while maintaining backward compatibility

---

## Schema Details

### context-analysis-output.schema.json

**Purpose:** Output from context analysis script

**Required Fields:**
- `version` - Schema version
- `timestamp` - When analysis was performed
- `project` - Project metadata
- `state` - Current state
- `todos` - Tasks
- `relationships` - Dependencies

**Key Features:**
- Extracts seed rules from project context
- Identifies research needs
- Maps parent/child relationships

### execution-plan.schema.json

**Purpose:** Structured execution plans for agent orchestration

**Required Fields:**
- `version` - Schema version
- `plan_id` - Unique identifier
- `created` - Creation timestamp
- `project` - Project reference
- `context_summary` - High-level summary
- `sections` - Plan sections with steps

**Key Features:**
- Haiku-optimized steps with minimal context
- Parallel execution groups
- Per-step validation criteria
- Error handling strategies
- Progress tracking

### agent-communication.schema.json

**Purpose:** Inter-agent messaging protocol

**Required Fields:**
- `version` - Schema version
- `message_id` - Unique identifier
- `from_agent` - Sending agent
- `to_agent` - Receiving agent
- `message_type` - Type of message
- `timestamp` - Message timestamp
- `payload` - Message content

**Message Types:**
- `task_assignment` - Assign work to executor
- `task_result` - Return execution result
- `error_escalation` - Escalate errors to debugger
- `progress_update` - Report progress
- `context_request/response` - Request context data
- `plan_update` - Update execution plan
- `validation_request/response` - Validate outcomes

### research-output.schema.json

**Purpose:** Research findings structure

**Required Fields:**
- `version` - Schema version
- `research_id` - Unique identifier
- `created` - Research timestamp
- `topic` - Research topic metadata
- `findings` - Research results

**Key Features:**
- Official examples with source URLs
- Best practices with rationale
- Security considerations
- Performance tips
- Industry standards
- Integration notes

---

## Examples

### Context Analysis Output

```json
{
  "version": "1.0.0",
  "timestamp": "2025-12-15T14:30:00Z",
  "project": {
    "name": "peti",
    "type": "python",
    "location": "/root/software/peti",
    "tech_stack": ["FastAPI", "LangChain", "Azure Cosmos DB"],
    "architecture": "RAG system with vector search"
  },
  "state": {
    "status": "active",
    "current_focus": "Implementing PDF processing pipeline",
    "working_features": ["Document ingestion", "Vector embeddings"],
    "in_progress": ["Search optimization"],
    "blockers": []
  },
  "todos": {
    "high_priority": [
      {
        "id": "t1",
        "description": "Optimize embedding batch size",
        "status": "in_progress",
        "priority": "high"
      }
    ]
  },
  "relationships": {
    "parent_projects": [],
    "child_projects": [],
    "integrations": [
      {
        "name": "Azure Cosmos DB",
        "type": "database",
        "status": "active"
      }
    ]
  },
  "seed_rules": {
    "project_level": [
      {
        "name": "async_first",
        "description": "Use async/await for all I/O operations"
      }
    ]
  },
  "research_needs": [
    {
      "topic": "RAG best practices",
      "category": "best_practice",
      "priority": "high",
      "reason": "Need optimization strategies for embeddings"
    }
  ]
}
```

### Agent Communication

```json
{
  "version": "1.0.0",
  "message_id": "msg-001",
  "from_agent": "opus-planner",
  "to_agent": "haiku-executor",
  "message_type": "task_assignment",
  "timestamp": "2025-12-15T14:35:00Z",
  "correlation_id": "plan-001",
  "priority": "normal",
  "payload": {
    "step": {
      "step_id": "1.1",
      "action": "Create FastAPI endpoint for PDF upload",
      "agent_type": "haiku-executor",
      "model": "haiku",
      "context": {
        "files": [
          {
            "path": "/root/software/peti/app/main.py",
            "sections": ["imports", "router_setup"],
            "load_full": false
          }
        ],
        "inline_context": "Add POST /upload endpoint with file validation"
      },
      "expected_outcome": "Endpoint created and accepting PDF files"
    }
  },
  "metadata": {
    "plan_id": "plan-001",
    "section_id": "s1",
    "step_id": "1.1"
  }
}
```

---

## Validation Tools

### Install jsonschema

```bash
pip install jsonschema
```

### Validate from Command Line

```bash
# Using Python
python -m jsonschema -i data.json schema.json

# Using jq (if available)
jq --schema-file schema.json . < data.json
```

---

## Contributing

When adding new schemas:

1. Follow semantic versioning
2. Include complete `$schema`, `$id`, `title`, `description`, `version`
3. Use `definitions` for reusable types
4. Document required vs optional fields
5. Add examples to this README
6. Update version history

---

## Version History

### 1.0.0 (2025-12-15)
- Initial schema set
- context-analysis-output.schema.json
- execution-plan.schema.json
- agent-communication.schema.json
- research-output.schema.json
