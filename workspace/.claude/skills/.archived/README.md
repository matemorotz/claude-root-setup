# Archived Skills

**Purpose:** Skills that have been replaced by better alternatives or are no longer actively used.

---

## workflow-builder (Archived 2025-12-01)

**Formerly:** building-skills
**Reason for Archive:** Prefer Anthropic's official **skill-creator** for standardization

### Why Archived?

After comprehensive comparison, we decided to use Anthropic's official `skill-creator` skill as the standard for creating new skills:

1. **Industry Standard:** Official Anthropic implementation
2. **Better Tooling:** Includes `init_skill.py` and `package_skill.py` scripts
3. **Distribution Ready:** Creates `.skill` packages for sharing
4. **Better Documentation:** Comprehensive bundled resources

### What workflow-builder Offered

- 6-phase creation workflow
- Progressive disclosure with shared knowledge via `@../../docs/`
- Minimal skill structure (<300 lines SKILL.md)
- Bash scripts: `init-skill.sh`, `validate-skill.sh`
- Templates for minimal/standard/complex skills

### Migration Path

**Old (workflow-builder):**
```bash
scripts/init-skill.sh
scripts/validate-skill.sh
```

**New (skill-creator):**
```bash
scripts/init_skill.py skill-name
scripts/package_skill.py skill-name/
```

### When to Still Reference

workflow-builder may still be useful for reference when:
- Understanding internal skill development patterns
- Reviewing the shared knowledge (`docs/`) approach
- Comparing different skill creation philosophies

### See Also

- **skill-creator:** `/root/software/.claude/skills/skill-creator/SKILL.md`
- **Comparison:** `/root/software/.claude/skills/skill_comparison_analysis.md`
- **Decision:** `/root/software/.claude/skills/DUPLICATE_ANALYSIS.md`

---

**Archived Skills Count:** 1
**Active Skills Count:** 17
**Last Updated:** 2025-12-01
