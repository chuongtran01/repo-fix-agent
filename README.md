# RepoFix Agent

RepoFix Agent is a repo-aware coding agent that can inspect a real codebase, identify relevant files, propose a fix, edit files, run tests, retry on failure, and summarize the final changes.

The goal of this project is to demonstrate practical agent engineering skills:

- Tool use
- File system operations
- Planning under uncertainty
- Multi-step workflow orchestration
- Test-based verification
- Error handling
- Rollback support

---

## High-Level Flow

```txt
User Request
   ↓
Analyze Request
   ↓
Inspect Repo
   ↓
Plan Fix
   ↓
Edit Files
   ↓
Run Tests
   ↓
Review Result
   ├── tests pass → Final Summary
   ├── tests fail + retries left → Inspect/Edit again
   └── tests fail + no retries left → Rollback or Report Failure
```
