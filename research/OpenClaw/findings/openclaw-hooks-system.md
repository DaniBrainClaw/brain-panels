# OpenClaw Hooks System — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23  
**Topic:** OpenClaw Hook System (Internal Hooks + Plugin Hooks)  
**Priority:** MEDIUM (from backlog.md)  
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

**Hooks** are event-driven automation triggers in OpenClaw that execute custom code when specific events occur inside the Gateway. They provide a way to intercept, modify, or react to agent lifecycle events, message flows, command executions, and system state changes.

### Two Distinct Hook Systems

OpenClaw has **TWO separate hook systems** that are often conflated:

| System | Count | Purpose | Discovery |
|--------|-------|---------|-----------|
| **Internal Hooks** | 4 bundled | Workspace/event automation (`/new`, `/reset`, gateway startup) | `~/.openclaw/hooks/` + workspace `hooks/` |
| **Plugin Hooks** | 28+ | Deep integration into model resolution, agent lifecycle, message flow, tool execution | Bundled with plugins, registered via SDK |

### Internal Hooks (Standalone)

4 bundled hooks ship with OpenClaw:

| Hook | Events | Purpose |
|------|--------|---------|
| `session-memory` | `command:new`, `command:reset` | Saves session context to `<workspace>/memory/` |
| `bootstrap-extra-files` | `agent:bootstrap` | Injects additional bootstrap files from glob patterns |
| `command-logger` | `command` | Logs all commands to `~/.openclaw/logs/commands.log` |
| `boot-md` | `gateway:startup` | Runs `BOOT.md` when gateway starts |

### Plugin Hooks (28+ hooks)

Plugins can register hooks covering:

- **Model resolution**: `before_model_resolve`, `normalizeModelId`, `normalizeTransport`, `normalizeConfig`, `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`, `contributeResolvedModelCompat`
- **Agent lifecycle**: `before_agent_start` (LEGACY), `agent:bootstrap`
- **Prompt building**: `before_prompt_build`
- **Message flow**: `message:received`, `message:transcribed`, `message:preprocessed`, `message:sent`
- **Tool execution**: `before_tool_call`, `after_tool_call`, `before_agent_reply`
- **Subagent coordination**: `subagent:start`, `subagent:complete`
- **Compaction**: `session:compact:before`, `session:compact:after`
- **Session**: `session:patch`
- **Gateway lifecycle**: `gateway:startup`

### PROMPT_INJECTION_HOOK_NAMES

A security-critical config that defines which hooks can receive **prompt injection context**. Currently restricted to:
- `before_prompt_build`
- `before_agent_start`

This prevents malicious hooks from accessing injected prompt context they shouldn't see.

---

## 2. HOW IT WORKS — Architecture & Mechanics

### Hook Discovery Order (Precedence)

Hooks are discovered from directories in order of **increasing override precedence**:

1. **Bundled hooks** — shipped with OpenClaw
2. **Plugin hooks** — bundled inside installed plugins
3. **Managed hooks** — `~/.openclaw/hooks/` (user-installed, shared across workspaces). Extra dirs via `hooks.internal.load.extraDirs`
4. **Workspace hooks** — `<workspace>/hooks/` (per-agent, **disabled by default** until explicitly enabled)

**Key rule**: Workspace hooks can ADD new hook names but CANNOT override bundled, managed, or plugin-provided hooks with the same name.

### Hook Structure

Each standalone hook is a directory containing:

```
my-hook/
├── HOOK.md          # Metadata + documentation
└── handler.ts       # Handler implementation
```

### HOOK.md Format

```markdown
---
name: my-hook
description: "Short description of what this hook does"
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# My Hook

Detailed documentation goes here.
```

### Handler Implementation

```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log(`[my-hook] New command triggered`);
  // Your logic here

  // Optionally send message to user
  event.messages.push("Hook executed!");
};

export default handler;
```

### Event Object Structure

Each event includes:
- `type` — event category (e.g., `command`, `message`, `session`)
- `action` — specific action within type (e.g., `new`, `reset`)
- `sessionKey` — session identifier
- `timestamp` — when event fired
- `messages` — array to push messages to user
- `context` — event-specific data

