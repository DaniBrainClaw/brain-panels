# Hook-to-Hook Communication — L27

**Research:** What's the recommended approach for hook-to-hook communication in OpenClaw?

**Status:** ✅ COMPLETADO — 2026-04-23 13:10 CET

---

## Exhaustive Research Order

Following the research protocol: What is → How works → Uses → Problems → Solutions → Edge cases → Creative uses

---

## 1. What is hook-to-hook communication?

Hook-to-hook communication refers to mechanisms where one hook can trigger, influence, or exchange data with another hook within the OpenClaw system. This enables:
- Coordinated behavior between multiple hooks from different plugins
- Data sharing across hook lifecycles
- Sequential processing chains where one hook's output feeds into another
- Event propagation patterns

---

## 2. How does hook-to-hook communication work?

### 2.1 Native Mechanisms

OpenClaw has **NO dedicated hook-to-hook communication API**. However, there are indirect mechanisms:

#### A. Sequential Modifying Hooks (Primary Pattern)

The most common hook-to-hook communication is via **sequential execution with result merging**:

```javascript
// From hook-runner-global-D9t7KsGJ.js
async function runModifyingHook(hookName, event, ctx, policy = {}) {
  let result;
  for (const hook of hooks) {
    const handlerResult = await hook.handler(event, ctx);
    if (policy.mergeResults) {
      result = policy.mergeResults(result, handlerResult, hook);
    }
  }
  return result;
}
```

**Key merge patterns:**
- `mergeBeforePromptBuild`: concatenates systemPrompt, prependContext, prependSystemContext, appendSystemContext
- `mergeBeforeModelResolve`: uses firstDefined to pick first non-undefined value
- `mergeSubagentSpawningResult`: combines status and threadBindingReady
- `mergeMessageSendingResult`: handles cancel (terminal) and message modifications

#### B. Terminal/Stop Conditions

Modifying hooks support `shouldStop` policy for early termination:

```javascript
// before_tool_call hook
shouldStop: (result) => result.block === true,
terminalLabel: "block=true"

// message_sending hook
shouldStop: (result) => result.cancel === true,
terminalLabel: "cancel=true"
```

When a handler returns `{ block: true }` or `{ cancel: true }`, lower-priority handlers are skipped.

#### C. Context Object Sharing

All hooks receive the same `ctx` object which CAN be mutated:

```javascript
// Hook handler signature
handler(event, ctx) // ctx is mutable
```

**However**, this is **NOT recommended** because:
- Void hooks run in parallel - no predictable execution order
- Different hooks may run in different executions (before_tool_call vs after_tool_call)
- No guarantee handlers will execute in a specific sequence

#### D. Session Store for Cross-Hook State

Hooks can use the session store to share state:

```javascript
// Within a hook handler
api.saveSessionStore(sessionKey, { 
  myHookData: "value",
  sharedState: { counter: 1 }
});
```

Other hooks can read this via `api.getSessionStore()`.

---

## 3. Uses — What can hook-to-hook communication achieve?

### 3.1 Data Chaining

One hook modifies data, next hook sees the modification:

- `before_prompt_build` hooks inject context that subsequent hooks see
- `message_sending` hooks can progressively transform outgoing messages

### 3.2 Blocking/Allow Patterns

One hook can block further processing:

- `before_tool_call` returning `{ block: true }` stops the tool execution
- `message_sending` returning `{ cancel: true }` aborts message send

### 3.3 Priority-Based Decision Making

Lower-priority hooks only see results if higher-priority didn't block:

```javascript
// mergeBeforeModelResolve uses firstDefined
const firstDefined = (prev, next) => prev ?? next;
```

### 3.4 Event Sequencing

The agent loop defines a natural hook chain:

```
message_received → before_dispatch → before_agent_reply → 
before_prompt_build → before_model_resolve → llm_input → 
[model call] → llm_output → before_tool_call → [tool execution] → 
after_tool_call → message_sending → message_sent → agent_end
```

