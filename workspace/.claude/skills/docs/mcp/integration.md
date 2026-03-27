# MCP Integration Standards

## Overview
Model Context Protocol (MCP) integration patterns and standards for the multi-agent system.

## Current MCP Services

### Memory System MCP
**Location**: `/root/memory_system`
**Port**: 8001
**Authentication**: `Authorization: Menycibu`

**Capabilities**:
- Memory CRUD operations
- Vector search with Azure Cosmos DB
- Timeline tracking for memory evolution
- Metadata-rich filtering

**Endpoints**:
```
POST /tools/create_memory
POST /tools/search_memory
POST /tools/update_memory
POST /tools/delete_memory
POST /tools/get_timeline
GET  /health
```

### MCP System Manager
**Location**: `/root/mcp-system-manager`
**Purpose**: File upload and system management
**Integration**: System-level operations

## Authentication Standard

### Required Header Format
```python
headers = {
    "Authorization": "Menycibu"
}
```

### Verification Pattern
```python
from fastapi import Header, HTTPException

def verify_auth(authorization: str = Header(None)):
    """Verify MCP authentication"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    if authorization != "Menycibu":
        raise HTTPException(
            status_code=403,
            detail="Invalid credentials"
        )

    return True
```

## MCP Client Pattern

### Standard Client Implementation
```python
import requests
from typing import Dict, Any, Optional

class MCPClient:
    """Standard MCP client for agent integration"""

    def __init__(self, base_url: str, auth_token: str = "Menycibu"):
        self.base_url = base_url
        self.headers = {"Authorization": auth_token}

    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call MCP tool with parameters.

        Args:
            tool_name: Name of the MCP tool
            params: Tool parameters

        Returns:
            Tool execution result

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}/tools/{tool_name}"

        try:
            response = requests.post(
                url,
                json=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise TimeoutError(f"MCP call to {tool_name} timed out")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"MCP call failed: {e.response.text}")

    def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
```

### Usage in Agents
```python
# Initialize MCP client
memory_client = MCPClient("http://localhost:8001")

# Use in agent
def query_memory(query: str) -> dict:
    """Query long-term memory"""
    result = memory_client.call_tool(
        "search_memory",
        {"query": query, "limit": 5}
    )
    return result
```

## MCP Server Pattern

### Standard Server Structure
```python
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import logging

app = FastAPI(title="MCP Server Name")
logger = logging.getLogger(__name__)

# Authentication
def verify_auth(authorization: str = Header(None)):
    if authorization != "Menycibu":
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return True

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mcp-server-name",
        "version": "1.0.0"
    }

# Tool Schema
class ToolParams(BaseModel):
    # Define parameters

# Tool Endpoint
@app.post("/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    params: Dict[str, Any],
    authorized: bool = Depends(verify_auth)
):
    """Execute MCP tool"""
    logger.info(f"Executing tool: {tool_name}")

    try:
        # Route to appropriate handler
        if tool_name == "tool_one":
            return handle_tool_one(params)
        elif tool_name == "tool_two":
            return handle_tool_two(params)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Tool not found: {tool_name}"
            )

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
```

## Tool Design Principles

### Workflow-Oriented Design
✅ **Good**: Complete workflows
```python
# Single tool completes entire workflow
@app.post("/tools/update_user_email")
async def update_user_email(user_id: str, new_email: str):
    # 1. Validate email format
    # 2. Check email not in use
    # 3. Update database
    # 4. Send confirmation email
    # 5. Log change
    return {"status": "success"}
```

❌ **Bad**: Fragmented operations
```python
# Multiple tools required for simple workflow
/tools/validate_email
/tools/check_duplicate
/tools/update_db
/tools/send_email
/tools/log_change
```

### Context-Optimized Descriptions
```python
{
    "name": "search_memory",
    "description": "Search long-term memory using vector similarity. Returns up to `limit` most relevant memories matching the query. Use for retrieving past conversations, decisions, or context.",
    "parameters": {
        "query": "Search query text",
        "limit": "Max results (default: 5)"
    }
}
```

### Actionable Error Messages
```python
def create_error_response(error_type: str, details: str) -> dict:
    """Create actionable error response"""
    suggestions = {
        "invalid_email": "Provide email in format: user@domain.com",
        "not_found": "Check user_id exists. Use /tools/list_users to see available IDs",
        "rate_limited": "Wait 60 seconds before retrying. Consider batching requests."
    }

    return {
        "error": {
            "type": error_type,
            "message": details,
            "suggestion": suggestions.get(error_type, "Check parameters and retry")
        }
    }
```

## Port Conventions