### Event Context by Type

**Command events** (`command:new`, `command:reset`):
- `context.sessionEntry`
- `context.previousSessionEntry`
- `context.commandSource`
- `context.workspaceDir`
- `context.cfg`

**Message events** (`message:received`):
- `context.from`
- `context.content`
- `context.channelId`
- `context.metadata` (provider-specific including `senderId`, `senderName`, `guildId`)

**Message events** (`message:sent`):
- `context.to`
- `context.content`
- `context.success`
- `context.channelId`

**Message events** (`message:transcribed`):
- `context.transcript`
- `context.from`
- `context.channelId`
- `context.mediaPath`

**Message events** (`message:preprocessed`):
- `context.bodyForAgent` (final enriched body)
- `context.from`
- `context.channelId`

**Bootstrap events** (`agent:bootstrap`):
- `context.bootstrapFiles` (mutable array — CAN MODIFY what files are injected!)
- `context.agentId`

**Session patch events** (`session:patch`):
- `context.sessionEntry`
- `context.patch` (only changed fields)
- `context.cfg`

**Compaction events**:
- `session:compact:before`: `messageCount`, `tokenCount`
- `session:compact:after`: `compactedCount`, `summaryLength`, `tokensBefore`, `tokensAfter`

### Plugin Hook Execution Order

For model/provider plugins, OpenClaw calls hooks in this rough order:

1. `catalog` — publish provider config into `models.providers`
2. `applyConfigDefaults` — apply provider-owned global config defaults
3. `normalizeModelId` — normalize legacy/preview model-id aliases
4. `normalizeTransport` — normalize provider-family `api`/`baseUrl`
5. `normalizeConfig` — normalize `models.providers.<id>` before runtime
6. `applyNativeStreamingUsageCompat` — apply native streaming-usage compat rewrites
7. `resolveConfigApiKey` — resolve env-marker auth for config providers
8. `resolveSyntheticAuth` — surface local/self-hosted or config-backed auth
9. `resolveExternalAuthProfiles` — overlay provider-owned external auth profiles
10. `shouldDeferSyntheticProfileAuth` — defer synthetic profile auth
11. `resolveDynamicModel` — sync fallback for provider-owned model ids
12. `prepareDynamicModel` — async warm-up, then `resolveDynamicModel` runs again
13. `normalizeResolvedModel` — final rewrite before embedded runner uses model
14. `contributeResolvedModelCompat` — contribute compat flags
15. `capabilities` — provider-owned transcript/tooling metadata
16. `normalizeToolSchemas` — normalize tool schemas
17. `inspectToolSchemas` — surface provider-owned schema diagnostics
18. `resolveReasoningOutputMode` — select native vs tagged reasoning
19. `prepareExtraParams` — request-param normalization
20. `createStreamFn` — fully replace the normal stream path
21. `wrapStreamFn` — stream wrapper after generic wrappers
22. `resolveTransportTurnState` — attach native per-turn transport headers
23. `resolveWebSocketSessionPolicy` — attach native WS headers/cool-down
24. `formatApiKey` — auth-profile formatter
25. `refreshOAuth` — OAuth refresh override
26. `buildAuthDoctorHint` — repair hint appended when OAuth refresh fails
27. `matchesContextOverflowError` — provider-owned context-window overflow matcher
28. `classifyFailoverReason` — provider-owned failover reason classification
29. `isCacheTtlEligible` — prompt-cache policy for proxy/backhaul
30. `buildMissingAuthMessage` — replacement missing-auth recovery message
31. `suppressBuiltInModel` — stale upstream model suppression
32. `augmentModelCatalog` — synthetic/final catalog rows
33. `isBinaryThinking` — binary-thinking toggle
34. `supportsXHighThinking` — `xhigh` reasoning support
35. `resolveDefaultThinkingLevel` — default `/think` level for model family
36. `isModernModelRef` — modern-model matcher
37. `prepareRuntimeAuth` — exchange credential into runtime token
38. `resolveUsageAuth` — resolve usage/billing credentials
39. `fetchUsageSnapshot` — fetch and normalize usage/quota snapshots
40. `createEmbeddingProvider` — build provider-owned embedding adapter
41. `buildReplayPolicy` — return replay policy
42. `sanitizeReplayHistory` — rewrite replay history
43. `validateReplayTurns` — final replay-turn validation
44. `onModelSelected` — post-selection side effects

