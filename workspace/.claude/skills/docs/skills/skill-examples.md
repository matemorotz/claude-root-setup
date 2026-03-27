# Skill Creation Examples

Complete real-world examples demonstrating the six-phase skill creation process.

## Example 1: Creating a Database Management Skill

### Phase 1: Understanding

```markdown
Skill Idea: Managing Databases

Examples:
1. Create database: Initialize Postgres DB with schema
2. Backup database: Create timestamped backup, verify integrity
3. Restore database: Restore from backup, validate data
4. Migrate schema: Apply migrations, rollback if fail
5. Monitor performance: Check query times, connections, locks

Edge Cases:
- Database already exists (create)
- Backup file corrupted (restore)
- Migration fails mid-way (migrate)
- Connection pool exhausted (monitor)

Degree of Freedom: Low to Medium
- Create/restore: Medium (some flexibility)
- Backup: Low (exact sequence for consistency)
- Migration: Low (critical to avoid data loss)
```

### Phase 2: Planning

```markdown
Structure:

managing-databases/
├── SKILL.md (~400 lines)
│   ├── Overview
│   ├── Quick Start (create DB)
│   ├── Workflow: Backup (detailed, low freedom)
│   ├── Workflow: Restore (detailed, low freedom)
│   └── Workflow: Basic Operations
├── migrations.md (~300 lines)
│   └── Schema migration details
├── monitoring.md (~200 lines)
│   └── Performance monitoring
└── scripts/
    ├── backup.sh
    ├── restore.sh
    └── migrate.py

Progressive Disclosure:
- SKILL.md: Core operations (create, backup, restore basics)
- migrations.md: Loaded only when migrating schema
- monitoring.md: Loaded only when monitoring needed
- scripts/: Loaded when specific automation needed
```

### Phase 3: Initialize

```bash
mkdir -p .claude/skills/managing-databases/scripts

cat > .claude/skills/managing-databases/SKILL.md <<'EOF'
---
name: managing-databases
description: Manage PostgreSQL databases including creation, backup, restore, migrations, and monitoring. Use when working with database operations that require careful sequencing and data safety.
---

# Managing Databases

## Overview
Comprehensive PostgreSQL database management workflows with safety-first approach.

## Quick Start
[Basic create database workflow]

## Workflows
[Detailed backup, restore, migration workflows]
EOF
```

### Phase 4: Write

**SKILL.md excerpt**:

```markdown
## Workflow: Database Backup

⚠️ CRITICAL: Follow exact sequence for data integrity

### Step 1: Verify Database Accessible

```bash
psql -h localhost -U postgres -d mydb -c "SELECT version();"
```

Expected: Version information displayed

### Step 2: Create Backup Directory

```bash
mkdir -p backups/$(date +%Y-%m)
```

### Step 3: Execute Backup

```bash
pg_dump -h localhost -U postgres -F c -b -v \
  -f backups/$(date +%Y-%m)/mydb_$(date +%Y%m%d_%H%M%S).backup \
  mydb
```

### Step 4: Verify Backup Integrity

```bash
pg_restore --list backups/$(date +%Y-%m)/mydb_*.backup | head -20
```

Expected: Table of contents displayed

### Step 5: Record Backup Metadata

```bash
echo "Backup: $(date), Size: $(du -h backups/$(date +%Y-%m)/mydb_*.backup)" \
  >> backups/backup.log
```

## Troubleshooting

### Connection Refused
**Problem**: `psql: could not connect to server`
**Cause**: PostgreSQL not running
**Solution**:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```
```

### Phase 5: Validate

```bash
# Frontmatter check
✓ name: managing-databases (hyphen-case, gerund-ish)
✓ description: Under 1024 chars, third person
✓ No XML tags

# Content check
wc -l SKILL.md
# 425 lines (under 500 ✓)

# Test activation
"Create a database backup" → ✓ Activates
"What are databases?" → ✓ Does NOT activate

# Test workflow
# Follow Step 1-5 → ✓ All commands work
```

### Phase 6: Iterate

```markdown
Iteration 1:
- User reported confusion about backup format (-F c)
- Added explanation of custom format benefits
- Added alternative: plain SQL format

Iteration 2:
- Edge case: Disk space full during backup
- Added pre-flight check for available space
- Added cleanup of old backups workflow
```

---

## Example 2: Creating the building-skills Meta-Skill

Real-world example of creating this skill itself, demonstrating the meta-process.

### Phase 1: Understanding (Building Skills)

```markdown
Skill Idea: Building Skills

Domain: Agent Skills creation following Anthropic standards
Need: Systematic way to create skills that follow best practices
Gap: No internal documentation of Anthropic specifications

Examples:
1. Simple skill: Create minimal skill for single workflow
2. Standard skill: Create skill with progressive disclosure
3. Complex skill: Create multi-file skill with scripts and templates
4. Validate skill: Check YAML, line count, activation patterns
5. Iterate skill: Monitor usage, gather feedback, improve

