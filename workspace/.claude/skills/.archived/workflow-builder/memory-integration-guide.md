# Memory-Skills Integration Guide

## Overview

This guide explains the **systematic methodology** for building skills with proper memory integration, based on the workflow used to create the Fresh Mountain project's Skills and Memories system.

**Purpose**: Teach the complete process from research to implementation, showing how to:
1. Research a topic and build a scientific knowledge base
2. Distill knowledge into minimal but complete skill templates
3. Integrate memories with skills bidirectionally
4. Maintain consistency across the system

---

## The Complete Workflow: Research → Knowledge Base → Skill Template

### Conceptual Framework

```
User Need/Domain
    ↓
Phase 1: Research
    ↓
Scientific Knowledge Base (comprehensive reference)
    ↓
Phase 2: Distillation
    ↓
Skill Template (minimal essential context)
    ↓
Phase 3: Integration
    ↓
Memory References (bidirectional links)
    ↓
Operational Skill
```

---

## Phase 1: Research & Knowledge Base Creation

### Step 1: Identify the Domain

**Question**: What domain knowledge needs to be systematized?

**Example** (Building Skills skill):
- Domain: Agent Skills creation following Anthropic standards
- Need: Systematic way to create skills that follow best practices
- Gap: No internal documentation of Anthropic specifications

### Step 2: Research Authoritative Sources

**Primary Sources to Research**:
1. **Official Documentation**
   - Anthropic Developer Docs
   - GitHub repositories (anthropics/skills)
   - Specification documents

2. **Working Examples**
   - Official skills (skill-creator, pdf, mcp-builder)
   - Community implementations
   - Best practice patterns

3. **Technical Specifications**
   - YAML frontmatter requirements
   - File structure conventions
   - Naming patterns
   - Validation rules

**Research Commands**:
```bash
# Web research
WebSearch: "Anthropic Claude Code Skills specification"
WebSearch: "Claude Agent Skills best practices"

# Repository research
WebFetch: https://github.com/anthropics/skills
WebFetch: https://docs.claude.com/en/docs/claude-code/skills

# Example analysis
Read: official skill SKILL.md files
Analyze: patterns, structure, naming conventions
```

### Step 3: Build Comprehensive Knowledge Base

**File Location**: `docs/skills/building-skills-knowledge-base.md`

**Structure of Knowledge Base**:
```markdown
# [Topic] - Complete Knowledge Base

## Overview
- Definition
- Source documentation
- Version information

## Core Concepts
- Fundamental principles
- Key characteristics
- Design patterns

## Technical Specifications
- YAML requirements
- File structure
- Naming conventions
- Validation rules

## Best Practices
- Do's and don'ts
- Common patterns
- Anti-patterns to avoid

## Working Examples
- Real implementations
- Code snippets
- Complete workflows

## References
- Official documentation
- Specifications
- Related resources
```

**Real Example** (building-skills-knowledge-base.md):
```markdown
# Building Skills - Complete Knowledge Base

## Overview
Comprehensive guide for creating Agent Skills based on official
Anthropic documentation and best practices.

**Source**: Anthropic Developer Documentation, GitHub anthropics/skills
**Last Updated**: 2025-11-01
**Specification Version**: 1.0 (launched 2025-10-16)

## What Are Agent Skills?
**Definition**: Skills are modular, self-contained packages...

## Core Design Principle: Progressive Disclosure
### Three-Level Loading System
[Complete technical explanation with examples]

## SKILL.md Structure
### Required YAML Frontmatter
[Complete specification with validation rules]

## Skill Naming Conventions
### Gerund Form (Verb + -ing)
[Examples, anti-patterns, rationale]

[... continues for ~70 pages with complete reference material]
```

**Knowledge Base Characteristics**:
- ✅ **Comprehensive**: All details, specifications, edge cases
- ✅ **Authoritative**: Sourced from official documentation
- ✅ **Versioned**: Date and version tracking
- ✅ **Reference-Oriented**: Organized for lookup, not linear reading
- ✅ **Examples-Rich**: Real code, working patterns
- ❌ **NOT optimized for context window** (can be 50-100 pages)