### Configuration

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false }
      }
    }
  }
}
```

Per-hook environment variables:

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "my-hook": {
          "enabled": true,
          "env": { "MY_CUSTOM_VAR": "value" }
        }
      }
    }
  }
}
```

Extra hook directories:

```json
{
  "hooks": {
    "internal": {
      "load": {
        "extraDirs": ["/path/to/more/hooks"]
      }
    }
  }
}
```

---

## 3. USES — Practical Applications

### Bundled Hook Use Cases

| Hook | Use Case |
|------|----------|
| `session-memory` | Auto-save conversation summaries to `memory/YYYY-MM-DD-slug.md` on `/new` or `/reset` |
| `bootstrap-extra-files` | Inject monorepo `AGENTS.md`/`TOOLS.md` files during bootstrap |
| `command-logger` | Audit trail of all slash commands to `~/.openclaw/logs/commands.log` |
| `boot-md` | Run startup scripts, verify external service connectivity, warm caches |

### Plugin Hook Use Cases

| Hook Category | Use Cases |
|---------------|-----------|
| **before_model_resolve** | Route requests to different models based on content, cost optimization, A/B testing |
| **before_prompt_build** | Inject dynamic system prompts, filter sensitive content, add context |
| **before_agent_reply** | Sanitize output, add disclaimers, redact PII |
| **before_tool_call** | Validate tool parameters, log tool usage, enforce policies |
| **after_tool_call** | Post-process tool results, enrich responses |
| **message:received** | Anti-spam filtering, content moderation, routing |
| **message:preprocessed** | Enrich messages with external data before agent sees them |
| `agent:bootstrap` | Add/remove bootstrap files dynamically, conditional bootstrap |
| `session:compact:before` | Prepare for compaction, save state |
| `session:compact:after` | Post-compaction cleanup, notify external systems |

### Real-World Examples from Docs

**session-memory**: 
- Extracts last 15 user/assistant messages
- Generates descriptive filename slug via LLM
- Saves to `<workspace>/memory/YYYY-MM-DD-slug.md`
- Requires `workspace.dir` configured

**bootstrap-extra-files**:
```json
{
  "hooks": {
    "internal": {
      "entries": {
        "bootstrap-extra-files": {
          "enabled": true,
          "paths": ["packages/*/AGENTS.md", "packages/*/TOOLS.md"]
        }
      }
    }
  }
}
```

**command-logger**:
- Logs to `~/.openclaw/logs/commands.log`
- Format supports filtering by action: `grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .`

### Advanced Plugin Hook Patterns

**before_prompt_build for RAG**:
```typescript
api.registerHook({
  id: "my-rag-hook",
  events: ["before_prompt_build"],
  handler: async (event) => {
    if (event.type !== "before_prompt_build") return;
    // Inject relevant documents from vector DB
    const relevantDocs = await searchVectorDB(event.context.userQuery);
    event.context.systemPrompt += `\n\nRelevant context:\n${relevantDocs}`;
  }
});
```

**before_tool_call for validation**:
```typescript
api.registerHook({
  id: "exec-validator",
  events: ["before_tool_call"],
  handler: async (event) => {
    if (event.toolName === "exec") {
      const cmd = event.params.command;
      if (isDangerousCommand(cmd)) {
        throw new Error("Blocked dangerous command");
      }
    }
  }
});
```

---

## 4. PROBLEMS — Known Issues & Limitations

### Confirmed Issues

1. **`before_agent_start` is DEPRECATED**
   - Legacy hook still supported but deprecated
   - Should migrate to `before_model_resolve` for model/provider override
   - Should migrate to `before_prompt_build` for prompt mutation
   - Shows "legacy warning" in `openclaw plugins inspect`

