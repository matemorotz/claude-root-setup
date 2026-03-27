# Skill vs Memory Split Logic

Decision framework for what goes in skills vs memories.

## Core Principle

**Skills**: Executable workflows (the "HOW")
**Memories**: Knowledge & context (the "WHAT" and "WHY")

## The Split Logic Decision Tree

```
For each piece of content, ask:

1. Is this EXECUTABLE?
   ├─ YES: Action steps, commands, procedures
   │   ↓
   │   Is it SKILL-SPECIFIC?
   │   ├─ YES → PUT IN SKILL
   │   └─ NO (shared across skills) → PUT IN MEMORY
   │
   └─ NO: Concepts, specifications, examples
       ↓
       Is it REUSABLE across multiple skills?
       ├─ YES → PUT IN MEMORY
       └─ NO (only for this skill) → PUT IN SKILL
```

## Content Type Matrix

| Content Type | Skill | Memory | Reason |
|--------------|-------|--------|---------|
| **Workflow steps** | ✅ | ❌ | Executable, skill-specific |
| **Code examples** | ✅ | ❌ | Part of workflow demonstration |
| **Validation checklist** | ✅ | ❌ | Skill-specific validation |
| **Templates** | ✅ | ❌ | Tools for skill execution |
| **Scripts** | ✅ | ❌ | Automation for skill |
| **Conceptual patterns** | ❌ | ✅ | Reusable knowledge |
| **Specifications** | ❌ | ✅ | Reference material |
| **Best practices** | 🟡 | ✅ | Short summary in skill, details in memory |
| **Real-world examples** | 🟡 | ✅ | One in skill, rest in memory |
| **Troubleshooting** | ✅ | ❌ | Skill-specific issues |
| **Domain knowledge** | ❌ | ✅ | Shared understanding |

## Detailed Decision Framework

### PUT IN SKILL (`.claude/skills/skill-name/`)

**Executable Workflows**:
```markdown
✅ Include in SKILL.md:
- Step-by-step procedures
- Command sequences
- Configuration instructions
- Validation steps
- One working example (inline)

Example:
## Workflow: Deploy Agent
1. Create agent file
2. Implement state schema
3. Add to routing logic
4. Test activation
```

**Skill-Specific Tools**:
```
✅ Include in skill directory:
- Templates (minimal-skill.md, standard-skill.md)
- Scripts (init-skill.sh, validate-skill.sh)
- Skill-specific checklists
```

**Skill-Specific Documentation**:
```markdown
✅ Include in skill (progressive disclosure):
- Integration guide (if complex and specific to this skill)
- Advanced workflows (specific to this skill's domain)
```

### PUT IN MEMORY (`docs/skills/` or `docs/domain/`)

**Reusable Concepts**:
```markdown
✅ docs/skills/degrees-of-freedom.md
- Applies to ALL skills (deploying-agents, mcp-integration, etc.)
- Concept: High/Medium/Low freedom patterns
- Reusable across domains

✅ docs/skills/progressive-disclosure-pattern.md
- Applies to all skill creation
- Concept: How to structure for efficiency
- Reusable knowledge
```

**Specifications**:
```markdown
✅ docs/skills/anthropic-specifications.md
- YAML requirements
- Naming conventions
- Validation rules
- Reference material, not workflow
```

**Domain Knowledge**:
```markdown
✅ docs/agents/architecture.md
- LangGraph patterns
- Multi-agent coordination
- Shared by: deploying-agents, testing-workflows

✅ docs/mcp/integration.md
- MCP standards
- Authentication patterns
- Shared by: mcp-integration, deploying-agents
```

**Comprehensive Examples**:
```markdown
✅ docs/skills/skill-examples.md
- 10+ detailed examples
- Multiple domains
- Learning resource for team
- Referenced by building-skills skill
```

## Example Splits

### Example 1: building-skills

**In Skill**:
```
.claude/skills/building-skills/
├── SKILL.md (~200 lines)
│   ├── Quick Start
│   ├── Six-Phase Process (workflow steps)
│   ├── One inline example
│   └── References to memory files
├── templates/ (skill-specific tools)
└── scripts/ (skill-specific automation)
```

**In Memory**:
```
docs/skills/
├── anthropic-specifications.md (reusable specs)
├── degrees-of-freedom.md (reusable pattern)
├── skill-examples.md (10+ examples for learning)
└── progressive-disclosure-guide.md (reusable concept)
```

