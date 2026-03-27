# {{DOMAIN_NAME}} MCP Services

## Available MCP Servers

| Server | Purpose | Tools | Status |
|--------|---------|-------|--------|
| server_1 | Service 1 | tool_a, tool_b | Active |
| server_2 | Service 2 | tool_c | Active |

---

## Tool Reference

### server_1

**Purpose:** Provide service 1 capabilities

**Tools:**

#### tool_a
- **Description:** Does something
- **Parameters:** `param1` (required), `param2` (optional)
- **Returns:** Result object
- **Example:**
  ```json
  {"param1": "value1"}
  ```

#### tool_b
- **Description:** Does something else
- **Parameters:** `param1` (required)
- **Returns:** Result object

---

### server_2

**Purpose:** Provide service 2 capabilities

**Tools:**

#### tool_c
- **Description:** Does another thing
- **Parameters:** `param1` (required)
- **Returns:** Result object

---

## MCP Configuration

```json
{
  "mcpServers": {
    "server_1": {
      "command": "python",
      "args": ["-m", "server_1"],
      "env": {
        "API_KEY": "${SERVER_1_API_KEY}"
      }
    }
  }
}
```

---

## Adding New MCP Servers

1. Configure in project root `mcp_config.json`
2. Add credentials to `.env`
3. Document in this file
4. Update `Agents.md` with which agents use which tools
