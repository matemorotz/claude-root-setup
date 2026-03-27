# Building Skills - Complete Knowledge Base

## Overview
Comprehensive guide for creating Agent Skills based on official Anthropic documentation and best practices.

**Source**: Anthropic Developer Documentation, GitHub anthropics/skills repository
**Last Updated**: 2025-11-01
**Specification Version**: 1.0 (launched 2025-10-16)

---

## What Are Agent Skills?

**Definition**: Skills are modular, self-contained packages that extend Claude's capabilities by providing specialized knowledge, workflows, and tools.

**Skills Provide**:
1. Specialized workflows
2. Tool integrations
3. Domain expertise
4. Bundled resources (scripts, templates, documentation)

**Key Characteristics**:
- **Model-Invoked**: Claude autonomously decides when to use a Skill based on context
- **Progressive Disclosure**: Load information only as needed (metadata → SKILL.md → supporting files)
- **Shareable**: Can be distributed via git (project skills) or plugins
- **Extensible**: Add new capabilities without modifying core system

---

## Core Design Principle: Progressive Disclosure

### Three-Level Loading System

```
Level 1: Metadata (Always Loaded)
├── name
└── description
    ↓ (loaded at startup into system prompt)

Level 2: SKILL.md Body (Loaded on Demand)
├── Instructions
├── Workflows
└── Examples
    ↓ (loaded when skill activates via Read tool)

Level 3: Supporting Files (Loaded as Needed)
├── scripts/
├── reference/
└── templates/
    ↓ (loaded only when specific content referenced)
```

### Why Progressive Disclosure Matters

- **Context Window Efficiency**: Don't load entire skill into context when only metadata needed
- **Scalability**: Skills can contain extensive documentation without overwhelming context
- **Performance**: Faster skill selection when only descriptions are evaluated
- **Composability**: Multiple skills can coexist without context bloat

### Progressive Disclosure in Practice

**Example: PDF Skill**
```
pdf/
├── SKILL.md           # Core instructions (~300 lines)
├── forms.md           # Form-filling details (~200 lines)
└── reference.md       # Complete API reference (~500 lines)
```

- Startup: Load name "pdf" and description
- Activation: Read SKILL.md for general PDF operations
- Form Filling: Read forms.md only when filling PDF forms
- Advanced Operations: Read reference.md only when needed

---

## SKILL.md Structure

### Required YAML Frontmatter

```yaml
---
name: skill-name-here
description: Clear description of what this skill does and when to use it
---
```

#### Field Specifications

**name** (Required)
- **Format**: hyphen-case (lowercase-with-hyphens)
- **Characters**: Lowercase Unicode alphanumeric + hyphens only
- **Length**: Maximum 64 characters
- **Convention**: Use gerund form (verb + -ing)
  - ✅ `processing-pdfs`, `analyzing-data`, `deploying-agents`
  - ❌ `pdf-processor`, `data-analyzer`, `agent-deployer`
- **Must Match**: Directory name must match skill name
- **No XML Tags**: Cannot contain `<` or `>` characters

**description** (Required)
- **Length**: Maximum 1024 characters
- **Cannot Be Empty**: Must contain meaningful description
- **Voice**: Third person
  - ✅ "Analyzes code for security vulnerabilities"
  - ❌ "I analyze code" or "You can use this to analyze"
- **Content**: Explain BOTH what it does AND when to use it
- **Keywords**: Include domain-specific terms for better matching
- **No XML Tags**: Cannot contain XML tags

### Optional YAML Frontmatter

```yaml
---
name: example-skill
description: Example skill demonstrating optional fields
license: MIT
allowed-tools: [Read, Write, Bash]
metadata:
  author: "Team Name"
  version: "1.0.0"
  category: "development"
---
```

**license** (Optional)
- **Format**: Short license name (e.g., "MIT", "Apache-2.0", "GPL-3.0")
- **Purpose**: Specify skill's license for distribution

**allowed-tools** (Optional, Claude Code only)
- **Format**: Array of tool names
- **Purpose**: Pre-approve specific tools for skill execution
- **Effect**: When specified, Claude can only use listed tools without additional permission
- **Use Case**: Restrict skill to safe operations (e.g., Read-only skills)

