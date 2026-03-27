# Approved Plans & Dangerous Skip Permissions

**Version:** 1.0.0
**Last Updated:** 2025-12-25
**Status:** Production Ready ✅

---

## Overview

The **Approved Plans** system allows you to pre-approve execution plans for **dangerouslySkipPermissions** mode, enabling autonomous execution without repeated permission prompts.

### When to Use

✅ **Use this when:**
- You've reviewed a plan and trust it completely
- You want autonomous execution without interruptions
- You're running repetitive, well-tested operations
- You want to execute plans overnight or unattended

❌ **DO NOT use when:**
- You haven't fully reviewed the plan
- The plan contains untested or experimental code
- You're working on production systems
- You're unsure about any step in the plan

---

## Quick Start

### 1. Review a Plan

```bash
# Generate or receive a plan
cat /root/software/.claude/plans/my-plan.json

# Review all steps carefully!
```

### 2. Approve the Plan

```bash
cd /root/software/.claude/scripts

# Approve for 24 hours (default)
python3 approve-plan.py /root/software/.claude/plans/my-plan.json

# Approve for 48 hours with note
python3 approve-plan.py /root/software/.claude/plans/my-plan.json \
    --expires 48h \
    --note "Reviewed and tested in dev environment"

# Approve for 7 days
python3 approve-plan.py /root/software/.claude/plans/my-plan.json \
    --expires 7d
```

### 3. Enable Dangerous Skip (One-Time Global Setting)

```bash
# Enable the feature globally
python3 approve-plan.py --enable-dangerous-skip

# WARNING: This allows approved plans to bypass sandbox!
```

### 4. Execute the Plan

Once enabled and approved, execution tools can check the approval status and use `dangerouslyDisableSandbox: true` automatically.

---

## How It Works

### Architecture

```
User reviews plan
    ↓
python approve-plan.py plan.json
    ↓
Plan added to approved_plans.json
    │
    ├─ Plan ID
    ├─ SHA256 hash (detects changes)
    ├─ Expiration timestamp
    └─ Approval note
    ↓
Execution engine checks approval
    ↓
If approved + feature enabled:
  → Use dangerouslyDisableSandbox: true
If not approved or expired:
  → Normal sandbox mode (ask permission)
```

### Security Features

1. **Content Hash Verification**
   - SHA256 hash computed when approving
   - Re-verified before each execution
   - Any change to plan invalidates approval

2. **Time-Based Expiration**
   - Default: 24 hours
   - Configurable per-approval
   - Prevents stale approvals

3. **Explicit Global Enable**
   - Feature must be globally enabled
   - Approval alone isn't enough
   - Two-step safety mechanism

4. **Audit Log**
   - All approvals logged
   - All revocations logged
   - Timestamped for tracking

---

## Usage Examples

### List All Approved Plans

```bash
python3 approve-plan.py --list
```

**Output:**
```
📋 Approved Plans:
================================================================================

🟢 plan-001
   Path: /root/software/.claude/plans/auth-implementation.json
   Hash: a1b2c3d4e5f6g7h8
   Approved: 2025-12-25T10:00:00Z
   Expires: 2025-12-26T10:00:00Z
   Status: Active (18.5h remaining)
   Note: Reviewed and tested

⏰ plan-002
   Path: /root/software/.claude/plans/old-plan.json
   Hash: x9y8z7w6v5u4t3s2
   Approved: 2025-12-20T10:00:00Z
   Expires: 2025-12-21T10:00:00Z
   Status: EXPIRED

🔴 plan-003
   Path: /root/software/.claude/plans/revoked-plan.json
   Hash: m1n2o3p4q5r6s7t8
   Approved: 2025-12-24T10:00:00Z
   Expires: 2025-12-25T10:00:00Z
   Status: Revoked
```

### Revoke a Plan

```bash
# Revoke approval
python3 approve-plan.py --revoke plan-001

# Plan is immediately revoked, even if not expired
```

### Check Feature Status

```bash
# View current settings
cat /root/.claude/settings.json | grep -A 10 fractal
```

**Output:**
```json
"fractal": {
  "approvedPlans": {
    "enabled": false,
    "dangerouslySkipPermissions": false,
    "registryPath": "/root/software/.claude/approved_plans.json"
  }
}
```

