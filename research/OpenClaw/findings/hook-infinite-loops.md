# Hook Infinite Loops — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23  
**Topic:** Can hooks trigger infinite loops? Is there protection?  
**Priority:** HIGH (from backlog.md #1)  
**Research Depth:** 6-Layer Exhaustive  

---

## TABLE OF CONTENTS
1. [What Is — Definition & Core Concept](#1-what-is--definition--core-concept)
2. [How It Works — Loop Mechanics](#2-how-it-works--loop-mechanics)
3. [Uses — Legitimate Chain Patterns](#3-uses--legitimate-chain-patterns)
4. [Problems — Infinite Loop Vulnerabilities](#4-problems--infinite-loop-vulnerabilities)
5. [Solutions — Prevention & Detection](#5-solutions--prevention--detection)
6. [Edge Cases — Unusual Loop Scenarios](#6-edge-cases--unusual-loop-scenarios)
7. [Creative Uses — Loop-Based Patterns](#7-creative-uses--loop-based-patterns)
8. [NEW Questions Opened by This Research](#8-new-questions-opened-by-this-research)
9. [Sources](#9-sources)

---

## 1. WHAT IS — Definition & Core Concept

### Definition

**Hook Infinite Loops** occur when two or more hooks trigger each other in a circular chain, causing repeated event firing that never terminates naturally. This is a class of **re-entrant event hazards** where hook A triggers hook B, which triggers hook A again, creating an unbounded execution cycle.

### Two Types of Hook Systems

OpenClaw has **TWO separate hook systems** with different loop risks:

| System | Count | Loop Risk | Loop Mechanism |
|--------|-------|-----------|----------------|
| **Internal Hooks** | 4 bundled | LOW | Standalone hooks, fire on lifecycle events |
| **Plugin Hooks** | 28+ | MEDIUM-HIGH | Deep integration into agent loop, model resolution, message flow |

### Core Loop Question

**Can hook A trigger hook B, which triggers hook A again?**

**Answer: YES — There is NO built-in protection against infinite hook loops in either system.**

---

## 2. HOW IT WORKS — Loop Mechanics

### Hook Discovery Order (Precedence)

Hooks are discovered in order of **increasing override precedence**:

1. **Bundled hooks** — shipped with OpenClaw (highest trust)
2. **Plugin hooks** — bundled inside installed plugins
3. **Managed hooks** — `~/.openclaw/hooks/` (user-installed, shared across workspaces)
4. **Workspace hooks** — `<workspace>/hooks/` (per-agent, **disabled by default**)

**Key rule**: Workspace hooks can **ADD** new hook names but **CANNOT override** bundled, managed, or plugin-provided hooks with the same name.

### Event Types That Can Create Loops

Internal hooks fire on these events:

| Event | Can Trigger Loop? | Mechanism |
|-------|-------------------|-----------|
| `command:new`, `command:reset` | LOW | Manual commands only |
| `session:compact:before/after` | **HIGH** | Auto-fires during compaction cycle |
| `session:patch` | **HIGH** | Can be triggered by session changes mid-turn |
| `agent:bootstrap` | MEDIUM | Bootstrap files can be modified |
| `gateway:startup` | LOW | One-time event at startup |
| `message:received` | **HIGH** | Messages can trigger session changes |
| `message:preprocessed` | **HIGH** | Modifies body before agent sees it |
| `message:sent` | MEDIUM | Can trigger response messages |
| `message:transcribed` | MEDIUM | Audio transcription completes |

### Hook Execution Order

From docs, internal hooks run in **insertion order** with no depth limit, no recursion counter, and no circuit breaker.

### Plugin Hook Chain (28+ hooks)

Plugin hooks cover model resolution lifecycle. Key chain points:

1. `before_model_resolve` → can set `modelOverride`
2. `normalizeModelId` → can modify model selection
3. `resolveDynamicModel` → async warm-up
4. `before_agent_start` (DEPRECATED) → prompt injection context
5. `before_prompt_build` → inject context into prompt
6. `before_tool_call` → intercept tool execution
7. `after_tool_call` → post-process results
8. `session:patch` → session state modification

### HOW LOOP FORMS: The Event Cascade

```
User sends message
    ↓
message:received fires
    ↓
Hook A modifies session state (via session:patch or direct mutation)
    ↓
session:patch fires
    ↓
Hook B sees modification, fires action
    ↓
Action triggers message:received again
    ↓
→ INFINITE LOOP ←
```

### Realistic Loop Scenario 1: Message → Session Patch → Message

```
Hook A (message:preprocessed) → adds context to body → triggers session enrichment
Hook B (session:patch) → sees enrichment → sends notification message
Hook C (message:sent) → sees notification → enriches context again
→ Loop back to Hook A
```

### Realistic Loop Scenario 2: Compaction Cycle

```
session:compact:before fires
    ↓
Hook A saves state → triggers session:patch
    ↓
session:compact:after fires
    ↓
Hook B restores state → triggers compaction again
    ↓
→ Loop until token limit or crash
```

### Realistic Loop Scenario 3: Tool Call → Session Change → Tool Call

```
before_tool_call fires for "exec" tool
    ↓
Hook validates command, adds metadata to session
    ↓
session:patch fires
    ↓
Hook sees patch, logs to external system
    ↓
External system sends webhook to OpenClaw
    ↓
message:received fires
    ↓
Agent responds, calls exec again
    ↓
→ Loop
```

---

## 3. USES — Legitimate Chain Patterns

### Legitimate Pattern 1: Error Recovery Chain

```typescript
// Hook A: Detects error, sets recovery flag
api.registerHook({
  id: "error-detector",
  events: ["after_tool_call"],
  handler: async (event) => {
    if (event.result.error) {
      event.context.sessionEntry.metadata.needsRecovery = true;
    }
  }
});

// Hook B: Sees recovery flag, triggers reset
api.registerHook({
  id: "recovery-trigger",
  events: ["session:patch"],
  handler: async (event) => {
    if (event.context.patch.metadata?.needsRecovery) {
      // Trigger legitimate recovery flow, NOT loop
      await triggerRecovery(event.sessionKey);
    }
  }
});
```

**Risk**: If recovery triggers same condition, loops

### Legitimate Pattern 2: State Synchronization

```typescript
// Hook A: Sync state to external system
api.registerHook({
  id: "state-syncer",
  events: ["session:patch"],
  handler: async (event) => {
    await syncToExternal(event.context.sessionEntry);
  }
});

// Hook B: Receive external webhook, update session
api.registerHook({
  id: "webhook-handler",
  events: ["message:received"],
  handler: async (event) => {
    if (isWebhookMessage(event)) {
      await updateSessionFromWebhook(event);
    }
  }
});
```

**Risk**: External system echoing webhooks creates loop

### Legitimate Pattern 3: Compaction State Preservation

```typescript
// Hook A: Save state before compaction
api.registerHook({
  id: "compaction-saver",
  events: ["session:compact:before"],
  handler: async (event) => {
    await saveState(event.context.messageCount);
  }
});

// Hook B: Restore state after compaction
api.registerHook({
  id: "compaction-restorer",
  events: ["session:compact:after"],
  handler: async (event) => {
    await restoreState();
  }
});
```

**Risk**: If restoration triggers compaction again, infinite loop

---

## 4. PROBLEMS — Infinite Loop Vulnerabilities

### Problem 1: NO Built-in Recursion Protection

**Confirmed**: OpenClaw has **NO**:
- Depth counter for nested hook invocations
- Recursion limit / circuit breaker
- Loop detection mechanism
- Timeout per hook chain

**Impact**: Any hook chain that creates circular event flow will run until:
- Gateway crashes (OOM, stack overflow)
- Process is killed externally
- Token limit hit during compaction
- System resources exhausted

### Problem 2: No Hook Execution Order Guarantee

**From docs**: "Hook execution order is not guaranteed for multiple hooks on same event"

**Impact**: Loop may or may not manifest depending on insertion order. Non-deterministic behavior makes loops hard to reproduce.

### Problem 3: session:patch Is a Loop Multiplier

The `session:patch` event fires when session properties are modified. If a hook on `session:patch` modifies the session again, it fires `session:patch` again → **direct recursion**.

```typescript
// DANGEROUS: Direct recursion via session:patch
api.registerHook({
  id: "self-modifying-patch",
  events: ["session:patch"],
  handler: async (event) => {
    // Modifying session here triggers session:patch AGAIN
    event.context.sessionEntry.metadata.visitCount++;
  }
});
```

### Problem 4: message:preprocessed → message Loop

The `message:preprocessed` hook can enrich `bodyForAgent`. If this enrichment triggers any action that sends a message, the cycle repeats:

```
message:preprocessed → enriches body → agent responds → message:sent → message:received → loop
```

### Problem 5: Compaction Cycles

Compaction (`session:compact:before` → compact → `session:compact:after`) is an auto-triggered cycle. Hooks that:
- Trigger session modifications during compaction
- Cause session state changes that hit compaction thresholds

...create infinite compaction loops.

### Problem 6: External System Echo

If hooks integrate with external systems that send messages back to OpenClaw:
1. Hook sends data to external system
2. External system sends webhook/HTTP trigger
3. `message:received` fires
4. Hook responds → sends to external system again
5. **Loop**

### Problem 7: before_agent_start (DEPRECATED) Loop Risk

`before_agent_start` is deprecated but still functional and in `PROMPT_INJECTION_HOOK_NAMES`. Plugins using this hook in circular ways:

```typescript
// Legacy plugin pattern - creates loop potential
api.registerHook({
  id: "legacy-redirect",
  events: ["before_agent_start"],
  handler: async (event) => {
    // Redirect causes re-evaluation
    event.context.providerOverride = "other";
  }
});
```

### Problem 8: No Hook-to-Hook Isolation

**From Extension Security Model**: No isolation between hooks. A compromised hook can:
- Modify other hooks' behavior
- Disable other hooks
- Access other hooks' data

**Loop Impact**: If Hook A can modify Hook B's registration, it can make Hook B trigger the same event again.

---

## 5. SOLUTIONS — Prevention & Detection

### Solution 1: Guard Counter Pattern (Manual)

```typescript
const HOOK_CALL_LIMIT = 100;
let hookCallCount = 0;

api.registerHook({
  id: "safe-handler",
  events: ["session:patch"],
  handler: async (event) => {
    hookCallCount++;
    if (hookCallCount > HOOK_CALL_LIMIT) {
      console.error("[safe-handler] Hook call limit exceeded");
      return;
    }
    
    try {
      // Your logic here
      await processSessionPatch(event);
    } finally {
      // Decrement when complete to allow next session
      hookCallCount--;
    }
  }
});
```

**Limitation**: Global counter persists across events; resets only on gateway restart

### Solution 2: Session-Level Guard

```typescript
api.registerHook({
  id: "session-guarded-handler",
  events: ["session:patch"],
  handler: async (event) => {
    const session = event.context.sessionEntry;
    
    // Initialize guard counter if not present
    if (!session.metadata._hookCallCount) {
      session.metadata._hookCallCount = {};
    }
    
    const id = "session-patch-handler";
    session.metadata._hookCallCount[id] = 
      (session.metadata._hookCallCount[id] || 0) + 1;
    
    if (session.metadata._hookCallCount[id] > 10) {
      console.error(`[${id}] Session call limit exceeded`);
      return;
    }
    
    // Your logic here
  }
});
```

**Better**: Uses session-scoped counter that resets on `/new` or `/reset`

### Solution 3: Event-Type Guard

```typescript
const recentEvents = new Map();
const EVENT_WINDOW_MS = 1000;
const MAX_SAME_EVENT = 5;

api.registerHook({
  id: "rate-guarded-handler",
  events: ["session:patch"],
  handler: async (event) => {
    const key = `${event.sessionKey}:${event.type}:${event.action}`;
    const now = Date.now();
    
    // Clean old entries
    for (const [k, t] of recentEvents) {
      if (now - t > EVENT_WINDOW_MS) recentEvents.delete(k);
    }
    
    // Check rate
    const count = (recentEvents.get(key) || 0);
    if (count > MAX_SAME_EVENT) {
      console.error(`[rate-guarded] Rate limit exceeded for ${key}`);
      return;
    }
    
    recentEvents.set(key, count + 1);
    
    // Your logic here
  }
});
```

### Solution 4: Circuit Breaker Pattern

```typescript
class HookCircuitBreaker {
  private failures = new Map();
  private readonly FAILURE_THRESHOLD = 5;
  private readonly RESET_TIMEOUT_MS = 60000;
  
  isOpen(hookId: string): boolean {
    const failure = this.failures.get(hookId);
    if (!failure) return false;
    
    if (Date.now() - failure.timestamp > this.RESET_TIMEOUT_MS) {
      this.failures.delete(hookId);
      return false;
    }
    
    return failure.count >= this.FAILURE_THRESHOLD;
  }
  
  recordFailure(hookId: string) {
    const existing = this.failures.get(hookId) || { count: 0, timestamp: Date.now() };
    this.failures.set(hookId, { count: existing.count + 1, timestamp: Date.now() });
  }
  
  recordSuccess(hookId: string) {
    this.failures.delete(hookId);
  }
}

const breaker = new HookCircuitBreaker();

api.registerHook({
  id: "circuit-broken-handler",
  events: ["session:patch"],
  handler: async (event) => {
    if (breaker.isOpen("session-patch-handler")) {
      console.warn("[circuit-broken] Circuit open, skipping");
      return;
    }
    
    try {
      await processSessionPatch(event);
      breaker.recordSuccess("session-patch-handler");
    } catch (err) {
      breaker.recordFailure("session-patch-handler");
      throw err;
    }
  }
});
```

### Solution 5: Disable Loop-Prone Events

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

**Limitation**: Doesn't apply to plugin hooks

### Solution 6: External System Loop Prevention

```typescript
api.registerHook({
  id: "webhook-handler",
  events: ["message:received"],
  handler: async (event) => {
    // Verify webhook signature
    if (!verifyWebhookSignature(event)) {
      return; // Reject unknown webhooks
    }
    
    // Tag message to prevent echo
    event.context.metadata.loopPrevention = {
      originHook: "webhook-handler",
      timestamp: Date.now()
    };
    
    await processWebhook(event);
  }
});

api.registerHook({
  id: "notification-sender",
  events: ["session:patch"],
  handler: async (event) => {
    // Don't send if message came from webhook (prevent echo)
    if (event.context.sessionEntry.metadata.loopPrevention?.originHook === "webhook-handler") {
      return;
    }
    
    await sendExternalNotification(event);
  }
});
```

### Solution 7: Monitor with Alerting

```typescript
let hookExecutionLog = [];

api.registerHook({
  id: "loop-monitor",
  events: ["*"],  // Monitor all events
  handler: async (event) => {
    const entry = {
      type: event.type,
      action: event.action,
      sessionKey: event.sessionKey,
      timestamp: Date.now()
    };
    
    hookExecutionLog.push(entry);
    
    // Keep only recent entries
    if (hookExecutionLog.length > 1000) {
      hookExecutionLog.shift();
    }
    
    // Detect rapid succession of same event type
    const recent = hookExecutionLog.filter(e => 
      e.type === event.type && 
      e.action === event.action &&
      e.sessionKey === event.sessionKey &&
      Date.now() - e.timestamp < 1000
    );
    
    if (recent.length > 20) {
      await alertSecurityTeam({
        type: "potential-hook-loop",
        eventType: event.type,
        sessionKey: event.sessionKey,
        count: recent.length
      });
    }
  }
});
```

---

## 6. EDGE CASES — Unusual Loop Scenarios

### Edge Case 1: Compaction Loop (Session OOM)

```typescript
// Hook triggers compaction
api.registerHook({
  id: "aggressive-compaction",
  events: ["session:patch"],
  handler: async (event) => {
    if (event.context.sessionEntry.messages.length > 50) {
      // This triggers compaction which fires session:compact:before/after
      // Which might trigger another session:patch
      await forceCompact(event.sessionKey);
    }
  }
});

// Compaction hook also modifies session
api.registerHook({
  id: "compaction-modifier",
  events: ["session:compact:after"],
  handler: async (event) => {
    event.context.sessionEntry.metadata.lastCompact = Date.now();
  }
});

// session:patch fires again from compaction-modifier
// → Loop: session:patch → forceCompact → session:compact:before/after → session:patch
```

### Edge Case 2: Cross-Plugin Loop

```typescript
// Plugin A
api.registerHook({
  id: "plugin-a-handler",
  events: ["session:patch"],
  handler: async (event) => {
    // Calls into Plugin B's registered tool
    await callPluginBTool(event);
  }
});

// Plugin B's tool triggers session modification
async function callPluginBTool(event) {
  event.context.sessionEntry.metadata.calledBy = "plugin-a";
  // This triggers session:patch again → Plugin A handler → Plugin B tool → Loop
}
```

### Edge Case 3: Before Agent Start Loop (Deprecated)

```typescript
// DEPRECATED but still functional
api.registerHook({
  id: "legacy-loop",
  events: ["before_agent_start"],
  handler: async (event) => {
    // This triggers re-evaluation of agent start
    event.context.providerOverride = "alternate";
  }
});

// Another hook on before_agent_start
api.registerHook({
  id: "other-legacy",
  events: ["before_agent_start"],
  handler: async (event) => {
    // Sees override, sets another override
    if (event.context.providerOverride === "alternate") {
      event.context.providerOverride = "original";
    }
  }
});
// → Loop: alternate → original → alternate → original
```

### Edge Case 4: Message Echo with Delay

```typescript
// Webhook causes message with delay
api.registerHook({
  id: "delayed-echo",
  events: ["message:sent"],
  handler: async (event) => {
    // Schedule delayed response (setTimeout)
    setTimeout(() => {
      // This sends a message that fires message:received
      sendDelayedMessage(event);
    }, 100);
  }
});

// message:received fires again
// Loop with delay makes it harder to detect
```

### Edge Case 5: Compaction-Safeguard Bypass

From docs: `src/agents/pi-hooks/compaction-safeguard.ts` adds guardrails to compaction. **But** if a malicious hook disables or bypasses the safeguard:

```typescript
api.registerHook({
  id: "safeguard-disabler",
  events: ["session:compact:before"],
  handler: async (event) => {
    // Attempt to disable safeguard
    event.context.metadata.disableCompactionGuard = true;
  }
});

// Safeguard checks for this flag but if hook runs after safeguard...
```

### Edge Case 6: Gateway Restart Loop

```typescript
api.registerHook({
  id: "restart-trigger",
  events: ["gateway:startup"],
  handler: async (event) => {
    // If something goes wrong during startup, trigger restart
    if (isUnhealthy()) {
      exec("openclaw gateway restart");
    }
  }
});

// Restart triggers gateway:startup again → Loop until max restart count or crash
```

### Edge Case 7: Cross-Channel Loop

```typescript
// Telegram channel hook
api.registerHook({
  id: "telegram-relay",
  events: ["message:received"],
  handler: async (event) => {
    if (event.context.channelId === "telegram") {
      // Relay to Discord
      await sendToDiscord(event.context.content);
    }
  }
});

// Discord channel hook
api.registerHook({
  id: "discord-relay",
  events: ["message:received"],
  handler: async (event) => {
    if (event.context.channelId === "discord") {
      // Relay to Telegram
      await sendToTelegram(event.context.content);
    }
  }
});

// If Discord bot sees Telegram's relay message and relays back → Loop
```

### Edge Case 8: Skills Snapshot Refresh Loop

```typescript
api.registerHook({
  id: "skill-snapshotter",
  events: ["session:compact:after"],
  handler: async (event) => {
    // Saving session might modify skills snapshot
    await saveSkillSnapshot(event.context.sessionEntry);
  }
});

// Skills watcher sees SKILL.md change, triggers snapshot refresh
// Snapshot refresh modifies session
// → session:patch fires → skill-snapshotter → Loop
```

---

## 7. CREATIVE USES — Loop-Based Patterns

### Creative Use 1: Self-Healing Session

```typescript
// Session automatically recovers from corruption
api.registerHook({
  id: "self-healer",
  events: ["session:patch"],
  handler: async (event) => {
    const session = event.context.sessionEntry;
    
    if (session.metadata.corrupted) {
      // Reset corruption flag and restore from backup
      session.metadata.corrupted = false;
      await restoreFromBackup(event.sessionKey);
    }
  }
});

// Another hook detects corruption
api.registerHook({
  id: "corruption-detector",
  events: ["before_tool_call"],
  handler: async (event) => {
    if (event.toolName === "read") {
      const content = await readFile(event.params.path);
      if (content.includes("CORRUPTED")) {
        event.context.sessionEntry.metadata.corrupted = true;
      }
    }
  }
});
```

**Limitation**: Must have corruption detection before self-healing can run

### Creative Use 2: Adaptive Rate Limiter

```typescript
// Adapts rate limit based on actual usage
api.registerHook({
  id: "adaptive-rater",
  events: ["before_tool_call"],
  handler: async (event) => {
    if (event.toolName === "exec") {
      const session = event.context.sessionEntry;
      const currentRate = session.metadata.apiRateLimit || 100;
      
      // If we're hitting rate limit, decrease
      if (event.result?.rateLimited) {
        session.metadata.apiRateLimit = Math.max(10, currentRate * 0.8);
      } else {
        // Slowly increase if we're under limit
        session.metadata.apiRateLimit = Math.min(500, currentRate * 1.1);
      }
    }
  }
});
```

### Creative Use 3: Cascading Backup

```typescript
// Cascading backup system
api.registerHook({
  id: "cascading-backup",
  events: ["session:compact:after"],
  handler: async (event) => {
    const session = event.context.sessionEntry;
    
    // Primary backup
    await backupToPrimary(event.sessionKey);
    
    // If primary succeeds, trigger secondary
    session.metadata.primaryBackupComplete = true;
  }
});

api.registerHook({
  id: "secondary-backup",
  events: ["session:patch"],
  handler: async (event) => {
    if (event.context.patch.metadata?.primaryBackupComplete) {
      await backupToSecondary(event.sessionKey);
    }
  }
});
```

### Creative Use 4: Progressive Enhancement

```typescript
// Each session patch adds more capability
api.registerHook({
  id: "progressive-enhancer",
  events: ["session:patch"],
  handler: async (event) => {
    const session = event.context.sessionEntry;
    const level = session.metadata.enhancementLevel || 0;
    
    if (level < 3) {
      session.metadata.enhancementLevel = level + 1;
      await applyEnhancement(event.sessionKey, level + 1);
    }
  }
});
```

### Creative Use 5: Chaos Engineering Monitor

```typescript
// Deliberately inject failures to test resilience
api.registerHook({
  id: "chaos-monitor",
  events: ["after_tool_call"],
  handler: async (event) => {
    // Check if chaos mode is enabled
    if (!event.context.sessionEntry.metadata.chaosMode) {
      return;
    }
    
    const chaosLevel = event.context.sessionEntry.metadata.chaosLevel || 1;
    if (Math.random() < chaosLevel * 0.1) {
      // Inject random failure
      throw new Error("Chaos injection: random failure");
    }
  }
});
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] Is there a maximum hook call depth before stack overflow? **[HIGH]**
- [ ] Can hooks trigger themselves recursively (same hook on same event)? **[MED]**
- [ ] What's the difference between internal hooks loop risk vs plugin hooks loop risk? **[MED]**

### b) Internal Mechanics
- [ ] What is exact hook execution order when multiple hooks fire on same event? **[MED]**
- [ ] Can session:patch be triggered without actual session modification? **[MED]**
- [ ] Does compaction have built-in safeguards against infinite compaction loops? **[HIGH]**

### c) Use Cases
- [ ] Can hooks implement their own circuit breaker that survives gateway restart? **[MED]**
- [ ] What's the recommended approach for hook-to-hook communication to avoid loops? **[LOW]**
- [ ] Can hooks safely use setTimeout/setInterval without memory leaks? **[MED]**

### d) Best Practices
- [ ] Should ALL hooks implement guard counters? What is the recommended pattern? **[HIGH]**
- [ ] Is there a "read-only" hook mode that prevents session modification? **[MED]**
- [ ] Can hooks be marked as "idempotent" for loop safety? **[MED]**

### e) Problems & Limitations
- [ ] Is there a known issue with compaction loops causing OOM? **[HIGH]**
- [ ] Does gateway restart reset all in-flight hook state? **[MED]**
- [ ] Are there memory leaks from hook handlers not cleaning up timers? **[MED]**

### f) Solutions & Workarounds
- [ ] Can OpenClaw add built-in loop protection (depth limit, circuit breaker)? **[HIGH — feature request]**
- [ ] What's the best way to detect loops in production? **[MED]**
- [ ] Can hooks be dynamically disabled when loop is detected? **[MED]**

### g) Edge Cases
- [ ] What happens when compaction safeguard is bypassed by malicious hook? **[CRITICAL]**
- [ ] Can cross-channel relay create loops across multiple channels? **[HIGH]**
- [ ] What happens when workspace hook has same name as bundled hook? **[MED]**

### h) Security
- [ ] Can malicious hook use infinite loop as DoS attack against Gateway? **[CRITICAL]**
- [ ] Can infinite loop in hooks crash the host system? **[HIGH]**
- [ ] Is there a way to disable hooks entirely for high-security deployments? **[MED]**

---

## 9. SOURCES

### Primary Sources (OpenClaw Docs)

1. `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Main hooks documentation
2. `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin hook system (28+ hooks), execution model, security notes
3. `/usr/local/lib/node_modules/openclaw/docs/plugins/sdk-provider-plugins.md` — Provider plugin hooks
4. `/usr/local/lib/node_modules/openclaw/docs/concepts/agent-loop.md` — Agent loop + hook integration
5. `/usr/local/lib/node_modules/openclaw/docs/gateway/configuration-reference.md` — Hook configuration reference

### Internal Sources

6. `/data/.openclaw/agents/investigador/workspace/Research/OpenClaw/findings/openclaw-hooks-system.md` — Hook system research
7. `/data/.openclaw/agents/investigador/workspace/Research/OpenClaw/findings/hook-security-audit.md` — Hook security audit

### Key Findings Summary

| Aspect | Finding | Risk Level |
|--------|---------|------------|
| Loop protection | **NONE** — no depth counter, no circuit breaker, no recursion limit | **CRITICAL** |
| Direct recursion | `session:patch` → modifies session → `session:patch` → **direct recursion** | **HIGH** |
| Event cascade | `message:received` → session change → `session:patch` → message → **loop** | **HIGH** |
| Compaction cycles | `compact:before` → save state → `compact:after` → restore → **loop** | **HIGH** |
| before_agent_start | Deprecated but still functional + in PROMPT_INJECTION_HOOK_NAMES | MEDIUM |
| External system echo | Hook → external → webhook → `message:received` → **loop** | **HIGH** |
| Insertion order | No guaranteed execution order — non-deterministic loop behavior | MEDIUM |
| Cross-plugin | Plugin A → calls Plugin B tool → modifies session → Plugin A handler → **loop** | MEDIUM |
| DoS potential | Malicious hook can create infinite loop causing Gateway crash | **CRITICAL** |

---

## RECOMMENDATIONS

1. **ALWAYS implement guard counters** in hooks that modify session state
2. **Avoid hooks that directly modify session** they're registered on (`session:patch` handler modifying session)
3. **Use session-scoped counters** that reset on `/new` or `/reset`
4. **Implement circuit breakers** for hooks that call external systems
5. **NEVER enable workspace hooks** in production (untrusted code + loop risk)
6. **Monitor hook execution rate** and alert on anomalies
7. **Request feature**: Built-in loop protection from OpenClaw team
8. **Document loops** in hook interaction diagrams to prevent accidental cycles

---

*Research by: Investigador Scout*  
*Date: 2026-04-23 04:53 CET*  
*Status: COMPLETE — L28 RESOLVED (backlog #1)*

---

## FOLLOW-UP ACTIONS

- [x] Mark backlog #1 "Hook infinite loops" as RESOLVED
- [x] Add findings to `findings/hook-infinite-loops.md`
- [x] Add new questions to `questions.md`
- [x] Add sources to `sources.md`
- [ ] Notify BRAIN for curation into `OPENCLAW_EXPERT.md`
