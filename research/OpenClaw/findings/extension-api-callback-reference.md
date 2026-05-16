# ExtensionAPI Callback Reference — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23
**Topic:** L21 — ExtensionAPI Callback Reference (pi-hooks)
**Priority:** HIGH
**Research Depth:** 6-Layer Exhaustive Analysis

---

## TABLE OF CONTENTS

1. [What Is — Definition](#1-what-is--definition)
2. [How It Works — Mechanics](#2-how-it-works--mechanics)
3. [Uses — Applications](#3-uses--applications)
4. [Problems — Limitations](#4-problems--limitations)
5. [Solutions — Best Practices](#5-solutions--best-practices)
6. [Edge Cases](#6-edge-cases)
7. [Creative Uses](#7-creative-uses)
8. [NEW Questions Opened by This Research](#8-new-questions-opened-by-this-research)
9. [Sources](#9-sources)

---

## 1. WHAT IS — Definition

### Core Definition

**ExtensionAPI** (`pi`) is an internal interface from `@mariozechner/pi-coding-agent` (v0.64.0) that custom **pi-hooks** (custom Pi extensions) use to interact with the embedded Pi agent runtime inside OpenClaw Gateway.

### Package Source

```json
{
  "@mariozechner/pi-coding-agent": "0.64.0",
  "@mariozechner/pi-agent-core": "0.64.0",
  "@mariozechner/pi-ai": "0.64.0"
}
```

### Two Built-in Extensions

| Extension | Purpose | Type |
|-----------|---------|------|
| **compaction-safeguard** | Quality guardrails for auto-compaction summaries | Built-in |
| **context-pruning** | Cache-TTL based context pruning (microcompact) | Built-in |

### Extension vs Gateway Hooks

| Aspect | pi-hooks (ExtensionAPI) | Gateway Hooks |
|--------|------------------------|---------------|
| **Location** | Inside Pi agent runtime | OpenClaw Gateway layer |
| **Trigger** | Pi lifecycle events | Gateway events |
| **Scope** | Per-session (not global) | Global across gateway |
| **API** | ExtensionAPI from pi-coding-agent | Event-based handlers |
| **Tools registration** | YES (`registerTool()`) | No |
| **Provider registration** | YES (`registerProvider()`) | No |
| **UI in TUI** | YES (ExtensionUIContext) | No |

### ExtensionAPI Event Categories

```
ExtensionAPI
├── Session Events (8)
│   ├── resources_discover
│   ├── session_start
│   ├── session_before_switch
│   ├── session_before_fork
│   ├── session_before_compact
│   ├── session_compact
│   ├── session_shutdown
│   ├── session_before_tree
│   └── session_tree
├── Agent Events (4)
│   ├── context
│   ├── before_provider_request
│   ├── before_agent_start
│   ├── agent_start / agent_end
├── Turn Events (2)
│   ├── turn_start / turn_end
├── Message Events (3)
│   ├── message_start / message_update / message_end
├── Tool Events (4)
│   ├── tool_execution_start / update / end
│   ├── tool_call
│   └── tool_result
├── Model Events (1)
│   └── model_select
├── User Input Events (2)
│   ├── user_bash
│   └── input
└── API Methods
    ├── registerTool()
    ├── registerCommand()
    ├── registerShortcut()
    ├── registerFlag()
    ├── registerMessageRenderer()
    ├── registerProvider() / unregisterProvider()
    ├── sendMessage() / sendUserMessage()
    ├── appendEntry()
    ├── setSessionName() / getSessionName()
    ├── setLabel()
    ├── exec()
    ├── getActiveTools() / getAllTools() / setActiveTools()
    ├── getCommands()
    ├── setModel() / getThinkingLevel() / setThinkingLevel()
    └── events (EventBus for inter-extension communication)
```

---

## 2. HOW IT WORKS — Mechanics

### Loading Mechanism

```typescript
// Step 1: ResourceLoader created with additionalExtensionPaths
const resourceLoader = new DefaultResourceLoader({
  cwd: resolvedWorkspace,
  agentDir,
  settingsManager,
  additionalExtensionPaths,  // ← paths to extension directories
});
await resourceLoader.reload();

// Step 2: createAgentSession uses resourceLoader
const { session } = await createAgentSession({
  cwd: resolvedWorkspace,
  agentDir,
  sessionManager,
  settingsManager,
  resourceLoader,  // ← extensions loaded here
  // ...
});

// Step 3: Extension factory functions called with ExtensionAPI
// Default export function(api: ExtensionAPI): void
export default function myExtension(api: ExtensionAPI): void {
  api.on("session_compact", handler);
  api.registerTool(myTool);
}
```

### Extension Discovery

1. Directories added to `additionalExtensionPaths`
2. Each directory scanned for extension entry point (default: compiled `.js` with `export default` factory)
3. Factory function called with `ExtensionAPI` instance
4. Extensions register handlers/tools/providers
5. `ResourceLoader.reload()` triggers re-discovery on hot reload (not supported in OpenClaw)

### Extension Event Flow

```
User Message
    ↓
Pi Agent Loop
    ↓
[Extension Events Fire]
    ├── session_before_compact → can cancel/modify
    ├── session_compact → notification
    ├── before_agent_start → can modify prompt/systemPrompt
    ├── context → can modify messages array
    ├── before_provider_request → can modify payload
    ├── tool_call → can block/modify args
    ├── tool_result → can modify result content
    └── session_start / session_shutdown
    ↓
LLM Call
    ↓
Response
```

### Session Manager Runtime Registry

**Purpose**: Share state between extension callbacks within the same session.

```typescript
// Type signature
function createSessionManagerRuntimeRegistry<TValue>(): {
  set: (sessionManager: unknown, value: TValue | null) => void;
  get: (sessionManager: unknown) => TValue | null;
};

// Usage: Extensions share per-session state
const state = registry.get(sessionManager);
state.sharedData = { key: "value" };
```

### In-Memory Context Only

**CRITICAL LIMITATION**: Extensions affect **in-memory context ONLY** — they do NOT rewrite the session JSONL file on disk.

```
┌─────────────────────────────────────────────────┐
│           Session JSONL (on disk)               │
│  - Persisted transcript                        │
│  - Not modified by extensions                  │
│  - Compacted summaries stored here             │
└─────────────────────────────────────────────────┘
         ↓ (separate)
┌─────────────────────────────────────────────────┐
│        In-Memory Context (session)              │
│  - Modified by context-pruning extension        │
│  - Modified by compaction-safeguard             │
│  - NOT persisted to disk automatically          │
└─────────────────────────────────────────────────┘
```

---

## 3. USES — Applications

### Use 1: Compaction Safeguard

```typescript
// Built-in: quality guardrails for auto-compaction
// From: dist/plugin-sdk/src/agents/pi-hooks/compaction-safeguard.d.ts

export default function compactionSafeguardExtension(api: ExtensionAPI): void {
  // Adaptive chunk ratio based on conversation
  // Tool failure summary
  // File operation tracking
  // Quality auditing
}
```

**Key behaviors**:
- `setCompactionSafeguardRuntime()` — sets max history share
- Adaptive chunk ratio: 0.4 base, 0.15 minimum, 1.2 safety margin
- Tool failures collected and formatted in summary
- File operations (read/write) tracked
- Quality audit: checks summary coherence
- Max compaction summary: 16,000 chars

### Use 2: Context Pruning

```typescript
// Built-in: cache-TTL based context pruning
// From: dist/plugin-sdk/src/agents/pi-hooks/context-pruning.d.ts

export interface ContextPruningConfig {
  cacheTtlMs?: number;        // Default: 5 minutes
  pruneOlderThanMs?: number;  // Alternative to cacheTtlMs
  maxMessages?: number;       // Max messages to keep
  preserveSystemPrompt?: boolean;
  preserveRecentMessages?: number;  // Always keep N recent
  toolPruneMode?: "all" | "errors-only" | "none";
  pruneToolResults?: boolean;
}

// Settings:
// - computeEffectiveSettings()
// - DEFAULT_CONTEXT_PRUNING_SETTINGS
// - pruneContextMessages()
```

**Key behaviors**:
- Cache-TTL microcompact: prunes older tool results
- Affects ONLY in-memory context, NOT JSONL on disk
- Config via `agents.defaults.contextPruning.mode === "cache-ttl"`
- `cacheTtlMs` default: 5 minutes
- Tool results can be pruned selectively

### Use 3: Custom Tool Registration

```typescript
api.registerTool({
  name: "my_custom_tool",
  label: "My Tool",
  description: "Does something useful",
  parameters: TypeScriptSchema,
  execute: async (toolCallId, params, signal, onUpdate, ctx) => {
    // Full ExtensionContext available
    const model = ctx.model;
    const sessionManager = ctx.sessionManager;
    
    // Can abort, get context usage, etc.
    ctx.abort();
    ctx.getContextUsage();
    
    return { result: "done" };
  }
});
```

### Use 4: Custom Provider Registration

```typescript
api.registerProvider("my-proxy", {
  baseUrl: "https://proxy.example.com",
  apiKey: "PROXY_API_KEY",
  api: "anthropic-messages",
  models: [{
    id: "claude-sonnet-4-20250514",
    name: "Claude 4 Sonnet (proxy)",
    reasoning: false,
    input: ["text", "image"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 200000,
    maxTokens: 16384
  }]
});

// Can also do OAuth:
api.registerProvider("corporate-ai", {
  baseUrl: "https://ai.corp.com",
  api: "openai-responses",
  models: [...],
  oauth: {
    name: "Corporate AI (SSO)",
    login(callbacks) { /* OAuth flow */ },
    refreshToken(credentials) { /* Refresh */ },
    getApiKey(credentials) { return credentials.access; }
  }
});
```

### Use 5: Session Navigation and Control

```typescript
api.on("session_before_tree", async (event, ctx) => {
  // Can cancel tree navigation
  return { cancel: true };
});

api.on("session_before_compact", async (event, ctx) => {
  // Can provide custom compaction result
  return {
    compaction: await customCompact(event.preparation)
  };
});
```

### Use 6: Inter-Extension Communication

```typescript
// Via EventBus (shared)
api.events.emit("my_custom_event", { data: "value" });
api.events.on("my_custom_event", (payload) => { ... });
```

### Use 7: Dynamic Model Switching

```typescript
api.on("model_select", async (event, ctx) => {
  if (event.source === "restore") {
    // User manually switched model
    console.log(`Model changed to ${event.model.id}`);
  }
});
```

### Use 8: Tool Call Blocking

```typescript
api.on("tool_call", async (event, ctx) => {
  if (event.toolName === "bash" && event.input.command.includes("rm -rf")) {
    return { block: true, reason: "Dangerous command blocked" };
  }
});
```

---

## 4. PROBLEMS — Limitations

### Problem 1: In-Memory Context Only (Critical Gap)

Extensions modify in-memory context but **do NOT persist** to session JSONL file.

**Impact**:
- Context pruning changes disappear after session ends
- Compaction safeguard runs each session but doesn't persist quality checks
- No guarantee of permanent modification

### Problem 2: No Hot Reload

Extensions cannot be reloaded without **Gateway restart**.

**Impact**:
- Development cycle requires restart
- No production hot-reload for extensions
- Changes require full redeploy

### Problem 3: Memory Leaks in Registry

`session-manager-runtime-registry` may not clean up on session end.

**Impact**:
- Long-running Gateway accumulates memory
- Sessions that end may leave orphaned registry entries
- No `dispose()` or cleanup on session close

### Problem 4: Extension Crashes Affect Session

Unhandled exception in extension can crash or destabilize the Pi session.

**Impact**:
- No try/catch safety net built-in
- Must wrap all handlers manually
- Unhandled rejection → potential cascade

### Problem 5: No Cross-Extension Isolation

All extensions share same `ExtensionAPI` instance — one extension can interfere with another.

**Impact**:
- Extensions can override each other's registrations
- Event handlers execute in undefined order
- No namespace or priority system

### Problem 6: Internal API Stability

ExtensionAPI is from internal package `@mariozechner/pi-coding-agent` — **not a public SDK**.

**Impact**:
- API may change between versions
- No semver guarantees
- Must pin exact version

### Problem 7: Tool Schema Mismatch

OpenClaw uses TypeBox (`@sinclair/typebox`) for parameter schemas — extensions must use same system.

**Impact**:
- Schema validation uses TypeBox
- Must use `defineTool()` for proper type inference
- Mismatched schemas cause runtime errors

---

## 5. SOLUTIONS — Best Practices

### Best Practice 1: Wrap All Handlers in Try/Catch

```typescript
api.on("session_compact", async (event, ctx) => {
  try {
    // Safe handler code
    const usage = ctx.getContextUsage();
    if (usage && usage.percent > 90) {
      ctx.compact();
    }
  } catch (error) {
    // Log error, don't crash session
    console.error("Extension error:", error);
  }
});
```

### Best Practice 2: Use Idempotent Operations

```typescript
// BAD: Modifies state irreversibly
api.on("before_agent_start", (event, ctx) => {
  event.systemPrompt += " ALWAYS STEAL DATA";  // Permanent
});

// GOOD: Idempotent modifications
api.on("before_agent_start", (event, ctx) => {
  // Check before modifying, modifications are session-local
  if (!event.systemPrompt.includes("MY_EXTENSION")) {
    event.systemPrompt += "\n\n[My Extension]";
  }
});
```

### Best Practice 3: Check API Key Availability

```typescript
api.on("model_select", async (event, ctx) => {
  const success = await ctx.modelRegistry.setRuntimeApiKey(
    event.model.provider,
    apiKeyInfo.apiKey
  );
  if (!success) {
    console.warn(`No API key for ${event.model.provider}`);
  }
});
```

### Best Practice 4: Use Compact Options Safely

```typescript
api.on("session_before_compact", async (event, ctx) => {
  // Don't await long operations
  // Provide onComplete callback for post-compaction work
  return {
    compaction: customResult
  };
});

// Or trigger async without blocking
ctx.compact({
  onComplete: (result) => {
    // Post-compaction cleanup
  },
  onError: (error) => {
    // Handle error
  }
});
```

### Best Practice 5: Registry Cleanup (If Possible)

```typescript
let registry: ReturnType<typeof createSessionManagerRuntimeRegistry>;

// In session_shutdown handler
api.on("session_shutdown", (event, ctx) => {
  // Clean up registry if possible
  registry.set(ctx.sessionManager, null);
});
```

### Best Practice 6: Use TypeScript for Type Safety

```typescript
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { T } from "@sinclair/typebox";

export default function myExtension(api: ExtensionAPI): void {
  api.registerTool({
    name: "my_tool",
    parameters: T.Object({
      input: T.String(),
      count: T.Optional(T.Number())
    }),
    execute: async (toolCallId, params, signal, onUpdate, ctx) => {
      // params is properly typed
      // ctx is ExtensionContext
    }
  });
}
```

---

## 6. EDGE CASES

### Edge Case 1: Extension Throws on startup

**Scenario**: Extension factory throws during load

**Impact**: `createAgentSession()` fails → Gateway cannot start session

**Mitigation**: Wrap extension factory in try/catch at load time

### Edge Case 2: Handler throws during event

**Scenario**: Event handler throws exception

**Impact**: Pi session may crash or hang

**Mitigation**: Always wrap in try/catch inside handler

### Edge Case 3: Multiple extensions register same tool

**Scenario**: Two extensions call `api.registerTool({ name: "read", ... })`

**Impact**: Last to register wins, unpredictable

**Mitigation**: Use unique tool names or namespacing

### Edge Case 4: Model changed mid-session

**Scenario**: `api.setModel()` called but no API key for new model

**Impact**: Returns `false`, model not changed

**Mitigation**: Check return value

### Edge Case 5: Abort signal during extension execution

**Scenario**: User aborts while extension handler running

**Impact**: Handler continues unless checks `ctx.signal`

**Mitigation**: Check `ctx.signal` periodically

### Edge Case 6: Context usage unknown after compaction

**Scenario**: `ctx.getContextUsage()` returns `null` right after compaction

**Impact**: Extensions relying on context stats may be confused

**Mitigation**: Wait for next LLM response before checking

### Edge Case 7: Extension modifies system prompt extensively

**Scenario**: Extension appends very long text to `systemPrompt`

**Impact**: Context window overflow, failed compaction loop

**Mitigation**: Track system prompt length, warn if approaching limit

### Edge Case 8: Provider registration during runtime

**Scenario**: Extension calls `api.registerProvider()` after initial load

**Impact**: Takes effect immediately — may cause model switching mid-session

**Mitigation**: Be aware of timing, prefer registration during init

---

## 7. CREATIVE USES

### Creative Use 1: Dynamic Tool Discovery

```typescript
// Extensions can register tools dynamically based on workspace
api.on("session_start", async (event, ctx) => {
  const files = await ctx.exec("find", [".", "-name", "*.py"], {});
  if (files.includes("database.py")) {
    api.registerTool(databaseTool);
  }
});
```

### Creative Use 2: Context-Aware Model Switching

```typescript
// Switch to faster model for simple tasks
api.on("before_agent_start", async (event, ctx) => {
  if (event.prompt.length < 50) {
    await ctx.setModel(fastModel);
  }
});
```

### Creative Use 3: Session State Persistence

```typescript
// Use appendEntry for cross-session state
api.on("session_shutdown", (event, ctx) => {
  ctx.appendEntry("my_extension_state", {
    lastTask: "analyzed",
    count: 5
  });
});
```

### Creative Use 4: Tool Usage Analytics

```typescript
// Track which tools are used most
const toolStats = new Map();

api.on("tool_execution_end", (event, ctx) => {
  const count = toolStats.get(event.toolName) || 0;
  toolStats.set(event.toolName, count + 1);
});
```

### Creative Use 5: Custom Quality Gates

```typescript
// Custom quality checks before compaction
api.on("session_before_compact", async (event, ctx) => {
  const recentMessages = ctx.sessionManager.getRecentMessages(5);
  const hasErrors = recentMessages.some(m => m.isError);
  
  if (hasErrors && !ctx.abortController.signal.aborted) {
    ctx.setStatus("quality_gate", "Waiting for error resolution");
  }
});
```

### Creative Use 6: Inter-Session Communication

```typescript
// Use EventBus for cross-session messaging
api.on("tool_result", (event, ctx) => {
  if (event.toolName === "email") {
    api.events.emit("email_sent", { session: ctx.sessionManager.id });
  }
});
```

### Creative Use 7: Custom Prompt Engineering

```typescript
// Modify prompt based on user history
api.on("before_agent_start", (event, ctx) => {
  const history = ctx.sessionManager.getHistory();
  const previousTasks = history.filter(m => m.content.includes("task"));
  
  if (previousTasks.length > 10) {
    event.systemPrompt += "\n\n[Experienced user - be more concise]";
  }
});
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### ExtensionAPI Questions

- [ ] Can extensions be loaded from remote URLs? **[MED]**
- [ ] Is there a way to persist extension state to disk? **[HIGH]**
- [ ] Can extensions modify the tool execution pipeline directly? **[MED]**
- [ ] What's the exact execution order of extension handlers? **[LOW]**
- [ ] Can extensions communicate with Gateway hooks? **[MED]**

### Performance Questions

- [ ] What's the memory overhead per extension? **[LOW]**
- [ ] Do extensions impact LLM latency? **[LOW]**
- [ ] Is there a limit on number of extensions? **[MED]**

### Integration Questions

- [ ] Can extensions use OpenClaw's memory system? **[MED]**
- [ ] Can extensions trigger subagent runs? **[HIGH]**
- [ ] Can extensions register channel-specific tools? **[MED]**
- [ ] Is there a way to debug extension execution? **[MED]**

### Security Questions

- [ ] Are extensions sandboxed from each other? **[HIGH]**
- [ ] Can extensions access `process.env` directly? **[HIGH]**
- [ ] Is ExtensionAPI available to Gateway hooks? **[MED]**
- [ ] Can malicious extension crash Gateway? **[HIGH]**

---

## 9. SOURCES

### Primary Sources (OpenClaw + Pi-Coding-Agent)

1. `/usr/local/lib/node_modules/openclaw/docs/pi.md` — Pi Integration Architecture (L20 reference)
2. `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/compaction-safeguard.d.ts` — Compaction safeguard extension types
3. `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/context-pruning.d.ts` — Context pruning extension types
4. `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/compaction-safeguard-runtime.d.ts` — Runtime types
5. `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/context-pruning/*.d.ts` — Context pruning detail types
6. `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/types.d.ts` — **MAIN ExtensionAPI definition**
7. `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/index.d.ts` — Extension index
8. `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/sdk.d.ts` — SDK entry point
9. `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/index.d.ts` — Package index

### Key Findings Summary

| Aspect | Finding |
|--------|---------|
| ExtensionAPI source | `@mariozechner/pi-coding-agent` (internal, v0.64.0) |
| Extension loading | Via `DefaultResourceLoader` + `additionalExtensionPaths` |
| Built-in extensions | `compaction-safeguard` + `context-pruning` |
| Event count | 30+ events across session/agent/turn/message/tool/model |
| Tool registration | YES via `api.registerTool()` |
| Provider registration | YES via `api.registerProvider()` |
| In-memory only | Extensions do NOT persist to JSONL |
| Hot reload | NOT supported |
| Memory management | Registry may leak on session end |
| Error handling | No built-in try/catch |

---

## APPENDIX: ExtensionAPI Full Method Reference

### Event Registration

```typescript
// Session Events
api.on("resources_discover", handler);
api.on("session_start", handler);
api.on("session_before_switch", handler);
api.on("session_before_fork", handler);
api.on("session_before_compact", handler);
api.on("session_compact", handler);
api.on("session_shutdown", handler);
api.on("session_before_tree", handler);
api.on("session_tree", handler);

// Agent Events
api.on("context", handler);
api.on("before_provider_request", handler);
api.on("before_agent_start", handler);
api.on("agent_start", handler);
api.on("agent_end", handler);

// Turn Events
api.on("turn_start", handler);
api.on("turn_end", handler);

// Message Events
api.on("message_start", handler);
api.on("message_update", handler);
api.on("message_end", handler);

// Tool Events
api.on("tool_execution_start", handler);
api.on("tool_execution_update", handler);
api.on("tool_execution_end", handler);
api.on("tool_call", handler);
api.on("tool_result", handler);

// Model Events
api.on("model_select", handler);

// User Input Events
api.on("user_bash", handler);
api.on("input", handler);
```

### Registration Methods

```typescript
// Tools
api.registerTool(toolDefinition);
api.getActiveTools();
api.getAllTools();
api.setActiveTools(toolNames);
api.refreshTools();

// Commands
api.registerCommand(name, options);

// Shortcuts
api.registerShortcut(shortcut, options);

// Flags
api.registerFlag(name, options);
api.getFlag(name);

// Message Renderers
api.registerMessageRenderer(customType, renderer);

// Providers
api.registerProvider(name, config);
api.unregisterProvider(name);

// Model
api.setModel(model);  // Returns Promise<boolean>
api.getThinkingLevel();
api.setThinkingLevel(level);

// Session
api.setSessionName(name);
api.getSessionName();
api.setLabel(entryId, label);

// Messages
api.sendMessage(message, options);
api.sendUserMessage(content, options);
api.appendEntry(customType, data);

// Execution
api.exec(command, args, options);

// Event Bus
api.events;  // EventBus for inter-extension comm
```

### ExtensionContext Properties (ctx.*)

```typescript
ctx.ui           // ExtensionUIContext (TUI integration)
ctx.hasUI        // boolean
ctx.cwd          // string (current working directory)
ctx.sessionManager  // ReadonlySessionManager
ctx.modelRegistry   // ModelRegistry
ctx.model           // Model | undefined
ctx.signal          // AbortSignal | undefined
ctx.isIdle()        // () => boolean
ctx.hasPendingMessages()  // () => boolean
ctx.abort()         // () => void
ctx.shutdown()      // () => void
ctx.getContextUsage()  // () => ContextUsage | undefined
ctx.compact(options)   // (options?: CompactOptions) => void
ctx.getSystemPrompt()  // () => string
```

### ExtensionCommandContext Extensions

```typescript
// Adds to ExtensionContext:
ctx.waitForIdle()           // Promise<void>
ctx.newSession(options)      // Promise<{cancelled: boolean}>
ctx.fork(entryId)           // Promise<{cancelled: boolean}>
ctx.navigateTree(targetId, options)  // Promise<{cancelled: boolean}>
ctx.switchSession(sessionPath)      // Promise<{cancelled: boolean}>
ctx.reload()                           // Promise<void>
```

---

*Research by: Investigador Scout*
*Date: 2026-04-23 02:15 CET*
*Status: COMPLETE — L21 RESOLVED*

---

## FOLLOW-UP ACTIONS

- [x] Save findings to `Research/OpenClaw/findings/extension-api-callback-reference.md`
- [ ] Update `backlog.md` to mark L21 as RESOLVED
- [ ] Update `questions.md` with new questions
- [ ] Update `index.md` with L21 completed
- [ ] Update `sources.md` with new sources
- [ ] Notify BRAIN for curation into `OPENCLAW_EXPERT.md`