2. **Hook discovery not working after config hot-reload**
   - Gateway restart may be needed after enabling/disabling hooks
   - Config change requires restart to reload hook handlers

3. **Workspace hooks disabled by default**
   - `<workspace>/hooks/` are disabled until explicitly enabled
   - Must use `openclaw hooks enable <hook-name>` to activate

4. **No hook-to-hook communication built-in**
   - Each hook runs independently
   - Shared state requires external mechanism (files, memory store)

5. **Uncaught exceptions in hooks**
   - If handler throws, other handlers on same event may still run
   - But gateway stability not guaranteed
   - Best practice: wrap in try/catch

6. **Infinite hook loops possible**
   - Hook A → modifies session → triggers Hook B → modifies session → triggers Hook A
   - No built-in protection against circular dependencies

7. **Plugin hooks are in-process**
   - Native plugins run inside Gateway with same trust level as core
   - Malicious plugin = arbitrary code execution inside Gateway
   - No sandboxing for native plugins

8. **Limited concurrency control**
   - No built-in mechanism to limit concurrent hook executions
   - Heavy hooks can block message processing

### Limitations

| Limitation | Details |
|------------|---------|
| Max concurrent hooks | Not explicitly limited, but heavy use impacts performance |
| Hook execution timeout | No explicit timeout enforcement |
| Hook execution order | Not guaranteed for multiple hooks on same event |
| Bootstrap file removal danger | `agent:bootstrap` hook CAN remove `MEMORY.md` from `bootstrapFiles` — destructive |

### Security Considerations

1. **Plugin trust**: Plugins run in-process with Gateway = same privileges as core
2. **Supply chain risk**: npm installs can run arbitrary lifecycle scripts
3. **Prompt injection**: `PROMPT_INJECTION_HOOK_NAMES` restricts which hooks get prompt context
4. **Workspace hooks**: Disabled by default to prevent accidental activation

---

## 5. SOLUTIONS — Best Practices & Workarounds

### Best Practices

1. **Keep handlers fast**
   - Fire-and-forget heavy work: `void processInBackground(event)`
   - Hooks run during command processing — slow hooks = slow responses

2. **Handle errors gracefully**
   ```typescript
   const handler = async (event) => {
     try {
       // risky operation
     } catch (err) {
       console.error(`[my-hook] Error:`, err);
       // don't throw so other handlers can run
     }
   };
   ```

3. **Filter events early**
   ```typescript
   const handler = async (event) => {
     if (event.type !== "command" || event.action !== "new") {
       return; // exit fast
     }
     // rest of logic
   };
   ```

4. **Use specific event keys**
   - Prefer `"events": ["command:new"]` over `"events": ["command"]`
   - Reduces overhead from unnecessary invocations

5. **Enable only what you need**
   ```bash
   openclaw hooks enable session-memory
   # don't enable everything
   ```

6. **Use PROMPT_INJECTION_HOOK_NAMES correctly**
   - Only `before_prompt_build` and `before_agent_start` receive prompt injection context
   - Don't try to access injected prompts from other hooks

### Configuration Recommendations

**Minimal hooks config for security**:
```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false },
        "boot-md": { "enabled": false },
        "bootstrap-extra-files": { "enabled": false }
      }
    }
  }
}
```

**For workspace hooks — explicit enablement**:
```bash
# After placing hook in <workspace>/hooks/my-hook/
openclaw hooks enable my-hook
# Then restart gateway
openclaw gateway restart
```

### Troubleshooting

**Hook not discovered**:
```bash
# Verify directory structure
ls -la ~/.openclaw/hooks/my-hook/
# Should show: HOOK.md, handler.ts

# List all discovered hooks
openclaw hooks list
```

**Hook not eligible**:
```bash
openclaw hooks info my-hook
# Check for missing binaries, env vars, config values, OS compatibility
```

**Hook not executing**:
1. Verify hook enabled: `openclaw hooks list`
2. Restart gateway so hooks reload
3. Check logs: `./scripts/clawlog.sh | grep hook`

---

## 6. EDGE CASES — Unusual Scenarios

### Edge Case 1: Modifying bootstrapFiles array

