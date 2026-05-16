# Hook Exception Handler Behavior — L41

**Research:** What happens if a hook handler throws an uncaught exception — does it crash the gateway?

**Status:** ✅ RESOLVED — 2026-04-23 12:40 CET

---

## Summary

**Plugin hooks:** Errors are caught individually per-handler. Default policy is **fail-open** (log + continue) for most hooks. `before_tool_call` is **fail-closed** (throws + halts). Gateway does NOT crash from hook handler errors under default fail-open policy.

**Internal hooks:** Each handler is individually wrapped in try/catch. Errors are logged but don't prevent other handlers from running.

---

## Detailed Findings

### Plugin Hook Exception Handling

From `hook-runner-global-D9t7KsGJ.js`:

```javascript
const catchErrors = options.catchErrors ?? true;  // Default: true
const failurePolicyByHook = options.failurePolicyByHook ?? {};
const shouldCatchHookErrors = (hookName) => 
  catchErrors && (failurePolicyByHook[hookName] ?? "fail-open") === "fail-open";
```

**Key mechanism:** Each handler is individually wrapped in try/catch:

```javascript
// runVoidHook (parallel fire-and-forget)
const promises = hooks.map(async (hook) => {
  try {
    await hook.handler(event, ctx);
  } catch (err) {
    handleHookError({ hookName, pluginId: hook.pluginId, error: err });
  }
});
await Promise.all(promises);  // Continues even if some handlers fail

// runModifyingHook (sequential, merged)
for (const hook of hooks) try {
  const handlerResult = await hook.handler(event, ctx);
  // ... merge result
} catch (err) {
  handleHookError({ hookName, pluginId: hook.pluginId, error: err });
  // Continues to next handler — does NOT halt
}
```

### Failure Policies

| Policy | Behavior | Used By |
|--------|----------|---------|
| `fail-open` (default) | Error logged, execution continues | All hooks except `before_tool_call` |
| `fail-closed` | Error thrown, execution halts | `before_tool_call` only |

**Initialization from `initializeGlobalHookRunner`:**
```javascript
state.hookRunner = createHookRunner(registry, {
  catchErrors: true,
  failurePolicyByHook: { before_tool_call: "fail-closed" }
});
```

### handleHookError Implementation

```javascript
const handleHookError = (params) => {
  const msg = `[hooks] ${params.hookName} handler from ${params.pluginId} failed: ${String(params.error)}`;
  if (shouldCatchHookErrors(params.hookName)) {
    logger?.error(msg);  // Log and continue
    return;
  }
  throw new Error(msg, { cause: params.error });  // Only throws for fail-closed
};
```

### Special Cases

#### Synchronous Hooks (tool_result_persist, before_message_write)

These hooks are **intentionally synchronous** and run on hot paths. They have special handling:

```javascript
// tool_result_persist — synchronous only
function runToolResultPersist(event, ctx) {
  for (const hook of hooks) try {
    const out = runSyncHookHandler(hook, { ...event, message: current }, ctx);
    if (isPromiseLike(out)) {
      // Warning: promise returned but hook is synchronous
      if (shouldCatchHookErrors("tool_result_persist")) {
        logger?.warn?.(msg);
        continue;  // Continue execution
      }
      throw new Error(msg);
    }
    // ... continue
  } catch (err) {
    const msg = `[hooks] tool_result_persist handler from ${hook.pluginId} failed: ${String(err)}`;
    if (shouldCatchHookErrors("tool_result_persist")) logger?.error(msg);
    else throw new Error(msg, { cause: err });  // fail-closed throws
  }
}
```

#### before_tool_call — fail-closed

This is the **only hook with fail-closed policy** by default:

```javascript
return runModifyingHook("before_tool_call", event, ctx, {
  // ... merge results
  shouldStop: (result) => result.block === true,
  terminalLabel: "block=true"
});
// If any handler throws, the error propagates up and halts the tool call chain
```

### Internal Hook Exception Handling

From `internal-hooks-2legcEEL.js`:

