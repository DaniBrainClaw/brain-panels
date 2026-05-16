# Extension Tool Integration — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23
**Topic:** L23 — Extension Tool Integration
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

**Extension Tool Integration** is the system by which **pi-hooks** (custom Pi extensions) can register, manage, and intercept LLM-callable tools via the ExtensionAPI. Extensions can:

1. **Register new tools** that the LLM can call during agent execution
2. **Modify active tools** dynamically during a session
3. **Intercept tool calls** before execution (`tool_call` event)
4. **Intercept tool results** after execution (`tool_result` event)
5. **Control which tools are available** via active tool list

### Key Components

| Component | Type | Purpose |
|-----------|------|---------|
| `api.registerTool()` | Method | Register a new LLM-callable tool |
| `api.getActiveTools()` | Method | Get list of currently active tool names |
| `api.getAllTools()` | Method | Get all configured tools with schema and metadata |
| `api.setActiveTools()` | Method | Enable/disable tools by name dynamically |
| `tool_call` event | Event | Fire before tool execution (can block/modify) |
| `tool_result` event | Event | Fire after tool execution (can modify result) |

### Extension vs Built-in Tools

| Aspect | Built-in Tools | Extension-Registered Tools |
|--------|----------------|---------------------------|
| **Registration** | Hardcoded in Pi runtime | Dynamic via `registerTool()` |
| **Schema** | Fixed TypeBox | Dynamic TypeBox schema |
| **Lifecycle** | Always available | Can be added/removed at runtime |
| **Execution** | Internal to Pi | Custom handler in extension |
| **Sandboxing** | Follows sandbox policy | Runs in extension context |

---

## 2. HOW IT WORKS — Mechanics

### Tool Registration Flow

```typescript
// Extension factory receives ExtensionAPI
export default function myExtension(api: ExtensionAPI): void {
  // Step 1: Register a tool with TypeBox schema
  api.registerTool({
    name: "my_custom_tool",
    label: "My Custom Tool",
    description: "Does something useful based on input",
    parameters: T.Object({
      input: T.String(),
      count: T.Optional(T.Number())
    }),
    execute: async (
      toolCallId: string,
      params: { input: string; count?: number },
      signal: AbortSignal | undefined,
      onUpdate: AgentToolUpdateCallback | undefined,
      ctx: ExtensionContext
    ): Promise<AgentToolResult> => {
      // Custom tool execution logic
      return { result: `Processed: ${params.input}` };
    }
  });
}
```

### Tool Execution Pipeline

```
LLM decides to call tool
        │
        ▼
┌───────────────────┐
│ tool_call event   │ ◄─── Can block, modify args, or allow
│ (before exec)     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Tool execution    │ ◄─── Extension's execute() handler
│ (custom logic)    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ tool_result event│ ◄─── Can modify result content
│ (after exec)     │
└─────────┬─────────┘
          │
          ▼
    Result to LLM
```

### Active Tool Management

Extensions can dynamically control which tools the LLM sees:

```typescript
// Get currently active tool names
const activeTools = api.getActiveTools(); // ["read", "exec", "message"]

// Get ALL tools with metadata
const allTools = api.getAllTools();
// Returns: { name, description, parameters }[]

// Dynamically enable/disable tools
api.setActiveTools(["read", "my_custom_tool"]);
// Only read + my_custom_tool available to LLM
```

### Tool Call Interception

```typescript
// Intercept BEFORE tool execution
api.on("tool_call", async (event, ctx) => {
  if (event.toolName === "exec" && event.input.command.includes("rm -rf")) {
    return { block: true, reason: "Dangerous command blocked" };
  }
  // Or modify arguments:
  // return { args: { ...event.args, safe: true } };
  return { allow: true };
});

// Intercept AFTER tool execution
api.on("tool_result", async (event, ctx) => {
  // Modify result content
  if (event.toolName === "read" && event.result.error) {
    return { result: { content: "File read failed (sanitized)" } };
  }
  // Or just allow through
  return { allow: true };
});
```

### Tool Definition Interface

```typescript
interface ToolDefinition<TParams, TDetails, TState> {
  name: string;           // Tool name for LLM calls
  label: string;          // Human-readable label
  description: string;    // LLM-facing description
  promptSnippet?: string; // One-line snippet for system prompt
  promptGuidelines?: string[]; // Guidelines when tool is active
  parameters: TSchema;    // TypeBox parameter schema
  prepareArguments?: (args: unknown) => Static<TParams>;
  execute: (
    toolCallId: string,
    params: Static<TParams>,
    signal: AbortSignal | undefined,
    onUpdate: AgentToolUpdateCallback<TDetails> | undefined,
    ctx: ExtensionContext
  ) => Promise<AgentToolResult<TDetails>>;
  renderCall?: (args, theme, context) => Component;
  renderResult?: (result, options, theme, context) => Component;
}
```

