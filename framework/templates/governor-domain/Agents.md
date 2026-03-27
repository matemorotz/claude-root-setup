# {{DOMAIN_NAME}} Agents

## Agent Index

| Agent | Purpose | MCP Tools | Status |
|-------|---------|-----------|--------|
| specialist_1 | Handle task type 1 | tool_a, tool_b | Active |
| specialist_2 | Handle task type 2 | tool_c | Active |

---

## Agent Details

### specialist_1

**Purpose:** Handle task type 1
**Location:** `./specialist_1/`
**MCP Tools:** tool_a, tool_b

**Capabilities:**
- Capability 1
- Capability 2

**Usage:**
```
Route when: User needs task type 1
Input: Task description
Output: Result
```

---

### specialist_2

**Purpose:** Handle task type 2
**Location:** `./specialist_2/`
**MCP Tools:** tool_c

**Capabilities:**
- Capability 1
- Capability 2

**Usage:**
```
Route when: User needs task type 2
Input: Task description
Output: Result
```

---

## Adding New Agents

1. Create agent directory: `mkdir agent_name`
2. Add `.governor/` folder with agent-specific config
3. Register in this file
4. Update `MCP.md` with required tools
5. Add examples to `Examples.md`