```javascript
for (const handler of allHandlers) try {
  await handler(event);
} catch (err) {
  const message = formatErrorMessage(err);
  log.error(`Hook error [${event.type}:${event.action}]: ${message}`);
  // Does NOT re-throw — other handlers continue
}
```

**Key difference from plugin hooks:** Internal hooks use a single try/catch around each handler, but the entire hook system continues even if a handler fails. Errors are logged but execution proceeds.

---

## Gateway Crash Scenarios

### When Gateway WOULD crash from hook errors

1. **`before_tool_call` fail-closed + handler throws** — If a plugin hook handler throws during `before_tool_call`, the error propagates up. However, this is **caught at a higher level** and typically results in tool call rejection, not gateway crash.

2. **Synchronous hooks (tool_result_persist, before_message_write) + fail-closed** — If `shouldCatchHookErrors` returns false for these synchronous hooks (which would only happen if explicitly configured), they throw and halt.

3. **Unrecoverable error in hook initialization** — If `initializeGlobalHookRunner` itself throws during gateway startup, the gateway fails to start (not a runtime crash).

### When Gateway Does NOT crash

1. **Any fail-open hook throwing** — Error is logged, execution continues
2. **Internal hook handler throwing** — Error is logged, other handlers continue
3. **Multiple handlers failing in runVoidHook** — All failures logged, Promise.all continues
4. **Modifying hook handler throwing** — Error logged, next handler runs

---

## Implications for Hook Developers

### Fail-Open Behavior (Most Hooks)

```typescript
// This will NOT crash the gateway — error is caught and logged
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    throw new Error("Something went wrong!");  // Caught, logged, continues
  }
});
```

### Fail-Closed Behavior (before_tool_call)

```typescript
// If this throws, the error propagates and blocks the tool call
api.registerHook({
  events: ["before_tool_call"],
  handler: async (event) => {
    throw new Error("Blocking this tool call!");  // Propagates up
  }
});
```

### Best Practice: Always Wrap in Try/Catch

Even though errors are caught by the hook runner, best practice is to handle errors inside your hook:

```typescript
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    try {
      // Risky operation
      await riskyOperation();
    } catch (err) {
      // Handle gracefully — prevents fail-open logging
      console.error("Hook error:", err);
      return;  // Or return a safe default
    }
  }
});
```

---

## Security Implications

1. **Fail-open means a malicious hook can fail silently** — Errors are logged but don't stop execution
2. **No audit trail of which hook failed** — Only error message logged, no structured event
3. **`before_tool_call` fail-closed provides stronger guarantees** — But still only as strong as the handler implementation
4. **Internal hook errors don't halt other internal hooks** — Each handler is independent

---

## Edge Cases

| Edge Case | Behavior |
|-----------|----------|
| Multiple handlers in runVoidHook all throw | All errors logged, all handlers complete, Promise.all resolves normally |
| Handler throws in runModifyingHook | Error logged, next handler runs, final result may be partial/undefined |
| Handler throws in runClaimingHook | Error logged, next handler tries, first `handled: true` wins |
| Synchronous hook returns Promise | Warning logged, Promise ignored, execution continues |
| Gateway restart during hook execution | In-flight hooks are interrupted, no cleanup guarantee |
| Circular hook triggers | Not handled by exception system — see L29 for infinite loop risk |

---

## New Research Questions Generated

1. **Can the failure policy be changed per-hook at runtime?** — Currently hardcoded at initialization
2. **Is there a way to configure custom failure policies for other hooks?** — Only `before_tool_call` has custom policy
3. **What happens when before_tool_call throws but the tool call was already approved?** — Error propagation vs approval state
4. **Can a hook handler detect if it's running in fail-open or fail-closed mode?** — No API exposed

---

## Sources

- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Plugin hook runner: exception handling, failure policies, `shouldCatchHookErrors`, `handleHookError`, `runVoidHook`, `runModifyingHook`, `runClaimingHook`
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hook trigger: `triggerInternalHook` with per-handler try/catch
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation

---

**Finding ID:** L41
**Completed:** 2026-04-23 12:40 CET
**Researcher:** Investigador Scout