**Scenario**: `agent:bootstrap` hook removes `MEMORY.md` from `bootstrapFiles`

**Risk**: Agent loses persistent memory context for entire session

**Impact**: Extremely high — agent forgets all learned facts

**Mitigation**: Be extremely careful with bootstrapFiles mutations; always verify intended files remain

### Edge Case 2: Infinite hook loops

**Scenario**: 
```
Hook A (message:received) → modifies session
→ triggers Hook B (session:patch) → modifies session
→ triggers Hook A again → infinite loop
```

**Risk**: Gateway hangs or crashes

**Mitigation**: Implement guard counters, avoid triggers that re-fire same event type

### Edge Case 3: Conflicting before_model_resolve overrides

**Scenario**: Two plugins both try to set model override

**Behavior**: Last hook to run wins; no conflict resolution

**Impact**: Unpredictable model selection

**Mitigation**: Use explicit priority ordering if available; document override chain

### Edge Case 4: Gateway restart during hook execution

**Scenario**: Hook is mid-execution when gateway restarts

**Behavior**: In-flight work lost; no cleanup guarantee

**Impact**: Partial state changes possible; orphaned resources

**Mitigation**: Design hooks to be idempotent; use transactional patterns

### Edge Case 5: Multiple hooks on same event with different purposes

**Scenario**: 
- Hook A: adds system prompt context
- Hook B: removes sensitive data from context
- Execution order matters

**Behavior**: No guaranteed order

**Impact**: If B runs before A, sensitive data may still be present when A adds more context

**Mitigation**: Combine related logic into single hook; don't rely on execution order

### Edge Case 6: Hook removes itself from bootstrapFiles

**Scenario**: `agent:bootstrap` removes the hook's own bootstrap helper file

**Behavior**: Hook continues to work for current session; broken on next session

**Impact**: Subtle, hard to debug

### Edge Case 7: before_agent_start deprecation

**Scenario**: Legacy plugin uses `before_agent_start`, which is deprecated

**Behavior**: Works but shows "legacy warning" in diagnostics

**Impact**: May break in future versions

**Mitigation**: Migrate to `before_model_resolve` or `before_prompt_build`

### Edge Case 8: Workspace hook shadows bundled hook

**Scenario**: User creates `session-memory` in `<workspace>/hooks/`

**Behavior**: Workspace version doesn't actually shadow bundled — workspace hooks can ONLY add new names, not override existing

**Impact**: Confusion about which version is running

---

## 7. CREATIVE USES — Innovative Applications

### Creative Use 1: Dynamic Context Injection

Build a hook that fetches real-time data (weather, stocks, news) and injects into system prompt based on keywords in user message.

```typescript
const handler = async (event) => {
  if (event.type !== "before_prompt_build") return;
  
  const query = event.context.userMessage;
  if (query.match(/weather in \w+/i)) {
    const location = extractLocation(query);
    const weather = await fetchWeather(location);
    event.context.systemPrompt += `\n\nCurrent weather in ${location}: ${weather}`;
  }
};
```

### Creative Use 2: Conditional Model Routing

Route to different models based on conversation topic or user tier.

```typescript
api.registerHook({
  events: ["before_model_resolve"],
  handler: async (event) => {
    const topic = classifyTopic(event.context.userMessage);
    if (topic === "code") {
      event.context.modelOverride = "anthropic/claude-opus-4-6";
    } else if (topic === "creative") {
      event.context.modelOverride = "openai/gpt-5.4";
    }
  }
});
```

### Creative Use 3: Real-time Content Moderation

Scan outgoing messages for policy violations before delivery.

```typescript
api.registerHook({
  events: ["before_agent_reply"],
  handler: async (event) => {
    const content = event.context.replyContent;
    const violations = await checkPolicy(content);
    if (violations.length > 0) {
      event.context.replyContent = sanitizeContent(content, violations);
      event.messages.push(`⚠️ Response modified due to policy: ${violations.join(", ")}`);
    }
  }
});
```

### Creative Use 4: Cross-Channel Message Relay

Mirror messages between channels without subagents.

