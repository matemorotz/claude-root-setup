# Autonomous Execution Workflow

**Version:** 1.0.0
**Last Updated:** 2025-12-25
**Principle:** After plan approval, execute autonomously without user interruption

---

## Core Principle

```
Plan Mode (Interactive)
    ↓ User reviews and approves
Execution Mode (Autonomous)
    ↓ Only interrupt on complex unexpected events
Results Delivered
```

---

## Workflow Phases

### Phase 1: Planning (Interactive) 🤝

**What Happens:**
- User and Claude discuss requirements
- OpusPlanner creates detailed execution plan
- User reviews ALL steps in the plan
- User approves plan with expiration

**User Interaction:** **REQUIRED**
- Discuss requirements
- Review plan steps
- Approve plan explicitly
- Enable dangerous skip if needed

**Example:**
```
User: "I need to add JWT authentication"

Claude: "Let me plan this implementation..."
[OpusPlanner creates plan]

Claude: "Here's the plan:
  1. Install dependencies (jsonwebtoken, bcrypt)
  2. Create User model with password hashing
  3. Implement JWT token generation
  4. Add authentication middleware
  5. Create login/register endpoints
  6. Add tests

  Review and approve?"

User: "Looks good, approve it"

[Plan approved and saved]
```

### Phase 2: Execution (Autonomous) 🤖

**What Happens:**
- Execute plan steps sequentially or in parallel
- Use `dangerouslyDisableSandbox: true` for approved operations
- Handle expected errors automatically
- Continue without interruption

**User Interaction:** **NONE** (unless complex unexpected event)

**Auto-Handled Situations:**
- ✅ Dependency installation
- ✅ File creation/modification
- ✅ Expected test failures (fix and retry)
- ✅ Common build errors
- ✅ Linting/formatting issues
- ✅ Import errors (add missing imports)
- ✅ Type errors (fix types)

**Example:**
```
[Execution starts]
✓ Step 1: npm install jsonwebtoken bcrypt
✓ Step 2: Created src/models/User.ts
✓ Step 3: Created src/auth/jwt.ts
✗ Step 4: Import error detected
  → Auto-fix: Added missing import
  → Retry: ✓ Success
✓ Step 5: Created src/routes/auth.ts
✗ Step 6: Test failed (missing mock)
  → Auto-fix: Added mock setup
  → Retry: ✓ Success
[Execution complete]
```

### Phase 3: Interruption (Exceptional) ⚠️

**ONLY interrupt user when:**
1. **Unexpected AND complex** situation
2. **Multiple solutions** possible (need user choice)
3. **Critical decision** required
4. **Security concern** detected

**Ask User When:**
- ❓ "Should I use OAuth 2.0 or JWT?" (design decision)
- ❓ "Database schema conflict - migrate or recreate?" (data safety)
- ❓ "Test suite requires external API - use mock or real?" (architectural choice)
- ❓ "Breaking change detected - continue anyway?" (impact decision)

**DO NOT ask user for:**
- ✓ Missing import (add automatically)
- ✓ Formatting issue (fix automatically)
- ✓ Dependency conflict (resolve automatically)
- ✓ Test failure (debug and fix)
- ✓ Build error (fix and retry)

---

## Decision Matrix: When to Interrupt

### Interrupt ⚠️

| Situation | Why Interrupt | Example |
|-----------|---------------|---------|
| Multiple valid approaches | Need user preference | "Use REST or GraphQL?" |
| Data loss risk | Safety check | "Delete migration will lose data" |
| Security decision | User must approve | "Use HTTP or require HTTPS?" |
| Breaking change impact | User must assess | "This breaks 3 existing APIs" |
| Architecture decision | Long-term implications | "Microservices or monolith?" |

### Auto-Handle ✓

| Situation | Auto-Fix Strategy | Example |
|-----------|-------------------|---------|
| Missing import | Add import automatically | `import { User } from './models'` |
| Type error | Fix type annotation | `user: User` instead of `user: any` |
| Lint error | Run formatter | `npm run lint --fix` |
| Test failure | Debug and fix | Add missing mock, fix assertion |
| Build error | Fix and retry | Update tsconfig, fix syntax |
| Dependency conflict | Use compatible version | `npm install pkg@^2.0.0` |

---

## Implementation Guidelines

### For OpusPlanner

**When creating plans:**

```json
{
  "plan_id": "add-auth",
  "auto_execution": {
    "enabled": true,
    "interrupt_only_on": [
      "multiple_solutions",
      "data_loss_risk",
      "security_decision",
      "breaking_change"
    ],
    "auto_handle": [
      "missing_imports",
      "type_errors",
      "lint_errors",
      "test_failures",
      "build_errors"
    ]
  },
  "sections": [...]
}
```

**When executing:**

```python
for step in plan.steps:
    try:
        result = execute_step(step)
    except ExpectedError as e:
        # Auto-fix
        fix = auto_fix_strategy(e)
        result = retry_step(step, fix)
    except UnexpectedComplexError as e:
        # Only now interrupt user
        user_decision = ask_user(e)
        result = execute_with_decision(step, user_decision)
```