---

## Phase 2: Distillation to Skill Template

### Distillation Principle

**From**: Comprehensive knowledge base (everything you might need)
**To**: Essential workflow guide (minimum you must know)

**Compression Ratio**: Typically 10:1 to 20:1
- Knowledge Base: 50-100 pages
- Skill Template: 5-10 pages (under 500 lines)

### Step 1: Identify Essential Workflows

**Question**: What are the 3-5 most common use cases?

**Example** (Building Skills):
1. Creating a simple skill (minimal structure)
2. Creating a skill with progressive disclosure (standard structure)
3. Creating a complex skill (multiple supporting files)
4. Validating a skill
5. Iterating based on usage

**Distillation Decision**:
- Include: Core workflows that cover 80% of use cases
- Reference: Advanced topics via `@knowledge-base.md`
- Omit: Edge cases, exhaustive specifications (keep in knowledge base)

### Step 2: Extract Minimal Essential Context

**What to Include in SKILL.md**:

1. **Core Workflow Steps**
   ```markdown
   ## Six-Phase Creation Process

   ### Phase 1: Understanding with Concrete Examples
   [Essential questions and approach]

   ### Phase 2: Planning Reusable Contents
   [Key decision points]

   [... phases 3-6 with actionable steps]
   ```

2. **Critical Decision Points**
   - When to use minimal vs standard vs complex structure
   - How to apply degrees of freedom (high/medium/low)
   - Validation checkpoints

3. **Working Templates**
   ```markdown
   ## YAML Frontmatter Template
   ```yaml
   ---
   name: skill-name-here
   description: Clear description...
   ---
   ```

4. **Common Patterns & Anti-Patterns**
   ```markdown
   ✅ Use gerund form: deploying-agents
   ❌ Avoid noun form: agent-deployer
   ```

**What to Reference (Not Include)**:
- Complete specification details → `@../../docs/skills/building-skills-knowledge-base.md`
- Exhaustive examples → knowledge base
- All validation rules → knowledge base
- Historical context → knowledge base

### Step 3: Implement Progressive Disclosure

**SKILL.md Structure** (300-500 lines):
```markdown
---
name: building-skills
description: [Concise, keyword-rich description]
---

# Building Skills - Meta-Skill

## Context Import
@../../docs/skills/building-skills-knowledge-base.md  # Full reference
@../../project.md                                      # Project context

## Overview
[2-3 paragraphs: what, why, key principle]

## Six-Phase Creation Process
[Essential steps with actionable instructions]

### Phase 1: Understanding
[Questions to ask, example format]

### Phase 2: Planning
[Structure decision matrix]

### Phase 3-6: Initialize, Write, Validate, Iterate
[Minimum viable workflow for each phase]

## Complete Example
[One end-to-end example showing the pattern]

## Validation Quick Reference
[Checklist format for fast reference]

## References
See knowledge base for complete specifications:
@../../docs/skills/building-skills-knowledge-base.md
```

**Distillation Metrics**:
- **Coverage**: 80% of use cases with 20% of content
- **Actionability**: Every section has clear next steps
- **Context Efficiency**: Under 500 lines, focused on workflows
- **Completeness**: Reference full knowledge base for details

---

## Phase 3: Memory-Skills Integration

### Understanding the Relationship

**Memories** (CLAUDE.md and docs/):
- **Loaded**: Automatically at startup (project context)
- **Purpose**: Provide persistent context, conventions, rules
- **Organization**: Topic-based, hierarchical

**Skills** (SKILL.md):
- **Loaded**: On-demand when activated
- **Purpose**: Provide specialized workflows and automation
- **Organization**: Domain-based, modular

**Integration**: Skills reference memories to inherit project context

---

## How to Add Memories to Skills

### Method 1: Direct Memory Import (@ Syntax)

**Import Syntax**:
```markdown
## Context Import

