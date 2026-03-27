---
name: populating-governor-domains
description: Automate population of .governor/ folders for new fractal domains in Fly Achensee. Use when creating new Level 1 domains (advertising, user_communication, etc.) following the filesystem-driven agent architecture.
---

# Populating Governor Domains Skill

Automates the creation and population of .governor/ folders for new fractal domains in the Fly Achensee multi-agent system.

## Context Import

Reference project architecture:
@../../../FRACTAL_ARCHITECTURE.md
@../../../FRACTAL_DESIGN_CLARIFICATION.md
@../../../MCP_DISCOVERY_DESIGN.md

Follow project conventions:
@../../../CLAUDE.md
@../../../project.md

## When to Use This Skill

- Creating new Level 1 domains (e.g., advertising, user_communication, booking_management)
- Expanding the fractal architecture to new business areas
- Setting up domain-specific governors with proper context and permissions

## Architecture Principles

### Fractal Pattern
Every .governor/ folder follows the same structure but with domain-specific context:
- Same LangGraph structure at every level
- Different context injection = specialized behavior
- Filesystem-driven knowledge management

### MCP Architecture (CRITICAL)
- **Root .env**: ALL MCP server connection details (GMAIL_MCP_URL, BOOKING_MCP_URL, SLACK_MCP_URL, etc.)
- **Subfolder MCP.md**: ALLOWED MCPs list for that domain (permission filter)
- Example: `customer_communication/.governor/MCP.md` allows `gmail, booking` but NOT `slack, analytics`

### Standard .governor/ Structure
```
domain_name/.governor/
├── Governor.md          # Domain-specific governor prompt
├── Project.md           # Domain scope and objectives
├── Agents.md            # Available specialist agents
├── Rules.md             # Domain-specific safety rules (15+)
├── MCP.md               # ALLOWED MCPs list (permission filter)
├── State.md             # Current domain status
├── Todo.md              # Domain task list
├── Examples.md          # 5+ workflow examples
├── knowledge/           # Domain-specific knowledge base
│   └── *.md             # FAQ, procedures, templates
├── skills/              # Domain-specific skills (optional)
└── external_agents/     # External agent integrations (optional)
```

## Domain Population Workflow

### Phase 1: Planning and Discovery

1. **Gather Domain Requirements**
   - What is the domain scope? (e.g., "Advertising and Marketing Campaigns")
   - What are the primary workflows? (e.g., "Create campaign", "Track analytics", "Manage social media")
   - Who are the specialist agents? (e.g., "campaign_manager", "analytics_specialist", "social_media_coordinator")

2. **Identify Required MCPs**
   - Review root .env for available MCP services
   - Determine which MCPs this domain needs access to
   - Example: advertising domain needs `analytics`, `social_media` but NOT `gmail`, `booking`

3. **Define Safety Rules**
   - What are the critical constraints for this domain?
   - What should NEVER be automated?
   - What requires human approval?

### Phase 2: Create Domain Structure

4. **Create Directory Structure**
```bash
cd /root/software/fly_achensee

# Create domain folder
DOMAIN_NAME="advertising"  # Change this
mkdir -p ${DOMAIN_NAME}/.governor/{knowledge,skills,external_agents}

echo "✅ Created directory structure for ${DOMAIN_NAME}"
```

5. **Copy Template Files from Reference Domain**
```bash
# Use customer_communication as reference template
REFERENCE_DOMAIN="customer_communication"
DOMAIN_NAME="advertising"  # Change this

cd /root/software/fly_achensee

# Copy structure (but DON'T copy content yet - we'll customize)
ls ${REFERENCE_DOMAIN}/.governor/*.md | while read file; do
    filename=$(basename "$file")
    touch ${DOMAIN_NAME}/.governor/${filename}
done

echo "✅ Created template files for ${DOMAIN_NAME}"
```

### Phase 3: Populate Core Files

6. **Create Project.md**

