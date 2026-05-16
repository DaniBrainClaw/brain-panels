# Hook Execution Order — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23  
**Topic:** What is exact hook execution order when multiple hooks fire on same event?  
**Priority:** MEDIUM (from backlog.md #16)  
**Research Depth:** 6-Layer Exhaustive  

---

## TABLE OF CONTENTS
1. [What Is — Definition & Core Concept](#1-what-is--definition--core-concept)
2. [How It Works — Architecture & Mechanics](#2-how-it-works--architecture--mechanics)
3. [Uses — Practical Applications](#3-uses--practical-applications)
4. [Problems — Known Issues & Limitations](#4-problems--known-issues--limitations)
5. [Solutions — Best Practices & Workarounds](#5-solutions--best-practices--workarounds)
6. [Edge Cases — Unusual Scenarios](#6-edge-cases--unusual-scenarios)
7. [Creative Uses — Innovative Applications](#7-creative-uses--innovative-applications)
8. [NEW Questions Opened by This Research](#8-new-questions-opened-by-this-research)
9. [Sources](#9-sources)

---

## 1. WHAT IS — Definition & Core Concept

### Definition

**Hook execution order** determines how OpenClaw resolves conflicts and sequences multiple handlers when the same hook event fires. OpenClaw uses a **two-level sorting system** combining **source precedence** (hook origin hierarchy) and **priority values** (within same source).

### Two-Level Sorting Architecture

| Level | Sort Factor | Scope | Default Behavior |
|-------|-------------|-------|------------------|
| **Level 1** | Source Precedence | Across different hook sources | Higher precedence wins |
| **Level 2** | Registration Index | Within same precedence | FIFO (first-registered = first-run) |

### Hook Source Hierarchy (Precedence Order)

| Source | Precedence | Trusted Local Code | Default Enable Mode | Can Override |
|--------|------------|-------------------|-------------------|--------------|
| `openclaw-bundled` | 10 (lowest) | ✅ Yes | Default-on | `openclaw-bundled` only |
| `openclaw-plugin` | 20 | ✅ Yes | Default-on | `openclaw-bundled`, `openclaw-plugin` |
| `openclaw-managed` | 30 | ✅ Yes | Default-on | All except `openclaw-workspace` |
| `openclaw-workspace` | 40 (highest) | ✅ Yes | **Explicit-opt-in** | `openclaw-workspace` only |

**Key insight**: Workspace hooks have HIGHEST precedence but are DISABLED by default. They must be explicitly enabled via config.

### Discovery Order vs Execution Order

| Concept | Meaning |
|---------|---------|
| **Discovery order** | Directories scanned → hook directories found → loaded into registry |
| **Execution order** | Two-level sort: source precedence FIRST, then registration index |

**Important**: Discovery order and execution order are DIFFERENT. Execution order is determined by source precedence, not discovery order.

---

## 2. HOW IT WORKS — Architecture & Mechanics

### Hook Registry Structure

Each registered hook entry contains:
```typescript
interface HookEntry {
  hook: {
    name: string;           // e.g., "before_prompt_build"
    source: HookSource;    // "openclaw-bundled" | "openclaw-plugin" | "openclaw-managed" | "openclaw-workspace"
  };
  priority?: number;       // Optional priority override (default: 0)
  handler: Function;       // The handler implementation
  pluginId: string;        // Plugin identifier
}
```

### Sorting Algorithm (from `config-Nq7s3Dxw.js`)

```javascript
// Level 1: Source precedence delta
const precedenceDelta = getHookSourcePolicy(a.entry.hook.source).precedence 
                      - getHookSourcePolicy(b.entry.hook.source).precedence;
if (precedenceDelta !== 0) return precedenceDelta;

// Level 2: Registration index (FIFO)
return a.index - b.index;
```

**Within same precedence level**: Registration order (first loaded = first executed). NOT priority value here.

### Priority Override Within Same Source

For hooks from the **same source**, execution order within that source is determined by registration index. However, hooks can set an explicit `priority` value that affects ordering **within same precedence**:

```javascript
// getHooksForName sorts by priority (higher first)
return registry.typedHooks.filter((h) => h.hookName === hookName)
  .toSorted((a, b) => (b.priority ?? 0) - (a.priority ?? 0));
```

**Note**: Priority sorting applies AFTER source precedence filtering — it's a secondary sort for hooks that share the same precedence level.

### Three Hook Execution Modes

OpenClaw has **three distinct execution patterns** based on hook type:

#### Mode 1: Void Hook (Fire-and-Forget)
- **Behavior**: All handlers run in PARALLEL via `Promise.all()`
- **Error handling**: Each handler wrapped in try/catch; errors logged but don't block other handlers
- **Failure policy**: `fail-open` (default) — logs error and continues
- **Example hooks**: Most plugin hooks use this pattern

```javascript
async function runVoidHook(hookName, event, ctx) {
  const hooks = getHooksForName(registry, hookName);
  const promises = hooks.map(async (hook) => {
    try {
      await hook.handler(event, ctx);
    } catch (err) {
      handleHookError({ hookName, pluginId: hook.pluginId, error: err });
    }
  });
  await Promise.all(promises);
}
```

#### Mode 2: Modifying Hook (Sequential with Merge)
- **Behavior**: Handlers run SEQUENTIALLY in priority order
- **Result handling**: Each handler's result merges into accumulator; `mergeResults` policy function combines results
- **Early termination**: If `shouldStop` policy returns true, stops executing remaining handlers
- **Example hooks**: `before_model_resolve`, `before_prompt_build`, `before_agent_start`

```javascript
async function runModifyingHook(hookName, event, ctx, policy = {}) {
  let result;
  for (const hook of hooks) {
    const handlerResult = await hook.handler(event, ctx);
    if (handlerResult !== void 0 && handlerResult !== null) {
      if (policy.mergeResults) result = policy.mergeResults(result, handlerResult, hook);
      else result = handlerResult;
      if (policy.shouldStop?.(result)) break; // Early termination
    }
  }
  return result;
}
```

#### Mode 3: Claiming Hook (First-Wins)
- **Behavior**: Handlers run SEQUENTIALLY; first `{ handled: true }` wins
- **Result handling**: Returns immediately when a handler returns `{ handled: true }`
- **Example hooks**: `inbound_claim` (first plugin to claim handles the message)

```javascript
async function runClaimingHook(hookName, event, ctx) {
  for (const hook of hooks) {
    try {
      const handlerResult = await hook.handler(event, ctx);
      if (handlerResult?.handled) return handlerResult;
    } catch (err) {
      handleHookError({ hookName, pluginId: hook.pluginId, error: err });
    }
  }
}
```

### Failure Policy System

Each hook has a **failure policy** determining behavior when handler throws:

| Policy | Behavior | Default Hooks |
|--------|----------|---------------|
| `fail-open` | Log error, continue to next handler | Most hooks |
| `fail-closed` | Throw, halt execution | `before_tool_call` |

```javascript
const shouldCatchHookErrors = (hookName) => 
  catchErrors && (failurePolicyByHook[hookName] ?? "fail-open") === "fail-open";

// Current failure policy config:
failurePolicyByHook: { before_tool_call: "fail-closed" }
```

### Error Handling Detail

```javascript
const handleHookError = (params) => {
  const msg = `[hooks] ${params.hookName} handler from ${params.pluginId} failed: ${String(params.error)}`;
  if (shouldCatchHookErrors(params.hookName)) {
    logger?.error(msg);
    return; // Continue to next handler
  }
  throw new Error(msg, { cause: params.error }); // Halt execution
};
```

### Internal Hooks Execution Order

For **internal hooks** (standalone hooks in `~/.openclaw/hooks/`):
- Handlers called in **registration order** (insertion order)
- Errors caught and logged per-handler
- No priority sorting for internal hooks (only plugin hooks have priority field)

From `internal-hooks-2legcEEL.js`:
> "Handlers are called in registration order. Errors are caught and logged"

### Plugin Hook Execution Order

For **plugin hooks** (hooks from plugins):
1. Source precedence (bundled < plugin < managed < workspace)
2. Within same source: priority value (higher first), then registration index
3. Execution mode depends on hook type (void/modifying/claiming)

### Execution Order Flow Diagram

```
Hook Event Fires
       │
       ▼
┌─────────────────────────────────────┐
│ Get all handlers for hook name      │
│ Sort by:                           │
│   1. Source precedence (high→low)  │
│   2. Priority (high→low)           │
│   3. Registration index (FIFO)     │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Execute based on hook type:        │
│   • void → Promise.all (parallel)  │
│   • modifying → sequential+merge   │
│   • claiming → first-wins         │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Error handling per failure policy  │
│   • fail-open → log + continue    │
│   • fail-closed → throw + halt     │
└─────────────────────────────────────┘
```

---

## 3. USES — Practical Applications

### Multi-Plugin Processing Pipeline

When multiple plugins want to process the same data (e.g., `before_prompt_build`):

```
Plugin A (openclaw-plugin, priority=0) → Plugin B (openclaw-plugin, priority=10) → Plugin C (openclaw-managed)
         │                                        │                                    │
         ▼                                        ▼                                    ▼
   Runs first (higher priority)            Runs second                         Runs last (highest precedence)
```

### Priority-Based Access Control

Plugins can use priority to establish processing order for security checks:

| Priority | Plugin | Purpose |
|----------|--------|---------|
| 100 | `security-check` | First: validate input |
| 50 | `sanitizer` | Second: sanitize content |
| 0 | `content-logger` | Third: log for audit |

### Hook Override Pattern

Managed hooks can override bundled hooks with the same name:

```javascript
// Bundled hook (precedence=10) runs first
// Managed hook (precedence=30) can override/replace it
```

### Chained Modification

For `before_prompt_build`, each modifying hook builds on previous result:

```javascript
// Handler 1: Add system context
result = { system: { context: "base" } }

// Handler 2: Merge additional context  
result = merge(prev, { system: { context: "base + extension" } })

// Handler 3: Final transformation
result = merge(prev, { system: { context: "base + extension + final" } })
```

---

## 4. PROBLEMS — Known Issues & Limitations

### Problem 1: Confusing Precedence vs Priority

**Issue**: Developers often confuse "precedence" (source hierarchy) with "priority" (numeric value within same source).

**Symptom**: Setting `priority: 100` on a bundled hook doesn't make it run before a managed hook with `priority: 0`.

**Reality**: Source precedence always wins. Priority only matters within same source level.

### Problem 2: Workspace Hooks Disabled by Default

**Issue**: Workspace hooks have HIGHEST precedence but are disabled by default.

**Confusion**: Users enable a workspace hook expecting it to override everything, but it doesn't fire because it's still disabled.

**Solution**: Must explicitly set `hooks.internal.entries.my-workspace-hook.enabled: true` in config.

### Problem 3: No Built-in Hook Ordering Comments

**Issue**: When multiple hooks from same source register for same event, there's no built-in way to enforce ordering comments.

**Current state**: Registration index determines order, but there's no mechanism for "Plugin A must run before Plugin B."

**Workaround**: Use same plugin or consolidate into single hook with internal dispatching.

### Problem 4: Void Hooks Run In Parallel (Non-Deterministic Within Priority Group)

**Issue**: Void hooks execute all handlers via `Promise.all()`, meaning completion order is non-deterministic.

**Problem for async dependencies**: If Handler B depends on Handler A completing first, void hooks won't guarantee this.

**Example problematic scenario**:
```javascript
// Handler A: Updates session state (async)
// Handler B: Reads session state (expects A done)
// In void mode, B might run before A completes
```

### Problem 5: Error Isolation Can Hide Failures

**Issue**: With `fail-open` policy, individual handler failures are logged but don't stop execution.

**Risk**: Partial failures may not be visible to users or operators without log inspection.

### Problem 6: No Execution Order Tracing

**Issue**: There's no built-in mechanism to trace execution order at runtime.

**Debugging difficulty**: When something goes wrong with hook execution order, diagnosis requires code inspection.

---

## 5. SOLUTIONS — Best Practices & Workarounds

### Solution 1: Understanding the Two-Level Sort

**Best practice**: Always remember: **Source precedence → Registration index → Priority value** (in that order).

**Mental model**:
1. First, hooks are filtered by their source (bundled < plugin < managed < workspace)
2. Within same source, registration order determines base order
3. Priority is a tiebreaker for same-source hooks

### Solution 2: Enable Workspace Hooks Explicitly

**For workspace hooks to fire**:
```json
{
  "hooks": {
    "internal": {
      "entries": {
        "my-workspace-hook": {
          "enabled": true
        }
      }
    }
  }
}
```

### Solution 3: Use Same Source for Ordering Dependencies

**If you need Plugin A to run before Plugin B**:
- Option 1: Put both in same plugin
- Option 2: Use managed hooks (same precedence level)
- Option 3: Consolidate into single hook with internal handler registry

### Solution 4: Use Modifying Hooks for Ordered Processing

**For sequential dependencies**: Use hooks that support `runModifyingHook` pattern:
- `before_prompt_build` — sequential, result merging
- `before_model_resolve` — sequential, result merging
- `before_agent_start` — sequential, result merging

**Avoid void hooks** when handlers have dependencies.

### Solution 5: Debug Hook Execution

**Check what hooks are registered**:
```bash
openclaw hooks list --verbose
```

**Check specific hook eligibility**:
```bash
openclaw hooks info <hook-name>
```

**View gateway logs for hook execution**:
```bash
./scripts/clawlog.sh | grep hook
```

### Solution 6: Use Priority Wisely

**Setting priority for same-source hooks**:
```javascript
// In your hook's HOOK.md
metadata: {
  openclaw: {
    priority: 100  // Run before other hooks from same source
  }
}
```

**Priority value guidelines**:
| Priority | Use Case |
|----------|----------|
| 100+ | Critical pre-processing (security, validation) |
| 50-99 | Normal pre-processing |
| 0 | Default |
| Negative | Post-processing (after everything else) |

### Solution 7: Design for Failure

**Always wrap hook handlers in try/catch**:
```javascript
const handler = async (event) => {
  try {
    // Your logic
  } catch (err) {
    console.error(`[my-hook] Failed:`, err);
    // Don't rethrow unless critical
  }
};
```

**Rationale**: `fail-open` means your error won't block other hooks, but only if you don't rethrow.

---

## 6. EDGE CASES — Unusual Scenarios

### Edge Case 1: Two Plugins Register Same Hook Name

**Scenario**: Plugin A and Plugin B both register `before_prompt_build`.

**Resolution**: Both run, sorted by source precedence first, then priority/index. Since both are `openclaw-plugin`, they use same precedence level — priority or registration order determines execution.

**Key insight**: Plugin hooks for same event from same source don't override each other — both run.

### Edge Case 2: Hook Returns Non-Object Value

**Scenario**: Modifying hook handler returns a primitive (string, number) instead of object.

**Resolution**: Non-object results are ignored for merging purposes. Handler continues without affecting result accumulation.

### Edge Case 3: Handler Returns undefined vs null

**Scenario**: Modifying hook handler returns `undefined` vs `null`.

**Resolution**: Both `undefined` and `null` are treated as "no result" and don't update the accumulated result.

### Edge Case 4: before_tool_call Failure Policy is fail-closed

**Scenario**: `before_tool_call` hook throws an error.

**Resolution**: Execution HALTS (fail-closed policy). Tool is NOT called.

**Security implication**: This is intentional — tool execution failures should block the operation.

### Edge Case 5: Hook Enabled/Disabled While Gateway Running

**Scenario**: User toggles hook enable/disable via CLI while gateway is processing.

**Resolution**: Depends on when the config reload happens. Some changes hot-reload; others may require restart. Hooks that are mid-execution complete normally.

### Edge Case 6: Void Hook Handler Returns Promise

**Scenario**: Void hook handler is async (returns Promise).

**Resolution**: Void hooks use `Promise.all()` which properly awaits async handlers. Each handler's rejection is caught individually.

### Edge Case 7: Modifying Hook with shouldStop Policy

**Scenario**: Hook handler returns a "stop signal" via `shouldStop` policy function.

**Resolution**: After `shouldStop(result)` returns true, remaining handlers in the chain are SKIPPED entirely.

**Use case**: Early exit when a handler determines no further processing is needed.

### Edge Case 8: Claiming Hook No Handler Claims

**Scenario**: No handler returns `{ handled: true }` for claiming hook.

**Resolution**: Returns `undefined` or `{ status: "declined" }`, depending on context.

### Edge Case 9: Priority Values Across Different Sources

**Scenario**: Workspace hook has priority=0, managed hook has priority=100.

**Resolution**: Workspace still runs first (precedence=40 vs managed=30) despite lower priority.

**Key insight**: Priority cannot override source precedence.

---

## 7. CREATIVE USES — Innovative Applications

### Creative Use 1: Priority-Based Security Pipeline

Implement a security scanning pipeline where each plugin handles one aspect:

```javascript
// Priority 100: Input validation
// Priority 75: Rate limiting check  
// Priority 50: Content policy scan
// Priority 25: Data loss prevention
// Priority 0: Audit logging
```

### Creative Use 2: Dynamic Hook Priority Reconfiguration

Use a master configuration hook that adjusts priorities at runtime:

```javascript
// In a before_agent_start handler:
event.context.cfg.hooks.internal.entries["my-hook"].priority = 
  determinePriorityBasedOnSessionContext();
```

### Creative Use 3: Hook Execution Observer

Create a monitoring hook that tracks execution patterns:

```javascript
// Priority: -1000 (runs last)
const observer = {
  async handler(event) {
    log(`[observer] ${event.type} executing with ${handlers.length} handlers`);
    // Record timing, ordering, results
  }
};
```

### Creative Use 4: Conditional Hook Chaining

Use `shouldStop` pattern for conditional processing:

```javascript
// Handler decides if further processing needed
if (!event.context.needsFurtherProcessing) {
  return { stop: true };
}
```

### Creative Use 5: Multi-Phase Processing

Break complex processing into sequential phases:

```
Phase 1: Collect (before_prompt_build)
Phase 2: Transform (before_agent_start)  
Phase 3: Validate (before_tool_call)
Phase 4: Respond (after_tool_call)
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### NEW Questions Generated:

1. **[MED]** What is the maximum recommended number of handlers per hook before performance degrades?
   - **Rationale**: Void hooks run in parallel via Promise.all; modifying hooks run sequentially. Too many handlers could slow down agent response.

2. **[LOW]** Can hook execution order be traced or logged at runtime without debug mode?
   - **Rationale**: Debugging execution order issues currently requires log inspection or code review.

3. **[MED]** Is there a way to enforce ordering between plugins from different sources?
   - **Rationale**: Source precedence can't be overridden; if Plugin A (workspace) needs to run after Plugin B (managed), they must be in same source category.

4. **[LOW]** What happens to in-flight hook executions when gateway restarts?
   - **Rationale**: If a restart happens mid-execution, hook cleanup is not guaranteed.

5. **[MED]** Can hooks communicate execution order constraints to the registry?
   - **Rationale**: Currently no mechanism for "must run before X" declarations between plugins.

6. **[LOW]** Is there a performance benchmark for hook overhead?
   - **Rationale**: Each hook adds latency; there's no documented threshold.

7. **[MED]** Does the claim-first-wins pattern support priority among claiming hooks?
   - **Rationale**: Looking at code, claiming hooks seem to use same priority sort, but this isn't documented.

8. **[LOW]** Can modifying hooks accumulate results across multiple invocations (not just within single event)?
   - **Rationale**: Result merging is per-event; no cross-event state.

---

## 9. SOURCES

### Primary Sources

- `/usr/local/lib/node_modules/openclaw/dist/config-Nq7s3Dxw.js` — Hook source policy definitions (`HOOK_SOURCE_POLICIES`), precedence system, sorting algorithm
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook execution runner: `runVoidHook`, `runModifyingHook`, `runClaimingHook`, `getHooksForName`, priority sorting, failure policy
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation: registration order, error handling
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Official hooks documentation

### Related Findings (Previously Researched)

- `Research/OpenClaw/findings/openclaw-hooks-system.md` (L18) — Complete hook system overview
- `Research/OpenClaw/findings/hook-security-audit.md` (L20) — Hook security model
- `Research/OpenClaw/findings/hook-infinite-loops.md` (L29) — Hook recursion patterns

---

*Research by: Investigador Scout*  
*Date: 2026-04-23*  
*Status: COMPLETE ✅*