@../../CLAUDE.md                    # Project-level memory
@../../project.md                   # Project conventions
@../../CLAUDE_MASTER_RULES.md       # Execution rules
@../../docs/agents/architecture.md  # Domain-specific memory
```

**Path Resolution**:
- Skills located in: `.claude/skills/skill-name/`
- Memories located in: Project root or `docs/`
- Relative path: `@../../` goes up two levels (skill-name → skills → .claude → project root)

**Real Example** (deploying-agents skill):
```markdown
---
name: deploying-agents
description: Deploy new agents following LangGraph patterns...
---

# Agent Deployment Skill

## Context Import

Reference project conventions:
@../../project.md

Follow master execution rules:
@../../CLAUDE_MASTER_RULES.md

## Agent Architecture Patterns
[Skill-specific content that builds on imported context]
```

**What Gets Imported**:
- Project conventions (coding standards, tech stack)
- Execution rules (priorities, testing requirements)
- Domain knowledge (architecture patterns, best practices)
- Topic-specific documentation (agents, MCP, etc.)

**Progressive Disclosure with Imports**:
```markdown
# In SKILL.md (always loaded when skill activates)
@../../project.md                   # Core project context

# Reference for deep dive (loaded only when mentioned)
For complete architecture details, see @../../docs/agents/architecture.md
For deployment procedures, see @../../docs/agents/deployment.md
```

### Method 2: Inline Reference (Without Import)

**When to Use**: Point to memory for optional deep dive, not required for workflow

**Example**:
```markdown
## Advanced Configuration

For complete MCP authentication standards, see:
`docs/mcp/integration.md`

For this workflow, basic auth pattern is sufficient:
```python
headers = {"Authorization": "Menycibu"}
```

**Difference**:
- `@../../docs/mcp/integration.md` → Loads file content into context
- `docs/mcp/integration.md` (plain text) → Reference only, user can read if needed

### Method 3: Implicit Memory Context

**Skills inherit project context automatically** because:
1. CLAUDE.md loaded at startup (before skill activation)
2. Skills execute within project context
3. No explicit import needed for global rules

**Example**:
```markdown
# No need to import these (already in context from CLAUDE.md):
- Python 3.x with type hints (project standard)
- Use venv_linux (project convention)
- No comments unless requested (coding standard)
```

### Memory Import Best Practices

✅ **Do Import**:
- Domain-specific knowledge needed for workflow
- Architecture patterns to follow
- Conventions that guide decisions

✅ **Don't Import**:
- General project info already in CLAUDE.md
- Content not needed for 80% of skill uses
- Large reference docs (use progressive disclosure instead)

**Example Decision Tree**:
```
Does skill need specific domain knowledge?
├─ YES → Import topic memory (@../../docs/domain/topic.md)
├─ NO → Rely on global CLAUDE.md context
└─ MAYBE → Reference in text, don't import (progressive disclosure)
```

---

## How to Add Skills to Memories

### Method 1: Document in CLAUDE.md

**Purpose**: Central registry of available skills with activation patterns

**Location**: `CLAUDE.md` (project root)

**Structure**:
```markdown
# Claude Global Configuration

## 🔌 SKILLS INTEGRATION

### Available Skills

**Project Skills** (`.claude/skills/` - in git, team-shared):

1. **skill-name**
   - Purpose: Brief description of what skill does
   - Triggers: "keyword phrase", "action pattern"
   - References: @docs/topic/file.md

2. **another-skill**
   - Purpose: ...
   - Triggers: ...
   - References: ...

### Skills-Memory Integration
Skills automatically inherit project context via `@../../` imports in SKILL.md files.

**Example Flow**:
```
User: "Deploy calendar agent"
    ↓
deploying-agents skill activates
    ↓
Loads: @docs/agents/architecture.md (LangGraph patterns)
       @project.md (tech stack, conventions)
       @CLAUDE_MASTER_RULES.md (execution rules)
    ↓
Executes: Following project patterns with validation
```

### Skill Activation
- **Model-Invoked**: Claude autonomously decides based on description
- **Progressive Disclosure**: Load metadata → SKILL.md → supporting files
- **Context-Aware**: Skills respect master rules and project conventions

**Reference**: @docs/skills/guidelines.md
```

