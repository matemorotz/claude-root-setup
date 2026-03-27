# Session Workflow Guide

How to effectively use the Skills and Memories system in every Claude Code session.

## Session Startup

### What Happens Automatically

When Claude Code launches:
```
1. Load CLAUDE.md (project memory)
   ├── @ imports: project.md, docs files
   └── Skills metadata (names + descriptions only)

2. Scan for skills
   ├── ~/.claude/skills/ (personal)
   ├── .claude/skills/ (project)
   └── Plugin skills

3. Ready for activation
   └── Skills activate based on your requests
```

**Context at startup**: ~20-30K tokens (efficient!)

## Using Skills in Session

### Skill Activation Patterns

**Explicit activation**:
```
"Create a new skill for database management"
→ building-skills activates
→ Loads SKILL.md (238 lines)
→ References shared memories as needed
```

**Implicit activation**:
```
"I need to deploy a new calendar agent"
→ deploying-agents activates
→ Loads agent deployment workflow
→ References architecture docs as needed
```

**Multi-skill workflow**:
```
"Create and deploy a new MCP server with tests"
→ mcp-integration activates (setup)
→ testing-workflows activates (validation)
→ deploying-services activates (deployment)
```

### How Memory Loading Works

**Progressive disclosure in action**:
```
You: "Create a new skill"
    ↓
building-skills/SKILL.md loaded (238 lines)
    ↓
You mention needing examples
    ↓
SKILL.md says: "For examples: @../../docs/skills/skill-examples.md"
    ↓
Claude loads skill-examples.md (370 lines)
    ↓
Total context: 238 + 370 = 608 lines (~15K tokens)
```

**Efficient**: Only 15K tokens added (vs 50K if everything loaded at once)

## Common Session Workflows

### Workflow 1: Creating a New Skill

**Request**: "Create a new skill for [domain]"

**What happens**:
1. building-skills activates
2. Loads 6-phase workflow (238 lines)
3. If you need examples → loads skill-examples.md
4. If you need degrees of freedom → loads degrees-of-freedom.md
5. If you need complete specs → loads building-skills-knowledge-base.md

**Commands**:
```bash
# Automated
.claude/skills/building-skills/scripts/init-skill.sh

# Manual
cp .claude/skills/building-skills/templates/standard-skill.md .claude/skills/my-skill/SKILL.md

# Validate
.claude/skills/building-skills/scripts/validate-skill.sh .claude/skills/my-skill/
```

### Workflow 2: Deploying an Agent

**Request**: "Deploy a new [domain] agent"

**What happens**:
1. deploying-agents activates
2. Loads agent deployment workflow
3. References docs/agents/architecture.md (LangGraph patterns)
4. References docs/skills/degrees-of-freedom.md (LOW freedom for deployment)

**Flow**:
```
Phase 1: Planning → Review architecture patterns
Phase 2: Implementation → Create agent file
Phase 3: Testing → Run tests in venv
Phase 4: Deployment → Integrate with governor
```

### Workflow 3: Setting Up MCP Server

**Request**: "Create an MCP server for [purpose]"

**What happens**:
1. mcp-integration activates
2. Loads MCP setup workflow
3. References docs/mcp/integration.md (standards)
4. References docs/skills/degrees-of-freedom.md (MEDIUM freedom for tool design)

### Workflow 4: Testing Changes

**Request**: "Test the new [feature]"

**What happens**:
1. testing-workflows activates
2. Loads testing procedures
3. Uses venv_linux environment
4. Follows A/B testing approach

## Session Best Practices

### Start of Session

**Good practices**:
```
✓ "Create a skill for X" (clear task)
✓ "Deploy new agent for Y" (specific domain)
✓ "Test the booking feature" (explicit action)
```

**Avoid**:
```
✗ "Help me" (too vague)
✗ "What can you do?" (informational, not task)
✗ "Tell me about skills" (doesn't trigger execution)
```

### During Session

**Leverage progressive disclosure**:
```
You: "Create database skill"
Claude: [Shows 6-phase workflow]

You: "Show me examples of database skills"
Claude: [Loads skill-examples.md, shows database example]

You: "What degree of freedom should I use?"
Claude: [Loads degrees-of-freedom.md, explains LOW for critical ops]
```

**Ask for specific memories**:
```
"Show me the complete Anthropic specifications"
→ Loads building-skills-knowledge-base.md

"What are all the available skills?"
→ References docs/skills/guidelines.md

"How does the scaling architecture work?"
→ Loads docs/skills/scaling-architecture.md
```

### End of Session

**Before committing**:
- Run validation scripts
- Test skill activation
- Update CHANGELOG if needed
- Commit with clear message

## Context Management

### Understanding Token Usage

**Startup** (~25K tokens):
```
CLAUDE.md: ~2K
project.md: ~1K
docs/skills/guidelines.md: ~3K
Skills metadata (5 skills): ~1K
Total: ~7K tokens
```