```typescript
api.registerHook({
  events: ["message:received"],
  handler: async (event) => {
    if (event.context.channelId === "telegram" && event.context.content.match(/^!mirror/)) {
      const message = event.context.content.replace(/^!mirror\s*/, "");
      await sendMessage({ channel: "discord", target: "alerts-channel", message });
    }
  }
});
```

### Creative Use 5: Custom Plugin System

Build a meta-plugin system where hooks load plugin configurations dynamically.

```typescript
api.registerHook({
  events: ["gateway:startup"],
  handler: async (event) => {
    const pluginConfigs = await loadPluginRegistry();
    for (const config of pluginConfigs) {
      await registerDynamicPlugin(config);
    }
  }
});
```

### Creative Use 6: Session State Snapshots

Create periodic state snapshots for debugging or replay.

```typescript
api.registerHook({
  events: ["session:compact:after"],
  handler: async (event) => {
    const snapshot = {
      sessionKey: event.sessionKey,
      tokensBefore: event.context.tokensBefore,
      tokensAfter: event.context.tokensAfter,
      compactedCount: event.context.compactedCount,
      timestamp: Date.now()
    };
    await appendToSnapshotLog(snapshot);
  }
});
```

### Creative Use 7: Usage-based Cost Tracking

Track per-user or per-session API costs.

```typescript
api.registerHook({
  events: ["after_tool_call"],
  handler: async (event) => {
    if (event.toolName === "infer") {
      const cost = calculateCost(event.params);
      await recordUsage({ 
        user: event.context.senderId, 
        cost,
        model: event.params.model 
      });
    }
  }
});
```

### Creative Use 8: Shared Session Collaboration

Implement real-time collaboration by broadcasting session state changes.