Edge Cases:
- SKILL.md exceeds 500 lines (need progressive disclosure)
- Templates referenced but don't exist
- Skill activates for wrong requests
- Import paths don't resolve

Degree of Freedom: Medium
- Core workflow: Medium (recommended six-phase process)
- Structure decision: Medium (minimal/standard/complex options)
- Content writing: Medium (guidelines with examples)
```

### Phase 2: Planning (Building Skills)

```markdown
Research:
1. Official Anthropic documentation
2. anthropics/skills repository examples
3. skill-creator, pdf, mcp-builder patterns

Knowledge Base:
- Create: docs/skills/building-skills-knowledge-base.md (~70 pages)
- Content: Complete Anthropic specifications
- Purpose: Reference material, not workflow

Skill Structure:
building-skills/
├── SKILL.md (~350 lines)
│   ├── Quick Start
│   ├── Six-Phase Process
│   └── References to supporting files
├── examples.md (~250 lines)
│   └── Real-world complete examples
├── degrees-of-freedom.md (~150 lines)
│   └── High/Medium/Low freedom patterns
├── memory-integration-guide.md (~1200 lines)
│   └── Complete integration methodology
├── templates/
│   ├── minimal-skill.md
│   ├── standard-skill.md
│   └── complex-skill.md
└── scripts/
    ├── init-skill.sh
    └── validate-skill.sh

Progressive Disclosure:
- SKILL.md: Essential six-phase process
- examples.md: Loaded when user needs detailed examples
- degrees-of-freedom.md: Loaded when deciding workflow freedom
- memory-integration-guide.md: Loaded for integration methodology
```

### Phase 3: Initialize (Building Skills)

```bash
mkdir -p .claude/skills/building-skills/{templates,scripts}

cat > .claude/skills/building-skills/SKILL.md <<'EOF'
---
name: building-skills
description: Create new Agent Skills following Anthropic best practices and specifications. Use when building skills for extending Claude's capabilities with specialized workflows, domain expertise, or tool integrations.
---

# Building Skills - Meta-Skill

## Quick Start
[5-minute path to first skill]

## Six-Phase Creation Process
[Phase 1-6 workflows]

## References
- @examples.md
- @degrees-of-freedom.md
- @memory-integration-guide.md
EOF
```

### Phase 4: Write (Building Skills)

Distillation from knowledge base:
- Knowledge base: ~70 pages (~5000 lines)
- SKILL.md: ~5 pages (~350 lines)
- Compression ratio: 14:1

Content decisions:
- Include: Six-phase process, essential templates, validation checklist
- Extract to examples.md: Detailed database example, real-world walkthroughs
- Extract to degrees-of-freedom.md: Detailed freedom pattern examples
- Reference: Complete specs in knowledge base

### Phase 5: Validate (Building Skills)

```bash
# Validation results
✓ YAML frontmatter correct
✓ Name: building-skills (gerund form, hyphen-case)
✓ Description: 194 chars (under 1024)
✓ SKILL.md: 350 lines (under 500)
✓ Progressive disclosure implemented
✓ Supporting files exist and referenced
✓ Templates directory populated
✓ Scripts functional

# Test activation
"Create a new skill" → ✓ Activates building-skills
"Build a database skill" → ✓ Activates building-skills
"What are skills?" → ✓ Does NOT activate (informational query)
```

### Phase 6: Iterate (Building Skills)

```markdown
Iteration 1 (2025-11-01):
- Initial creation with six-phase process
- SKILL.md was 818 lines (exceeded limit)

Iteration 2 (2025-11-02):
- Implemented progressive disclosure
- Extracted examples.md and degrees-of-freedom.md
- Reduced SKILL.md to 350 lines
- Added Quick Start section
- Created templates and scripts

Result:
- 57% reduction in SKILL.md size
- Better follows Anthropic self-contained pattern
- Working templates for users
- Automation scripts reduce manual work
```

---

## Example 3: Creating a Server Management Skill

Demonstrates creating a skill with critical safety protocols.

### Phase 1: Understanding (Server Management)

```markdown
Skill Idea: Managing Servers

Examples:
1. SSH hardening: Disable password auth, change port, setup fail2ban
2. User management: Create user, add SSH key, configure sudo
3. Key rotation: Generate new key, add to server, test, remove old
4. Access audit: List authorized keys, check active sessions
5. Troubleshoot connection: Test connectivity, check logs, verify config