**metadata** (Optional)
- **Format**: Key-value string map (nested YAML)
- **Purpose**: Custom metadata for skill management
- **Examples**: author, version, category, tags

### Markdown Body

**No Restrictions**: The markdown content after frontmatter has no specific format requirements

**Best Practices**:
- Keep under 500 lines for optimal performance
- Use clear section headers
- Include concrete examples
- Provide step-by-step workflows
- Add troubleshooting section

---

## Skill Naming Conventions

### Gerund Form (Verb + -ing)

**Why Gerund Form?**
- Describes ongoing action/capability
- More natural for "what the skill does"
- Consistent across all official Anthropic skills

**Examples from Official Repository**:
- ✅ `processing-pdfs` - Processes PDF documents
- ✅ `analyzing-spreadsheets` - Analyzes Excel spreadsheets
- ✅ `creating-presentations` - Creates PowerPoint presentations
- ✅ `deploying-agents` - Deploys new agents
- ✅ `managing-databases` - Manages database operations

**Anti-Patterns**:
- ❌ `pdf-processor` - Noun form
- ❌ `spreadsheet-analysis` - Noun form
- ❌ `presentation-creator` - Noun form
- ❌ `helper` - Too vague
- ❌ `utils` - Too generic
- ❌ `tool` - Reserved word concept

---

## Description Writing Guide

### Anatomy of a Good Description

**Template**:
```
[Action verb] [object] [using/with] [method/technology].
Use when [specific trigger scenario].
[Key capability or constraint].
```

**Examples**:

**Excellent**:
```yaml
description: "Deploy new specialist agents following LangGraph multi-agent architecture patterns. Use when creating new agents for the CoreTeam system. Includes agent template, state management, and integration with governor."
```
- ✅ Action-focused ("Deploy new specialist agents")
- ✅ Method specified ("LangGraph multi-agent architecture")
- ✅ Clear trigger ("when creating new agents")
- ✅ System context ("CoreTeam system")
- ✅ Key features listed

**Good**:
```yaml
description: "Create MCP servers to integrate external APIs with proper authentication and error handling. Use when building Model Context Protocol endpoints."
```
- ✅ Clear action and object
- ✅ Key requirements mentioned
- ✅ Trigger scenario provided

**Poor**:
```yaml
description: "Helps with agents"
```
- ❌ Too vague ("helps with")
- ❌ No trigger scenario
- ❌ No method or context
- ❌ No key features

**Bad**:
```yaml
description: "Agent tool"
```
- ❌ Extremely vague
- ❌ No action verb
- ❌ No usage context

### Description Checklist

- [ ] Written in third person
- [ ] Contains action verb
- [ ] Specifies what the skill does
- [ ] Explains when to use it
- [ ] Includes domain-specific keywords
- [ ] Under 1024 characters
- [ ] No XML tags
- [ ] Helps Claude decide if skill applies

---

## Degrees of Freedom

### Concept
Match specificity to task complexity and error-proneness.

### High Freedom (Multiple Valid Approaches)

**When**: Creative tasks, multiple solutions acceptable
**Guidance Level**: Minimal, general principles

**Example**:
```markdown
## Creating Algorithmic Art

Explore creative approaches:
- Experiment with different algorithms
- Vary color palettes
- Try different composition rules

Consider: fractals, noise functions, particle systems, or cellular automata.
```

### Medium Freedom (Preferred Pattern)

**When**: Standard tasks with best practices
**Guidance Level**: Recommended approach with configuration options

**Example**:
```markdown
## Setting Up MCP Server

Recommended structure:
1. Create FastAPI application
2. Implement authentication middleware
3. Define tool endpoints following pattern:
   - POST /tools/{tool_name}
4. Add health check endpoint

Customize port, authentication method, and tool implementations.
```

### Low Freedom (Exact Sequence)

**When**: Error-prone operations requiring specific order
**Guidance Level**: Detailed step-by-step instructions

