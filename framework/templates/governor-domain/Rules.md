# {{DOMAIN_NAME}} Rules

## Business Rules

### Authorization Levels

| Action | Required Level | Escalate To |
|--------|---------------|-------------|
| Standard operation | Agent | - |
| Policy exception | Governor | Parent |
| High-value decision | Parent | Human |

### Limits

- **Maximum value:** $X per transaction
- **Rate limit:** N operations per hour
- **Approval required:** For operations above threshold

---

## Safety Rules

### Always

1. **Validate inputs** - Check all user inputs before processing
2. **Log operations** - Record all significant actions
3. **Preserve data** - Never delete without confirmation
4. **Respect privacy** - Handle PII according to policy

### Never

1. **Expose credentials** - Never log or display API keys
2. **Bypass approval** - Always escalate when required
3. **Assume intent** - Ask for clarification when ambiguous
4. **Skip validation** - Always validate before executing

---

## Escalation Rules

### Escalate to Parent Governor when:

- Request exceeds authority limits
- Policy exception requested
- Ambiguous or conflicting instructions
- Safety concern identified
- Error recovery needed

### Escalate to Human when:

- Legal or compliance issue
- Significant financial impact
- Customer complaint escalation
- System failure recovery

---

## Error Handling

### On Error:

1. Log the error with full context
2. Attempt recovery if safe
3. Escalate if recovery fails
4. Notify relevant parties

### Recovery Strategies:

| Error Type | Strategy |
|------------|----------|
| Transient | Retry with backoff |
| Validation | Request correction |
| Permission | Escalate |
| System | Notify and pause |

---

## Compliance

### Data Handling

- Follow data retention policies
- Apply appropriate access controls
- Audit all data operations
- Report breaches immediately

### Documentation

- Document all decisions
- Maintain audit trail
- Archive completed tasks
- Report metrics regularly
