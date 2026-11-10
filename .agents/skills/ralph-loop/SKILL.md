---
name: ralph-loop
description: Iterative autonomous loop pattern for Antigravity agents. Externalizes agent state and task memory to disk (PRD.md and progress.txt), executes tasks sequentially with fresh session context, handles rate-limit fallbacks, and maintains verifiable progress across long-running development missions.
---

# Ralph Loop for Antigravity

Ralph Loop solves context degradation and multi-turn forgetting by externalizing state to persistent disk files and executing atomic, verifiable iterations.

## Core Architectural Principles

1. **Externalize Memory to Disk**:
   - `PRD.md`: Defines high-level project requirements, architecture boundaries, and user stories.
   - `tasks.md` / `task-list`: Explicit, atomic, numbered tasks with verifiable criteria.
   - `progress.txt`: Append-only chronological log of completed tasks, test results, and next targets. Never delete prior progress.
2. **Fresh Session Iterations**:
   - Each iteration begins by reading the current state from disk files rather than relying on LLM context history.
   - The agent reads `PRD.md`, checks `progress.txt`, identifies the next incomplete task, executes that single task, verifies it with tests, logs the result, commits to Git, and advances.
3. **Execution Protocol (One Task Per Cycle)**:
   ```text
   1. Read PRD.md / Architecture specifications.
   2. Check progress.txt for latest checkpoint.
   3. Select exactly ONE pending task.
   4. Execute code changes / tests for that task.
   5. Run validation test suite to verify no regressions.
   6. Append progress to progress.txt (with timestamp, test output, commit hash).
   7. Commit changes to Git with concise conventional commit message.
   8. Advance to next task or signal mission completion.
   ```
4. **Model Fallback Chain**:
   - Primary: Fast / high-throughput model (e.g. Gemini 3 Flash).
   - Fallback 1: Reasoning / Deep Thinking model (e.g. Claude Opus 4.6 / Claude Sonnet 4.6).
   - Fallback 2: High-context Pro model (e.g. Gemini 3.1 Pro High).
   - Rate limit or quota errors trigger seamless fallback transition without losing disk-persisted state.

## Rules of Engagement

- **Never edit or delete entries in `progress.txt`**: Only append new checkpoints.
- **Do not multitask**: Do not attempt multiple roadmap items in one iteration. Verify and commit after each atomic task.
- **Continuous automated verification**: An item is only marked complete when automated unit/integration tests pass.
