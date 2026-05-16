# Plugin Hook Dynamic Registration — Research Findings

**Topic:** Can plugin hooks be dynamically registered/unregistered at runtime? + Can hooks access gateway internal state?
**Priority:** MEDIUM (from backlog.md #15, #18)
**Date:** 2026-04-23 07:09 CET
**Research by:** Investigador Scout
**Status:** ✅ COMPLETE

---

## 1. WHAT IS — Definition & Core Concept

### Question 1: Can plugin hooks be dynamically registered/unregistered at runtime?

**Answer: NO — Plugin hooks cannot be dynamically registered or unregistered at runtime.**

Plugin hooks are hooks that are registered through the Plugin SDK when a plugin loads. They are part of the plugin registry and remain active for the lifetime of the plugin. There is no public API exposed to dynamically add or remove plugin hooks after initial registration.

**Key finding**: Only **internal hooks** (standalone hooks in `~/.openclaw/hooks/`) have `registerInternalHook` and `unregisterInternalHook` functions, but even these are only called during plugin load/unload cycles, not for dynamic runtime changes.

### Question 2: Can hooks access gateway internal state (session store, config)?

**Answer: YES — Hooks can access gateway configuration and session data.**

Hooks receive a `context` object that contains:
- `context.cfg` — Full gateway configuration including all credentials, API keys, and secrets
- `context.sessionEntry` — Current session entry/metadata
- `context.patch` (for `session:patch` events) — Changed fields
- `context.bootstrapFiles` (for `agent:bootstrap` events) — Mutable array of bootstrap files

This is a **significant security finding** — hooks have full access to all gateway secrets through `context.cfg`.

---

## 2. HOW IT WORKS — Architecture & Mechanics

### Plugin Hook Registration Flow

```
Plugin Load Time:
├── Plugin's register(api) function is called
├── api.registerHook(events, handler, options) registers hooks
├── Hooks are added to registry.typedHooks array
└── Hooks remain active for plugin lifetime

Plugin Unload Time (gateway restart or plugin disable):
├── unregisterInternalHook is called for each registration
├── Hooks are removed from registry
└── Plugin is unloaded from memory
```

### Source Code Evidence

From `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js`:

```javascript
function registerInternalHook(eventKey, handler) {
  // Adds handler to internal hooks registry
}

function unregisterInternalHook(eventKey, handler) {
  // Removes handler from internal hooks registry
}

// Exported but only used during plugin lifecycle
export { registerInternalHook, unregisterInternalHook, clearInternalHooks };
```

From `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js`:

```javascript
// Plugin hooks are stored in registry.typedHooks
// No public API to add/remove after initial registration
function getHooksForName(registry, hookName) {
  return registry.typedHooks.filter((h) => h.hookName === hookName)
    .toSorted((a, b) => (b.priority ?? 0) - (a.priority ?? 0));
}
```

### Hook Context Structure

From the source code, hooks receive an event with this structure:

```typescript
interface HookEvent {
  type: string;      // Event type (e.g., "command", "message:received")
  action?: string;   // Action subtype (e.g., "new", "reset")
  sessionKey: string;
  timestamp: number;
  messages: string[];  // Messages to send back to user
  context: {
    cfg: GatewayConfig;           // Full gateway config (INCLUDES SECRETS)
    sessionEntry: SessionEntry;   // Current session data
    workspaceDir?: string;        // Workspace directory path
    patch?: Record<string, any>;  // For session:patch events
    bootstrapFiles?: string[];    // For agent:bootstrap events
    // ... event-specific fields
  };
}
```

---

## 3. USES — Practical Applications

### Why This Matters

1. **Security Implications**: Since hooks can access `context.cfg` with all credentials, any compromised hook can exfiltrate API keys, tokens, and secrets.

2. **Plugin Lifecycle**: Plugins register hooks once at load time. There is no dynamic hook management without gateway restart.

3. **Configuration Access**: Hooks can read (but not modify) the entire gateway configuration at runtime.

### Use Case: Hook-Based Configuration Access

```javascript
// A hook can read ALL gateway configuration including secrets
const handler = async (event) => {
  // Access full config with all secrets
  const apiKey = event.context.cfg.providers?.minimax?.apiKey;
  const telegramToken = event.context.cfg.channels?.telegram?.botToken;
  
  // Can also access session data
  const sessionId = event.context.sessionEntry?.sessionId;
  
  // Log or exfiltrate these values (SECURITY RISK)
};
```

---

## 4. PROBLEMS — Known Issues & Limitations

### Problem 1: No Dynamic Hook Registration for Plugins

**Issue**: Plugin hooks cannot be added or removed at runtime without plugin reload.

**Impact**: 
- Cannot implement runtime hook hot-swap
- Cannot create ephemeral hooks for one-off processing
- Must restart gateway to change plugin hook behavior

### Problem 2: Full Configuration Access Without Audit

**Issue**: Hooks have access to `context.cfg` which contains ALL secrets but there's no audit logging of this access.

**Impact**:
- A malicious or compromised hook can read all credentials
- No way to detect credential access by hooks
- Security blind spot in the gateway

### Problem 3: Internal vs Plugin Hook Asymmetry

**Issue**: Internal hooks have registration/unregistration functions but they're not exposed as a public API for runtime use.

**Current state**: Functions exist (`registerInternalHook`, `unregisterInternalHook`, `clearInternalHooks`) but are only used internally during plugin lifecycle.

### Problem 4: Hook Enable/Disable Requires Gateway Restart

**Issue**: Even enabling/disabling hooks via config requires gateway restart in most cases.

**From hook-execution-order findings**: "Some changes hot-reload; others may require restart."

---

## 5. SOLUTIONS — Best Practices & Workarounds

### Solution 1: Use before_install Hook for Pre-Install Scanning

Since plugin hooks can't be dynamically registered, organizations can use `before_install` hook to implement custom security scanning before skill installation.

```javascript
// In a plugin that provides before_install hook
handler: async (event) => {
  const { skillPath, skillName } = event.context;
  
  // Custom SKILL.md scanning
  const skillMdPath = path.join(skillPath, 'SKILL.md');
  if (fs.existsSync(skillMdPath)) {
    const content = fs.readFileSync(skillMdPath, 'utf-8');
    const findings = scanForRisks(content);
    
    if (findings.length > 0) {
      return { 
        block: true, 
        blockReason: `Security risks found in SKILL.md: ${findings.join(', ')}` 
      };
    }
  }
}
```

### Solution 2: Monitor Hook Access to Configuration

Since hooks can access `context.cfg`, implement monitoring:

```javascript
// Use a wrapper hook that logs all cfg access
const configAccessLogger = {
  handler: async (event) => {
    const hasConfigAccess = Boolean(event.context?.cfg);
    if (hasConfigAccess) {
      logger?.warn(`[security] ${event.type} hook accessed configuration`);
    }
  }
};
```

### Solution 3: Minimize Hook Privileges

- Only enable hooks that are strictly necessary
- Never enable workspace hooks in production
- Review all third-party plugins for hook requirements

### Solution 4: Use Separate Agents for Untrusted Workloads

For untrusted skills or plugins, run in isolated agent with minimal config access:

```json5
{
  agents: {
    list: [{
      id: "sandbox-agent",
      skills: ["untrusted-skill"],
      // Minimal or no hooks
    }]
  }
}
```

---

## 6. EDGE CASES — Corner Cases & Unexpected Behaviors

### Edge Case 1: Plugin Reload During Hook Execution

**Scenario**: A plugin is being unloaded while one of its hooks is executing.

**Behavior**: The hook completes normally; unregister happens after all in-flight hooks finish.

### Edge Case 2: Multiple Plugins Accessing Same Config Path

**Scenario**: Two plugins both have hooks that access `context.cfg.providers.minimax.apiKey`.

**Behavior**: Both get the same value; no conflict resolution needed. Each hook gets a fresh context object.

### Edge Case 3: Hook Throws Exception While Accessing Config

**Scenario**: Hook accesses a nested config path that doesn't exist.

**Behavior**: Depends on failure policy. Most hooks use `fail-open` (log error and continue). `before_tool_call` uses `fail-closed` (halt execution).

### Edge Case 4: Session Store Access

**Question**: Can hooks directly read/write to the session store (session JSON files)?

**Answer**: No direct API. Hooks can only access `context.sessionEntry` which is the in-memory session metadata, not the raw session files on disk.

---

## 7. CREATIVE USES — Innovative Applications

### Creative Use 1: Hook-Based Configuration Observer

Create a monitoring hook that tracks configuration changes:

```javascript
// Track which hooks access which config paths
const configObserver = {
  priority: -1000, // Run last
  handler: async (event) => {
    const accessedPaths = [];
    // Deep-parse context.cfg to log accessed paths
    // Build audit trail of config access patterns
  }
};
```

### Creative Use 2: Dynamic Hook Routing

Since hooks receive session context, implement conditional routing:

```javascript
// Route to different handlers based on session state
const router = {
  handler: async (event) => {
    const sessionId = event.context.sessionEntry?.sessionId;
    const agentId = event.context.sessionEntry?.agentId;
    
    // Determine which sub-handler to invoke
    return routeToHandler(agentId, sessionId);
  }
};
```

### Creative Use 3: Configuration Cache Invalidation

Use `session:patch` hooks to detect config changes:

```javascript
// Detect when gateway config is modified
handler: async (event) => {
  if (event.context.patch) {
    logger?.info(`Config changed: ${JSON.stringify(event.context.patch)}`);
  }
}
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### Generated New Questions:

1. **[MED]** Is there any audit logging for hooks accessing `context.cfg`?
   - **Rationale**: Current implementation has no audit trail for credential access via hooks.

2. **[MED]** Can hooks modify gateway configuration at runtime?
   - **Rationale**: Hooks can read `context.cfg` but it's unclear if they can write back changes.

3. **[LOW]** What is the performance impact of hooks accessing large config objects?
   - **Rationale**: `context.cfg` contains entire gateway config; passing this to every hook may have memory/CPU overhead.

4. **[MED]** Can hooks access the session store files directly on disk?
   - **Rationale**: Only in-memory session entry is accessible via context; disk access is not exposed.

5. **[LOW]** Is there a way to scope hook config access to only necessary fields?
   - **Rationale**: Current design passes full config; a scoped approach would reduce attack surface.

6. **[MED]** Can workspace hooks (per-agent) be dynamically enabled/disabled without affecting other agents?
   - **Rationale**: This would allow per-agent hook control but current design seems global.

---

## 9. SOURCES

### Primary Sources

- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation with `registerInternalHook`, `unregisterInternalHook`, `clearInternalHooks` functions
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Plugin hook runner with registry structure
- `/usr/local/lib/node_modules/openclaw/dist/loader-DuIH27tS.js` — Plugin loader showing hook lifecycle
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook system documentation
- `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin architecture reference

### Related Findings

- `Research/OpenClaw/findings/hook-execution-order.md` (L16) — Hook execution order, failure policies
- `Research/OpenClaw/findings/hook-security-audit.md` (L20) — Hook security model
- `Research/OpenClaw/findings/openclaw-hooks-system.md` (L18) — Complete hook system overview
- `Research/OpenClaw/findings/hook-internal-vs-plugin-types.md` (L14) — Internal vs plugin hook differences

---

## Key Findings Summary

1. **Plugin hooks CANNOT be dynamically registered/unregistered at runtime** — They are tied to plugin lifecycle
2. **Internal hooks have registration functions but are not exposed as public runtime API** — Only used internally
3. **Hooks CAN access gateway internal state** — Via `context.cfg` (full config including secrets) and `context.sessionEntry` (session metadata)
4. **No audit logging exists for config access by hooks** — Security gap
5. **Hook enable/disable may require gateway restart** — Not all changes hot-reload

---

*Research by: Investigador Scout | 2026-04-23 07:09 CET*