**Real Example** (Fresh Mountain CLAUDE.md):
```markdown
## 🔌 SKILLS INTEGRATION

### Available Skills

1. **deploying-agents**
   - Deploy new specialist agents following LangGraph patterns
   - Triggers: "deploy agent", "create new agent"
   - References: @docs/agents/architecture.md

2. **mcp-integration**
   - Set up MCP endpoints with authentication standards
   - Triggers: "create MCP", "setup MCP server"
   - References: @docs/mcp/integration.md

3. **testing-workflows**
   - Automated testing with venv validation and A/B testing
   - Triggers: "run tests", "validate implementation"
   - References: @CLAUDE_MASTER_RULES.md (testing priorities)

4. **building-skills**
   - Meta-skill for creating new skills
   - Triggers: "create skill", "build new skill"
   - References: @docs/skills/building-skills-knowledge-base.md

5. **managing-servers**
   - SSH server management with critical safety protocols
   - Triggers: "manage server", "SSH hardening"
   - ⚠️ **Includes safety warnings for admin access changes**
```

### Method 2: Create Topic-Based Documentation

**Purpose**: Organize domain knowledge and reference skills

**Location**: `docs/skills/guidelines.md`

**Structure**:
```markdown
# Skills Usage Guidelines

## Overview
[What skills are, how they work]

## Available Skills

### Project Skills (`.claude/skills/`)

#### skill-name
**Purpose**: What this skill does
**When to Use**: Specific scenarios
**Triggers**: Keyword patterns
**References**: Related memories

[Detailed usage information]

## How Skills Work

### Model-Invoked Behavior
[Explanation of activation patterns]

### Progressive Disclosure
[Explanation of three-level loading]

### Memory Integration
[How skills reference project memories]

## Creating New Skills
[Link to building-skills skill]

## Troubleshooting Skills
[Common issues and solutions]
```

**Real Example** (docs/skills/guidelines.md):
```markdown
# Skills Usage Guidelines

## Available Skills

### deploying-agents
**Purpose**: Automate new agent deployment following LangGraph patterns
**When to Use**: Creating new specialist agents for CoreTeam system
**Triggers**: "deploy agent", "create new agent", "add specialist"
**References**: `@../../docs/agents/architecture.md`, `@../../project.md`

[Complete usage documentation with examples]
```

### Method 3: Topic-Specific Memory References

**Purpose**: Link skills to relevant domain documentation

**Example** (docs/agents/deployment.md):
```markdown
# Agent Deployment Procedures

## Deployment Checklist
[Standard checklist...]

## Automated Deployment

**Using deploying-agents Skill**:
The `deploying-agents` skill automates this workflow following
the procedures documented here.

Activation: "Deploy new [domain] agent"

The skill will:
1. Load architecture patterns from `@architecture.md`
2. Follow project conventions from `@../../project.md`
3. Execute deployment checklist
4. Run validation tests

**Reference**: `.claude/skills/deploying-agents/SKILL.md`
```

### Memory-to-Skills Linking Best Practices

✅ **Include in Memory**:
- Skill name and purpose
- Trigger keywords for activation
- What memories/docs the skill references
- Example activation flows

✅ **Organize Hierarchically**:
```
CLAUDE.md (root)
├── Skills Integration section (registry of all skills)
└── References to topic docs

docs/skills/guidelines.md
├── Detailed usage for each skill
└── Creation and troubleshooting guides

docs/[domain]/[topic].md
└── Domain-specific skills mentioned in context
```

---

## Bidirectional Integration Pattern

### Complete Integration Example

**Scenario**: Creating and integrating the `deploying-agents` skill

**Step 1: Create Knowledge Base**
```bash
# Research LangGraph patterns, agent architecture
# Create comprehensive reference
docs/agents/architecture.md (architecture patterns)
docs/agents/deployment.md (deployment procedures)
```

**Step 2: Create Skill with Memory Imports**
```markdown
# .claude/skills/deploying-agents/SKILL.md

---
name: deploying-agents
description: Deploy new agents following LangGraph multi-agent
architecture patterns. Use when creating new specialist agents
for the CoreTeam system.
---

## Context Import
@../../project.md                    # Project conventions
@../../CLAUDE_MASTER_RULES.md        # Execution rules

## Agent Architecture Patterns
[Skill workflow that builds on imported context]

For complete architecture details, see:
@../../docs/agents/architecture.md

For deployment procedures, see:
@../../docs/agents/deployment.md
```

