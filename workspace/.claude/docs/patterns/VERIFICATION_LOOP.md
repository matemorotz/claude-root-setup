# Verification Loop

**Source:** AGENT_COORDINATION_PATTERN.md
**Section:** Parent Verifies Child

---

### Parent-Verifies-Child Architecture

When an agent spawns a subagent, the **parent agent's hook** is responsible for verifying the subagent's response:

```
┌─────────────────────────────────────────────────────────┐
│                   PARENT AGENT                           │
│  (e.g., OpusPlanner, SonnetCoder)                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Determine task needs subagent                        │
│  2. Package context + task + expected outcome            │
│  3. Spawn subagent (background)                          │
│  4. Continue other work (non-blocking)                   │
│  5. **Parent's hook verifies response**                  │
│  6. Validate against expected outcome                    │
│  7. Accept, retry, or escalate                           │
│                                                           │
└─────────────────────────────────────────────────────────┘
                          ↓
                   Spawn subagent
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  SUBAGENT (Background)                   │
│  (e.g., SonnetCoder, HaikuExecutor)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Receive: context + task + expected outcome           │
│  2. Execute task independently                           │
│  3. Return: result                                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
                          ↓
                   Return result
                          ↓
┌─────────────────────────────────────────────────────────┐
│              PARENT'S HOOK (Verification)                │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Check: Does result match expected outcome?              │
│    ✅ YES → Accept result, continue                      │
│    ❌ NO  → Retry or escalate                            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## I/O Style Coordination



---

**See also:**
- [Documentation Index](../INDEX.md)
- [Source: AGENT_COORDINATION_PATTERN.md](../AGENT_COORDINATION_PATTERN.md)