**Example**:
```markdown
## SSH Security Hardening

⚠️ CRITICAL: Follow exact order to avoid lockout

1. FIRST: Verify current SSH access
   ```bash
   ssh user@server 'echo "Access confirmed"'
   ```

2. Create backup SSH key
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/backup_key
   ```

3. Add backup key to server
   ```bash
   ssh-copy-id -i ~/.ssh/backup_key user@server
   ```

4. TEST backup key in NEW terminal
   ```bash
   ssh -i ~/.ssh/backup_key user@server
   ```

5. ONLY AFTER SUCCESSFUL TEST: Proceed with hardening
```

---

## File Structure Patterns

### Minimal Skill

```
my-skill/
└── SKILL.md
```

**Use When**:
- Simple, straightforward workflow
- All instructions fit under 500 lines
- No scripts or templates needed

### Standard Skill

```
my-skill/
├── SKILL.md           # Core instructions
├── reference.md       # Detailed documentation
└── examples/
    ├── example1.txt
    └── example2.txt
```

**Use When**:
- SKILL.md approaching 500 line limit
- Additional reference material helpful
- Examples improve understanding

### Complex Skill

```
my-skill/
├── SKILL.md           # Core instructions (~300 lines)
├── reference.md       # API/technical reference (~500 lines)
├── workflows.md       # Detailed workflows (~400 lines)
├── scripts/
│   ├── helper.py
│   ├── validator.sh
│   └── template_generator.py
├── templates/
│   ├── basic-template.txt
│   └── advanced-template.txt
└── examples/
    ├── simple/
    └── advanced/
```

**Use When**:
- Complex domain with multiple workflows
- Executable scripts improve reliability
- Templates ensure consistency
- Multiple usage patterns

### Document Skills Pattern (Official Anthropic)

```
pdf/
├── SKILL.md           # Overview & quick start (~250 lines)
├── forms.md           # PDF form handling (~200 lines)
├── reference.md       # Complete library reference (~500 lines)
└── scripts/
    ├── extract_text.py
    ├── merge_pdfs.py
    └── fill_form.py
```

**Progressive Disclosure**:
1. SKILL.md: General PDF operations
2. forms.md: Only when filling forms
3. reference.md: Only when advanced operations needed
4. scripts/: Loaded when specific script referenced

---

## Content Guidelines

### What to Include

#### ✅ Procedural Knowledge
```markdown
## Deploying an Agent

1. Create agent file in `/agents/` directory
2. Implement state schema matching system
3. Add to governor routing logic
4. Write unit tests
5. Run integration tests
6. Deploy to production
```

#### ✅ Domain-Specific Details
```markdown
## LangGraph State Management

State must be TypedDict with Annotated fields:
```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    context: str
```

#### ✅ Concrete Examples
```markdown
## Example: Calendar Agent

```python
def create_calendar_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("fetch_events", fetch_events)
    workflow.add_node("process_events", process_events)
    return workflow.compile()
```

#### ✅ Error Handling Patterns
```markdown
## Common Errors

**Port Already in Use**
```bash
# Check what's using port
sudo lsof -i :8001

# Kill process
sudo kill -9 <PID>
```

#### ✅ Validation Checklists
```markdown
## Deployment Checklist

- [ ] Tests passing
- [ ] Type hints included
- [ ] Error handling comprehensive
- [ ] Documentation updated
- [ ] Code reviewed
```

### What to Avoid

#### ❌ Time-Sensitive Information
```markdown
<!-- DON'T -->
As of October 2025, the latest version is 2.0

<!-- DO -->
Check the latest version in the documentation
```

#### ❌ Vague Guidance
```markdown
<!-- DON'T -->
Configure the server appropriately

<!-- DO -->
Configure server with these settings:
- Port: 8001
- Auth: API key in Authorization header
- Timeout: 30 seconds
```

#### ❌ Inconsistent Terminology
```markdown
<!-- DON'T -->
Create an agent... add a specialist... deploy the new worker

<!-- DO -->
Create an agent... add an agent... deploy the agent
```

#### ❌ Too Many Options
```markdown
<!-- DON'T -->
You can use FastAPI, Flask, Django, Tornado, Sanic, or Bottle

<!-- DO -->
Use FastAPI for MCP servers (recommended for async support)
Alternative: Flask for simpler synchronous servers
```