---

## 3. USES — Applications

### Use 1: Custom API Integration

```typescript
// Register a tool that calls external APIs
api.registerTool({
  name: "weather",
  label: "Weather Lookup",
  description: "Get current weather for a location",
  parameters: T.Object({
    city: T.String(),
    units: T.Optional(T.Enum(["celsius", "fahrenheit"]))
  }),
  execute: async (toolCallId, params, signal, onUpdate, ctx) => {
    const response = await fetch(
      `https://api.weather.com/v3/wx?city=${params.city}&units=${params.units}`
    );
    return { result: await response.text() };
  }
});
```

### Use 2: Database Operations

```typescript
// Register database tools
api.registerTool({
  name: "db_query",
  label: "Database Query",
  description: "Execute a read-only database query",
  parameters: T.Object({
    query: T.String()
  }),
  execute: async (toolCallId, params, signal, onUpdate, ctx) => {
    // Validate query is SELECT only
    if (!params.query.trim().toUpperCase().startsWith("SELECT")) {
      return { result: { error: "Only SELECT queries allowed" } };
    }
    // Execute with connection from ctx
    const result = await ctx.sessionManager.db.query(params.query);
    return { result: JSON.stringify(result) };
  }
});
```

### Use 3: Tool Call Blocking/Security

```typescript
// Security: block dangerous tool calls
api.on("tool_call", async (event, ctx) => {
  const dangerous = [
    { tool: "exec", pattern: /rm\s+-[rf]/ },
    { tool: "write", pattern: /\/etc\/passwd/ },
    { tool: "edit", pattern: /\.ssh\/authorized_keys/ }
  ];

  for (const rule of dangerous) {
    if (event.toolName === rule.tool) {
      const args = JSON.stringify(event.args);
      if (rule.pattern.test(args)) {
        return { block: true, reason: `Blocked: ${rule.tool} with dangerous args` };
      }
    }
  }
  return { allow: true };
});
```

### Use 4: Result Sanitization

```typescript
// Sanitize sensitive data from results
api.on("tool_result", async (event, ctx) => {
  if (event.toolName === "exec" && event.result.content) {
    // Redact API keys in command output
    const sanitized = event.result.content.replace(
      /[a-zA-Z0-9]{20,}/g,
      "[REDACTED]"
    );
    return { result: { content: sanitized } };
  }
  return { allow: true };
});
```

### Use 5: Dynamic Tool Activation

```typescript
// Enable tools based on context
api.on("session_start", async (event, ctx) => {
  // Check workspace for specific files
  const files = await ctx.exec("ls", ["."], {});
  if (files.stdout.includes("database.py")) {
    api.setActiveTools([...api.getActiveTools(), "db_query"]);
  }
});
```

### Use 6: Tool Usage Analytics

```typescript
// Track tool usage
const toolStats = new Map();
api.on("tool_execution_end", (event, ctx) => {
  const count = toolStats.get(event.toolName) || 0;
  toolStats.set(event.toolName, count + 1);
  ctx.ui.setStatus("tool-stats", `Tools: ${count + 1}`);
});
```

---

## 4. PROBLEMS — Limitations

### Problem 1: No Sandbox Isolation (CRITICAL)

Extensions run **in-process** with the Gateway. A malicious extension can:
- Access all process memory
- Read/write any file on the system
- Make arbitrary network requests
- Access all credentials via `ctx.sessionManager`

**Impact**: Compromised extension = full system compromise

### Problem 2: No Tool Schema Validation After Mutation

> "Later `tool_call` handlers see earlier mutations. No re-validation is performed after mutation."

If a `tool_call` handler modifies arguments, there's no re-validation against the schema.

**Impact**: Malformed arguments could reach the tool handler

### Problem 3: Tool Name Collisions

If two extensions register tools with the same name, the last one wins — unpredictable behavior.

**Impact**: Unclear which tool the LLM will call

### Problem 4: No Type Safety at Runtime

The TypeBox schema is used for validation, but extension handlers receive `unknown` types that must be cast.

**Impact**: Runtime errors if parameters are wrong

### Problem 5: No Built-in Error Handling

If a tool handler throws, there's no automatic catch — the session may crash.

**Impact**: Extension bugs can break the agent

### Problem 6: Active Tool List Race Conditions

If multiple extensions call `setActiveTools()` concurrently, the final state is unpredictable.

**Impact**: Unclear which tools are actually active

### Problem 7: Context Access in Tool Handlers

Tool handlers receive `ExtensionContext` which includes:
- `ctx.sessionManager` — full session access
- `ctx.modelRegistry` — all API keys
- `ctx.cwd` — file system access

**Impact**: Tool handlers have the same privileges as the extension itself

---

## 5. SOLUTIONS — Best Practices

### Solution 1: Wrap All Handlers in Try/Catch

```typescript
api.registerTool({
  name: "my_tool",
  // ... other fields
  execute: async (toolCallId, params, signal, onUpdate, ctx) => {
    try {
      // Safe handler code
      const result = await doSomething(params);
      return { result };
    } catch (error) {
      // Log error, return safe result
      console.error("Tool error:", error);
      return { result: { error: "Operation failed" } };
    }
  }
});
```

### Solution 2: Use Unique Tool Names with Namespace

```typescript
// Bad: collision risk
api.registerTool({ name: "query", ... });