Template:
```markdown
# {Domain Name} - Project Scope

**Domain:** {Domain Name}
**Governor Type:** Level 1 Domain Governor
**Parent:** Root Manager (Agent.md)
**Last Updated:** {Current Date}

## Scope

This domain handles all {domain description} for Fly Achensee Tandemflying Paragliding Company.

### Primary Responsibilities
- {Responsibility 1}
- {Responsibility 2}
- {Responsibility 3}

### Key Workflows
1. **{Workflow 1 Name}**: {Description}
2. **{Workflow 2 Name}**: {Description}
3. **{Workflow 3 Name}**: {Description}

### Success Metrics
- {Metric 1}
- {Metric 2}
- {Metric 3}

## Integration Points

### Parent Governor
- **Reports to:** Root Manager Agent
- **Escalation path:** Complex cross-domain tasks, policy decisions
- **Communication:** Task completion reports, blocking issues

### Peer Domains
- **{Peer Domain 1}**: {Integration point}
- **{Peer Domain 2}**: {Integration point}

### External Systems
- **MCP Services:** {List allowed MCPs}
- **Data Sources:** {External data sources}
- **APIs:** {Third-party APIs}

## Constraints

- NEVER {constraint 1}
- ALWAYS {constraint 2}
- ONLY {constraint 3} with approval
```

7. **Create Agents.md**

Template:
```markdown
# {Domain Name} - Available Agents

**Last Updated:** {Current Date}

This document defines the specialist agents available within the {domain name} domain.

## Specialist Agents

### 1. {Agent 1 Name}
**Type:** Specialist
**Specialization:** {What they do}

**Responsibilities:**
- {Responsibility 1}
- {Responsibility 2}
- {Responsibility 3}

**Tools/MCPs:**
- {MCP 1}: {Purpose}
- {MCP 2}: {Purpose}

**Typical Tasks:**
- "{Example task 1}"
- "{Example task 2}"

**Escalation Triggers:**
- {When to escalate to governor}

---

### 2. {Agent 2 Name}
**Type:** Specialist
**Specialization:** {What they do}

**Responsibilities:**
- {Responsibility 1}
- {Responsibility 2}

**Tools/MCPs:**
- {MCP 1}: {Purpose}

**Typical Tasks:**
- "{Example task 1}"
- "{Example task 2}"

**Escalation Triggers:**
- {When to escalate}

---

### 3. {Agent 3 Name}
**Type:** Specialist
**Specialization:** {What they do}

**Responsibilities:**
- {Responsibility 1}
- {Responsibility 2}

**Tools/MCPs:**
- {MCP 1}: {Purpose}

**Typical Tasks:**
- "{Example task 1}"

**Escalation Triggers:**
- {When to escalate}

## Agent Selection Guidelines

**Route to {Agent 1}** when:
- {Condition 1}
- {Condition 2}

**Route to {Agent 2}** when:
- {Condition 1}
- {Condition 2}

**Route to {Agent 3}** when:
- {Condition 1}

**Escalate to Governor** when:
- Multiple agents needed
- Cross-domain coordination required
- Policy decision needed
- Conflict resolution needed
```

8. **Create Rules.md**

Template (minimum 15 rules):
```markdown
# {Domain Name} - Safety Rules

**Last Updated:** {Current Date}

These rules govern all operations within the {domain name} domain.

## Critical Rules (NEVER)

### Rule 1: {Rule Name}
**NEVER {action}**

**Rationale:** {Why this is critical}

**Examples:**
- ❌ Bad: {Example of violation}
- ✅ Good: {Example of compliance}

### Rule 2: {Rule Name}
**NEVER {action}**

**Rationale:** {Why}

**Examples:**
- ❌ Bad: {Example}
- ✅ Good: {Example}

{... Repeat for 5+ NEVER rules}

## Required Actions (ALWAYS)

### Rule 6: {Rule Name}
**ALWAYS {action}**

**Rationale:** {Why}

**Examples:**
- ❌ Bad: {Example of violation}
- ✅ Good: {Example of compliance}

{... Repeat for 5+ ALWAYS rules}

## Conditional Rules (ONLY)

### Rule 11: {Rule Name}
**ONLY {action} when {condition}**

**Rationale:** {Why}

**Approval Required:** {Yes/No, from whom}

**Examples:**
- ❌ Bad: {Example}
- ✅ Good: {Example}

{... Repeat for 5+ ONLY rules}

## Escalation Rules

### When to Escalate to Parent Governor
- {Condition 1}
- {Condition 2}
- {Condition 3}

### When to Request Human Approval
- {Condition 1}
- {Condition 2}

### When to Abort Operation
- {Condition 1}
- {Condition 2}
```