#### ❌ Assuming Tools Pre-installed
```markdown
<!-- DON'T -->
Run pytest to test

<!-- DO -->
Install pytest if needed:
```bash
/root/venv_linux/bin/pip install pytest
```
Then run:
```bash
/root/venv_linux/bin/pytest
```

---

## Skill Creation Process

### Phase 1: Understanding with Concrete Examples

**Goal**: Gather specific use cases before generalizing

**Questions to Ask**:
- What specific tasks will this skill handle?
- What are 3-5 concrete examples of skill usage?
- What are the inputs and expected outputs?
- What edge cases or errors might occur?
- What tools or technologies are involved?

**Example**:
```
Skill Idea: Managing SSH servers

Concrete Examples:
1. Harden SSH: Disable password auth, change port, setup fail2ban
2. Add new user: Create user, add SSH key, configure sudo
3. Rotate SSH keys: Generate new key, add to server, test, remove old
4. Audit access: List authorized keys, check active sessions
5. Troubleshoot connection: Test connectivity, check logs, verify config
```

### Phase 2: Planning Reusable Contents

**Analyze Examples for**:
- Common patterns across examples
- Necessary scripts or tools
- Reference materials needed
- Templates that ensure consistency

**Skill Structure Decision**:
```
SKILL.md (~400 lines)
├── Overview
├── Workflow: Hardening SSH
├── Workflow: User Management
├── Workflow: Key Rotation
└── Quick Reference

reference/
└── security-checklist.md (~300 lines)

scripts/
├── ssh-harden.sh
├── key-rotate.sh
└── audit-access.sh
```

### Phase 3: Initializing the Skill

**Manual Approach**:
```bash
# Create skill directory
mkdir -p .claude/skills/skill-name

# Create SKILL.md with template
cat > .claude/skills/skill-name/SKILL.md <<'EOF'
---
name: skill-name
description: Description of what this skill does and when to use it
---

# Skill Title

## Overview

## Workflow

## Examples

## References
EOF
```

**Using Official Scripts** (if available):
```bash
# From anthropics/skills repo
python scripts/init_skill.py skill-name --path .claude/skills/
```

### Phase 4: Writing the Skill

**Writing Style**: Imperative/Infinitive form

```markdown
<!-- GOOD -->
## Deploying an Agent

Create the agent file:
```bash
touch agents/calendar_agent.py
```

<!-- AVOID -->
## Deploying an Agent

You should create the agent file:
```bash
touch agents/calendar_agent.py
```
```

**Organization Tips**:
- Start with overview/context
- Progress from simple to complex
- Use clear section headers
- Include code blocks with syntax highlighting
- Add inline comments to code examples
- Provide troubleshooting section

### Phase 5: Validation

**YAML Frontmatter Validation**:
- [ ] `name` is hyphen-case, lowercase, under 64 chars
- [ ] `name` matches directory name
- [ ] `description` is non-empty, under 1024 chars
- [ ] `description` written in third person
- [ ] Optional fields follow correct format
- [ ] No XML tags in name or description

**Content Validation**:
- [ ] SKILL.md under 500 lines (or split appropriately)
- [ ] Uses progressive disclosure if complex
- [ ] Includes concrete examples
- [ ] Error handling documented
- [ ] No time-sensitive information
- [ ] Consistent terminology
- [ ] Clear workflow steps

**Testing Validation**:
- [ ] Test with multiple request phrasings
- [ ] Verify skill activates correctly
- [ ] Check skill doesn't activate incorrectly
- [ ] Test with different Claude models (if possible)
- [ ] Verify supporting files load correctly

**Using Official Validation** (if available):
```bash
# From anthropics/skills repo
python scripts/quick_validate.py .claude/skills/skill-name/
```

### Phase 6: Iteration

**Monitor Usage**:
- Does skill activate when expected?
- Does skill activate when NOT expected?
- Are workflows clear and effective?
- Do users need additional context?

**Iterate Based on**:
- User feedback
- Observed skill behavior
- Edge cases discovered
- New use cases identified

**Version Control**:
```bash
# Track changes
git add .claude/skills/skill-name/
git commit -m "skill-name: Add error handling for edge case X"

