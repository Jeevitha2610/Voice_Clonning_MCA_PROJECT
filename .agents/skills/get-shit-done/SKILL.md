---
name: get-shit-done
description: Meta-workflow engine for phased autonomous engineering. Provides structured workflows for plan-phase, execute-phase, verify-work, code-review, and validation to ensure rigor, systematic delivery, and zero unverified assumptions across complex projects.
---

# Get Shit Done (GSD): Phased Autonomous Engineering

GSD is an execution framework that structures complex software projects into distinct, rigorously verified phases: Discovery, Planning, Execution, Verification, and Review.

## Workflow Phases

### 1. Plan Phase (`plan-phase`)
- Break high-level requirements into tightly scoped phases and subtasks.
- Define explicit acceptance criteria, expected deliverables, and automated test checkpoints.
- Identify risk vectors, external dependencies, and performance constraints prior to writing code.

### 2. Execute Phase (`execute-phase`)
- Execute atomic task blocks sequentially without scope creep.
- Adhere strictly to the project architecture and technology stack constraints.
- Implement code and accompanying tests together in parallel.

### 3. Verify Work (`verify-work`)
- Execute comprehensive test suites, static type checking (`mypy`/`pyright`), and style audits.
- Validate that all acceptance criteria are met with verifiable evidence (logs, test outputs, benchmark metrics).
- Reject any work that fails automated tests or exhibits regressions.

### 4. Code Review & Polish (`code-review`)
- Perform systematic inspection of diffs:
  - Architecture compliance and separation of concerns.
  - Resource lifecycle management (memory leaks, file handle closures, GPU VRAM caching).
  - Error isolation, exception hierarchies, and meaningful error messages.
  - Documentation and typing clarity.

### 5. Validate Phase (`validate-phase`)
- Confirm end-to-end user workflows.
- Verify environmental reproducibility and clean startup states.
- Prepare Git commits and milestone summaries.

## Core Mandates
- **Zero Unverified Assumptions**: Never declare a milestone finished without test runs and verifiable terminal output.
- **Strict Scope Discipline**: Implement what was planned; do not introduce extraneous libraries or rewrite unrelated modules.
- **Fail Fast & Repair**: Diagnose root causes immediately upon test failures before proceeding.
