#!/bin/bash
# Auto-start domain agents at session start (idempotent)

_start_agent() {
    local dir="$1" port="$2" name="$3"
    local venv_python
    venv_python="$(dirname "$dir")/venv/bin/python3"
    [ -f "$venv_python" ] || venv_python="python3"

    # Already running — skip
    curl -sf "http://127.0.0.1:$port/health" >/dev/null 2>&1 && return 0
    # Dir missing — skip
    [ -d "$dir" ] || return 0

    nohup bash -c "cd '$dir' && '$venv_python' -m uvicorn main:app --host 127.0.0.1 --port $port" \
        >"$dir/../${name}.log" 2>&1 &
    disown
}

_start_agent "/root/software/GoogleMCP/google_mcp_agent"       8091 "google_mcp"
_start_agent "/root/software/finance_domain/finance_mcp_agent" 8092 "finance_domain"
