# Skills Usage Guidelines

## Overview
Skills are model-invoked capabilities that extend Claude's functionality through organized folders of instructions, scripts, and resources.

## Available Skills

### Project Skills (`.claude/skills/`)
Team-shared skills, version-controlled in git.

#### deploying-agents
**Purpose**: Automate new agent deployment following LangGraph patterns
**When to Use**: Creating new specialist agents for CoreTeam system
**Triggers**: "deploy agent", "create new agent", "add specialist"
**References**: `@../../docs/agents/architecture.md`, `@../../project.md`

#### mcp-integration
**Purpose**: Set up MCP endpoints with authentication and standards
**When to Use**: Creating or integrating MCP servers
**Triggers**: "create MCP", "integrate MCP server", "setup endpoint"
**References**: `@../../docs/mcp/integration.md`, `@../../project.md`

#### testing-workflows
**Purpose**: Automated testing with venv validation and A/B testing
**When to Use**: Testing code changes, running test suites
**Triggers**: "run tests", "validate implementation", "test changes"
**References**: `@../../CLAUDE_MASTER_RULES.md`, `@../../project.md`

## How Skills Work

### Model-Invoked Behavior
Skills are **autonomously invoked** by Claude based on:
1. **Description Match**: Request context matches skill description
2. **Trigger Keywords**: Specific phrases in user requests
3. **Task Pattern**: Type of work matches skill capability

### Progressive Disclosure
Skills use three-level loading:
1. **Metadata**: Name + description (always loaded)
2. **SKILL.md Body**: Main instructions (loaded when skill activates)
3. **Supporting Files**: Scripts, references (loaded as needed)

### Memory Integration
Skills automatically reference project memories:
```markdown
# In SKILL.md
@../../project.md              # Project context
@../../CLAUDE_MASTER_RULES.md  # Execution rules
@../../docs/agents/architecture.md  # Domain-specific docs
```

## Skill Activation Patterns

### Direct Activation
User explicitly requests skill domain:
```
User: "Deploy a new calendar agent"
→ deploying-agents skill activates
→ Follows agent architecture patterns
→ Uses LangGraph templates
→ Validates per master rules
```

### Implicit Activation
User request matches skill capabilities:
```
User: "I need to test the new booking feature"
→ testing-workflows skill activates
→ Uses venv_linux environment
→ Follows A/B testing approach
→ Validates per completion checklist
```

### Multi-Skill Workflows
Complex tasks may activate multiple skills:
```
User: "Create and test a new email agent with MCP integration"
→ deploying-agents skill (agent creation)
→ mcp-integration skill (MCP endpoint setup)
→ testing-workflows skill (validation)
```

## Creating New Skills

### Skill Creation Checklist
- [ ] Clear, specific purpose defined
- [ ] Trigger keywords identified
- [ ] Supporting documentation created
- [ ] Follows Anthropic naming conventions
- [ ] SKILL.md under 500 lines
- [ ] References project memories
- [ ] Tested with multiple requests

### Naming Convention
Use gerund form (verb + -ing):
- ✅ `deploying-agents`
- ✅ `analyzing-performance`
- ✅ `debugging-issues`
- ❌ `agent-deploy`
- ❌ `performance`
- ❌ `debug`

### SKILL.md Structure
```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it (max 1024 chars)
---

# Skill Title

## Context Import
@../../relevant/memory.md

## Overview
Brief description

## Workflow
Step-by-step instructions

## Best Practices
Dos and don'ts

## References
Related documentation
```

### Description Writing
Write in **third person**, be **specific**:
- ✅ "Deploy new specialist agents following LangGraph multi-agent architecture patterns. Use when creating new agents for the CoreTeam system."
- ❌ "Helps with agents"

Include:
- What the skill does
- When to use it
- Key domain terms
- Integration points

## Skill Best Practices

### Do's
✓ Keep SKILL.md under 500 lines
✓ Use progressive disclosure (split complex content)
✓ Reference project memories for context
✓ Include concrete examples
✓ Provide clear workflow steps
✓ Document error handling
✓ Include troubleshooting section

### Don'ts
✗ Don't duplicate project memory content
✗ Don't include time-sensitive information
✗ Don't use inconsistent terminology
✗ Don't make skills too generic
✗ Don't skip validation steps
✗ Don't assume context without referencing

## Skill-Memory-Agent Integration

### Integration Flow
```
User Request
    ↓
Skill Activation (based on description match)
    ↓
Memory Loading (via @ imports)
    ↓
Agent Execution (follows skill + memory guidance)
    ↓
Validation (per master rules)
    ↓
Result
```