9. **Create MCP.md (CRITICAL - Permission Filter)**

**IMPORTANT:** This file defines ALLOWED MCPs for this domain, NOT connection details!

Template:
```markdown
# {Domain Name} - MCP Service Permissions

**Last Updated:** {Current Date}

This file defines which MCP services are ALLOWED for agents in this domain.

**Architecture:**
- **Root .env** contains ALL MCP server connection details (URLs, auth tokens)
- **This file** contains the ALLOWED list (permission filter)

## Allowed MCPs

**Allowed MCPs for {domain name}:**
- {mcp_service_1}
- {mcp_service_2}
- {mcp_service_3}

## MCP Service Descriptions

### {mcp_service_1}
**Purpose:** {What it does}
**Used By:** {Which agents use this}
**Operations:** {What operations are allowed}
**Connection:** Defined in root .env as `{SERVICE_NAME}_MCP_URL`

### {mcp_service_2}
**Purpose:** {What it does}
**Used By:** {Which agents use this}
**Operations:** {What operations are allowed}
**Connection:** Defined in root .env as `{SERVICE_NAME}_MCP_URL`

## NOT Allowed

The following MCPs are NOT allowed for this domain:
- {denied_mcp_1} - Reason: {Why not allowed}
- {denied_mcp_2} - Reason: {Why not allowed}

## Permission Rationale

**Why {mcp_service_1} is allowed:**
- {Reason 1}
- {Reason 2}

**Why {denied_mcp_1} is denied:**
- {Reason 1}
- {Reason 2}

## Adding New MCPs

To add a new MCP to this domain:
1. Ensure MCP server connection is in root .env (`{SERVICE_NAME}_MCP_URL`)
2. Add MCP name to "Allowed MCPs" list above
3. Document purpose and usage
4. Update AgentFactory integration
5. Test with AgentFactory.get_tools_for_domain()
```

**Example for advertising domain:**
```markdown
## Allowed MCPs

**Allowed MCPs for advertising:**
- analytics
- social_media

## MCP Service Descriptions

### analytics
**Purpose:** Campaign analytics and reporting
**Used By:** analytics_specialist
**Operations:** Track metrics, generate reports, analyze performance
**Connection:** Defined in root .env as `ANALYTICS_MCP_URL`

### social_media
**Purpose:** Social media post management
**Used By:** social_media_coordinator
**Operations:** Post content, schedule posts, monitor engagement
**Connection:** Defined in root .env as `SOCIAL_MEDIA_MCP_URL`

## NOT Allowed

The following MCPs are NOT allowed for this domain:
- gmail - Reason: Advertising doesn't handle customer emails (that's customer_communication domain)
- booking - Reason: Advertising doesn't manage bookings (that's customer_communication domain)
```

10. **Create Governor.md**

Use the universal template from `agent_archetypes/governor_archetype.md` with domain-specific context injection.

Template:
```markdown
# {Domain Name} Governor

You are a Governor Agent responsible for **{Domain Name} Operations**.

**Your Domain:** {Description from Project.md}
**Available Agents:** {From Agents.md}
**Available MCP Services:** {From MCP.md - ALLOWED list only}

## Context Variables (Injected by AgentFactory)

- `{SCOPE}` - {Domain Name}
- `{PROJECT_DESCRIPTION}` - {From Project.md}
- `{AGENTS_INDEX}` - {From Agents.md}
- `{MCP_INDEX}` - {From MCP.md - allowed list}
- `{RULES}` - {From Rules.md}
- `{KNOWLEDGE_SUMMARY}` - {From knowledge/ folder}

## Your Responsibilities

1. **Task Analysis**: Understand incoming requests within {domain} scope
2. **Agent Routing**: Delegate to appropriate specialist agents
3. **Workflow Orchestration**: Coordinate multi-agent workflows
4. **Quality Assurance**: Ensure all rules are followed
5. **Parent Coordination**: Escalate to root manager when needed

## Decision Rules

**Route to Specialist** when:
- Task is within single agent's capability
- Clear agent match exists
- No cross-domain coordination needed

**Coordinate Multiple Agents** when:
- Task requires multiple specialists
- Complex workflow within domain
- Sequential agent execution needed

**Escalate to Parent** when:
- Cross-domain coordination required
- Policy decision needed beyond domain scope
- Resource allocation conflicts
- Complex business logic requiring manager input

## Safety Rules

{Include critical rules from Rules.md}

**CRITICAL RULES:**
- NEVER {rule 1}
- NEVER {rule 2}
- ALWAYS {rule 3}

## Response Format

All responses MUST use this JSON schema:

```json
{
  "next": {
    "agent": "specialist_agent_name | governor_agent | PARENT_ESCALATION",
    "message": "Clear instruction or task for next agent",
    "context": {
      "domain": "{domain_name}",
      "workflow_id": "unique_id",
      "previous_steps": []
    }
  }
}
```

## Example Workflows

{Include examples from Examples.md only if needed for complex repeating workflows  make a skill}
```

