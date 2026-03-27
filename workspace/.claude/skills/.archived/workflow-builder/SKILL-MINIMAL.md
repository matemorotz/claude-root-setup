---
name: building-skills-minimal
description: Create Agent Skills following Anthropic standards (minimal workflow with memory references)
---

# Building Skills - Minimal Workflow

Minimal skill demonstrating workflow-focused SKILL.md with detailed info in project docs.

## Quick Start

**Automated**:
```bash
scripts/init-skill.sh
```

**Manual**: Copy template, edit YAML, add workflow

## Six-Phase Workflow

### Phase 1: Understanding
Gather 3-5 concrete examples

### Phase 2: Planning
Choose structure (minimal/standard/complex)

### Phase 3: Initialize
Create skill directory with template

### Phase 4: Write
Follow writing guidelines

### Phase 5: Validate
```bash
scripts/validate-skill.sh
```

### Phase 6: Iterate
Monitor and improve

## Detailed References

**For complete specifications**: @../../docs/skills/building-skills-knowledge-base.md

**For real-world examples**: @examples.md (local) or see project docs

**For degrees of freedom guide**: @degrees-of-freedom.md (local)

**For memory integration**: @memory-integration-guide.md (local)

## Templates & Scripts

- templates/minimal-skill.md
- templates/standard-skill.md
- templates/complex-skill.md
- scripts/init-skill.sh
- scripts/validate-skill.sh

---

**This demonstrates**: Minimal SKILL.md (~80 lines) referencing both local progressive disclosure AND project documentation.