// Good: namespaced
api.registerTool({ name: "myorg_database_query", ... });
```

### Solution 3: Validate Arguments in Tool Handler

```typescript
execute: async (toolCallId, params, signal, onUpdate, ctx) => {
  // Explicit validation
  if (typeof params.input !== "string" || params.input.length > 1000) {
    return { result: { error: "Invalid input" } };
  }
  // Proceed with logic
  return { result: doSomething(params.input) };
}
```

### Solution 4: Use Read-Only Session Access When Possible

```typescript
// Prefer read-only operations
const messages = ctx.sessionManager.getMessages();
const entry = ctx.sessionManager.getEntry(entryId);

// Avoid writing unless necessary
// ctx.sessionManager.appendEntry() // Use sparingly
```

### Solution 5: Implement Proper AbortSignal Handling

```typescript
execute: async (toolCallId, params, signal, onUpdate, ctx) => {
  // Check abort signal periodically
  if (signal?.aborted) {
    return { result: { error: "Aborted" } };
  }

  // Pass signal to async operations
  const response = await fetch(url, { signal });

  // Update progress
  onUpdate?.({ status: "downloading", progress: 50 });

  return { result };
}
```

### Solution 6: Use Tool Events for Cross-Cutting Concerns

```typescript
// Separate security checks from tool implementation
api.on("tool_call", async (event, ctx) => {
  // Security check once
  if (isBlocked(event.toolName, event.args)) {
    return { block: true, reason: "Security policy" };
  }
  return { allow: true };
});

// Tool implementation is clean
api.registerTool({
  name: "sensitive_operation",
  execute: async (...) => {
    // No security logic here
    return { result: doOperation() };
  }
});
```

---

## 6. EDGE CASES

### Edge Case 1: Extension Throws During Tool Registration

**Scenario**: `registerTool()` throws during extension load

**Impact**: Extension fails to load → Gateway may crash

**Mitigation**: Wrap registration in try/catch at load time

### Edge Case 2: Tool Handler Returns Invalid Result Type

**Scenario**: Tool returns wrong shape for `AgentToolResult`

**Impact**: LLM receives malformed result → unpredictable behavior

**Mitigation**: Validate return type matches interface

### Edge Case 3: Multiple Extensions Register Same Tool Name

**Scenario**: Extension A and B both call `registerTool({ name: "query" })`

**Impact**: Last to register wins — unpredictable which handler runs

**Mitigation**: Use unique namespaced tool names

### Edge Case 4: setActiveTools Removes All Tools

**Scenario**: Extension calls `setActiveTools([])` accidentally

**Impact**: LLM has no tools to call → agent cannot function

**Mitigation**: Always include at least basic tools in set

### Edge Case 5: tool_call Handler Blocks But Doesn't Return Reason

**Scenario**: `tool_call` returns `{ block: true }` without reason

**Impact**: LLM sees generic block → may retry or fail silently

**Mitigation**: Always provide block reason

### Edge Case 6: AbortSignal Never Fires

**Scenario**: User aborts but tool doesn't check `signal`

**Impact**: Tool continues running → wasted resources

**Mitigation**: Check signal at checkpoints in long operations

### Edge Case 7: Tool Result Modified After LLM Already Saw Original

**Scenario**: `tool_result` handler modifies result after LLM processed

**Impact**: Inconsistent state — LLM and actual result differ

**Mitigation**: Understand event timing, only modify before LLM processes

---

## 7. CREATIVE USES

### Creative Use 1: Tool Proxy/Gateway

```typescript
// Create a proxy that logs all tool calls
api.on("tool_call", async (event, ctx) => {
  await logToolCall(event.toolName, event.args);
  return { allow: true };
});