# Document changes
echo "## v1.1.0 - 2025-11-01\n- Added edge case handling" >> CHANGELOG.md
```

---

## Best Practices Summary

### Design
✅ Use progressive disclosure (metadata → SKILL.md → supporting files)
✅ Keep SKILL.md under 500 lines
✅ Match specificity to task complexity (degrees of freedom)
✅ Test across different Claude models
✅ Include concrete examples

### Naming & Description
✅ Use gerund form for names (verb + -ing)
✅ Write descriptions in third person
✅ Include what skill does AND when to use it
✅ Add domain-specific keywords
✅ Be specific, avoid vague terms

### Content
✅ Provide step-by-step workflows
✅ Include error handling
✅ Add validation checklists
✅ Use consistent terminology
✅ Avoid time-sensitive information

### Structure
✅ Start simple, add complexity as needed
✅ Split content when approaching 500 lines
✅ Organize supporting files logically
✅ Include table of contents for long reference files
✅ Use clear section headers

### Maintenance
✅ Version control skills in git
✅ Monitor skill activation patterns
✅ Iterate based on feedback
✅ Keep documentation synchronized
✅ Regular reviews and updates

---

## Anti-Patterns to Avoid

### ❌ Vague Naming
```yaml
# BAD
name: helper
description: Helps with stuff

# GOOD
name: deploying-agents
description: Deploy new specialist agents following LangGraph multi-agent architecture patterns
```

### ❌ Generic Descriptions
```yaml
# BAD
description: Agent deployment tool

# GOOD
description: Deploy new specialist agents following LangGraph multi-agent architecture patterns. Use when creating new agents for the CoreTeam system.
```

### ❌ Monolithic Skills
```
# BAD: Everything in one 2000-line SKILL.md
mega-skill/
└── SKILL.md (2000 lines!)

# GOOD: Progressive disclosure
well-designed-skill/
├── SKILL.md (300 lines)
├── advanced.md (400 lines)
└── reference.md (500 lines)
```

### ❌ Punting Error Handling
```markdown
<!-- BAD -->
If an error occurs, debug it appropriately

<!-- GOOD -->
Common Errors:

**Connection Refused (Port 8001)**
Check if server is running:
```bash
sudo systemctl status mcp-server
```

Start if needed:
```bash
sudo systemctl start mcp-server
```
```

### ❌ Windows File Paths
```bash
# BAD
C:\Users\name\project\file.txt

# GOOD
/root/project/file.txt
# or
~/project/file.txt
```

### ❌ Too Many Options
```markdown
<!-- BAD -->
Choose any of these 10 frameworks...

<!-- GOOD -->
Recommended: FastAPI (async support, modern)
Alternative: Flask (simpler, synchronous)
```

---

## Official Examples Analysis

### algorithmic-art
- **Name**: `algorithmic-art` ✅ (gerund-ish form)
- **Description**: "Create generative art using p5.js with seeded randomness"
- **Structure**: Likely includes templates and examples
- **Degree of Freedom**: High (creative exploration)

### mcp-builder
- **Name**: `mcp-builder` ❓ (not gerund, but accepted pattern)
- **Description**: "Create MCP servers to integrate external APIs"
- **Degree of Freedom**: Medium (preferred patterns with customization)

### pdf (Document Skill)
- **Name**: `pdf` ❓ (domain noun, document skill exception)
- **Structure**: SKILL.md + forms.md + reference.md
- **Progressive Disclosure**: ✅ Excellent example
- **Degree of Freedom**: Low to Medium (specific operations)

### skill-creator (Meta Skill)
- **Name**: `skill-creator` ✅
- **Purpose**: Meta-skill for creating skills
- **Structure**: SKILL.md + scripts (init, validate, package)
- **Self-Referential**: Uses progressive disclosure to teach progressive disclosure

---

## Validation Rules Reference

### YAML Frontmatter
```python
# Allowed properties
allowed_properties = [
    'name',           # Required
    'description',    # Required
    'license',        # Optional
    'allowed-tools',  # Optional
    'metadata'        # Optional
]

