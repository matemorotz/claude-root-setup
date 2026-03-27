---
name: mcp-integration
description: Set up MCP (Model Context Protocol) endpoints with proper authentication and standards. Use when creating or integrating MCP servers.
---

# MCP Integration Skill

This skill automates MCP server setup and integration following the project's established patterns and authentication standards.

## Context Import

Reference project MCP conventions:
@../../project.md

Follow master execution rules:
@../../CLAUDE_MASTER_RULES.md

## MCP System Overview

### Current MCP Infrastructure
- **Memory System MCP**: `/root/memory_system`
  - Port: 8001
  - Auth Header: `Authorization: Menycibu`
  - Operations: Memory CRUD, vector search, timeline tracking

- **MCP System Manager**: `/root/mcp-system-manager`
  - File upload service
  - System management tools

### Technology Stack
- FastAPI for API endpoints
- Azure Cosmos DB for storage
- HTTP streamable endpoints for agent integration
- Authentication: API key in Authorization header

## MCP Integration Workflow

### Phase 1: Deep Research and Planning

1. **Understand Agent-Centric Design**
   - Build for workflows, not just API endpoints
   - Think about task completion, not single operations
   - Design for limited context windows
   - Provide actionable error messages

2. **Study MCP Protocol**
   - Review official MCP documentation
   - Understand tool definitions and schemas
   - Learn request/response patterns
   - Study error handling conventions

3. **API Documentation Review**
   - Exhaustively review target API docs
   - Map API endpoints to MCP tools
   - Identify authentication requirements
   - Document rate limits and constraints

4. **Create Implementation Plan**
   - List all tools to implement
   - Define tool schemas (name, description, parameters)
   - Plan error handling strategy
   - Design workflow-oriented tool groupings

### Phase 2: Implementation

5. **Project Structure Setup**
```
mcp-server-name/
├── server.py              # Main MCP server
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── README.md             # Documentation
├── tools/                # Tool implementations
│   ├── __init__.py
│   ├── tool1.py
│   └── tool2.py
└── tests/                # Test suite
    └── test_server.py
```

6. **Core Infrastructure**
```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Authentication
def verify_auth(authorization: str = Header(None)):
    """Verify API key authentication"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")

    # Extract token (format: "Authorization: <token>")
    expected = "Menycibu"  # Use env var in production
    if authorization != expected:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    return True

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-server-name"}

# MCP tool endpoint template
@app.post("/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    params: dict,
    authorized: bool = Depends(verify_auth)
):
    """Execute MCP tool"""
    # Tool execution logic
    pass
```

7. **Tool Development**

**Tool Schema Template:**
```python
{
    "name": "tool_name",
    "description": "Clear description of what this tool does and when to use it",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
}
```

**Implementation Best Practices:**
- One tool = one clear workflow step
- Descriptive tool names (verb + noun)
- Comprehensive parameter descriptions
- Meaningful return values
- Consistent error messages

8. **Error Handling**
```python
from enum import Enum

class ErrorCode(Enum):
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"
    AUTH_FAILED = "auth_failed"
    RATE_LIMITED = "rate_limited"

def create_error_response(code: ErrorCode, message: str, suggestion: str = None):
    """Create actionable error response"""
    return {
        "error": {
            "code": code.value,
            "message": message,
            "suggestion": suggestion or "Please check your input and try again"
        }
    }
```

### Phase 3: Review and Refine

9. **Code Quality Review**
   - [ ] Follows project conventions (project.md)
   - [ ] Uses type hints consistently
   - [ ] Includes comprehensive error handling
   - [ ] Authentication properly implemented
   - [ ] Tools are workflow-oriented
   - [ ] Documentation is complete

10. **Testing**
```python
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_auth_required():
    response = client.post("/tools/some_tool")
    assert response.status_code == 401

def test_tool_execution():
    headers = {"Authorization": "Menycibu"}
    response = client.post(
        "/tools/some_tool",
        json={"param": "value"},
        headers=headers
    )
    assert response.status_code == 200
```

