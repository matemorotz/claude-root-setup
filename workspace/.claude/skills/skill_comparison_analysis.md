# Building-Skills vs Skill-Creator: Comprehensive Analysis

**Date:** 2025-12-01
**Purpose:** Cross-check Anthropic's official skill-creator against custom building-skills implementation

---

## Overview Comparison

| Aspect | building-skills (Custom) | skill-creator (Anthropic) |
|--------|--------------------------|---------------------------|
| **Source** | Custom implementation | Official Anthropic |
| **Focus** | Minimal workflow with shared knowledge | Complete self-contained guides |
| **Structure** | SKILL.md + @references to shared docs | SKILL.md + bundled resources (scripts/references/assets) |
| **Philosophy** | Progressive disclosure via shared memory | Progressive disclosure via skill-local files |
| **Line Limit** | <500 lines total | <500 lines SKILL.md (unlimited in references) |
| **Validation** | validate-skill.sh | package_skill.py (includes validation) |
| **Initialization** | init-skill.sh | init_skill.py |

---

## Key Differences

### 1. Knowledge Organization

**building-skills (Custom):**
```
.claude/
├── skills/
│   └── skill-name/
│       └── SKILL.md (workflow only, ~200-300 lines)
└── docs/                    ← Shared across ALL skills
    ├── concepts/
    ├── specifications/
    ├── patterns/
    └── domains/
```

- References shared knowledge: `@../../docs/skills/examples.md`
- Avoids duplication across skills
- Centralized knowledge base

**skill-creator (Anthropic):**
```
skill-name/
├── SKILL.md (workflow + guidance, <500 lines)
├── scripts/         ← Skill-specific
├── references/      ← Skill-specific
└── assets/          ← Skill-specific
```

- All resources bundled with skill
- Self-contained and portable
- Each skill includes own documentation

**Analysis:**
- **Anthropic approach** = Better for distribution/sharing (everything in one package)
- **Custom approach** = Better for internal use (avoid duplication, centralized updates)

---

### 2. Progressive Disclosure

**building-skills:**
```markdown
# In SKILL.md
For detailed specs: @../../docs/topic/specifications.md
```

Loads from shared docs/ directory when referenced.

**skill-creator:**
```markdown
# In SKILL.md
For detailed specs: See references/specifications.md
```

Loads from skill's own references/ directory.

**Analysis:**
- Both use progressive disclosure
- Different scopes: global (building-skills) vs local (skill-creator)
- building-skills avoids duplication when multiple skills need same reference

---

### 3. Degrees of Freedom

**Both agree on:**
- High freedom: Text-based instructions
- Medium freedom: Pseudocode/scripts with parameters
- Low freedom: Specific scripts, few parameters

**building-skills:** References `@../../docs/skills/degrees-of-freedom.md`
**skill-creator:** Explains inline in SKILL.md

**Analysis:** Same concept, different delivery

---

### 4. Creation Workflow

**building-skills (6 phases):**
1. Understanding
2. Planning
3. Initialize
4. Write
5. Validate
6. Iterate

**skill-creator (6 steps):**
1. Understand with concrete examples
2. Plan reusable contents
3. Initialize (run init_skill.py)
4. Edit (implement + write)
5. Package (run package_skill.py)
6. Iterate

**Analysis:** Almost identical! Building-skills skips "Package" step (internal use)

---

### 5. Bundled Resources

**building-skills:**
- Minimal in skill directory
- Most knowledge in shared docs/
- scripts/ and templates/ when needed

**skill-creator:**
- scripts/ - Executable code
- references/ - Documentation for Claude
- assets/ - Files used in output (templates, fonts, etc.)

**Analysis:** Anthropic's structure is more comprehensive and standard

---

### 6. Validation

**building-skills:** `validate-skill.sh`
- Checks YAML frontmatter
- Validates name/description
- Checks line count
- Verifies @ references

**skill-creator:** `package_skill.py` (includes validation)
- YAML frontmatter format
- Naming conventions
- Description completeness
- File organization
- Creates distributable .skill file (zip)

**Analysis:** Anthropic includes packaging + distribution

---

### 7. What NOT to Include

**building-skills:**
- Keep SKILL.md <500 lines
- Reference shared knowledge

**skill-creator:**
- No README.md
- No INSTALLATION_GUIDE.md
- No QUICK_REFERENCE.md
- No CHANGELOG.md
- Only files needed for AI agent

**Analysis:** Anthropic is stricter about avoiding auxiliary documentation

---

## Best Practices Comparison

### Token Efficiency

**building-skills:**
- Keep workflows in SKILL.md (~200-300 lines)
- Put detailed knowledge in shared docs/
- Load only what's referenced