api.on("tool_result", async (event, ctx) => {
  await logToolResult(event.toolName, event.result);
  return { allow: true };
});
```

### Creative Use 2: Tool Mocking for Testing

```typescript
// In test mode, mock external tools
if (process.env.TEST_MODE) {
  api.registerTool({
    name: "external_api",
    execute: async (toolCallId, params, signal, onUpdate, ctx) => {
      return { result: { data: "mocked_response" } };
    }
  });
}
```

### Creative Use 3: Dynamic Tool Discovery

```typescript
// Discover tools based on workspace files
api.on("session_start", async (event, ctx) => {
  const files = await ctx.exec("find", [".", "-name", "*.py"], {});
  if (files.includes("database.py")) {
    api.registerTool(databaseTool);
  }
  if (files.includes("api.py")) {
    api.registerTool(apiTool);
  }
});
```

### Creative Use 4: Rate Limiting Per Tool

```typescript
const toolCallCounts = new Map();
api.on("tool_call", async (event, ctx) => {
  const count = toolCallCounts.get(event.toolName) || 0;
  if (count > 100) {
    return { block: true, reason: "Rate limit exceeded" };
  }
  toolCallCounts.set(event.toolName, count + 1);
  return { allow: true };
});
```

### Creative Use 5: Tool Result Caching

```typescript
const resultCache = new Map();
api.on("tool_call", async (event, ctx) => {
  const cacheKey = `${event.toolName}:${JSON.stringify(event.args)}`;
  if (resultCache.has(cacheKey)) {
    return { result: resultCache.get(cacheKey), cached: true };
  }
  return { allow: true };
});

api.on("tool_result", async (event, ctx) => {
  const cacheKey = `${event.toolName}:${JSON.stringify(event.args)}`;
  resultCache.set(cacheKey, event.result);
  return { allow: true };
});
```

### Creative Use 6: Context-Aware Tool Filtering

```typescript
// Enable/disable tools based on user level
api.on("tool_call", async (event, ctx) => {
  const userLevel = ctx.sessionManager.getUserLevel?.() || "guest";
  const toolPermissions = {
    guest: ["read", "ls"],
    user: ["read", "ls", "write", "edit"],
    admin: ["read", "ls", "write", "edit", "exec"]
  };
  if (!toolPermissions[userLevel].includes(event.toolName)) {
    return { block: true, reason: `Tool not available for ${userLevel}` };
  }
  return { allow: true };
});
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### Security Questions
- [ ] Can a tool handler access ctx.sessionManager and modify session data? **[HIGH]**
- [ ] Can tool result interception be used for data exfiltration? **[HIGH]**
- [ ] Is there a way to sandbox tool execution separately from extension? **[MED]**

### Integration Questions
- [ ] Can extensions register tools that call other extensions' tools? **[MED]**
- [ ] Can tool handlers trigger subagent runs? **[MED]**
- [ ] Can extensions add tools to the system prompt dynamically? **[MED]**

### Performance Questions
- [ ] What's the overhead of tool call interception? **[LOW]**
- [ ] Can many tool handlers cause latency? **[LOW]**

### Operational Questions
- [ ] Can tool registration be hot-reloaded without restart? **[MED]**
- [ ] Are tool execution times logged? **[LOW]**
- [ ] Can extensions see which tool called another tool? **[MED]**

---

## 9. SOURCES

### Primary Sources (OpenClaw + Pi-Coding-Agent)

1. `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/types.d.ts` — ExtensionAPI type definitions (registerTool, tool_call, tool_result)
2. `/usr/local/lib/node_modules/openclaw/docs/pi.md` — Pi Integration Architecture
3. `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin architecture (security model)
4. `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/*.d.ts` — Type definitions

### Key Findings Summary

| Aspect | Finding |
|--------|---------|
| Tool registration | `api.registerTool(toolDefinition)` |
| Tool interception | `tool_call` and `tool_result` events |
| Active tool control | `getActiveTools()`, `setActiveTools()` |
| Security | No sandbox — runs in-process |
| Schema | TypeBox with `defineTool()` helper |
| Error handling | No built-in — must wrap manually |

---

## APPENDIX: Complete Tool Events Reference

```typescript
// Tool execution lifecycle events
api.on("tool_execution_start", handler);  // When tool starts
api.on("tool_execution_update", handler); // During streaming tool
api.on("tool_execution_end", handler);    // When tool ends

// Tool call interception (before LLM sees result)
api.on("tool_call", handler);             // Block or modify args
api.on("tool_result", handler);           // Block or modify result

// Specific tool events
api.on("bash_tool_call", handler);        // bash tool specifically
api.on("read_tool_call", handler);        // read tool specifically
// ... etc for each built-in tool
```

---

*Research by: Investigador Scout*
*Date: 2026-04-23 02:35 CET*
*Status: COMPLETE — L23 RESOLVED*

---

## FOLLOW-UP ACTIONS

- [x] Save findings to `Research/OpenClaw/findings/extension-tool-integration.md`
- [ ] Update `Research/OpenClaw/questions.md` to mark L23 as RESOLVED
- [ ] Update `Research/OpenClaw/index.md` with L23 completed
- [ ] Update `Research/OpenClaw/sources.md` with new sources
- [ ] Notify BRAIN for curation into `OPENCLAW_EXPERT.md`