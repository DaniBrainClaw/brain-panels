# TaskFlow System — 7-Step Deep Research

## Step 1: What Is
TaskFlow is a durable flow substrate for multi-step background work in OpenClaw. It allows jobs to outlive one prompt or detached run, while maintaining one owner session, one return context, and a place to inspect or resume work.

## Step 2: How It Works
1. **Managed flows** created via `api.runtime.tasks.flow.createManaged()`.
2. **Child tasks** linked via `runTask()` — connects detached ACP/subagent work to parent flow.
3. **State persistence** via `stateJson` — persisted state bag survives restarts.
4. **Revision tracking** — every mutating method is revision-checked for conflict-safe mutations.
5. **Waiting/Resume pattern:** `setWaiting()` → external event → `resume()`.
6. **Lifecycle:** create → run → wait → resume → finish/fail/cancel.

**API Shape:**
- Canonical: `api.runtime.tasks.flow`
- Alias: `api.runtime.taskFlow` (deprecated)

**Methods:**
- `createManaged({ controllerId, goal, currentStep, stateJson })`
- `runTask({ flowId, runtime, childSessionKey, runId, task, status })`
- `setWaiting({ flowId, expectedRevision, currentStep, stateJson, waitJson })`
- `resume({ flowId, expectedRevision, status, currentStep, stateJson })`
- `finish({ flowId, expectedRevision, stateJson })`
- `fail({ flowId, expectedRevision, stateJson })`
- `cancel({ flowId })` or `requestCancel({ flowId })`

## Step 3: Use Cases
- **Multi-step background jobs** with one owner session.
- **Inbox triage workflows** — classify messages, wait for replies, finalize.
- **PR intake lane** — fetch PRs, classify, route to actions (close, request changes, refactor, escalate).
- **Plugin orchestration** — tool work that must survive restarts.
- **External system wait** — flow waits for human input or external API callback.

## Step 4: Problems
- **Lobster dependency** — TaskFlow is the runtime substrate; authoring uses Lobster language (`.lobster` files).
- **No built-in branching** — conditional logic must live in calling code/Lobster.
- **Revision conflicts** — must carry forward `flow.revision` after each mutation or fail.
- **ACP/subagent overhead** — setting up proper child session keys and runtime labels is complex.
- **No setFlowOutput** — `stateJson` is the only state bag; no separate output accumulation API.

## Step 5: Solutions
- **Start with Lobster examples** (`inbox-triage.lobster`, `pr-intake.lobster`).
- **Keep conditionals above the runtime** — let authoring layer handle business logic.
- **Store minimum state** — only what's needed to resume.
- **Use `getTaskSummary(flowId)`** — compact health view of child work.
- **Use `cancel()`** for full cancellation including linked child tasks.

## Step 6: Edge Cases
- **One-task mirrored flows** — created by core runtime for detached ACP/subagent work (managed flow skill not needed).
- **Flow identity persistence** — survives Gateway restarts.
- **waitJson structure** — `kind: "reply"`, `channel`, `threadKey` for reply-based waits.
- **controllerId naming** — use `plugin-name/flow-purpose` format (e.g., `my-plugin/inbox-triage`).
- **Revision check failures** — mutation fails if revision mismatch; caller must handle.

## Step 7: Creative Uses
- **Cross-agent orchestration:** One agent creates flow, another resumes — same flow survives session boundaries.
- **Human-in-the-loop:** `setWaiting()` with `waitJson` for manual approval steps.
- **State machine flows:** Model multi-state workflows (draft → review → approved → published).
- **Resumable batch jobs:** Large dataset processing with checkpointed state.
- **Integration with MCP:** Child task can be MCP server invocation with result passed back via stateJson.

---

## TaskFlow vs Cron Jobs

| Aspect | TaskFlow | Cron Jobs |
|--------|----------|-----------|
| Trigger | Explicit (code) | Time-based |
| State | Persisted in flow | Lost between runs |
| Wait/Resume | Yes | No |
| Parent-child linking | Yes | No |
| Revision safety | Yes | No |
| Use case | Multi-step orchestration | Recurring automation |

---

## Hypothesis Update
- **Original:** "TaskFlow is for orchestration — unknown details."
- **Confirmed:** TaskFlow provides durable parent-child task linking with revision-safe state. It IS the right tool for multi-step work that survives restarts.

---

## Sources
- `taskflow/SKILL.md` — OpenClaw taskflow skill reference
- `taskflow/examples/inbox-triage.lobster` — Lobster example
- `taskflow/examples/pr-intake.lobster` — PR intake example