11. **Create Examples.md**

Provide 5+ realistic workflow examples:
```markdown
# {Domain Name} - Workflow Examples

**Last Updated:** {Current Date}

## Example 1: {Workflow Name}

**User Request:** "{Example user request}"

**Expected Flow:**
1. Governor receives request
2. Governor routes to {agent_name}
3. {agent_name} uses {mcp_service} to {action}
4. {agent_name} returns result to governor
5. Governor responds to user

**Example JSON Flow:**
```json
{
  "step": 1,
  "agent": "governor",
  "action": "analyze_request",
  "decision": "route_to_specialist",
  "next_agent": "{agent_name}"
}
```

{... 4+ more examples}
```

12. **Create State.md and Todo.md**

Initialize with domain setup status:
```markdown
# {Domain Name} - Current State

**Last Updated:** {Current Date}
**Status:** 🚧 SETUP IN PROGRESS

## Recent Achievements
- ✅ .governor/ folder structure created
- ✅ Core documentation files populated
- ⏳ Knowledge base population in progress
- ⏳ AgentFactory integration pending

## Current Status
- Agents defined: {count}
- Rules defined: {count}
- Allowed MCPs: {count}
- Knowledge files: {count}

## Next Steps
1. Populate knowledge/ folder with domain-specific FAQs
2. Test AgentFactory context loading
3. Validate MCP permission filtering
4. Run integration tests
```

### Phase 4: Knowledge Base Population

13. **Create Domain-Specific Knowledge Files**

```bash
DOMAIN_NAME="advertising"

# Create FAQ file
cat > /root/software/fly_achensee/${DOMAIN_NAME}/.governor/knowledge/faq.md <<'EOF'
# {Domain Name} - Frequently Asked Questions

## {Category 1}

### Q: {Question 1}
**A:** {Answer}

**Example:**
{Example scenario}

### Q: {Question 2}
**A:** {Answer}

## {Category 2}

{... more FAQs}
EOF

# Create procedures file
cat > /root/software/fly_achensee/${DOMAIN_NAME}/.governor/knowledge/procedures.md <<'EOF'
# {Domain Name} - Standard Operating Procedures

## Procedure 1: {Procedure Name}

**When to Use:** {Trigger conditions}

**Steps:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

**Expected Outcome:** {What success looks like}

{... more procedures}
EOF
```

### Phase 5: Testing and Validation

14. **Test AgentFactory Integration**

```bash
cd /root/software/fly_achensee

# Run AgentFactory test
python scripts/test_agent_factory.py

# Expected output:
# ✅ GovernorContext Loading
# ✅ Archetype Templates
# ✅ Subfolder Scanning - Found: customer_communication, advertising, user_communication
# ✅ Context Injection
# ✅ Governor Metadata
```

15. **Validate MCP Discovery**

```python
# Test MCP permission filtering
from src.shared.agent_factory import AgentFactory

factory = AgentFactory()

# Test advertising domain (should only get analytics, social_media)
advertising_mcps = factory.get_allowed_mcps("advertising")
print(f"Advertising allowed MCPs: {advertising_mcps}")
# Expected: ['analytics', 'social_media']

# Test customer_communication domain (should only get gmail, booking)
customer_mcps = factory.get_allowed_mcps("customer_communication")
print(f"Customer Communication allowed MCPs: {customer_mcps}")
# Expected: ['gmail', 'booking']

# Verify filtering works
assert 'gmail' not in advertising_mcps, "❌ Advertising should NOT have gmail access"
assert 'analytics' not in customer_mcps, "❌ Customer Communication should NOT have analytics access"

print("✅ MCP permission filtering working correctly")
```