### Example: Agent Deployment Flow
```
User: "Deploy booking agent"
    ↓
deploying-agents skill activates
    ↓
Loads: project.md (LangGraph patterns)
       CLAUDE_MASTER_RULES.md (execution rules)
       docs/agents/architecture.md (agent patterns)
    ↓
Follows workflow:
  1. Planning (clarify purpose, review existing)
  2. Implementation (create agent file, follow template)
  3. Testing (dev branch, venv, validation)
  4. Deployment (code review, integration, monitoring)
    ↓
Validates per checklist:
  - LangGraph patterns ✓
  - Type hints ✓
  - Error handling ✓
  - Tests passing ✓
    ↓
Agent deployed successfully
```

## Skill Maintenance

### Regular Review
- Review skill descriptions quarterly
- Update trigger keywords based on usage
- Refine workflows based on feedback
- Keep supporting docs synchronized

### Version Control
Skills in `.claude/skills/` are version-controlled:
```bash
# Add new skill
git add .claude/skills/new-skill/

# Update existing skill
git add .claude/skills/existing-skill/SKILL.md
git commit -m "Update skill: improved error handling"

# Team members get updates
git pull origin main
```

### Testing Skills
```bash
# Test skill activation
# Ask questions that should trigger skill
echo "Test: Does 'deploy agent' trigger deploying-agents skill?"

# Verify skill follows workflows
# Check that skill references correct memories

# Validate skill outputs
# Ensure results match expected patterns
```

## Troubleshooting Skills

### Skill Not Activating
**Problem**: Request doesn't trigger expected skill
**Solutions**:
1. Check description matches request domain
2. Add relevant keywords to description
3. Make description more specific
4. Test with explicit skill-related terms

### Skill Activates Incorrectly
**Problem**: Wrong skill activates for request
**Solutions**:
1. Make skill descriptions more specific
2. Reduce overlap between skill domains
3. Use clear, distinct keywords
4. Review trigger patterns

### Skill Missing Context
**Problem**: Skill doesn't have needed information
**Solutions**:
1. Add memory imports: `@../../docs/topic.md`
2. Include reference files in skill folder
3. Update project.md with missing context
4. Add supporting documentation

### Skill Workflow Fails
**Problem**: Skill activates but workflow doesn't complete
**Solutions**:
1. Check validation steps are achievable
2. Verify memory references are correct
3. Ensure supporting files exist
4. Test workflow steps manually

## Skill Examples

### Good Skill Description
```yaml
---
name: analyzing-performance
description: Analyze system performance metrics, identify bottlenecks, and recommend optimizations. Use when investigating slow performance, high resource usage, or system inefficiencies. Includes profiling, benchmarking, and optimization strategies.
---
```

### Bad Skill Description
```yaml
---
name: performance
description: Helps with performance
---
```

### Good Skill Workflow
```markdown
## Workflow

### Phase 1: Analysis
1. Gather performance metrics
   - CPU usage: `top` or `htop`
   - Memory: `free -h`
   - Disk I/O: `iostat`

2. Identify bottlenecks
   - Profile Python code
   - Check database queries
   - Review network latency

### Phase 2: Recommendations
3. Propose optimizations
   - Code-level improvements
   - Infrastructure changes
   - Configuration tuning

4. Validate improvements
   - Benchmark before/after
   - Monitor production metrics
```

### Bad Skill Workflow
```markdown
## Workflow
1. Check performance
2. Fix issues
3. Done
```

## Integration with Master Rules

Skills automatically follow CLAUDE_MASTER_RULES.md:
- **Priority 1**: Research best practices first
- **Priority 2**: Dynamic planning based on context
- **Priority 3**: Human partner → Task solving → Learning
- **Priority 4**: Consistent schemes and patterns
- **Priority 5**: Safe code changes (A/B testing)
- **Priority 6**: Test environment validation

Skills enhance rules by providing:
- Domain-specific workflows
- Concrete implementation steps
- Validation checklists
- Error handling patterns

## References

See also:
- `.claude/skills/deploying-agents/` - Agent deployment skill
- `.claude/skills/mcp-integration/` - MCP integration skill
- `.claude/skills/testing-workflows/` - Testing automation skill
- `CLAUDE_MASTER_RULES.md` - Core execution principles
- `project.md` - Project context and conventions
- Official skills repo: https://github.com/anthropics/skills