---

## 4. Problems — What's broken or missing?

### 4.1 No Direct Inter-Hook Triggering

**PROBLEM:** There is NO API to explicitly trigger another hook from within a hook. You cannot do:

```javascript
// NOT POSSIBLE
function myHook(event, ctx) {
  ctx.triggerHook("another_hook", event, ctx); // No such API
}
```

### 4.2 Void Hooks Run in Parallel

**PROBLEM:** `runVoidHook` executes all handlers in parallel via `Promise.all`:

```javascript
const promises = hooks.map(async (hook) => {
  await hook.handler(event, ctx);
});
await Promise.all(promises);
```

This means:
- No predictable order
- Cannot chain void hooks sequentially
- Race conditions possible when sharing mutable state

### 4.3 No Pub/Sub or Event Bus Between Hooks

**PROBLEM:** Hooks cannot subscribe to other hook events. There's no:

- `ctx.on("hook:before_tool_call", handler)`
- `ctx.emit("hook:custom_event", data)`
- Event bus for inter-hook messaging

### 4.4 Context Mutation is Unreliable

**PROBLEM:** While you CAN mutate `ctx`, it's risky because:
- Execution order varies by hook type
- No atomicity guarantees
- Can conflict with other hooks

### 4.5 No Hook-to-Hook Error Propagation

**PROBLEM:** Errors in one hook don't automatically affect others (unless fail-closed policy):
- Hook errors are caught individually
- One hook failing doesn't prevent others

### 4.6 Session Store is Asynchronous and Per-Session

**PROBLEM:** Using session store for hook communication:
- Only works within same session
- Adds async overhead
- Requires sessionKey knowledge

---

## 5. Solutions — Recommended Patterns

### 5.1 Use Modifying Hooks with mergeResults

**RECOMMENDED:** When you need hook A → hook B communication, ensure:
- Both hooks register for the same event (e.g., `before_tool_call`)
- Use `runModifyingHook` semantics (sequential execution)
- Define clear mergeResults behavior

```javascript
// In hook definition
{
  hookName: "before_tool_call",
  priority: 100,
  handler: async (event, ctx) => {
    return { block: false, log: true };
  }
}
```

### 5.2 Use Terminal Conditions for Blocking

**RECOMMENDED:** To prevent lower-priority hooks from running:

```javascript
// High priority hook
return { block: true, blockReason: "security policy" };
// Lower priority hooks are skipped
```

### 5.3 Use Session Store for Cross-Hook State

**RECOMMENDED:** For state that must persist across different hook events:

```javascript
// Hook A
await api.saveSessionStore(sessionKey, { 
  authToken: encryptedToken 
});

// Hook B (different event)
const store = await api.getSessionStore(sessionKey);
const token = store.authToken;
```

### 5.4 Chain via Tool Execution

**WORKAROUND:** Use tool execution as a coordination mechanism:

- Hook A sets up state, calls a tool
- Tool execution triggers `before_tool_call` / `after_tool_call` hooks
- Hook B reads results from tool execution

### 5.5 Use Multiple Priority Levels

**RECOMMENDED:** Leverage priority for ordering:

```javascript
// Execution order: priority 100 → 50 → 0 → -50
const hookA = { hookName: "before_tool_call", priority: 100, ... };
const hookB = { hookName: "before_tool_call", priority: 50, ... };
```

### 5.6 Use before_install for Pre-Install Coordination

**FOR PLUGINS:** The `before_install` hook runs sequentially and can block installs:

```javascript
// Hook A
return { block: false, augment: { findings: [...] } };

// Hook B (lower priority) sees augment data
// Can access acc.augment from previous hooks
```

---

## 6. Edge Cases

### 6.1 Hooks with Same Priority

**EDGE CASE:** Two hooks with same priority registered for same event.

**BEHAVIOR:** Execution order is **insertion order** (order in which hooks were registered), which is not deterministic across restarts or plugin load order.