**Step 3: Document Skill in Memories**
```markdown
# CLAUDE.md

## 🔌 SKILLS INTEGRATION

1. **deploying-agents**
   - Deploy new specialist agents following LangGraph patterns
   - Triggers: "deploy agent", "create new agent"
   - References: @docs/agents/architecture.md
```

```markdown
# docs/agents/deployment.md

## Automated Deployment

**When deploying new agents**: Use `deploying-agents` skill
for automated workflow

The skill follows procedures documented in this file and
references architecture patterns from `architecture.md`.
```

**Step 4: Create Topic Guidelines**
```markdown
# docs/skills/guidelines.md

### deploying-agents
**Purpose**: Automate new agent deployment following LangGraph patterns
**When to Use**: Creating new specialist agents for CoreTeam system
**Triggers**: "deploy agent", "create new agent", "add specialist"
**References**: `@../../docs/agents/architecture.md`, `@../../project.md`

[Detailed usage, examples, troubleshooting]
```

**Result**: Bidirectional integration
- **Skill → Memory**: Imports project.md, architecture.md, deployment.md
- **Memory → Skill**: CLAUDE.md documents skill, docs reference skill

---

## Minimal Context Approach

### Principle: Load Only What's Needed, When It's Needed

**Three-Level Loading**:
```
Startup (Always Loaded):
└── CLAUDE.md with skill metadata (name + description)
    ↓
Skill Activation (Loaded on Demand):
├── SKILL.md body (~300-500 lines)
└── Imported memories via @../../ syntax
    ↓
Progressive Disclosure (Loaded as Referenced):
├── Supporting files (@advanced.md, @reference.md)
└── Knowledge bases (when explicit deep dive needed)
```

### Context Budget Management

**Assume**:
- Startup context: ~10K tokens (CLAUDE.md + project.md + rules)
- Skill activation: +5K tokens (SKILL.md + essential imports)
- Progressive disclosure: +10K tokens (if advanced features used)
- Total: ~25K tokens (well under 200K limit)

**Example** (building-skills skill):
```
Startup:
├── CLAUDE.md (~2K tokens) ✓
└── Skill metadata: "building-skills: Create new Agent Skills..." (~50 tokens) ✓

User: "Create a new skill for database management"
↓
Skill Activates:
├── building-skills/SKILL.md (~5K tokens) ✓
└── Imports: project.md (~2K tokens) ✓
Total: ~9K tokens

Skill References (NOT automatically loaded):
├── building-skills-knowledge-base.md (~50K tokens) ✗
└── Available if needed via explicit reference

Claude: "For complete specifications, I can reference the knowledge base.
         For this standard use case, I'll follow the six-phase process..."
```

### Minimal Essential Content Guidelines

**SKILL.md should contain**:
1. ✅ Workflows for 80% of use cases
2. ✅ Critical decision points
3. ✅ Working templates
4. ✅ Validation checklists
5. ✅ Common troubleshooting

**SKILL.md should NOT contain**:
1. ❌ Complete specifications (→ knowledge base)
2. ❌ All possible edge cases (→ knowledge base)
3. ❌ Historical context (→ knowledge base)
4. ❌ Exhaustive examples (→ knowledge base)
5. ❌ Rarely-used advanced features (→ supporting files)

**When to Split Content**:
```markdown
# SKILL.md approaching 500 lines?

## Option 1: Progressive Disclosure
# SKILL.md (~300 lines)
For advanced workflows, see @advanced.md
For complete API reference, see @reference.md

# advanced.md (~400 lines)
[Advanced use cases]

# reference.md (~500 lines)
[Complete specifications]

## Option 2: Reference Knowledge Base
# SKILL.md (~400 lines)
For complete specifications, see:
@../../docs/topic/knowledge-base.md

# knowledge-base.md (~5000 lines)
[Comprehensive reference, loaded only when needed]
```

---

## Complete Workflow: Step-by-Step User Instructions

