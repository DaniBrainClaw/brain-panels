# Hook Types Difference: Internal vs Plugin Hooks — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23  
**Topic:** What is exact difference between internal hooks (5) vs plugin hooks (28+)?  
**Priority:** MEDIUM (from backlog.md #14)  
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

OpenClaw has **TWO fundamentally different hook systems** that are often conflated:

| Aspect | Internal Hooks | Plugin Hooks (Typed Hooks) |
|--------|---------------|---------------------------|
| **Origin** | Standalone hook directories | Plugin SDK registration |
| **Count** | 4 bundled + custom in `~/.openclaw/hooks/` | 44+ provider runtime + channel + tool hooks |
| **Discovery** | Directory-based auto-discovery | Programmatic registration via SDK |
| **Execution model** | Fire-and-forget, registration order | Void/modifying/claiming modes |
| **Purpose** | Workspace/event automation | Deep provider/channel/tool integration |
| **Security** | No prompt injection context by default | Controlled via `PROMPT_INJECTION_HOOK_NAMES` |

### Internal Hooks (Standalone Hooks)

**Definition**: Internal hooks are **standalone hook directories** auto-discovered from specific directories. They respond to agent lifecycle events like `/new`, `/reset`, `/stop`, and gateway startup.

**4 Bundled Internal Hooks**:

| Hook Name | Events | Purpose |
|-----------|--------|---------|
| `session-memory` | `command:new`, `command:reset` | Saves session context to `<workspace>/memory/` |
| `bootstrap-extra-files` | `agent:bootstrap` | Injects additional bootstrap files from glob patterns |
| `command-logger` | `command` | Logs all commands to `~/.openclaw/logs/commands.log` |
| `boot-md` | `gateway:startup` | Runs `BOOT.md` when gateway starts |

**Discovery locations** (in order of precedence):
1. **Bundled hooks** — shipped with OpenClaw
2. **Managed hooks** — `~/.openclaw/hooks/` (user-installed)
3. **Extra dirs** — configured via `hooks.internal.load.extraDirs[]`
4. **Workspace hooks** — `<workspace>/hooks/` (per-agent, **disabled by default**)

### Plugin Hooks (Typed Hooks)

**Definition**: Plugin hooks are **typed function callbacks** registered by plugins via the Plugin SDK (`registerHook()`). They cover deep integration points across the entire agent lifecycle.

**44+ Provider Runtime Hooks** covering:
- Model resolution (11 hooks): `normalizeModelId`, `normalizeTransport`, `normalizeConfig`, `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`, `contributeResolvedModelCompat`, `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`
- Provider lifecycle (15+ hooks): `catalog`, `applyConfigDefaults`, `resolveConfigApiKey`, `resolveSyntheticAuth`, `resolveExternalAuthProfiles`, `shouldDeferSyntheticProfileAuth`, `capabilities`, `normalizeToolSchemas`, `inspectToolSchemas`, `formatApiKey`, `refreshOAuth`, `buildAuthDoctorHint`
- Transport/policy (8 hooks): `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`, `matchesContextOverflowError`, `classifyFailoverReason`, `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`
- Thinking/reasoning (4 hooks): `isBinaryThinking`, `supportsXHighThinking`, `resolveDefaultThinkingLevel`, `isModernModelRef`
- Auth/usage (5 hooks): `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`, `onModelSelected`
- Replay/transcript (4 hooks): `buildReplayPolicy`, `sanitizeReplayHistory`, `validateReplayTurns`

**Other Plugin Hook Categories**:
- **Tool hooks**: `before_tool_call`, `after_tool_call`, `tool_result_persist`, `before_agent_reply`
- **Message hooks**: `message:received`, `message:transcribed`, `message:preprocessed`, `message:sent`, `before_message_write`
- **Session hooks**: `session:patch`, `session:compact:before`, `session:compact:after`
- **Agent hooks**: `agent:bootstrap`, `before_agent_start` (deprecated), `before_prompt_build`
- **Subagent hooks**: `subagent:start`, `subagent:complete`
- **Gateway hooks**: `gateway:startup`
- **Install hooks**: `before_install`, `after_install`

---

## 2. HOW IT WORKS — Architecture & Mechanics

### Internal Hooks Architecture

**Hook structure** (per directory):
```
my-hook/
├── HOOK.md          # Metadata + YAML frontmatter
└── handler.ts       # Handler implementation
```

**HOOK.md format**:
```markdown
---
name: my-hook
description: "Short description"
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# My Hook
Detailed docs here.
```

**Handler implementation**:
```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") return;
  console.log(`[my-hook] New command triggered`);
  event.messages.push("Hook executed!"); // Optional: send to user
};
export default handler;
```

**Execution**: Internal hooks run via `runInternalHook()` — handlers called in **registration order**, each wrapped in try/catch, errors logged but don't halt other handlers.

### Plugin Hooks Architecture

**Registration** (via Plugin SDK):
```typescript
api.registerHook({
  hookName: "before_tool_call",
  pluginId: "my-plugin",
  priority: 50,
  handler: async (event, ctx) => {
    // Your logic
  }
});
```

**Hook registry**: Plugin hooks stored in `registry.typedHooks[]` array, sorted by `(b.priority ?? 0) - (a.priority ?? 0)` (higher first).

**Three execution modes**:

| Mode | Function | Behavior | Example Hooks |
|------|----------|----------|---------------|
| **Void** | `runVoidHook()` | Parallel via Promise.all, fail-open | `message:received`, `message:sent` |
| **Modifying** | `runModifyingHook()` | Sequential, result merged | `before_prompt_build`, `before_model_resolve` |
| **Claiming** | `runClaimingHook()` | First `{ handled: true }` wins | `inbound_claim` |

**Execution flow**:
```
Hook Event Fires
       │
       ▼
getHooksForName(registry, hookName)
  Sort by: priority (high→low)
       │
       ▼
runVoidHook() | runModifyingHook() | runClaimingHook()
```

### Key Differences Summary

| Aspect | Internal Hooks | Plugin Hooks |
|--------|---------------|--------------|
| **Entry point** | `registerInternalHook()` | `registerHook()` |
| **Discovery** | Directory scan | Programmatic registration |
| **Hook name conflict** | Later precedence overrides earlier | Same source precedence, priority decides |
| **Source types** | `openclaw-bundled`, `openclaw-managed`, `openclaw-workspace` | `openclaw-plugin` |
| **Execution order** | Registration index (FIFO) | Priority value (higher first) |
| **Error handling** | Per-handler try/catch, logged | Per-handler try/catch + failure policy |
| **Prompt injection context** | NONE by default | Controlled via `PROMPT_INJECTION_HOOK_NAMES` |
| **Can modify event context** | Limited (messages array push) | Full modification rights |
| **async support** | Yes | Yes (Promise.all for void, sequential for modifying) |
| **Priority field** | No | Yes (`priority?: number`) |
| **Access to config** | Via `context.cfg` | Via plugin context |

### PROMPT_INJECTION_HOOK_NAMES

Security-critical config restricting which hooks receive **prompt injection context**:

```javascript
PROMPT_INJECTION_HOOK_NAMES = ["before_prompt_build", "before_agent_start"]
```

Only these two hooks can see the full prompt context. All other hooks (including internal hooks) run without access to injected prompt content.

---

## 3. USES — Practical Applications

### Internal Hooks Use Cases

| Hook | Best For |
|------|----------|
| `session-memory` | Auto-saving conversation summaries to `memory/` on new session |
| `bootstrap-extra-files` | Injecting monorepo AGENTS.md/TOOLS.md at bootstrap |
| `command-logger` | Audit trail of all slash commands |
| `boot-md` | Startup scripts, external service verification, cache warming |

### Plugin Hooks Use Cases (Provider Runtime)

| Hook Category | Use Case |
|---------------|----------|
| `normalizeModelId` | Normalize legacy model-id aliases before lookup |
| `normalizeTransport` | Normalize provider-family api/baseUrl |
| `resolveDynamicModel` | Handle arbitrary upstream model ids |
| `prepareDynamicModel` | Async warm-up with network metadata |
| `before_prompt_build` | Inject dynamic system prompts, filter sensitive content |
| `before_tool_call` | Validate tool parameters, enforce policies (fail-closed) |
| `before_agent_reply` | Sanitize output, add disclaimers, redact PII |

### Plugin Hooks Use Cases (Tool/Message)

| Hook | Use Case |
|------|----------|
| `before_tool_call` | Block dangerous tool calls, validate parameters |
| `after_tool_call` | Log tool results, post-process outputs |
| `tool_result_persist` | Persist tool results to external storage |
| `message:received` | Pre-process inbound messages |
| `message:transcribed` | Process audio transcription before agent sees it |
| `message:preprocessed` | Final enriched body before agent processes |
| `before_message_write` | Modify outbound messages |
| `before_install` | Scan skill installer metadata |
| `after_install` | Post-install skill setup |

---

## 4. PROBLEMS — Known Issues & Limitations

### Problem 1: Conflation of Two Systems

**Issue**: Documentation and discussions often use "hooks" to mean both internal and plugin hooks, causing confusion.

**Symptom**: User reads "hooks run in registration order" but plugin hooks run by priority. Confused about which applies where.

**Reality**: Internal hooks use registration index; plugin hooks use priority value.

### Problem 2: Workspace Hooks Disabled by Default

**Issue**: Workspace hooks have HIGHEST precedence (40) but are disabled until explicitly enabled.

**Confusion**: User enables workspace hook expecting it to fire, but it doesn't because `hooks.internal.entries.my-hook.enabled: true` is missing.

### Problem 3: No Prompt Injection for Internal Hooks

**Issue**: Internal hooks have NO access to prompt injection context.

**Limitation**: If you need a hook to modify the system prompt, you must use `before_prompt_build` (plugin hook), not an internal hook.

### Problem 4: `before_agent_start` Deprecated

**Issue**: The `before_agent_start` internal hook is deprecated but still works (just shows warning).

**Current state**: Use `before_prompt_build` + `before_model_resolve` separately for new plugins.

### Problem 5: before_tool_call Uses fail-closed

**Issue**: `before_tool_call` throws if handler errors, halting tool execution.

**Risk**: A buggy `before_tool_call` handler can break all tool calls.

**Workaround**: Wrap handlers in try/catch to prevent errors from propagating.

### Problem 6: No Native Hook-to-Hook Communication

**Issue**: Internal hooks run independently with no shared state mechanism.

**Workaround**: Use session store (`event.context.sessionEntry`) or file-based communication between hooks.

---

## 5. SOLUTIONS — Best Practices & Workarounds

### Solution 1: Choose Right Hook Type

| Need | Use |
|------|-----|
| Workspace/event automation (`/new`, `/reset`) | Internal hook |
| Provider-specific model behavior | Plugin hook (provider runtime hook) |
| Tool validation/policy | Plugin hook (`before_tool_call`) |
| Message pre-processing | Plugin hook (`message:received`) |
| Prompt modification | Plugin hook (`before_prompt_build`) |

### Solution 2: Debug Hook Registration

```bash
# List all discovered hooks
openclaw hooks list --verbose

# Check specific hook info
openclaw hooks info <hook-name>

# View gateway logs
./scripts/clawlog.sh | grep hook
```

### Solution 3: Enable Workspace Hooks Explicitly

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

### Solution 4: Use Priority for Plugin Hook Ordering

```typescript
api.registerHook({
  hookName: "before_tool_call",
  priority: 100,  // Run first (security checks)
  handler: async (event, ctx) => {
    if (!isValid(event.context.toolCall)) {
      return { block: true, blockReason: "Invalid parameters" };
    }
  }
});
```

### Solution 5: Use before_install for Scanner Integration

```typescript
api.registerHook({
  hookName: "before_install",
  handler: async (event, ctx) => {
    // Scan SKILL.md content before skill install
    const content = await readFile(event.context.skillPath);
    if (containsMaliciousPatterns(content)) {
      return { block: true, blockReason: "Malicious pattern detected" };
    }
  }
});
```

---

## 6. EDGE CASES — Unusual Scenarios

### Edge Case 1: Same Hook Name from Internal + Plugin

**Scenario**: Internal hook named `session-memory` and plugin hook named `session-memory`.

**Resolution**: Both can coexist — internal hooks have source `openclaw-managed` or `openclaw-workspace`, plugin hooks have source `openclaw-plugin`. Source precedence determines execution order.

### Edge Case 2: Plugin Hook Returns Non-Object

**Scenario**: Plugin hook handler returns a primitive instead of expected object.

**Resolution**: For modifying hooks, primitives are ignored. For claiming hooks, primitives don't match `handlerResult?.handled`, so claim fails.

### Edge Case 3: before_tool_call Block Response Format

**Scenario**: `before_tool_call` returns `{ block: true }` but wrong format.

**Resolution**: If block response is malformed, Gateway treats it as allow (no block).

### Edge Case 4: Plugin Hook for Non-Provider Event

**Scenario**: Plugin registers for event that isn't a provider runtime hook.

**Resolution**: Plugins can register any hook name, but only certain hooks are called by OpenClaw core. Unrecognized hook names are silently ignored.

### Edge Case 5: Internal Hook in Extra Dirs Has Same Name as Bundled

**Scenario**: Custom hook in `hooks.internal.load.extraDirs[]` has same name as bundled hook.

**Resolution**: Same source precedence rules apply. `canOverride` policies determine if custom can override bundled.

---

## 7. CREATIVE USES — Innovative Applications

### Creative Use 1: Multi-Provider Model Routing

Use `before_model_resolve` to route requests based on content analysis:
```typescript
api.registerHook({
  hookName: "before_model_resolve",
  priority: 100,
  handler: async (event, ctx) => {
    if (containsCode(event.context.userMessage)) {
      return { providerOverride: "anthropic", modelOverride: "claude-sonnet" };
    }
  }
});
```

### Creative Use 2: Real-Time Message Filtering

Use `message:received` to filter spam before agent sees it:
```typescript
api.registerHook({
  hookName: "message:received",
  handler: async (event, ctx) => {
    if (isSpam(event.context.content)) {
      return { handled: true, /* silent ignore */ };
    }
  }
});
```

### Creative Use 3: Tool Usage Analytics

Use `after_tool_call` to track tool usage patterns:
```typescript
api.registerHook({
  hookName: "after_tool_call",
  handler: async (event, ctx) => {
    await logToolUsage(event.context.toolName, event.context.sessionKey);
  }
});
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### NEW Questions Generated:

1. **[MED]** Can plugin hooks be dynamically registered/unregistered at runtime?
   - **Rationale**: Plugins load at startup; unclear if new hooks can be added without restart.

2. **[MED]** Can hooks access gateway internal state (session store, config)?
   - **Rationale**: Internal hooks access `context.cfg`; plugin hooks access via ExtensionContext; exact boundaries unclear.

3. **[LOW]** What is the exact difference between `before_install` and `after_install` hooks?
   - **Rationale**: Can be used for pre/post skill install validation.

4. **[LOW]** Can internal hooks use priority values like plugin hooks?
   - **Rationale**: Internal hooks use registration index, not priority field.

5. **[MED]** What happens when multiple plugins register for same claiming hook?
   - **Rationale**: First `{ handled: true }` wins, but priority may affect order.

---

## 9. SOURCES

### Primary Sources

- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Internal hooks documentation
- `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin architecture, provider runtime hooks (44+ hooks table)
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook execution runner implementation
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation
- `/usr/local/lib/node_modules/openclaw/dist/loader-DuIH27tS.js` — Hook registry: `registry.typedHooks.push()`

### Related Findings

- `Research/OpenClaw/findings/openclaw-hooks-system.md` (L18) — Complete hook system overview
- `Research/OpenClaw/findings/hook-security-audit.md` (L20) — Hook security model
- `Research/OpenClaw/findings/hook-execution-order.md` (L16) — Hook execution order mechanics

---

*Research by: Investigador Scout*  
*Date: 2026-04-23*  
*Status: COMPLETE ✅*