### Disable Dangerous Skip

```bash
# Disable globally (safest)
python3 approve-plan.py --disable-dangerous-skip

# Approvals remain, but won't bypass sandbox
```

---

## Configuration

### Settings Location

**User Settings:** `/root/.claude/settings.json`

```json
{
  "fractal": {
    "approvedPlans": {
      "enabled": false,                  // Enable approved plans feature
      "registryPath": "/root/software/.claude/approved_plans.json",
      "dangerouslySkipPermissions": false, // Allow bypassing sandbox
      "requireExplicitApproval": true,   // Require explicit approval
      "autoExpireHours": 24,             // Default expiration
      "warnOnExpiredPlans": true         // Warn about expired plans
    }
  }
}
```

### Registry Location

**Registry File:** `/root/software/.claude/approved_plans.json`

```json
{
  "version": "1.0.0",
  "approved_plans": {
    "plan-001": {
      "plan_id": "plan-001",
      "plan_path": "/root/software/.claude/plans/my-plan.json",
      "plan_hash": "a1b2c3d4e5f6g7h8",
      "approved_at": "2025-12-25T10:00:00Z",
      "expires_at": "2025-12-26T10:00:00Z",
      "expires_hours": 24,
      "note": "Reviewed and tested",
      "status": "active"
    }
  },
  "settings": {
    "enable_dangerous_skip": false,
    "require_explicit_approval": true,
    "auto_expire_hours": 24
  },
  "audit_log": [
    {
      "action": "approve",
      "plan_id": "plan-001",
      "timestamp": "2025-12-25T10:00:00Z",
      "expires_hours": 24,
      "note": "Reviewed and tested"
    }
  ]
}
```

---

## Integration with Execution

### In Execute-Plan Script

```python
#!/usr/bin/env python3
from pathlib import Path
import json
import sys

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
from approve_plan import PlanApprovalManager

def execute_plan(plan_path: Path):
    """Execute a plan with approval check"""

    # Load settings
    with open("/root/.claude/settings.json") as f:
        settings = json.load(f)

    dangerous_skip_enabled = settings.get("fractal", {}).get(
        "approvedPlans", {}
    ).get("dangerouslySkipPermissions", False)

    if not dangerous_skip_enabled:
        print("ℹ️  Dangerous skip disabled - using normal sandbox mode")
        use_dangerous_skip = False
    else:
        # Check if plan is approved
        manager = PlanApprovalManager()

        with open(plan_path) as f:
            plan_content = f.read()
            plan = json.loads(plan_content)

        plan_id = plan.get("plan_id")
        is_approved = manager.is_plan_approved(plan_id, plan_content)

        if is_approved:
            print(f"✅ Plan approved: {plan_id}")
            print("   Using dangerouslyDisableSandbox: true")
            use_dangerous_skip = True
        else:
            print(f"⚠️  Plan NOT approved: {plan_id}")
            print("   Using normal sandbox mode")
            use_dangerous_skip = False

    # Execute with appropriate mode
    execute_with_mode(plan, use_dangerous_skip)
```

### In Bash Tool Calls

```python
# When calling Bash tool
bash_params = {
    "command": "npm install",
    "description": "Install dependencies"
}

# If plan is approved and feature enabled:
if use_dangerous_skip:
    bash_params["dangerouslyDisableSandbox"] = True

# Execute
tool_use("Bash", bash_params)
```

---

## Workflow Example

### Complete Approval → Execution Flow