### 6.2 Mixed Hook Types

**EDGE CASE:** What if one hook is void, another is modifying, for same event?

**BEHAVIOR:** Hooks are typed by their event (not by handler). `message_sending` is modifying, `message_received` is void. They don't mix.

### 6.3 Cross-Plugin Hook Communication

**EDGE CASE:** Plugin A hook wants to communicate with Plugin B hook.

**SOLUTION:** Only possible if:
- Both register for same event
- Use session store
- Use shared tool execution chain

### 6.4 Hook Failure and State

**EDGE CASE:** What happens to shared state if a hook throws?

**BEHAVIOR:** Depends on failure policy:
- `fail-open` (default): error logged, other hooks continue
- `fail-closed` (before_tool_call): throws and halts

### 6.5 Sessionless Hooks

**EDGE CASE:** Some hooks run outside session context (e.g., gateway:startup).

**PROBLEM:** Cannot use session store for communication. Limited to context object mutation.

---

## 7. Creative Uses

### 7.1 Multi-Stage Validation Chain

```javascript
// Hook 1: priority 100 - Security check
return { valid: true, securityFindings: [...] };

// Hook 2: priority 50 - Compliance check
// Reads acc.securityFindings, adds complianceFindings

// Hook 3: priority 0 - Final decision
// Blocks if any findings present
return { block: findings.length > 0 };
```

### 7.2 Distributed Rate Limiting

```javascript
// Each hook increments counter in session store
const store = await api.getSessionStore(sessionKey);
const count = (store.rateLimitCount || 0) + 1;
await api.saveSessionStore(sessionKey, { rateLimitCount: count });

// Later hook checks threshold
return { block: count > 100 };
```

### 7.3 Plugin Dependency Resolution

```javascript
// before_install: priority 100
// Records plugin dependencies
return { dependencies: ["plugin-a", "plugin-b"] };

// after_install: priority 50
// Reads acc.dependencies, triggers installation of deps
```

### 7.4 Cross-Session Coordination

```javascript
// Use shared session store key
await api.saveSessionStore("SHARED_GLOBAL", { 
  globalState: "shared across sessions" 
});
```

### 7.5 Hook Pipeline Tracing

```javascript
// Each hook adds to trace
const trace = acc.trace || [];
trace.push({ plugin: myPluginId, stage: "before_tool_call" });
return { trace };
```

---

## Summary

| Aspect | Finding |
|--------|---------|
| **Native hook-to-hook API** | ❌ NONE |
| **Sequential execution** | ✅ Yes (modifying hooks only) |
| **Result merging** | ✅ Yes (via mergeResults) |
| **Terminal conditions** | ✅ Yes (block:true, cancel:true) |
| **Context mutation** | ⚠️ Risky (void hooks parallel) |
| **Session store** | ✅ Yes (cross-hook state) |
| **Event bus** | ❌ NONE |
| **Priority control** | ✅ Yes |

---

## NEW QUESTIONS GENERATED

1. **[MED]** Can hooks implement a custom event bus using session store?
2. **[MED]** What is performance impact of session store for inter-hook state?
3. **[LOW]** Can hooks register for "synthetic" events triggered by other hooks?
4. **[MED]** Is there a recommended pattern for plugin A to wait for plugin B's hook?
5. **[LOW]** Can hooks share state without session store via in-memory cache?

---

## Sources

- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook execution runner: `runVoidHook`, `runModifyingHook`, `runClaimingHook`, `mergeResults`, `shouldStop`, priority sorting
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation
- `/usr/local/lib/node_modules/openclaw/docs/plugins/building-plugins.md` — Plugin hook reference
- `/usr/local/lib/node_modules/openclaw/docs/plugins/sdk-overview.md` — SDK hook types and return values
- `/usr/local/lib/node_modules/openclaw/docs/concepts/agent-loop.md` — Agent loop hook chain
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation

---

*Research completed by: Investigador Scout — 2026-04-23 13:10 CET*