11. **Build and Run**
```bash
# Install dependencies
/root/venv_linux/bin/pip install -r requirements.txt

# Run tests
/root/venv_linux/bin/pytest tests/

# Start server
/root/venv_linux/bin/python server.py
```

### Phase 4: Integration

12. **Agent Integration**
```python
# In agent code
import requests

class MCPClient:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.headers = {"Authorization": auth_token}

    def call_tool(self, tool_name: str, params: dict):
        """Call MCP tool"""
        response = requests.post(
            f"{self.base_url}/tools/{tool_name}",
            json=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage in agent
mcp_client = MCPClient("http://localhost:8001", "Menycibu")
result = mcp_client.call_tool("search_memory", {"query": "user preferences"})
```

13. **Service Configuration**
```bash
# Systemd service (optional)
sudo nano /etc/systemd/system/mcp-server-name.service

[Unit]
Description=MCP Server Name
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mcp-server-name
ExecStart=/root/venv_linux/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## MCP Design Principles

### Build for Workflows
❌ Bad: `get_user()`, `update_email()`, `save_user()`
✅ Good: `update_user_email(user_id, new_email)` - Complete workflow

### Optimize for Limited Context
- Keep tool descriptions under 100 words
- Use clear, specific parameter names
- Return only essential information
- Provide follow-up tool suggestions

### Actionable Error Messages
❌ Bad: "Invalid input"
✅ Good: "Email format invalid. Expected: user@domain.com. Received: {input}"

### Natural Task Subdivisions
Group related tools logically:
- Memory operations: create, read, update, delete, search
- User management: register, authenticate, update_profile
- Data processing: upload, transform, export

## Project-Specific Patterns

### Authentication Standard
```python
# Always use this authentication pattern
def verify_auth(authorization: str = Header(None)):
    if authorization != "Menycibu":  # From project.md
        raise HTTPException(status_code=403, detail="Invalid credentials")
```

### Port Conventions
- Memory System: 8001
- Custom MCP Servers: 8002, 8003, etc.
- Check running services: `sudo netstat -tulpn | grep LISTEN`

### Health Check Standard
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "service-name",
        "version": "1.0.0"
    }
```

## Common MCP Patterns

### Memory MCP Pattern
Tools: create_memory, search_memory, update_memory, delete_memory, get_timeline

### File Operations MCP Pattern
Tools: upload_file, process_file, download_file, list_files

### Data Integration MCP Pattern
Tools: fetch_data, transform_data, sync_data, export_data

## Troubleshooting

### Port Conflicts
```bash
# Check port usage
sudo netstat -tulpn | grep :8001

# Kill process if needed
sudo kill -9 <PID>
```

### Authentication Issues
- Verify header format: `Authorization: Menycibu`
- Check environment variables loaded
- Test with curl:
```bash
curl -H "Authorization: Menycibu" http://localhost:8001/health
```

### Connection Issues
- Check service is running: `systemctl status mcp-service`
- Verify firewall rules
- Test locally first, then remote

## Example: Creating a New MCP Server

```bash
# 1. Create project structure
mkdir -p /root/mcp-new-service/{tools,tests}
cd /root/mcp-new-service

# 2. Create server.py (use template above)

# 3. Create requirements.txt
cat > requirements.txt <<EOF
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
EOF

# 4. Install dependencies
/root/venv_linux/bin/pip install -r requirements.txt

# 5. Create health check
# 6. Implement tools
# 7. Add authentication
# 8. Write tests
# 9. Start server

/root/venv_linux/bin/uvicorn server:app --host 0.0.0.0 --port 8002
```

## References

See also:
- `/root/memory_system` - Example MCP implementation
- `/root/mcp-system-manager` - System management MCP
- `project.md` - MCP conventions and standards
- Official MCP documentation: https://modelcontextprotocol.io