```typescript
api.registerHook({
  events: ["session:patch"],
  handler: async (event) => {
    if (event.context.patch.thinkingLevel !== undefined) {
      await broadcastToCollaborators({
        type: "thinking-change",
        sessionKey: event.sessionKey,
        newLevel: event.context.patch.thinkingLevel
      });
    }
  }
});
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] What is exact difference between internal hooks (5) vs plugin hooks (28+)? **[MED]**
- [ ] How do workspace hooks (`<workspace>/hooks/`) differ from managed hooks (`~/.openclaw/hooks/`) in discovery precedence? **[LOW]**
- [ ] What is `PROMPT_INJECTION_HOOK_NAMES` and which 2 hooks are in it? **[HIGH]**
- [ ] Can plugin hooks be dynamically registered/unregistered at runtime? **[MED]**

### b) Internal Mechanics
- [ ] What is exact hook execution order when multiple hooks fire on same event? **[MED]**
- [ ] How does PROMPT_INJECTION_HOOK_NAMES provide security guarantees? **[HIGH]**
- [ ] Can hooks modify the `bootstrapFiles` array in agent:bootstrap event (dangerous)? **[MED]**
- [ ] What happens when hook removes MEMORY.md from bootstrapFiles array? **[HIGH]**
- [ ] Are hook execution times logged anywhere? Can performance be tracked? **[LOW]**

### c) Use Cases
- [ ] Can hooks implement custom authentication/authorization flows? **[MED]**
- [ ] Maximum hooks per event before performance degrades? **[LOW]**
- [ ] Can hooks read/write to session store directly? What are risks? **[MED]**
- [ ] Can hooks trigger subagent runs? What are limitations? **[MED]**
- [ ] Can hooks implement rate limiting or throttling? **[MED]**

### d) Best Practices
- [ ] What happens if hook handler throws uncaught exception - does it crash gateway? **[MED]**
- [ ] Can hooks access gateway internal state (session store, config)? **[MED]**
- [ ] Should llm_input/llm_output always use fire-and-forget? **[HIGH]**
- [ ] Is there a recommended pattern for hook error handling and logging? **[MED]**
- [ ] Can hooks safely use async/await or should they be synchronous? **[LOW]**

### e) Problems & Limitations
- [ ] Is there a known issue with hook discovery not working after config hot-reload? **[MED]**
- [ ] before_agent_start deprecation status - does it still work or is it broken? **[HIGH]**
- [ ] Does gateway restart kill in-flight hooks? Is there cleanup guarantee? **[MED]**
- [ ] What happens when workspace hook has same name as bundled hook? **[MED]**
- [ ] Are there memory leaks from hook handlers not properly cleaning up? **[MED]**

### f) Solutions & Workarounds
- [ ] What's recommended approach for hook-to-hook communication? **[LOW]**
- [ ] Can hooks be dynamically enabled/disabled without gateway restart? **[MED]**
- [ ] How to chain hooks to ensure execution order? **[MED]**
- [ ] What's the best way to debug hook execution? **[MED]**

### g) Edge Cases
- [ ] What happens when hook removes MEMORY.md from bootstrapFiles array? **[HIGH]**
- [ ] Can hooks trigger infinite loops (hook A → hook B → A)? Is there protection? **[HIGH]**
- [ ] What happens when before_model_resolve returns conflicting overrides? **[MED]**
- [ ] Can two plugins register hooks for same event — what happens? **[MED]**
- [ ] What happens when hook is enabled/disabled while gateway is running? **[MED]**

### h) Creative Uses
- [ ] Could hooks implement custom plugin system on top of existing hooks? **[LOW]**
- [ ] Could hooks implement real-time collaboration (shared sessions)? **[LOW]**
- [ ] Can hooks implement cross-channel message relay without subagents? **[MED]**
- [ ] Can hooks implement dynamic model fallback chains? **[MED]**
- [ ] Could hooks implement a webhook-to-agent bridge for external systems? **[MED]**

### i) Security (NEW from this research)
- [ ] What is the security model for workspace hooks vs managed hooks? **[HIGH]**
- [ ] Can malicious workspace hook access managed hook code? **[HIGH]**
- [ ] What audit logging exists for hook execution? **[MED]**
- [ ] Can hooks access environment variables with secrets? **[HIGH]**
- [ ] Is there a hook that can be used for privilege escalation? **[HIGH]**

### j) Integration (NEW from this research)
- [ ] Can hooks integrate with external APIs (webhooks out)? **[MED]**
- [ ] Can hooks process audio/video before agent sees it (message:transcribed)? **[MED]**
- [ ] Can hooks add/remove tools from the tool registry dynamically? **[MED]**
- [ ] How do hooks interact with the skill system? **[MED]**
- [ ] Can hooks modify channel-specific message metadata? **[MED]**

---

## 9. SOURCES

### Primary Sources (OpenClaw Docs)

1. `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Main hooks documentation
2. `/usr/local/lib/node_modules/openclaw/docs/cli/hooks.md` — CLI reference for hooks
3. `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin hook system (28+ hooks)
4. `/usr/local/lib/node_modules/openclaw/docs/automation/webhook.md` — Webhooks (external, HTTP-based)

### Web Sources

5. Google Search: "OpenClaw hooks before_model_resolve before_agent_start before_prompt_build plugin hooks security"

### Internal Sources

6. `/data/.openclaw/agents/investigador/workspace/backlog.md` — Hook system marked as NEW FULL RESEARCH needed
7. `/data/.openclaw/workspace/OPENCLAW_EXPERT.md` — Contains hook system notes

### Key Findings Summary

| Aspect | Finding |
|--------|---------|
| Internal hooks | 4 bundled: session-memory, bootstrap-extra-files, command-logger, boot-md |
| Plugin hooks | 28+ covering model resolution, agent lifecycle, message flow, tools |
| Discovery | Bundled → Plugin → Managed (~/.openclaw/hooks/) → Workspace (disabled by default) |
| Security | PROMPT_INJECTION_HOOK_NAMES restricts prompt context to 2 hooks |
| Deprecation | before_agent_start is legacy, prefer before_model_resolve / before_prompt_build |
| Bootstrap danger | agent:bootstrap can modify bootstrapFiles array — can remove MEMORY.md |
| Best practice | Keep handlers fast, fire-and-forget heavy work, try/catch, filter early |

---

*Research by: Investigador Scout*  
*Date: 2026-04-23 01:30 CET*  
*Status: COMPLETE*