**Skill activation** (~15K tokens added):
```
SKILL.md: ~5K
Referenced memory: ~10K
Total added: ~15K tokens
```

**Peak usage** (~40K tokens):
```
Startup + Skill + Progressive disclosure
Still well under 200K limit!
```

### When Context Gets Large

**Signs**:
- Responses slow down
- "Context is full" warnings
- Can't load more files

**Solutions**:
```bash
# 1. Start fresh session
# Ctrl+Shift+P → "Reload Window"

# 2. Clear conversation
# Keep skill in context, restart conversation

# 3. Simplify task
# Break large task into smaller steps
```

## Tips for Efficiency

### Reference Patterns

**Good** (specific):
```
"For database example, see skill-examples.md"
→ Claude loads just that section
```

**Less efficient** (general):
```
"See all documentation"
→ Claude might load too much
```

### Skill Chaining

**Effective pattern**:
```
"Create skill (building-skills) →
Test it (testing-workflows) →
Deploy to project (git commit)"
```

### Memory Reuse

**Efficient**:
```
docs/skills/degrees-of-freedom.md
Referenced by:
- building-skills
- deploying-agents
- mcp-integration
- managing-servers

Loaded once, reused by all!
```

## Troubleshooting Sessions

### Skill Doesn't Activate

**Problem**: Request doesn't trigger expected skill

**Solutions**:
- Use explicit skill-related keywords
- "Create a skill" vs "Help with skills"
- Check skill description matches your request

### Memory Not Loading

**Problem**: Referenced memory doesn't appear

**Check**:
```bash
# Verify file exists
ls docs/skills/degrees-of-freedom.md

# Verify @ reference in SKILL.md
grep "@.*degrees-of-freedom" .claude/skills/*/SKILL.md
```

### Context Overload

**Problem**: Too much loaded, responses slow

**Fix**:
- Start new session
- Be more specific in requests
- Load memories incrementally

## Example Session Transcript

```
Session Start
───────────────────────────────────────

You: "Create a new skill for managing PostgreSQL databases"

Claude: [building-skills activates, loads 238-line workflow]
"I'll help you create a database management skill following the
six-phase process...

Phase 1: Let's gather examples. What specific tasks will this skill handle?"

You: "Backup, restore, and migrations"

Claude: [No additional load needed, workflow has this]
"Got it. For database operations, we should use LOW freedom (exact
sequences) because of data criticality. Let me show you the structure..."

You: "Can you show me an example of a similar skill?"

Claude: [Loads skill-examples.md]
"Here's a complete database skill example from the knowledge base..."

You: "What's LOW freedom mean exactly?"

Claude: [Loads degrees-of-freedom.md]
"LOW freedom means exact step-by-step sequences with no deviation..."

You: "Okay, let's create it"

Claude: [Executes init-skill.sh]
"Creating skill with these details..."

[Session continues with minimal context loading]
───────────────────────────────────────
Total context used: ~35K tokens
Peak: ~40K tokens (efficient!)
```

## Session Checklist

### Before Starting
- [ ] Clear task in mind
- [ ] Know which skill(s) needed
- [ ] Have relevant files ready

### During Session
- [ ] Let skills activate naturally
- [ ] Ask for specific memories when needed
- [ ] Monitor context usage
- [ ] Test as you go

### After Completing
- [ ] Validate with scripts
- [ ] Test skill activation
- [ ] Commit changes
- [ ] Update documentation if needed

## Advanced Patterns

### Skill Development Session

**Full cycle in one session**:
```
1. "Create skill for X" → building-skills
2. "Show examples" → Load skill-examples.md
3. "What freedom level?" → Load degrees-of-freedom.md
4. "Create the skill" → Execute workflow
5. "Test it" → testing-workflows
6. "Validate" → Run validate-skill.sh
7. "Commit" → Git workflow
```

### Multi-Skill Orchestration

**Complex workflow**:
```
"Create, test, and deploy new email agent with MCP integration"

Activation sequence:
1. deploying-agents (create agent)
2. mcp-integration (setup MCP)
3. testing-workflows (validate)
4. Git workflow (commit/deploy)

Each loads only its workflow + shared memories as referenced
```

### Learning Session

**Exploring the system**:
```
"Explain the skills and memory architecture"
→ Load scaling-architecture.md

"How do I decide what goes where?"
→ Load skill-memory-split-logic.md

"Show me all the patterns"
→ Load degrees-of-freedom.md

Context efficient: Load only what's asked for
```

## Summary

**Every session**:
1. Skills activate based on your request (automatic)
2. Memories load only when referenced (progressive)
3. Context stays efficient (<50K tokens typically)
4. Work completes successfully

**Key principle**:
> **Ask for what you need, when you need it**
>
> Skills provide workflow, memories provide knowledge,
> progressive disclosure keeps context efficient.

**Result**:
Productive sessions with minimal context overhead!