**In SKILL.md**:
```markdown
## Six-Phase Process
[Workflow steps inline]

For complete specifications: @../../docs/skills/anthropic-specifications.md
For degrees of freedom guide: @../../docs/skills/degrees-of-freedom.md
For detailed examples: @../../docs/skills/skill-examples.md
```

### Example 2: deploying-agents

**In Skill**:
```
.claude/skills/deploying-agents/
├── SKILL.md (~300 lines)
│   ├── Deployment workflow (steps)
│   ├── One agent example (inline)
│   ├── Integration checklist
│   └── References to shared knowledge
└── templates/
    └── agent-template.py
```

**In Memory** (shared knowledge):
```
docs/agents/
├── architecture.md (LangGraph patterns - shared)
├── deployment.md (procedures - shared)
└── state-management.md (patterns - shared)

docs/skills/
└── degrees-of-freedom.md (use LOW freedom for deployments)
```

**In SKILL.md**:
```markdown
## Deployment Workflow
[Specific steps inline]

Follow LOW freedom approach (see @../../docs/skills/degrees-of-freedom.md)
for deployment to ensure consistency.

Architecture patterns: @../../docs/agents/architecture.md
Detailed procedures: @../../docs/agents/deployment.md
```

### Example 3: mcp-integration

**In Skill**:
```
.claude/skills/mcp-integration/
├── SKILL.md (~250 lines)
│   ├── MCP setup workflow
│   ├── Tool design workflow
│   ├── One MCP server example
│   └── Testing procedures
└── templates/
    └── mcp-server-template.py
```

**In Memory** (shared knowledge):
```
docs/mcp/
├── integration.md (standards - shared with deploying-agents)
├── authentication.md (patterns - shared)
└── tool-design.md (best practices - shared)

docs/skills/
└── degrees-of-freedom.md (use MEDIUM freedom for tool design)
```

## Size Guidelines

### Skill Files

**SKILL.md**:
- Target: 200-300 lines (minimal workflow)
- Maximum: 500 lines (Anthropic recommendation)
- If exceeding: Split with progressive disclosure

**Progressive Disclosure Files** (in skill dir):
- Target: 200-400 lines each
- Purpose: Detailed workflows, advanced features
- Loaded: Only when referenced

