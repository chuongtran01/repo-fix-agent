# Architecture

This project uses LangGraph as the outer workflow orchestrator.

LangGraph is responsible for:

- Maintaining shared state
- Controlling execution order
- Routing between nodes
- Preventing infinite retry loops
- Enforcing verification before completion

The LLM is used inside individual nodes for reasoning tasks such as planning, editing, reviewing test failures, and summarizing changes.

## Project Structure

```txt
src/repo_fix_agent/
├── graph/
│   ├── builder.py      # Builds the LangGraph workflow
│   ├── state.py        # Defines shared agent state
│   └── routes.py       # Conditional routing logic
│
├── nodes/
│   ├── analyze_request.py  # Understands the user's bug/fix request
│   ├── inspect_repo.py     # Finds and reads relevant files
│   ├── plan_fix.py         # Produces a step-by-step fix plan
│   ├── edit_files.py       # Applies targeted code changes
│   ├── run_tests.py        # Runs test/typecheck commands
│   ├── review_result.py    # Decides whether to retry, finish, or rollback
│   ├── rollback.py         # Restores original files when needed
│   └── final_summary.py    # Summarizes changes and test results
│
├── tools/
│   ├── file_tools.py       # read_file, write_file, replace_in_file
│   ├── search_tools.py     # grep/search helpers
│   ├── command_tools.py    # safe command execution
│   └── git_tools.py        # git diff, restore, status
│
├── prompts/
│   ├── planner.md
│   ├── editor.md
│   ├── reviewer.md
│   └── summarizer.md
│
├── llm/
│   └── model.py            # LLM wrapper
│
└── main.py                 # CLI entry point
```

## Core Agent State

```python
class AgentState(TypedDict):
    user_request: str
    repo_path: str

    relevant_files: list[str]
    files_read: dict[str, str]

    plan: list[str]
    changed_files: list[str]
    original_files: dict[str, str]

    test_command: str
    test_output: str
    tests_passed: bool

    iteration: int
    max_iterations: int

    errors: list[str]
    final_summary: str
```

## Main Nodes

### 1. Analyze Request

Understands the user's request and determines the type of task.

Example input:

Fix the failing login test.

Example output:

- Task type: bug fix
- Likely areas: auth, login, tests
- Needs tests: yes

### 2. Inspect Repo

Finds files that may be relevant to the request.

Uses tools such as:

- `list_files()`
- `read_file()`
- `search_code()`
- `grep()`

This node should not edit anything.

### 3. Plan Fix

Creates a high-level plan based on inspected files.

Example:

1. Read the failing auth test
2. Inspect login service behavior
3. Compare expected vs actual response
4. Update login validation logic
5. Run auth tests

### 4. Edit Files

Applies targeted changes.

Preferred editing strategy:

`replace_in_file(path, old, new)`

Avoid rewriting entire files unless necessary.

Before editing, the agent stores the original file content for rollback.

### 5. Run Tests

Runs a safe test command such as:

- `npm test`
- `pytest`
- `mvn test`

The command should be restricted by a safety allowlist.

### 6. Review Result

Decides what to do next.

Possible outcomes:

- tests passed -> `final_summary`
- tests failed + retries left -> `inspect_repo` or `edit_files`
- tests failed + no retries left -> `rollback`

### 7. Rollback

Restores modified files if the agent cannot produce a valid fix.

Rollback can use either:

- `write_file(path, original_content)`
- `git checkout -- path`

### 8. Final Summary

Summarizes:

- Files changed
- What was fixed
- Tests run
- Whether tests passed
- Any remaining concerns

## Safety Rules

The agent should follow these rules:

- Never edit a file before reading it.
- Never run destructive shell commands.
- Always save original file content before editing.
- Always run tests after editing.
- Stop after a maximum number of retries.
- Roll back if the fix fails and cannot be safely completed.
- Summarize all changed files.

## Allowed Commands

Initially allow only safe commands:

- `npm test`
- `npm run test`
- `npm run typecheck`
- `pytest`
- `python -m pytest`
- `mvn test`
- `gradle test`

Do not allow:

- `rm -rf`
- `sudo`
- `curl | bash`
- `git push`
- `npm publish`
- `docker system prune`

## MVP Scope

The first version should support:

- Reading a local repo
- Searching files
- Planning a fix
- Editing one to three files
- Running one test command
- Retrying once or twice
- Producing a final summary

Out of scope for MVP:

- Opening pull requests
- Deploying code
- Editing many files
- Running arbitrary shell commands
- Handling huge monorepos
- Long-term memory

## Example Usage

```bash
python -m repo_fix_agent.main \
  --repo-path /path/to/my/repo \
  --request "Fix the failing login test" \
  --test-command "npm test"
```

## Example Final Output

```txt
Fix completed successfully.

Files changed:
- src/auth/login.ts
- tests/auth/login.test.ts

Summary:
- Updated login validation to correctly handle missing email input.
- Adjusted test expectation to match the normalized error response.
- Ran npm test successfully.

Tests:
- npm test: passed
```

## Roadmap

See `ROADMAP.md` for the full phased roadmap.