**skill-creator:**
- "Context window is a public good"
- "Default assumption: Claude is already very smart"
- "Challenge each piece of information"
- Keep SKILL.md <500 lines
- Use references/ for details

**Analysis:** Both emphasize token efficiency, Anthropic more explicit

---

### Writing Style

**Both agree:**
- Use imperative/infinitive form
- Concise examples over verbose explanations
- Clear workflows

**Examples:**
```markdown
<!-- Good -->
Create the file:
```bash
touch file.txt
```

<!-- Avoid -->
You should create the file
```

---

### Progressive Disclosure Patterns

**Both recommend:**

1. **High-level guide with references**
   ```markdown
   # Quick start
   [code example]

   # Advanced
   - Form filling: See FORMS.md
   - API reference: See REFERENCE.md
   ```

2. **Domain-specific organization**
   ```
   └── references/
       ├── finance.md
       ├── sales.md
       └── product.md
   ```

3. **Conditional details**
   - Show basic, link to advanced

**Analysis:** Same patterns, slightly different terminology

---

## Scripts Comparison

### building-skills

**init-skill.sh:**
- Interactive prompts
- Creates from template
- Validates input

**validate-skill.sh:**
- Checks structure
- Validates YAML
- Verifies @ references

### skill-creator

**init_skill.py:**
- Creates skill directory
- Generates SKILL.md template
- Creates example directories
- Adds example files

**package_skill.py:**
- Validates skill
- Creates .skill file (zip)
- For distribution

**Analysis:** Anthropic includes packaging/distribution tooling

---

## Recommendations

### For Internal Skills (Not Distributed)
**Use building-skills approach:**
- Leverage shared docs/ for common knowledge
- Avoid duplication across skills
- Simpler structure
- Easier to maintain consistency

### For Distributed Skills (Shared Externally)
**Use skill-creator approach:**
- Self-contained packages
- All resources bundled
- Standard structure
- Professional distribution (.skill files)

### Hybrid Approach (Best of Both)

```
.claude/
├── skills/
│   ├── skill-name/
│   │   ├── SKILL.md        (workflow, <300 lines)
│   │   ├── scripts/        (skill-specific executables)
│   │   ├── references/     (skill-specific docs)
│   │   └── assets/         (templates, files)
│   └── ...
└── docs/
    ├── concepts/            (shared across all skills)
    ├── patterns/            (reusable patterns)
    └── specifications/      (Anthropic specs)
```

**Benefits:**
- Skill-specific resources stay with skill (Anthropic style)
- Shared knowledge in docs/ (building-skills style)
- Easy to convert to .skill package when needed
- Avoid duplication while maintaining portability

---

## Validation Checklist (Combined)

From both systems, a skill should:

### Structure
- [ ] YAML frontmatter with name and description
- [ ] Name is hyphen-case, <64 chars
- [ ] Description <1024 chars, third person, includes "when to use"
- [ ] SKILL.md <500 lines
- [ ] Proper directory structure

### Content
- [ ] Clear workflows
- [ ] Imperative/infinitive style
- [ ] Concise examples
- [ ] Progressive disclosure used
- [ ] Appropriate degree of freedom

### Resources
- [ ] Scripts tested and working
- [ ] References properly linked
- [ ] Assets in correct directory
- [ ] No auxiliary documentation (README, CHANGELOG, etc.)

### References (building-skills specific)
- [ ] @ references resolve
- [ ] Shared knowledge referenced correctly

### Distribution (skill-creator specific)
- [ ] Can be packaged with package_skill.py
- [ ] All resources self-contained

---

## Conclusion

**Building-skills (Custom):**
- ✅ Great for internal skill ecosystems
- ✅ Avoids duplication
- ✅ Centralized knowledge management
- ❌ Not designed for distribution

**Skill-creator (Anthropic):**
- ✅ Industry standard
- ✅ Self-contained and portable
- ✅ Professional distribution
- ✅ Better for sharing
- ❌ Can lead to duplication across skills

**Recommendation:**
1. **Adopt Anthropic's structure** for new skills (scripts/references/assets)
2. **Keep shared docs/** for truly reusable knowledge (Anthropic specs, degrees of freedom guide)
3. **Use Anthropic's tooling** (init_skill.py, package_skill.py) when available
4. **Follow Anthropic's best practices** for description, token efficiency, and progressive disclosure

---

## Action Items

1. ✅ Consolidate all skills to `/root/software/.claude/skills/`
2. Convert building-skills to use Anthropic structure where beneficial
3. Keep shared docs/ for cross-skill knowledge
4. Adopt Anthropic's validation and packaging tools
5. Update skill creation workflow to use init_skill.py

**Both systems are excellent** - they share core principles with different implementation philosophies. The best approach combines both: Anthropic's structure with selective use of shared knowledge when it prevents duplication.