# Name validation
name_pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'  # hyphen-case
max_name_length = 64

# Description validation
max_description_length = 1024
description_must_not_be_empty = True
no_xml_tags = True  # No < or >

# Metadata validation
metadata_is_string_map = True  # Key-value pairs
```

### File Structure
```python
# Required
must_have_SKILL_md = True

# Directory name
directory_name_must_match_skill_name = True

# Content
SKILL_md_recommended_max_lines = 500
```

---

## Templates

### Basic Skill Template

```yaml
---
name: skill-name-here
description: Clear description of what this skill does and when Claude should use it
---

# Skill Title

## Overview
Brief introduction to what this skill does and why it exists.

## Workflow

### Step 1: Initial Setup
Detailed instructions for first step.

### Step 2: Main Operation
Core workflow steps.

### Step 3: Validation
How to verify success.

## Examples

### Example 1: Common Use Case
```bash
# Commands here
```

### Example 2: Advanced Use Case
```bash
# Commands here
```

## Troubleshooting

### Common Issue 1
**Problem**: Description
**Solution**: Fix

### Common Issue 2
**Problem**: Description
**Solution**: Fix

## Best Practices

### Do's
✓ Best practice 1
✓ Best practice 2

### Don'ts
✗ Anti-pattern 1
✗ Anti-pattern 2

## References
- Related documentation
- External resources
```

### Complex Skill with Progressive Disclosure

**SKILL.md**:
```yaml
---
name: complex-skill
description: Handles complex operations with multiple workflows and configurations
---

# Complex Skill

## Quick Start
Essential information to get started quickly.

## Common Workflows

### Workflow 1: Basic Operation
Most common use case with minimal steps.

### Workflow 2: Standard Operation
Standard approach for typical scenarios.

For advanced workflows, see @workflows.md
For complete API reference, see @reference.md
For troubleshooting guide, see @troubleshooting.md

## Examples
Most common examples here.

## Quick Reference
Frequently used commands and patterns.
```

**workflows.md** (loaded on demand):
```markdown
# Advanced Workflows

## Workflow 3: Complex Multi-Step Process
Detailed steps for complex scenarios.

## Workflow 4: Integration with External Systems
Integration patterns and considerations.
```

**reference.md** (loaded when needed):
```markdown
# Complete API Reference

## Table of Contents
1. [Functions](#functions)
2. [Parameters](#parameters)
3. [Return Values](#return-values)

[Extensive documentation...]
```

---

## Testing Skills

### Manual Testing

**Test Activation**:
```
Try these requests:
1. "Deploy a new calendar agent" (should activate deploying-agents)
2. "Create an MCP server" (should activate mcp-integration)
3. "Test the booking feature" (should activate testing-workflows)
```

**Test Non-Activation**:
```
These should NOT activate wrong skills:
1. "Tell me about agents" (should NOT activate deploying-agents)
2. "What is MCP?" (should NOT activate mcp-integration)
```

### Automated Validation

**Using Official Scripts**:
```bash
# Quick validation
python scripts/quick_validate.py .claude/skills/my-skill/

# Full validation and packaging
python scripts/package_skill.py .claude/skills/my-skill/
```

### Cross-Model Testing

**Test with Different Models**:
- Haiku: Fast, efficient (test clarity of instructions)
- Sonnet: Balanced (test typical usage)
- Opus: Most capable (test complex scenarios)

---

## References

### Official Documentation
- Anthropic Skills Docs: https://docs.claude.com/en/docs/claude-code/skills
- Best Practices: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- Official Skills Repo: https://github.com/anthropics/skills
- Skills Spec: https://github.com/anthropics/skills/blob/main/agent_skills_spec.md

### Key Skills to Study
- `skill-creator`: Meta-skill for creating skills
- `pdf`: Excellent progressive disclosure example
- `mcp-builder`: Good workflow structure
- `template-skill`: Minimal starting point

---

**This knowledge base is a living document. Update as new patterns emerge and official guidance evolves.**
