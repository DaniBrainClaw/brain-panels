# Extension to Extension Communication

## What is it?

Extension-to-Extension (E2E) Communication is the mechanism by which multiple OpenClaw extensions can coordinate, share data, and react to shared events through a common EventBus. Since all extensions loaded in the same session share the same EventBus instance, one extension can subscribe to events fired by another extension, enabling indirect communication patterns.

## How it works

### Core Architecture: Shared EventBus

```
ExtensionRunner
  ├── createEventBus() → EventBus instance
  ├── extensions: Extension[]
  │     └── each Extension
  │           └── handlers: Map<string, HandlerFn[]>
  └── emit(event) → chains handlers sequentially
```

All extensions in a session share ONE EventBus instance created in `loader.js` line 287:

```js
const resolvedEventBus = eventBus ?? createEventBus();
```

When `loadExtensions()` is called, the same `eventBus` is passed to each extension's `createExtensionAPI()`, where it's stored as `pi.events`.

### Event Emission Pattern

Every `emit*` method in `ExtensionRunner` follows the same pattern:

```js
async emit(event) {
    const ctx = this.createContext();
    for (const ext of this.extensions) {
        const handlers = ext.handlers.get(event.type);
        if (!handlers || handlers.length === 0) continue;
        for (const handler of handlers) {
            try {
                const handlerResult = await handler(event, ctx);
                if (handlerResult !== undefined) {
                    event.payload = handlerResult; // chain the result
                }
            } catch (err) {
                this.emitError({ extensionPath: ext.path, event: event.type, error: err.message, stack: err.stack });
            }
        }
    }
    return event;
}
```

**Key behavior:** If a handler returns a non-`undefined` value, it becomes the event payload for subsequent handlers (chained transformation). If handler returns `undefined`, payload passes through unchanged.

### Available Events

The `ExtensionAPI.events` (EventBus) supports 20+ event types:

| Event | Handler Signature | Purpose |
|-------|-----------------|---------|
| `session_start` | `(event) => void` | New session initialized |
| `session_before_switch` | `(event, ctx) => SessionBeforeSwitchResult` | About to switch session |
| `session_before_fork` | `(event, ctx) => SessionBeforeForkResult` | About to fork session |
| `session_before_compact` | `(event, ctx) => SessionBeforeCompactResult` | Before auto-compaction |
| `session_compact` | `(event) => void` | Compaction triggered |
| `session_shutdown` | `(event) => void` | Session ending |
| `before_agent_start` | `(event, ctx) => BeforeAgentStartResult` | Before agent starts |
| `agent_start` | `(event) => void` | Agent started |
| `agent_end` | `(event) => void` | Agent finished |
| `turn_start` | `(event) => void` | New turn started |
| `turn_end` | `(event) => void` | Turn completed |
| `message_start` | `(event) => void` | Message incoming |
| `message_update` | `(event) => void` | Message edited |
| `message_end` | `(event) => void` | Message finalized |
| `tool_execution_start` | `(event) => void` | Tool about to execute |
| `tool_execution_update` | `(event) => void` | Tool progress update |
| `tool_execution_end` | `(event) => void` | Tool completed |
| `tool_call` | `(event, ctx) => ToolCallEventResult` | LLM called a tool |
| `tool_result` | `(event, ctx) => ToolResultEventResult` | Tool returned result |
| `model_select` | `(event) => void` | Model being selected |
| `before_model_resolve` | `(event, ctx) => BeforeModelResolveResult` | Before model is resolved |
| `before_provider_request` | `(event, ctx) => BeforeProviderRequestEventResult` | Before API call to provider |
| `before_prompt_build` | `(event, ctx) => BeforePromptBuildResult` | Before prompt construction |
| `context` | `(event, ctx) => ContextEventResult` | Context message added |
| `resources_discover` | `(event) => void` | Resource discovery requested |
| `user_bash` | `(event, ctx) => UserBashEventResult` | User ran bash command |
| `input` | `(event, ctx) => InputEventResult` | User input received |

### ExtensionRunner.emit* Methods

Each major event has a dedicated `emit*` method in ExtensionRunner:

```js
emitSessionShutdownEvent(extensionRunner)    // Line 47-50 — special exported helper
emit(event)                                  // Generic base emit (line 396)
emitToolResult(event)                        // Line 427
emitToolCall(event)                          // Line 474
emitUserBash(event)                          // Line 493
emitContext(messages)                        // Line 520
emitBeforeProviderRequest(payload)           // Line 549 — returns transformed payload
emitBeforeAgentStart(prompt, images, systemPrompt) // Line 581
emitResourcesDiscover(cwd, reason)          // Line 630
emitInput(text, images, source)              // Line 669
```

### Context Object

All handlers receive a shared `ctx` (ExtensionContext) with:
- `session` — current AgentSession
- `model` — active model
- `cfg` — gateway config (contains secrets!)
- `agentDir` — agent directory path
- `runtime` — ExtensionRuntime with session-state methods

## Uses

1. **Inter-extension coordination** — Extension A fires a custom event, Extension B reacts
2. **Chained transformation** — Multiple extensions each transform a payload sequentially
3. **Session state sharing** — Extensions read/write via shared `runtime.appendEntry()` to session store
4. **Tool result interception** — Extension A registers tool, Extension B intercepts result via `tool_result`
5. **Provider request middleware** — Multiple extensions each transform API request payload
6. **Session lifecycle hooks** — Clean up resources when session ends via `session_shutdown`

## Problems

1. **No priority ordering** — Handler execution order is insertion order (Map iteration), no way to control priority
2. **Silent error swallowing** — Errors in one handler don't stop others, but also no rollback
3. **No dead-letter queue** — Failed events are logged via `emitError()` but no retry mechanism
4. **No pub/sub acknowledgment** — Publishing extensions have no way to know if any handler processed the event
5. **Shared EventBus across all extensions** — One misbehaving extension could flood the event bus
6. **Session-scoped only** — Events don't persist across sessions; new session = fresh EventBus

## Solutions

1. **Priority via naming convention** — Prefix handlers with priority numbers (e.g., `01_myHandler`)
2. **Error isolation** — Each handler wrapped in try/catch individually; failures don't cascade
3. **Idempotent handlers** — Design handlers to handle duplicate/missing events gracefully
4. **Extension ordering at load time** — Control which extension loads first to determine handler order
5. **State persistence via appendEntry** — Use `runtime.appendEntry()` for cross-handler data sharing

## Edge Cases

1. **Handler throws synchronous exception** — Caught by try/catch, logged via `emitError()`, event continues to next handler
2. **Handler returns `undefined`** — Payload passes through unchanged (not replaced)
3. **No handlers for event** — `emit()` returns event unchanged; `hasHandlers()` returns false
4. **Same handler registered twice** — Both instances are called (no deduplication)
5. **Extension loaded twice** — Both instances share same EventBus; both handlers called
6. **`session_shutdown` handler throws** — Exception caught, logged, shutdown continues
7. **`before_provider_request` returns wrong type** — TypeScript types don't enforce at runtime; downstream provider may receive unexpected payload

## Creative Uses

1. **Distributed tracing** — Each extension appends span info via `appendEntry()`, collected at session end
2. **Event-driven middleware chain** — Build a middleware pipeline where each extension inspects/modifies a payload
3. **Extension dependency injection** — Use `resources_discover` to announce capabilities other extensions consume
4. **Cross-cutting logging** — Multiple extensions attach to `tool_result`/`turn_end` with different loggers
5. **Dynamic feature flags** — One extension sets flags via runtime, another reads them in handler
6. **Chaos engineering** — Test extension that randomly delays or drops events to test error handling

## Sources

- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/loader.js` — createEventBus instantiation (line 287), shared eventBus across extensions
- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/runner.js` — ExtensionRunner.emit* methods (lines 44-50, 396-427, 427-456, 474-493, 493-509, 520-538, 549-580, 581-613, 630-657, 669-686)
- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/types.d.ts` — Event types and ExtensionContext (lines 702-728, 852)
- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/event-bus.js` — EventBus implementation (source from index.js.map export)