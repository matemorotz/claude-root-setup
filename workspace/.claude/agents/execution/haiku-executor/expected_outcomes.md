# HaikuExecutor Expected Outcomes

## File Edit Tasks

**Expected:**
- File modified successfully
- Changes match specified edit exactly
- No syntax errors introduced
- Original formatting preserved (indentation, spacing)
- Only specified sections changed

**Validation:**
```bash
# Check file exists and is valid
test -f ${file_path}

# For Python files
python -m py_compile ${file_path}

# For TypeScript files
npx tsc --noEmit ${file_path}

# For JavaScript files
npx eslint ${file_path}
```

**Success Criteria:**
- Exit code 0
- File size reasonable (not empty, not huge)
- Git diff shows only intended changes

---

## Command Execution Tasks

**Expected:**
- Command completes with exit code 0
- Output matches expected pattern
- No errors in stderr (unless expected)
- Execution time < ${timeout} seconds

**Validation:**
```bash
# Check exit code
test $? -eq 0

# Check output contains expected string
echo "${output}" | grep -q "${expected_pattern}"

# Check no errors (unless allowed)
test -z "${stderr}" || echo "${stderr}" | grep -q "${allowed_error_pattern}"
```

**Success Criteria:**
- Command ran successfully
- Expected output produced
- No unexpected errors

---

## Research Tasks

**Expected:**
- Research file created at specified path
- Contains working code examples (if requested)
- Includes official documentation links
- Structured according to template
- All sections present

**Validation:**
```bash
# Check file structure
grep -q "## Overview" ${research_file}
grep -q "## Official Examples" ${research_file}
grep -q "## Best Practices" ${research_file}
grep -q "## References" ${research_file}

# Check has content (not empty)
test $(wc -l < ${research_file}) -gt 50
```

**Success Criteria:**
- File exists and is well-structured
- Contains actionable information
- References are valid URLs

---

## API Call Tasks

**Expected:**
- HTTP request sent successfully
- Response received with expected status code
- Response body parsed correctly
- Data extracted as specified

**Validation:**
```bash
# Check HTTP status
test ${http_status} -eq 200

# Check response not empty
test -n "${response_body}"

# Check response contains expected keys
echo "${response_body}" | jq -e '.data' > /dev/null
```

**Success Criteria:**
- API call successful
- Response contains expected data
- No authentication errors

---

## General Validation Rules

### Always Check:
1. **Exit codes** - Must be 0 for success
2. **File integrity** - Files not corrupted
3. **Output format** - Matches expected structure
4. **Error messages** - Clear and actionable
5. **Execution time** - Within reasonable limits

### Never Allow:
1. **Silent failures** - Always report errors
2. **Partial execution** - Either complete or fail
3. **Unreported side effects** - Document all changes
4. **Ambiguous status** - Success/failure must be clear

### Report Format:
```json
{
  "status": "success" | "error",
  "step_number": <number>,
  "result": "<what was accomplished>",
  "validation": {
    "exit_code": <number>,
    "execution_time": "<seconds>",
    "changes_made": ["<file1>", "<file2>"],
    "output_size": "<bytes>"
  },
  "error": null | {
    "message": "<error message>",
    "file": "<file path>",
    "line": <line number>,
    "fix_suggestion": "<how to fix>"
  }
}
```