### For Execution Agents

**HaikuExecutor:**
- Execute steps without confirmation
- Auto-fix common issues
- Only escalate to SonnetDebugger if complex

**SonnetDebugger:**
- Analyze errors automatically
- Apply known fix patterns
- Only interrupt user if no solution found

**SonnetCoder:**
- Implement features autonomously
- Follow project patterns
- Only ask user for design choices

---

## Auto-Fix Strategies

### Missing Imports

```python
# Detected: 'User' is not defined
# Auto-fix:
from models import User  # Add import
```

### Type Errors

```python
# Detected: Parameter 'user' implicitly has 'any' type
# Auto-fix:
def process_user(user: User):  # Add type hint
```

### Test Failures

```python
# Detected: Mock not configured
# Auto-fix:
@patch('auth.jwt.sign')
def test_auth(mock_sign):
    mock_sign.return_value = 'token'
    # Continue test
```

### Build Errors

```bash
# Detected: Module not found
# Auto-fix:
npm install missing-module --save
npm run build  # Retry
```

### Dependency Conflicts

```bash
# Detected: Peer dependency conflict
# Auto-fix:
npm install --legacy-peer-deps
# Or
npm install compatible-version
```

---

## Example: Complete Autonomous Execution

### Plan Approval

```bash
# User approves plan
python3 approve-plan.py /tmp/add-auth-plan.json --expires 48h

# Enable autonomous mode
python3 approve-plan.py --enable-dangerous-skip
```

### Execution Log (No User Interaction)

```
🚀 Executing plan: add-auth
✅ Plan approved - autonomous mode enabled

[Step 1/10] Install dependencies
  → Running: npm install jsonwebtoken bcrypt
  ✓ Success (12.3s)

[Step 2/10] Create User model
  → Creating: src/models/User.ts
  ✓ Created (0.2s)

[Step 3/10] Add password hashing
  → Updating: src/models/User.ts
  ✗ Type error: 'bcrypt' has no default export
  → Auto-fix: Changed to named import
  → Retry: ✓ Success (0.5s)

[Step 4/10] Create JWT utilities
  → Creating: src/auth/jwt.ts
  ✗ Import error: Cannot find 'User'
  → Auto-fix: Added import from '../models/User'
  → Retry: ✓ Success (0.3s)

[Step 5/10] Add authentication middleware
  → Creating: src/middleware/auth.ts
  ✓ Success (0.4s)

[Step 6/10] Create auth endpoints
  → Creating: src/routes/auth.ts
  ✓ Success (0.6s)

[Step 7/10] Add tests
  → Creating: tests/auth.test.ts
  ✗ Test failed: Missing mock for jwt.sign
  → Auto-fix: Added @patch decorator
  → Retry: ✓ All tests pass (3.2s)

[Step 8/10] Run linter
  → Running: npm run lint
  ✗ Lint errors: 3 issues found
  → Auto-fix: npm run lint --fix
  → Retry: ✓ No errors (1.1s)

[Step 9/10] Run type check
  → Running: npm run typecheck
  ✓ No type errors (2.4s)

[Step 10/10] Build project
  → Running: npm run build
  ✓ Build successful (8.7s)

✅ Execution complete!
   Total time: 29.7s
   Steps: 10
   Auto-fixes: 4
   User interruptions: 0
```

---

## Configuration

### Enable Autonomous Mode

**File:** `/root/.claude/settings.json`

```json
{
  "fractal": {
    "approvedPlans": {
      "enabled": true,
      "dangerouslySkipPermissions": true,
      "autoFixStrategies": {
        "missingImports": true,
        "typeErrors": true,
        "lintErrors": true,
        "testFailures": true,
        "buildErrors": true
      },
      "interruptOnlyFor": [
        "multiple_solutions",
        "data_loss_risk",
        "security_decision",
        "breaking_change"
      ]
    }
  }
}
```

---

## Safety Guarantees

Even in autonomous mode:

1. ✅ **Plan must be approved** - No execution without user review
2. ✅ **Hash verification** - Plan can't be modified after approval
3. ✅ **Time expiration** - Approvals expire automatically
4. ✅ **Audit log** - All actions logged
5. ✅ **Interrupt on critical** - User asked for important decisions
6. ✅ **Rollback available** - Changes can be reverted

---

## Summary

**Planning Phase:** Interactive, collaborative, user reviews everything
**Execution Phase:** Autonomous, fast, only interrupt when truly needed
**Result:** Efficient development without constant interruptions

**Key Principle:** Trust the approved plan, handle expected issues automatically, interrupt only for complex unexpected situations.

---

**Related Documentation:**
- `/root/software/.claude/docs/APPROVED_PLANS_GUIDE.md` - Plan approval system
- `/root/software/.claude/fractal/COMPLETE_WORKFLOW_GUIDE.md` - Complete workflow
- `/root/software/.claude/plan.md` - Auto-initialization plan