16. **Run Complete Test Suite**

```bash
cd /root/software/fly_achensee

# Run all tests
pytest tests/test_22_datasets.py -v  # Should still pass (22/22)
python scripts/test_agent_factory.py  # Should find new domain

echo "✅ All tests passing with new domain"
```

### Phase 6: Documentation Update

17. **Update Root Documentation**

Update `state.md`:
```markdown
**8. Domain Structure** ✅ PARTIAL
- **Level 1 Domains:**
  - `customer_communication/.governor/` - ✅ COMPLETE
  - `advertising/.governor/` - ✅ COMPLETE (NEW)
  - `user_communication/.governor/` - ⏳ Empty structure ready
- **Status:** 2/3 domains populated
```

Update `todo.md`:
```markdown
#### T4B.1: Populate Advertising Domain
**Status:** ✅ COMPLETE
**Completed:** {Date}
```

## Quick Reference Checklist

When creating a new domain, ensure:

- [ ] Directory structure created (8 files + 3 folders)
- [ ] Project.md defines domain scope clearly
- [ ] Agents.md lists 3+ specialist agents with responsibilities
- [ ] Rules.md contains 15+ safety rules (NEVER, ALWAYS, ONLY)
- [ ] **MCP.md contains ALLOWED MCPs list (permission filter)**
- [ ] Governor.md uses archetype template with context injection
- [ ] Examples.md provides 5+ realistic workflows
- [ ] State.md and Todo.md initialized
- [ ] knowledge/ folder has domain-specific FAQs and procedures
- [ ] AgentFactory test passes (5/5)
- [ ] MCP permission filtering validated
- [ ] Root documentation updated (state.md, todo.md)

## Common Mistakes to Avoid

### ❌ Mistake 1: Putting MCP Connection Details in MCP.md
**Wrong:**
```markdown
# MCP.md
GMAIL_MCP_URL=https://gm.mcp.metamate.community/
GMAIL_AUTH_TOKEN=abc123
```

**Correct:**
```markdown
# MCP.md
## Allowed MCPs
- gmail

# Connection details are in root .env!
```

### ❌ Mistake 2: Copying Content Without Customization
**Wrong:** Copy-paste Governor.md from customer_communication without changes

**Correct:** Use archetype template, inject domain-specific context

### ❌ Mistake 3: Too Few or Too Many Rules
**Wrong:** Only 3-5 or 30+ rules in Rules.md

**Correct:** Around 15 rules (5 NEVER, 5 ALWAYS, 5 ONLY)

### ❌ Mistake 4: No Knowledge Base
**Wrong:** Empty knowledge/ folder

**Correct:** At least FAQ + procedures for domain

### ❌ Mistake 5: Allowing All MCPs
**Wrong:** Copy all MCPs from another domain

**Correct:** Only allow MCPs needed for THIS domain's workflows

## Advanced: Automation Script

For repetitive domain creation, consider creating:
```bash
# scripts/create_domain.sh
DOMAIN_NAME=$1
# ... automated population logic
```

## Troubleshooting

### Issue: AgentFactory can't find new domain
**Solution:** Check directory structure - must have `.governor/` folder

### Issue: MCP permission filtering not working
**Solution:** Verify MCP.md has "Allowed MCPs:" section with list

### Issue: Context injection failing
**Solution:** Ensure all 8 core files exist in .governor/ folder

### Issue: Tests failing after new domain
**Solution:** Run `python scripts/test_agent_factory.py` - check for errors in context loading

## References

- Fractal Architecture: `FRACTAL_ARCHITECTURE.md`
- MCP Discovery: `MCP_DISCOVERY_DESIGN.md`
- Agent Archetypes: `agent_archetypes/governor_archetype.md`
- Reference Domain: `customer_communication/.governor/`
- AgentFactory: `src/shared/agent_factory.py`