**Templates/Scripts**:
- No size limit (they're tools, not documentation)

### Memory Files

**Concept Documents**:
- Target: 300-600 lines
- Purpose: Complete explanation of reusable concept
- Example: degrees-of-freedom.md

**Specification Documents**:
- Target: 500-1000 lines
- Purpose: Complete reference material
- Example: anthropic-specifications.md

**Example Collections**:
- Target: 500-1000 lines
- Purpose: Multiple detailed examples
- Example: skill-examples.md

**Domain Knowledge**:
- Target: 400-800 lines
- Purpose: Architecture, patterns, standards
- Example: agents/architecture.md

## The 80/20 Rule

**In Skills**: 20% of content covers 80% of use cases
- Core workflow steps
- Essential templates
- Quick reference

**In Memories**: 80% of content for 20% of advanced needs
- Complete specifications
- All edge cases
- Comprehensive examples
- Deep dives

## Loading Optimization

### Startup Context (Always Loaded)
```
CLAUDE.md
├── @project.md (~100 lines)
├── @docs/skills/guidelines.md (~300 lines - general usage)
└── Skills metadata (name + description only)

Total: ~500 lines
```

### Skill Activation (Loaded When Triggered)
```
Skill SKILL.md (~200-300 lines)
+ Referenced memory file if mentioned (~400 lines)

Total added: ~700 lines
```

### Progressive Disclosure (Loaded Only When Needed)
```
Advanced workflow mentioned
→ Load @advanced.md (~400 lines)

Complete specs needed
→ Load @../../docs/skills/specs.md (~800 lines)

Total: Only load what's mentioned
```

## Decision Examples

### Example: "Degrees of Freedom" Content

**Question**: Where does degrees-of-freedom content go?

**Analysis**:
- Is it executable? NO (it's a concept/pattern)
- Is it reusable? YES (applies to building-skills, deploying-agents, mcp-integration, managing-servers)
- Is it skill-specific? NO (general pattern)

**Decision**: PUT IN MEMORY
```
docs/skills/degrees-of-freedom.md

Referenced by:
- .claude/skills/building-skills/SKILL.md
- .claude/skills/deploying-agents/SKILL.md
- .claude/skills/mcp-integration/SKILL.md
- .claude/skills/managing-servers/SKILL.md
```

### Example: "Skill Creation Workflow"

**Question**: Where does six-phase creation process go?

**Analysis**:
- Is it executable? YES (step-by-step workflow)
- Is it skill-specific? YES (only for building-skills)
- Is it reusable? NO (specific to skill creation)

**Decision**: PUT IN SKILL
```
.claude/skills/building-skills/SKILL.md

Contains:
- Phase 1: Understanding (steps)
- Phase 2: Planning (steps)
- Phase 3-6: Initialize, Write, Validate, Iterate
```

### Example: "Real-World Skill Examples"

**Question**: Where do 10+ detailed skill creation examples go?

**Analysis**:
- Is it executable? NO (learning material)
- Is it reusable? YES (team learning, reference for future skills)
- Is it skill-specific? NO (examples benefit everyone)
- Is it large? YES (10+ examples = 500+ lines)

**Decision**: SPLIT
```
.claude/skills/building-skills/SKILL.md
├── One inline example (database skill - 50 lines)
└── Reference: "For more examples: @../../docs/skills/skill-examples.md"

docs/skills/skill-examples.md
└── 10+ detailed examples (500 lines)
```

### Example: "Anthropic Specifications"

**Question**: Where do complete YAML specs, naming rules, validation requirements go?

**Analysis**:
- Is it executable? NO (reference material)
- Is it reusable? YES (anyone creating skills)
- Is it skill-specific? NO (general specification)
- Is it large? YES (70 pages of specs)

**Decision**: PUT IN MEMORY
```
docs/skills/building-skills-knowledge-base.md

Referenced by:
- .claude/skills/building-skills/SKILL.md
- Team can read without skill activation
- Single source of truth
```

## Anti-Patterns to Avoid

### ❌ Don't Duplicate Content

**Bad**:
```
.claude/skills/building-skills/degrees-of-freedom.md (500 lines)
.claude/skills/deploying-agents/degrees-of-freedom.md (500 lines)
.claude/skills/mcp-integration/degrees-of-freedom.md (500 lines)
```

**Good**:
```
docs/skills/degrees-of-freedom.md (500 lines - single source)

Referenced by:
- building-skills/SKILL.md
- deploying-agents/SKILL.md
- mcp-integration/SKILL.md
```

### ❌ Don't Put Workflows in Memory

**Bad**:
```
docs/skills/skill-creation-workflow.md
(Contains: Step-by-step how to create skill)

.claude/skills/building-skills/SKILL.md
(Contains: Just references the workflow)
```

**Good**:
```
.claude/skills/building-skills/SKILL.md
(Contains: The actual workflow steps)

docs/skills/anthropic-specifications.md
(Contains: Reference specs that workflow uses)
```

### ❌ Don't Put Tool Files in Memory

**Bad**:
```
docs/skills/templates/minimal-skill.md
docs/skills/scripts/init-skill.sh
```

**Good**:
```
.claude/skills/building-skills/templates/minimal-skill.md
.claude/skills/building-skills/scripts/init-skill.sh
```

Tools belong with the skill that uses them.

## Summary: Quick Decision Guide

```
Is it a WORKFLOW or PROCEDURE?
└─ YES → PUT IN SKILL

Is it a TOOL (template/script)?
└─ YES → PUT IN SKILL

Is it a CONCEPT or PATTERN?
├─ Used by multiple skills? → PUT IN MEMORY
└─ Only this skill? → PUT IN SKILL (or split if large)

Is it SPECIFICATIONS or REFERENCE?
└─ YES → PUT IN MEMORY

Is it EXAMPLES?
├─ One example for workflow demo → PUT IN SKILL (inline)
└─ Multiple examples for learning → PUT IN MEMORY

Is it KNOWLEDGE or CONTEXT?
├─ Domain-specific (agents, MCP, etc.) → PUT IN MEMORY (docs/domain/)
└─ Skill-specific integration → PUT IN SKILL (if complex)
```

---

**Golden Rule**: Skills execute, Memories inform. If Claude needs it to DO something, it's in the skill. If Claude needs it to UNDERSTAND something, it's in memory.