### Creating a New Skill with Memory Integration

#### Prerequisites
- Identify domain/topic for skill
- Understand what workflows need automation
- Know related project memories (if any)

#### Workflow

**Step 1: Research the Topic** (Phase 1)
```bash
# Research authoritative sources
WebSearch: "[topic] best practices"
WebFetch: https://official-docs-url

# Analyze working examples
Read: examples/existing-implementation.py

# Document research notes
mkdir -p docs/[topic]
touch docs/[topic]/research-notes.md

# Gather 3-5 concrete use cases
echo "Example 1: [specific scenario]" >> docs/[topic]/research-notes.md
echo "Example 2: [another scenario]" >> docs/[topic]/research-notes.md
```

**Step 2: Build Knowledge Base** (if needed for complex topics)
```bash
# Create comprehensive reference
cat > docs/[topic]/[topic]-knowledge-base.md <<'EOF'
# [Topic] - Complete Knowledge Base

## Overview
[Definition, sources, version]

## Core Concepts
[Fundamental principles]

## Technical Specifications
[Detailed specs, all edge cases]

## Best Practices
[Do's, don'ts, patterns, anti-patterns]

## Working Examples
[Real implementations]

## References
[Official docs, specifications]
EOF

# Build out knowledge base (50-100 pages OK)
# Include: specifications, edge cases, exhaustive examples
# This is the authoritative reference
```

**Step 3: Distill to Skill Template**
```bash
# Create skill directory
mkdir -p .claude/skills/[skill-name]

# Create SKILL.md with essential workflows
cat > .claude/skills/[skill-name]/SKILL.md <<'EOF'
---
name: skill-name
description: Clear description of what this skill does and when to use it. Include domain keywords and trigger scenarios.
---

# Skill Title

## Context Import
@../../project.md
@../../docs/[topic]/[topic]-knowledge-base.md  # If exists

## Overview
[Brief introduction - what, why, key principle]

## Workflow
[Essential steps for 80% of use cases]

## Examples
[Working code examples]

## References
See knowledge base for complete details:
@../../docs/[topic]/[topic]-knowledge-base.md
EOF
```

**Step 4: Add Memory Imports to Skill**
```markdown
# Edit .claude/skills/[skill-name]/SKILL.md

## Context Import

# Import relevant project memories
@../../project.md                           # Always import
@../../CLAUDE_MASTER_RULES.md              # If execution rules matter
@../../docs/[related-topic]/[file].md      # Domain-specific context

# Progressive disclosure for deep dive
For complete specifications, see:
@../../docs/[topic]/[topic]-knowledge-base.md
```

**Step 5: Document Skill in Memories**
```markdown
# Edit CLAUDE.md

## 🔌 SKILLS INTEGRATION

### Available Skills

X. **skill-name**
   - [Purpose description]
   - Triggers: "keyword phrase", "action pattern"
   - References: @docs/[topic]/[file].md
```

```markdown
# Edit docs/skills/guidelines.md

### skill-name
**Purpose**: [What it does]
**When to Use**: [Specific scenarios]
**Triggers**: [Activation keywords]
**References**: [Memory files skill uses]

[Detailed usage documentation]
```

```markdown
# If domain-specific, edit docs/[topic]/[file].md

## Automated [Task] via Skill

The `skill-name` skill automates this workflow.

Activation: "[trigger phrase]"

The skill will:
1. [Action 1]
2. [Action 2]

**Reference**: `.claude/skills/skill-name/SKILL.md`
```

**Step 6: Validate Integration**
```bash
# Check YAML frontmatter
head -20 .claude/skills/[skill-name]/SKILL.md

# Verify imports resolve
grep "@../../" .claude/skills/[skill-name]/SKILL.md
# Ensure all referenced files exist

# Check skill documented in memories
grep "skill-name" CLAUDE.md
grep "skill-name" docs/skills/guidelines.md

# Test skill activation
# Try requests that should trigger skill
# Verify skill activates correctly
```