### Standard Port Assignments
- **8001**: Memory System MCP
- **8002**: Custom MCP Server 1
- **8003**: Custom MCP Server 2
- **8004+**: Additional MCP services

### Port Management
```bash
# Check port availability
sudo netstat -tulpn | grep :8001

# Find process using port
sudo lsof -i :8001

# Kill process if needed
sudo kill -9 <PID>
```

## Service Management

### Systemd Service Template
```ini
[Unit]
Description=MCP Server Name
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mcp-server-path
Environment="PYTHONPATH=/root/mcp-server-path"
ExecStart=/root/venv_linux/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Service Commands
```bash
# Create service
sudo nano /etc/systemd/system/mcp-server.service

# Enable and start
sudo systemctl enable mcp-server
sudo systemctl start mcp-server

# Check status
sudo systemctl status mcp-server

# View logs
sudo journalctl -u mcp-server -f

# Restart
sudo systemctl restart mcp-server
```

## Agent-MCP Integration

### Integration Pattern
```python
class AgentWithMCP:
    """Agent with MCP integration"""

    def __init__(self):
        self.memory_client = MCPClient("http://localhost:8001")

    def execute_with_memory(self, task: dict) -> dict:
        """Execute task with memory context"""
        # 1. Query relevant memories
        memories = self.memory_client.call_tool(
            "search_memory",
            {"query": task["description"], "limit": 3}
        )

        # 2. Include in context
        context = f"Relevant memories: {memories}\n\nTask: {task}"

        # 3. Execute with enriched context
        result = self.execute_task(context)

        # 4. Store decision in memory
        self.memory_client.call_tool(
            "create_memory",
            {
                "content": f"Task: {task}, Result: {result}",
                "metadata": {"type": "decision", "agent": "agent_name"}
            }
        )

        return result
```

### Error Handling
```python
def safe_mcp_call(client: MCPClient, tool: str, params: dict) -> Optional[dict]:
    """MCP call with error handling"""
    try:
        return client.call_tool(tool, params)
    except TimeoutError:
        logger.warning(f"MCP timeout for {tool}, using fallback")
        return None
    except Exception as e:
        logger.error(f"MCP call failed: {e}")
        return None
```

## Testing MCP Integration

### Unit Testing
```python
from unittest.mock import Mock, patch
import pytest

def test_mcp_client_call():
    """Test MCP client tool call"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "success"}

        client = MCPClient("http://localhost:8001")
        result = client.call_tool("test_tool", {})

        assert result["result"] == "success"
        mock_post.assert_called_once()
```

### Integration Testing
```python
import pytest
import subprocess
import time

@pytest.fixture
def mcp_server():
    """Start MCP server for testing"""
    process = subprocess.Popen([
        "/root/venv_linux/bin/uvicorn",
        "server:app",
        "--host", "127.0.0.1",
        "--port", "8001"
    ])

    time.sleep(2)  # Wait for startup
    yield process
    process.kill()

def test_mcp_integration(mcp_server):
    """Test actual MCP integration"""
    client = MCPClient("http://localhost:8001")

    # Health check
    assert client.health_check()

    # Tool call
    result = client.call_tool("search_memory", {"query": "test"})
    assert "results" in result
```

## Best Practices

### Security
✓ Always use authentication headers
✓ Never hardcode credentials (use env vars)
✓ Validate all input parameters
✓ Rate limit endpoints
✓ Log security events

### Performance
✓ Set appropriate timeouts
✓ Implement caching where applicable
✓ Use connection pooling
✓ Monitor response times
✓ Optimize database queries

### Reliability
✓ Implement health checks
✓ Use circuit breakers
✓ Retry with exponential backoff
✓ Graceful degradation
✓ Comprehensive logging

### Documentation
✓ Document all tools and parameters
✓ Provide usage examples
✓ Document error codes
✓ Keep API versioned
✓ Maintain changelog

## Troubleshooting

### Connection Issues
```bash
# Test MCP server reachable
curl http://localhost:8001/health

# Test with authentication
curl -H "Authorization: Menycibu" http://localhost:8001/health

# Check firewall
sudo ufw status
```

### Authentication Issues
```python
# Verify header format
headers = {"Authorization": "Menycibu"}  # Correct
headers = {"Authorization": "Bearer Menycibu"}  # Wrong for our system
```

### Performance Issues
```python
# Add timeouts
requests.post(url, json=params, timeout=10)

# Use connection pooling
session = requests.Session()
session.post(url, json=params)
```

## References

See also:
- `/root/memory_system` - Memory MCP implementation example
- `/root/mcp-system-manager` - System management MCP
- `docs/skills/mcp-integration.md` - MCP integration skill
- MCP Protocol docs: https://modelcontextprotocol.io
