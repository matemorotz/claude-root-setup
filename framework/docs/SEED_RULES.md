# Seed Rules — Workflow-Scoped Context Blocks

**Purpose**: Reusable context blocks that reproduce agent workflows consistently from the same initial context and seed chain
**Last Updated**: 2026-03-26

---

## What Are Seed Rules?

Seed rules are **individual JSON files** that define a single actionable rule for agents. Each rule is a self-contained context block — it knows its purpose, its source of truth, what it instructs, and how it connects to other rules.

**The runtime contract is simple**: only the `rule` one-liner from each seed is ever injected into an agent's system prompt. Everything else is for tooling and development only.

---

## Schema

Each seed rule is stored as a JSON file. The filename (without `.json`) is the rule ID.

```json
{
  "id": "jwt_authentication_pattern",
  "goal": "Ensure all protected routes use the project's established JWT verification to avoid inconsistent auth implementations",
  "grounding": "app/auth.py:verify_token,app/auth.py:create_access_token",
  "rule": "Protect all non-public endpoints with @require_auth; generate tokens with create_access_token() from app/auth.py",
  "connected_seed_rules": {
    "auth_workflow": ["bcrypt_password_hashing", "sqlalchemy_user_model"],
    "api_workflow": ["fastapi_route_pattern", "jwt_authentication_pattern"]
  }
}
```

### Field Reference

| Field | Type | Injected into prompts? | Description |
|-------|------|----------------------|-------------|
| `id` | string | No | Snake_case filename without `.json`. Format: `{domain}_{concept}_{type}` where type is `pattern`, `convention`, or `decision`. |
| `goal` | string | **No** | One sentence answering "why does this rule exist?" — for developers and tooling only. |
| `grounding` | string | **No** | Comma-separated references to the knowledge source: `file:symbol`, `CLAUDE.md#section`, or `pattern:Name`. |
| `rule` | string | **Yes — only this field** | Single imperative one-liner. The only content injected at runtime. |
| `connected_seed_rules` | object | **No** | Keys are workflow names; values are ordered arrays of rule IDs in that workflow chain. For tooling only. |

---

## Storage Structure

Seeds live **inside each project**, version-controlled alongside the code they govern:

```
{project_root}/
  seeds/
    workflows/
      auth_workflow/
        jwt_authentication_pattern.json
        bcrypt_password_hashing.json
        sqlalchemy_user_model.json
      api_workflow/
        fastapi_route_pattern.json
        response_format_convention.json
      coding_conventions/
        snake_case_naming_convention.json
        pytest_testing_convention.json
      general/
        project_overview_pattern.json
        tech_stack_decision.json
```

- **One directory per workflow** — each workflow is independently reproducible
- **Seeds are reusable** — a seed can be referenced from multiple workflows via `connected_seed_rules`
- **Workflow name = directory name**
- **Auto-generated location**: `rule-distiller.py` writes to `seeds/workflows/general/` by default

---

## Runtime Behavior: System Prompt Assembly

When an agent starts with a workflow, `assemble_prompt_rules()` is called. It:
1. Reads all `.json` files from `seeds/workflows/{workflow}/`
2. Follows `connected_seed_rules[workflow]` chains (depth 1, deduplicated)
3. Returns **only the `rule` strings**, joined by newlines

```
Workflow: auth_workflow
  Seed chain: jwt_authentication_pattern → bcrypt_password_hashing → sqlalchemy_user_model

System prompt injection (only rule fields):
  "Protect all non-public endpoints with @require_auth; generate tokens with create_access_token() from app/auth.py
   Hash all passwords with bcrypt before storing; never store plaintext passwords
   All user models inherit from Base in app/models/base.py; always use Alembic for schema changes"
```

The full JSON objects (goal, grounding, connected_seed_rules) are **never loaded into the prompt**.

---

## Connected Seed Rules — Workflow Chains

The `connected_seed_rules` object maps workflow names to ordered arrays of rule IDs:

```json
"connected_seed_rules": {
  "auth_workflow": ["bcrypt_password_hashing", "sqlalchemy_user_model"],
  "api_workflow": ["fastapi_route_pattern"]
}
```

Each key is a workflow name. Each value is an ordered list of rule IDs that follow this rule in that workflow's seed chain.

**Relationship semantics**:
- Keys ending in `_workflow` → rules typically applied together in that workflow
- Key `prerequisite` → rules that must be in place before this one applies
- Key `coding_workflow`, `architecture_workflow` → inferred category groupings from auto-generation

When building a system prompt for `auth_workflow`, the assembler starts with all seeds in `seeds/workflows/auth_workflow/` and expands their `connected_seed_rules["auth_workflow"]` lists (one level deep).

---

## Examples

### Pattern Rule
```json
{
  "id": "fastapi_route_pattern",
  "goal": "Ensure all API endpoints follow the project's router structure to keep route registration consistent",
  "grounding": "app/routes/auth.py,app/routes/users.py,app/main.py:include_router",
  "rule": "Define all routes in app/routes/{resource}.py as APIRouter instances; register in app/main.py with include_router",
  "connected_seed_rules": {
    "api_workflow": ["jwt_authentication_pattern", "sqlalchemy_user_model"]
  }
}
```

### Convention Rule
```json
{
  "id": "snake_case_naming_convention",
  "goal": "Maintain consistent naming so agents and developers can predict symbol names without looking up each file",
  "grounding": "pattern:PythonNamingConventions,CLAUDE.md#naming",
  "rule": "Use snake_case for all function and variable names; use PascalCase only for class names",
  "connected_seed_rules": {
    "coding_workflow": ["pytest_testing_convention", "directory_structure_convention"]
  }
}
```

### Decision Rule
```json
{
  "id": "tech_stack_decision",
  "goal": "Ensure new code uses only the approved technology stack to avoid dependency sprawl",
  "grounding": "project.md#tech-stack",
  "rule": "Use only the approved stack: Python 3.12, FastAPI, SQLAlchemy, pytest, LangGraph",
  "connected_seed_rules": {}
}
```

---

## Auto-Generation

The pipeline generates seed rules automatically on first session:

```bash
# Step 4 of session-start.sh pipeline:
python scripts/rule-distiller.py extracted_patterns.json \
  --project myproject \
  --workflow general \
  --output-dir /path/to/project
```

Output: `seeds/workflows/general/{rule_id}.json` per detected pattern.

To target a specific workflow:
```bash
python scripts/rule-distiller.py patterns.json --project myproject --workflow auth_workflow
```

---

## Writing Seed Rules Manually

Rules are most useful when written by a human who knows the project:

**DO:**
- Write the `rule` as a single, actionable imperative sentence
- Reference specific file paths and function names in `grounding`
- Connect rules that agents should load together via `connected_seed_rules`
- Keep `goal` focused on "why" not "what"

**DON'T:**
- Write multi-sentence rules — split into multiple seed files instead
- Include full code in any field
- Duplicate information across rules
- Reference non-existent files in `grounding`

---

## API Reference

```python
from docs.fractal_memory import OpusLevelMemory

opus = OpusLevelMemory(".claude/memory/opus_level", project_root="/path/to/project")

# Load all rules for a workflow
rules = opus.get_seed_rules("myproject", workflow="auth_workflow")

# Assemble runtime system prompt (rule strings only)
prompt_fragment = opus.assemble_prompt_rules("auth_workflow")

# Store new rules
opus.store_seed_rules("myproject", rules_list, workflow="auth_workflow")
```

```python
from docs.context_distiller import build_system_prompt_rules

# Extract only rule strings from a list of seed rule dicts
prompt = build_system_prompt_rules(rules)
```

---

**Status**: ✅ Active Architecture
**Applies To**: All seed rule generation, storage, and agent context loading
**Auto-Generated At**: `seeds/workflows/general/` on first project session