**Step 7: Test Complete Integration**
```bash
# Test memory imports work
# Skill should have access to imported context

# Test skill follows project conventions
# Execution should match CLAUDE_MASTER_RULES.md

# Test progressive disclosure
# Verify supporting files load only when referenced

# Test bidirectional links
# Memory → Skill references work
# Skill → Memory imports work
```

**Step 8: Iterate Based on Usage**
```markdown
# Monitor skill behavior
# Document what works, what needs improvement

# Update skill based on feedback
# Edit SKILL.md with improvements

# Update memories if needed
# If skill changes significantly, update CLAUDE.md documentation

# Version control changes
git add .claude/skills/[skill-name]/
git add docs/[topic]/
git add CLAUDE.md
git commit -m "skill-name: [improvement description]"
```

---

## Real-World Example: Building the building-skills Skill

### The Meta-Process Applied to Itself

**Context**: Need a systematic way to create skills following Anthropic standards

### Phase 1: Research

**Actions Taken**:
```bash
# 1. Searched official documentation
WebSearch: "Anthropic Claude Code Skills specification"
WebSearch: "Claude Agent Skills best practices"

# 2. Fetched authoritative sources
WebFetch: https://docs.claude.com/en/docs/claude-code/skills
WebFetch: https://github.com/anthropics/skills

# 3. Analyzed working examples
Read: skill-creator/SKILL.md  # Official meta-skill
Read: pdf/SKILL.md            # Progressive disclosure example
Read: mcp-builder/SKILL.md    # Standard workflow example

# 4. Documented findings
Created: research notes with:
- YAML frontmatter specifications
- Progressive disclosure pattern
- Gerund naming convention
- Degrees of freedom concept
- Validation requirements
```

### Phase 2: Knowledge Base Creation

**Created**: `docs/skills/building-skills-knowledge-base.md` (~70 pages)

**Content Included**:
- Complete YAML specification with validation rules
- Progressive disclosure explanation with diagrams
- Skill naming conventions with 20+ examples
- Description writing guide with templates
- Degrees of freedom concept with examples
- File structure patterns (minimal/standard/complex)
- Complete validation checklist
- Anti-patterns with explanations
- Templates for all skill types
- Official examples analysis

**Characteristics**:
- Comprehensive (everything researched)
- Authoritative (sourced from Anthropic)
- Reference-oriented (not linear workflow)
- ~70 pages (not context-optimized)

### Phase 3: Distillation to Skill

**Created**: `.claude/skills/building-skills/SKILL.md` (~500 lines, ~5 pages)

**Distillation Decisions**:

**Included** (essential workflow):
```markdown
## Six-Phase Creation Process

### Phase 1: Understanding with Concrete Examples
[Key questions, example format]

### Phase 2: Planning Reusable Contents
[Structure decision matrix]

### Phase 3: Initialize Skill
[Directory creation, YAML template]

### Phase 4: Write the Skill
[Writing style, content guidelines, degrees of freedom]

### Phase 5: Validate the Skill
[Validation checklist]

### Phase 6: Iterate Based on Usage
[Monitoring and update process]

## Complete Example: Creating a Database Skill
[One end-to-end walkthrough]
```

**Referenced** (not included):
- Complete YAML specification → knowledge base
- All validation rules → knowledge base
- Exhaustive examples → knowledge base
- Anti-patterns catalog → knowledge base
- Historical context → knowledge base

**Compression**: ~70 pages → ~5 pages (14:1 ratio)

### Phase 4: Memory Integration

**Memory Imports Added** (Skill → Memory):
```markdown
# .claude/skills/building-skills/SKILL.md

## Context Import
@../../docs/skills/building-skills-knowledge-base.md
@../../project.md
```

**Skill Documentation Added** (Memory → Skill):
```markdown
# CLAUDE.md

4. **building-skills**
   - Meta-skill for creating new skills
   - Triggers: "create skill", "build new skill"
   - References: @docs/skills/building-skills-knowledge-base.md
```

```markdown
# docs/skills/guidelines.md

### Creating New Skills

Use `building-skills` skill for systematic skill creation.

The skill follows Anthropic best practices and provides
six-phase creation process with validation.

**Reference**: `.claude/skills/building-skills/SKILL.md`
```

### Result

