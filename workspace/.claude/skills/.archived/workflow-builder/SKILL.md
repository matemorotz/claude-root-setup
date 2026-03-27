---
name: building-skills
description: Create new Agent Skills following Anthropic best practices. Use when building skills for extending Claude's capabilities with specialized workflows, domain expertise, or tool integrations.
---

# Building Skills - Workflow

Create Agent Skills following Anthropic standards with minimal workflow and shared knowledge.

## Quick Start

**Automated**:
```bash
.claude/skills/building-skills/scripts/init-skill.sh
```

**Manual**:
1. Copy template: `templates/minimal-skill.md` → `.claude/skills/my-skill/SKILL.md`
2. Edit YAML frontmatter (name, description)
3. Add workflow steps
4. Validate: `scripts/validate-skill.sh .claude/skills/my-skill/`

## Six-Phase Creation Workflow

### Phase 1: Understanding
Gather 3-5 concrete examples before generalizing.

**Questions**:
- What specific tasks will this skill handle?
- What are the inputs and expected outputs?
- What tools or technologies are involved?
- What degree of freedom is appropriate? (High/Medium/Low)

**For detailed examples**: @../../docs/skills/skill-examples.md

### Phase 2: Planning
Analyze patterns and choose structure.

**Structure Options**:
- **Minimal**: SKILL.md only (<300 lines)
- **Standard**: SKILL.md + supporting files (<500 lines main)
- **Complex**: Progressive disclosure with multiple files

**For degrees of freedom guide**: @../../docs/skills/degrees-of-freedom.md

### Phase 3: Initialize
Create skill directory with template.

**Automated**:
```bash
scripts/init-skill.sh
# Follow prompts
```

**Manual**:
```bash
mkdir -p .claude/skills/skill-name
cp templates/minimal-skill.md .claude/skills/skill-name/SKILL.md
# Edit name, description, workflow
```

### Phase 4: Write
Follow writing guidelines.

**Style**: Imperative/infinitive form
```markdown
<!-- Good -->
Create the file:
```bash
touch file.txt
```

<!-- Avoid -->
You should create the file
```

**Keep SKILL.md focused on workflow** (~200-300 lines)
**Reference shared knowledge** using @../../docs/

**For complete specifications**: @../../docs/skills/building-skills-knowledge-base.md

### Phase 5: Validate
Check structure and content.

**Automated**:
```bash
scripts/validate-skill.sh .claude/skills/skill-name/
```

**Manual Checks**:
- [ ] YAML frontmatter valid (name, description)
- [ ] Name is hyphen-case, <64 chars
- [ ] Description is <1024 chars, third person
- [ ] SKILL.md under 500 lines
- [ ] Workflows are clear and actionable
- [ ] @ references resolve

**Test Activation**:
- Try requests that SHOULD trigger skill
- Try requests that should NOT trigger skill
- Verify workflows execute correctly

### Phase 6: Iterate
Monitor usage and improve.

**Update Process**:
```bash
# Document change
echo "## v1.1.0 - $(date +%Y-%m-%d)
- Improved workflow clarity" >> CHANGELOG.md

# Update files
# Edit SKILL.md or supporting files

# Validate
scripts/validate-skill.sh .claude/skills/skill-name/

# Commit
git add .claude/skills/skill-name/
git commit -m "skill-name v1.1.0: [description]"
```

## Templates

**Available templates**:
- `templates/minimal-skill.md` - Simple workflow (~100-300 lines)
- `templates/standard-skill.md` - Standard pattern (~300-500 lines)
- `templates/complex-skill.md` - Progressive disclosure (500+ lines split)

**Usage**:
```bash
cp templates/standard-skill.md .claude/skills/my-skill/SKILL.md
```

## Scripts

**init-skill.sh**: Create new skill from template
- Interactive prompts
- Validates input
- Creates directory structure

**validate-skill.sh**: Validate skill structure
- Checks YAML frontmatter
- Validates name/description
- Checks line count
- Verifies @ references

**Usage**:
```bash
# Create skill
scripts/init-skill.sh

# Validate skill
scripts/validate-skill.sh .claude/skills/my-skill/
```

## Skill-Memory Integration

**Keep skills minimal** (workflow focused):
```markdown
# In SKILL.md (~200 lines)
## Workflow
[Executable steps]

For detailed specs: @../../docs/topic/specifications.md
For examples: @../../docs/topic/examples.md
```

**Put detailed knowledge in shared memories**:
```
docs/
├── concepts/ (reusable patterns)
├── specifications/ (reference material)
├── patterns/ (implementation patterns)
└── domains/ (domain-specific knowledge)
```

**For complete integration guide**: @memory-integration-guide.md

**For split logic**: @../../docs/skills/skill-memory-split-logic.md

## Best Practices

### Workflow in Skill
✓ Step-by-step procedures
✓ Command sequences
✓ Validation steps
✓ One inline example

### Knowledge in Memory
✓ Reusable concepts (degrees of freedom)
✓ Specifications (Anthropic specs)
✓ Multiple detailed examples
✓ Domain knowledge (architecture patterns)

### Progressive Disclosure
✓ Load only what's referenced
✓ Keep SKILL.md <500 lines
✓ Split large content to supporting files
✓ Reference shared memories with @../../

## Troubleshooting

**Skill not activating**:
- Check description has relevant keywords
- Test with explicit skill-related terms
- Make description more specific

**Validation fails**:
- Name must be hyphen-case (lowercase-with-hyphens)
- Description must be <1024 chars
- @ references must resolve

**Import not found**:
```bash
# Verify path from skill directory
ls ../../docs/skills/file.md
```

## Shared Knowledge References

**Within this skill**:
- @memory-integration-guide.md - Complete integration methodology
- templates/ - Ready-to-use skill templates
- scripts/ - Automation tools

**Shared memories** (accessible to all skills):
- @../../docs/skills/building-skills-knowledge-base.md - Complete Anthropic specifications
- @../../docs/skills/skill-examples.md - 10+ detailed real-world examples
- @../../docs/skills/degrees-of-freedom.md - High/Medium/Low freedom patterns
- @../../docs/skills/skill-memory-split-logic.md - Decision framework
- @../../docs/skills/scaling-architecture.md - Scaling strategies
- @../../docs/skills/guidelines.md - Project-wide skills usage

**Official Anthropic**:
- https://github.com/anthropics/skills
- https://docs.claude.com/en/docs/claude-code/skills
- https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
