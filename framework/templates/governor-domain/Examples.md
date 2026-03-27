# {{DOMAIN_NAME}} Examples

## Workflow Examples

### Example 1: Standard Task

**Scenario:** User requests a standard operation

**Input:**
```
User: "Please do task type 1"
```

**Governor Processing:**

1. **Context Extraction:**
   - Request type: task_type_1
   - Urgency: normal
   - Customer: identified

2. **Plan Generation:**
   ```json
   {
     "steps": [
       {"agent": "specialist_1", "task": "Execute task", "done": false}
     ]
   }
   ```

3. **Routing:**
   - Route to: `specialist_1`
   - Task: Execute task type 1

4. **Agent Execution:**
   - Tool used: `tool_a`
   - Result: Success

5. **Response:**
   - Format result for user
   - Return response

**Output:**
```
Task completed successfully. Result: ...
```

---

### Example 2: Multi-Step Workflow

**Scenario:** User requests operation requiring multiple agents

**Input:**
```
User: "Please do complex task"
```

**Governor Processing:**

1. **Context Extraction:**
   - Request type: complex_task
   - Requires: specialist_1, specialist_2

2. **Plan Generation:**
   ```json
   {
     "steps": [
       {"agent": "specialist_1", "task": "Step 1", "done": false},
       {"agent": "specialist_2", "task": "Step 2", "done": false}
     ]
   }
   ```

3. **Sequential Execution:**
   - Step 1: specialist_1 executes → done: true
   - Step 2: specialist_2 executes → done: true

4. **Aggregation:**
   - Combine results from both agents

**Output:**
```
Complex task completed.
Step 1 result: ...
Step 2 result: ...
```

---

### Example 3: Escalation

**Scenario:** Request exceeds authority

**Input:**
```
User: "Please do high-value operation"
```

**Governor Processing:**

1. **Context Extraction:**
   - Request type: high_value_operation
   - Value: exceeds threshold

2. **Escalation Check:**
   - Rule: Operations above $X require escalation
   - Action: Route to PARENT_GOVERNOR

3. **Escalation:**
   ```json
   {
     "escalate_to": "PARENT_GOVERNOR",
     "reason": "Value exceeds threshold",
     "context": {...}
   }
   ```

**Output:**
```
This request requires approval. Escalating to supervisor.
```

---

## Anti-Patterns

### DON'T: Infinite Loops

```
❌ Bad:
Step 1: Check status
Step 2: If not done, go to Step 1
```

```
✅ Good:
Step 1: Check status (max 3 retries)
Step 2: If still not done, escalate
```

### DON'T: Scope Creep

```
❌ Bad:
User: "Send email"
Agent: Sends email, then creates follow-up task, then schedules reminder...
```

```
✅ Good:
User: "Send email"
Agent: Sends email, terminates
```

### DON'T: Skip Validation

```
❌ Bad:
Receive input → Execute immediately
```

```
✅ Good:
Receive input → Validate → Confirm → Execute
```