**User Request**: "Create a skill for database management"

**Activation Flow**:
```
1. Startup: CLAUDE.md loaded (includes building-skills metadata)
2. Request matches: "create skill" trigger
3. building-skills skill activates
4. Loads: SKILL.md (~5K tokens)
5. Imports: project.md (~2K tokens)
6. Executes: Six-phase process
7. Has access to: knowledge base via @ reference (not auto-loaded)
8. Result: Systematic skill creation following best practices
```

**Context Efficiency**:
- Without distillation: 70-page knowledge base loaded every time (~50K tokens)
- With distillation: 5-page skill + imports (~7K tokens)
- Knowledge base available via progressive disclosure when needed
- **Savings**: ~43K tokens (86% reduction)

---

## Best Practices Summary

### Research → Knowledge Base
✅ Research authoritative sources first
✅ Build comprehensive reference (no size limit)
✅ Include all specifications, edge cases, examples
✅ Organize for reference lookup
✅ Version and date the knowledge base

### Knowledge Base → Skill Template
✅ Identify 3-5 most common workflows
✅ Distill to essential decision points
✅ Target 300-500 lines for SKILL.md
✅ Reference knowledge base for deep dive
✅ Include working templates and examples

### Adding Memories to Skills
✅ Import domain-specific context: `@../../docs/topic/file.md`
✅ Import project conventions: `@../../project.md`
✅ Use progressive disclosure for large references
✅ Don't import what's already in global CLAUDE.md
✅ Test that all imports resolve

### Adding Skills to Memories
✅ Document in CLAUDE.md (central registry)
✅ Create topic guidelines in docs/skills/
✅ Reference skills in domain docs when relevant
✅ Include trigger keywords for activation
✅ Show example integration flows

### Minimal Context Approach
✅ Keep SKILL.md under 500 lines
✅ Split content via progressive disclosure
✅ Reference (don't import) large knowledge bases
✅ Load only essential context at activation
✅ Make deep references available but not auto-loaded

---

## Troubleshooting

### Knowledge Base Too Large
**Problem**: Knowledge base is 100+ pages
**Solution**: This is OK! Knowledge bases are references, not always loaded. Use progressive disclosure in skill.

### Skill Doesn't Activate
**Problem**: Request doesn't trigger skill
**Solution**:
1. Check description has relevant keywords
2. Add trigger examples to CLAUDE.md documentation
3. Make description more specific

### Import Path Not Resolving
**Problem**: `@../../path/file.md` not found
**Solution**:
```bash
# From skill directory, verify path
cd .claude/skills/skill-name/
ls ../../docs/topic/file.md  # Should exist

# Path structure:
# .claude/skills/skill-name/SKILL.md
# ../../ goes to project root
# Then docs/topic/file.md
```

### Too Much Context Loading
**Problem**: Context window filling up
**Solution**: Use progressive disclosure
```markdown
# Instead of importing everything:
@../../docs/complete-reference.md  # 50K tokens

# Reference it:
For complete reference, see @../../docs/complete-reference.md
# Only loads if explicitly needed
```

### Skill and Memory Out of Sync
**Problem**: Skill updated but memory still references old behavior
**Solution**: Update bidirectional links
```bash
# Update skill
vim .claude/skills/skill-name/SKILL.md

# Update memory documentation
vim CLAUDE.md
vim docs/skills/guidelines.md

# Commit together
git add .claude/skills/skill-name/ CLAUDE.md docs/
git commit -m "Sync skill and memory docs"
```

---

## References

### Related Files
- `SKILL.md` - This skill's main workflow guide
- `../../docs/skills/building-skills-knowledge-base.md` - Complete reference
- `../../docs/skills/guidelines.md` - Skills usage in project
- `../../CLAUDE.md` - Project memory with skill registry

### Official Documentation
- Anthropic Skills Docs: https://docs.claude.com/en/docs/claude-code/skills
- Skills Repository: https://github.com/anthropics/skills
- Best Practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices

---

**This guide is the meta-documentation showing the process used to create the Fresh Mountain Skills and Memories system. Use it as a template for creating systematic, well-integrated skills in any domain.**