```bash
# 1. Generate a plan (via OpusPlanner or manually)
cat > /tmp/my-implementation-plan.json <<EOF
{
  "plan_id": "implement-auth",
  "version": "1.0.0",
  "project": "myapp",
  "sections": [...]
}
EOF

# 2. Review the plan thoroughly
cat /tmp/my-implementation-plan.json
# READ EVERY STEP CAREFULLY!

# 3. Approve the plan
python3 /root/software/.claude/scripts/approve-plan.py \
    /tmp/my-implementation-plan.json \
    --expires 48h \
    --note "Reviewed all steps, tested in dev"

# Output:
# ✅ Plan approved: implement-auth
#    Hash: a1b2c3d4
#    Expires: 2025-12-27T10:00:00 UTC
#    Duration: 48 hours
#
# ⚠️  WARNING:
#    This plan can now execute Bash commands without sandboxing!
#    To enable this feature, run:
#    python approve-plan.py --enable-dangerous-skip

# 4. Enable dangerous skip (one-time, if not already enabled)
python3 /root/software/.claude/scripts/approve-plan.py \
    --enable-dangerous-skip

# Output:
# ⚠️  Dangerous skip ENABLED
#    Approved plans can now bypass sandbox restrictions

# 5. Execute the plan
python3 /root/software/.claude/scripts/execute-plan.py \
    /tmp/my-implementation-plan.json

# Output:
# ✅ Plan approved: implement-auth
#    Using dangerouslyDisableSandbox: true
# [Execution proceeds without permission prompts]

# 6. After completion, revoke or let expire
python3 /root/software/.claude/scripts/approve-plan.py \
    --revoke implement-auth
```

---

## Security Best Practices

### ✅ DO:

1. **Review every step** before approving
2. **Test in dev environment** first
3. **Use short expiration times** (24-48h)
4. **Add descriptive notes** to approvals
5. **Revoke immediately** after completion
6. **Disable feature** when not actively using
7. **Check audit log** regularly

### ❌ DON'T:

1. **Don't approve without reading** the entire plan
2. **Don't use long expiration times** (>7 days)
3. **Don't leave feature enabled** permanently
4. **Don't approve plans with secrets** or credentials
5. **Don't share approved plans** between systems
6. **Don't ignore hash mismatch warnings**

---

## Troubleshooting

### Plan Not Being Recognized as Approved

```bash
# Check if plan is in registry
python3 approve-plan.py --list

# Check if feature is enabled
cat /root/.claude/settings.json | grep dangerouslySkip

# Check plan hash matches
# (Plan content changed after approval invalidates it)
```

### Hash Mismatch Warning

If you see:
```
⚠️  Plan content changed! Hash mismatch.
   Expected: a1b2c3d4
   Got: x9y8z7w6
```

**Solution:**
1. Review what changed in the plan
2. If changes are safe, re-approve:
   ```bash
   python3 approve-plan.py /path/to/plan.json
   ```

### Expired Approval

```bash
# Check expiration
python3 approve-plan.py --list

# Re-approve if still needed
python3 approve-plan.py /path/to/plan.json --expires 24h
```

---

## Audit and Monitoring

### View Audit Log

```bash
# View all approval/revocation events
cat /root/software/.claude/approved_plans.json | jq '.audit_log'
```

**Output:**
```json
[
  {
    "action": "approve",
    "plan_id": "implement-auth",
    "timestamp": "2025-12-25T10:00:00Z",
    "expires_hours": 24,
    "note": "Reviewed and tested"
  },
  {
    "action": "revoke",
    "plan_id": "implement-auth",
    "timestamp": "2025-12-25T20:00:00Z"
  }
]
```

### Clean Up Expired Plans

```python
# Add to cron or run periodically
python3 -c "
import json
from datetime import datetime
from pathlib import Path

registry_path = Path('/root/software/.claude/approved_plans.json')
with open(registry_path) as f:
    registry = json.load(f)

now = datetime.utcnow()
expired = []

for plan_id, approval in registry['approved_plans'].items():
    expires_at = datetime.fromisoformat(approval['expires_at'].replace('Z', ''))
    if now > expires_at:
        expired.append(plan_id)

for plan_id in expired:
    del registry['approved_plans'][plan_id]

with open(registry_path, 'w') as f:
    json.dump(registry, f, indent=2)

print(f'Cleaned up {len(expired)} expired plans')
"
```

---

## Summary

The Approved Plans system provides:

✅ **Safety** - Hash verification, expiration, audit log
✅ **Convenience** - Autonomous execution without prompts
✅ **Control** - Explicit approval, revocation, global toggle
✅ **Transparency** - Full audit trail, status visibility

**Use responsibly!** This feature bypasses important safety mechanisms.

---

**Related Documentation:**
- `/root/software/.claude/plan.md` - General planning guide
- `/root/software/.claude/fractal/COMPLETE_WORKFLOW_GUIDE.md` - Fractal workflow
- `/root/software/.claude/scripts/execute-plan.py` - Execution engine
