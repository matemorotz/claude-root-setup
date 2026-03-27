# SeedAnalyzer Rules

## Core Principles (Inherited from Project Seeds)
- Pattern recognition over guessing - only extract what's explicitly present
- Validation required - seeds must match actual implementation
- Efficiency focus - optimize for token reduction while preserving essentials
- Actionable output - developers should be able to apply seeds immediately

## Specific Rules

### 1. Pattern Extraction Rules

#### What Qualifies as a Pattern?
- **Repetition threshold:** Appears 3+ times in codebase
- **Consistency threshold:** >80% of instances follow same structure
- **Significance threshold:** Impacts architecture or quality

#### Pattern Categories
- **Architectural:** How components are organized (e.g., layered, event-driven)
- **Naming:** Conventions for files, functions, variables
- **Technical:** Framework usage, library patterns
- **Quality:** Type hints, testing, error handling
- **Process:** Git workflow, deployment patterns

#### Validation Requirements
- **Code match:** Pattern exists in actual implementation
- **Documentation match:** Pattern described in docs (if applicable)
- **Consistency check:** Pattern followed throughout codebase
- **Exception handling:** Note valid exceptions to patterns

### 2. Seed Hierarchy Rules

#### Hierarchy Levels (Required)
```yaml
project_seeds:          # Top level - universal truths
  ↓
domain_seeds:          # Backend, frontend, infrastructure
  ↓
module_seeds:          # Specific services/components
  ↓
function_seeds:        # Individual operations
```

#### Inheritance Rules
- **Explicit inheritance:** Use "inherits_from" key
- **No redundancy:** Don't repeat inherited seeds
- **Override allowed:** Lower levels can override higher (document reason)
- **Completeness:** All seeds in hierarchy documented

#### Example:
```yaml
backend_seeds:
  inherits_from: ["project_seeds"]
  overrides:
    - error_handling: "Custom: Use Loguru instead of project standard"
```

### 3. Prompt Optimization Rules

#### Always Measure
- **Before:** Token count, line count, file size
- **After:** Same metrics post-optimization
- **Reduction:** Calculate % reduction, target >70%
- **Quality:** Verify essential context preserved

#### Optimization Strategy
1. **Extract essentials** - What MUST be always-in-context?
2. **Create quick reference** - 100-200 line summary with essentials
3. **Move details** - Verbose content to separate docs
4. **Add @file references** - Dynamic loading for details
5. **Keyword navigation** - Map keywords → docs to load

#### Essential Context Criteria
- **Decision-making info:** Facts needed for every task
- **Core architecture:** System design fundamentals
- **Tech stack:** Languages, frameworks, versions
- **Key conventions:** Naming, patterns, standards
- **Emergency info:** Troubleshooting quick reference

#### Non-Essential (Move to On-Demand Docs)
- **Detailed examples:** Code snippets (reference, don't inline)
- **API documentation:** Full endpoint specs (load when needed)
- **Implementation details:** How services work internally
- **Historical context:** Why decisions were made
- **Extended guides:** Step-by-step tutorials

### 4. Analysis Workflow Rules

#### Discovery Phase Requirements
- **Read minimum 5 files** - Get representative sample
- **Check multiple domains** - Backend, frontend, tests, docs
- **Validate patterns** - Count occurrences, check consistency
- **Document exceptions** - Note deviations from patterns

#### Seed Extraction Requirements
- **YAML format required** - Parseable, hierarchical
- **Examples required** - Show how to apply each seed
- **Validation required** - Check against actual code
- **Completeness required** - Cover all major domains

#### Optimization Requirements
- **Before/after comparison** - Show improvements
- **Token count reduction** - Quantify savings
- **Preserve essentials** - Verify nothing critical lost
- **Navigation improved** - Keyword-based loading faster

---

## Expected Outputs

### 1. Seed Rules File (YAML)
```yaml
project_name: "[Name]"
analysis_date: "[YYYY-MM-DD]"
analyzed_files: [list of files analyzed]

project_seeds:
  core_principles:
    - [principle_name]: "[description]"
  architectural_patterns:
    - [pattern_name]: "[description]"
  naming_conventions:
    - [convention_name]: "[description]"

[domain]_seeds:
  inherits_from: ["project_seeds"]
  tech_stack:
    - [component]: "[technology]"
  [domain]_patterns:
    - [pattern_name]: "[description]"
```

### 2. Optimization Report (Markdown)
- Current state analysis
- Issues identified
- Before/after comparison
- Token reduction metrics
- Recommendations

### 3. Quick Reference File (Markdown)
- 100-200 lines maximum
- Essential facts only
- Keyword navigation map
- @file references for details

---

## Quality Standards

### Good Pattern Extraction
- ✅ Patterns occur 3+ times
- ✅ Consistency >80%
- ✅ Validated against code
- ✅ Exceptions documented
- ❌ No guessing or assumptions
- ❌ No over-generalization

### Good Seed Structure
- ✅ YAML format
- ✅ Hierarchical (4 levels)
- ✅ Inheritance explicit
- ✅ Examples included
- ✅ Validated against implementation
- ❌ No redundancy (respect inheritance)
- ❌ No vague descriptions

### Good Prompt Optimization
- ✅ 70%+ token reduction
- ✅ Essentials preserved
- ✅ Quick reference created
- ✅ @file references for details
- ✅ Keyword navigation map
- ❌ No loss of critical context
- ❌ No broken navigation

---

## Critical Constraints

### Never Guess
- If pattern unclear, mark as "needs_validation"
- If inheritance ambiguous, ask for clarification
- If essentials unclear, err on side of inclusion

### Always Validate
- Count pattern occurrences before including
- Check code matches documented seeds
- Verify token reductions don't break usability
- Test keyword navigation works

### Always Document
- List files analyzed
- Note exceptions to patterns
- Explain optimization decisions
- Provide before/after metrics

---

## Anti-Patterns to Avoid

### ❌ Over-Extraction
- Creating seeds for one-off occurrences
- Generalizing from single examples
- Including implementation details in project-level seeds

### ❌ Under-Extraction
- Missing obvious repeated patterns
- Ignoring architectural conventions
- Skipping quality standards

### ❌ Poor Optimization
- Removing essential context
- Creating navigation dead-ends (no references)
- Breaking keyword-based loading
- Token reduction <50% (not worth the effort)

### ❌ Weak Validation
- Seeds not matching actual code
- Inheritance chains broken
- Patterns inconsistently applied
- Examples don't work

---

## Success Metrics

### Pattern Extraction Success
- 100% of patterns occurring 5+ times documented
- 90%+ of patterns occurring 3-4 times documented
- All exceptions noted
- Validation passed

### Optimization Success
- Token reduction >70%
- Essential context 100% preserved
- Navigation time <30s for any fact
- Developer feedback positive

### Seed Structure Success
- All 4 hierarchy levels present
- Inheritance relationships clear
- No redundancy
- Examples functional
- Parseable YAML

---

**Remember:** Seeds are living documentation. Update them as code evolves. Validate regularly. Use them to onboard new developers and maintain consistency.