Edge Cases:
- Admin lockout (removed own access without backup)
- Key corruption (can't access server)
- Port change breaks connection
- Multiple admin users (coordination needed)

Degree of Freedom: LOW (safety-critical)
- All SSH operations require exact sequence
- Must verify backup access before changes
- Must test in separate session
- Must warn user of risks
```

### Phase 2: Planning (Server Management)

```markdown
Structure:
managing-servers/
├── SKILL.md (~400 lines)
│   ├── ⚠️ CRITICAL SAFETY RULE (prominent)
│   ├── Workflow: SSH Hardening (low freedom)
│   ├── Workflow: User Management (low freedom)
│   └── Workflow: Key Rotation (low freedom)
├── security-checklist.md (~200 lines)
│   └── Complete security hardening guide
└── scripts/
    ├── backup-access-test.sh
    └── ssh-hardening-check.sh

Safety Features:
- Explicit warnings before critical operations
- User confirmation prompts (must type "PROCEED")
- Backup access verification
- Testing in separate session requirements
- Rollback procedures
```

### Phase 3-4: Implementation with Safety

```markdown
## ⚠️ CRITICAL SAFETY RULE

**NEVER remove or disable admin access without:**
1. **Explicit warning** to user about potential lockout
2. **User confirmation** to proceed
3. **Verification** that backup access exists
4. **Testing** backup access in separate session

### Workflow: SSH Hardening

⚠️ **WARNING TO USER REQUIRED**

Before executing, display this warning:

```
⚠️  CRITICAL SECURITY CHANGE WARNING

This will modify SSH configuration:
- Disable password authentication
- Disable root login
- Change SSH port (optional)

RISK: If backup access not working, you will be LOCKED OUT.

Verified backup access: [YES/NO]
Emergency access available: [YES/NO]

Type 'PROCEED' to continue or 'CANCEL' to abort:
```

**WAIT FOR USER CONFIRMATION before continuing**

[Then proceed with step-by-step hardening workflow]
```

---

## Example 4: Creating an MCP Integration Skill

Demonstrates creating a skill for technical integration workflows.

### Phase 1: Understanding (MCP Integration)

```markdown
Skill Idea: MCP Integration

Examples:
1. Create basic MCP server: FastAPI endpoint with auth
2. Add MCP tools: Implement tool endpoints following pattern
3. Test MCP server: Health check, tool execution validation
4. Deploy MCP server: Systemd service, port configuration
5. Integrate with agents: Connect agents to MCP endpoints

Degree of Freedom: Medium
- Server framework: Recommended (FastAPI) with alternative (Flask)
- Tool design: Recommended (workflow-oriented) with options
- Deployment: Standard pattern with configuration options
```

### Phase 2: Planning (MCP Integration)

```markdown
Structure:
mcp-integration/
├── SKILL.md (~350 lines)
│   ├── Quick Start: Basic MCP server
│   ├── Workflow: Tool Design
│   ├── Workflow: Deployment
│   └── Examples inline
└── scripts/
    ├── create-mcp-server.sh
    └── test-mcp-server.sh

Reference project memory:
- Import: @../../docs/mcp/integration.md (standards)
- Follow: Authentication pattern (Authorization: Menycibu)
- Apply: Port conventions (8001, 8002+)
```

---

## Example 5: Minimal Skill Example

Simplest possible skill demonstrating core requirements only.

### Complete Minimal Skill

```yaml
---
name: greeting-responder
description: Respond to user greetings with friendly acknowledgment. Use when user says hello, hi, or greets Claude.
---

# Greeting Responder

## Overview
Simple skill that detects and responds to user greetings.

## Workflow

When user greets:
1. Detect greeting keywords (hello, hi, hey, greetings)
2. Generate friendly acknowledgment
3. Offer to help with tasks

## Example

User: "Hello!"
Response: "Hello! I'm ready to help. What would you like to work on today?"
```

**Result**: 100 lines, fully functional, demonstrates minimum viable skill.

---

## Key Takeaways from Examples

### From Database Example
- Low freedom for critical operations (backup, migration)
- Exact sequences prevent data loss
- Validation at each step

### From building-skills Example
- Meta-skills teach patterns that apply to themselves
- Progressive disclosure: 70 pages → 5 pages in SKILL.md
- Self-contained with templates and scripts

### From Server Management Example
- Safety-critical operations require explicit warnings
- User confirmation before irreversible changes
- Backup verification before proceeding
- Testing in separate session

### From MCP Integration Example
- Reference project memories for standards
- Medium freedom allows recommended + alternatives
- Import existing patterns rather than duplicate

### From Minimal Example
- Not all skills need complexity
- Simple workflows work for simple tasks
- Under 100 lines is fine if that's all you need

---

## Pattern Recognition Across Examples

**All examples follow**:
1. Clear YAML frontmatter
2. Domain-specific description
3. Progressive disclosure (simple → complex)
4. Working code examples
5. Appropriate degree of freedom for domain

**Structure patterns**:
- **Minimal**: SKILL.md only (~100-300 lines)
- **Standard**: SKILL.md + supporting files (~300-500 lines main)
- **Complex**: SKILL.md + multiple supporting files + scripts

**Safety patterns**:
- Critical operations → Explicit warnings
- Irreversible changes → User confirmation
- Data/access risk → Backup verification
- Multi-step safety → Test before proceeding
