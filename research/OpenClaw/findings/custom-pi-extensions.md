# OpenClaw Custom Pi Extensions — Research Findings

**Research Date:** 2026-04-23 01:55 CET  
**Status:** COMPLETE  
**Topic:** Custom Pi Extensions (pi-hooks) — Extension Architecture  

---

## What is It?

**Custom Pi Extensions** (also called `pi-hooks`) are modular runtime extensions that hook into OpenClaw's embedded Pi agent (`pi-coding-agent`) to modify or augment agent behavior during a session. They are **distinct from OpenClaw's hook system** (`before_model_resolve`, `before_prompt_build`, etc.) — they operate inside the Pi agent runtime, not at the OpenClaw gateway layer.

Two extensions ship built-in with OpenClaw:
1. **compaction-safeguard** — Quality guardrails for session compaction (summarization)
2. **context-pruning** — Cache-TTL based context pruning ("microcompact"-style)

---

## How It Works

### Architecture

```
createAgentSession()
  └── ResourceLoader
        └── additionalExtensionPaths[] → loads .js extension files
              └── Extension registers via ExtensionAPI (callback-based)
                    └── Session runtime calls extension hooks at specific points
```

### Core Files

| File | Purpose |
|------|---------|
| `dist/plugin-sdk/src/agents/pi-hooks/compaction-safeguard.d.ts` | Compaction safeguard extension type definition |
| `dist/plugin-sdk/src/agents/pi-hooks/context-pruning.d.ts` | Context pruning extension type definition |
| `dist/plugin-sdk/src/agents/pi-hooks/session-manager-runtime-registry.d.ts` | Session-scoped runtime registry |
| `dist/agents/pi-embedded-runner/extensions.ts` | Extension loading logic |
| `pi.md` (docs) | Architecture overview of Pi integration |

### Loading Mechanism

Extensions are loaded via `additionalExtensionPaths` passed to `DefaultResourceLoader` during `createAgentSession()`:

```typescript
const resourceLoader = new DefaultResourceLoader({
  cwd: resolvedWorkspace,
  agentDir,
  settingsManager,
  additionalExtensionPaths,  // ← extension paths pushed here
});
await resourceLoader.reload();
```

### Extension API

Each extension receives an `ExtensionAPI` object from `@mariozechner/pi-coding-agent`. The extension then registers callbacks for specific lifecycle events:

```typescript
// From compaction-safeguard.d.ts
export default function compactionSafeguardExtension(api: ExtensionAPI): void {
  // Registers compaction-related callbacks
}
```

```typescript
// From context-pruning.d.ts
export { default } from "./context-pruning/extension.js";
export { pruneContextMessages } from "./context-pruning/pruner.js";
// Exports for use by the extension loader
```

### Session Manager Runtime Registry

```typescript
// session-manager-runtime-registry.d.ts
export declare function createSessionManagerRuntimeRegistry<TValue>(): {
  set: (sessionManager: unknown, value: TValue | null) => void;
  get: (sessionManager: unknown) => TValue | null;
};
```

This creates a per-session registry for extension-specific runtime state — allows extensions to store and retrieve session-scoped data without global state.

---

## Built-in Extensions

### 1. Compaction Safeguard (`compaction-safeguard`)

**Purpose:** Quality guardrails for session compaction (auto-summarization when context overflows)

**Behavior:**
- Adaptive token budgeting for compaction summaries
- Tool failure tracking and formatting
- File operation summaries in compaction output
- Format: structured fallback summary, preserved recent turns, tool failure sections
- Quality auditing of generated summaries

**Key functions exported:**
- `collectToolFailures()` — Extract tool failures from messages
- `formatToolFailuresSection()` — Format failures for compaction prompt
- `splitPreservedRecentTurns()` — Split messages into summarizable vs preserved
- `formatPreservedTurnsSection()` — Format preserved turns
- `readWorkspaceContextForSummary()` — Extract "Session Startup" and "Red Lines" from AGENTS.md
- `auditSummaryQuality()` — Validate summary quality
- `computeAdaptiveChunkRatio()` — Adaptive chunk sizing
- `summarizeInStages()` — Multi-stage summarization

**Triggered by:** `resolveCompactionMode(params.cfg) === "safeguard"` in `extensions.ts`

**Config option:** `agents.defaults.contextPruning.mode === "cache-ttl"` — but this is for context pruning, not compaction safeguard specifically

### 2. Context Pruning (`context-pruning`)

**Purpose:** Opt-in "microcompact"-style context pruning. Affects **in-memory context only** — does NOT rewrite session history on disk.

**Key exported items:**
- `pruneContextMessages()` from `./context-pruning/pruner.js`
- `ContextPruningConfig`, `ContextPruningToolMatch`, `EffectiveContextPruningSettings` types
- `computeEffectiveSettings()`, `DEFAULT_CONTEXT_PRUNING_SETTINGS`

**Triggered by:** `cfg?.agents?.defaults?.contextPruning?.mode === "cache-ttl"` in extensions loading

**What it does:**
- Tracks cache TTL for context messages
- Prunes messages based on settings (max age, token budget, etc.)
- Per-message pruning decisions based on tool match patterns

---

## Extension Points Available

### Currently Known Extension Points

| Extension | Hook Point | Description |
|-----------|-------------|-------------|
| `compaction-safeguard` | Compaction lifecycle | Intercepts before/during/after compaction |
| `context-pruning` | Context assembly | Prunes messages before they're sent to LLM |

### How Extensions Register

Based on the type definitions, extensions appear to use a **callback registration pattern** via `ExtensionAPI`:

```typescript
// Hypothetical extension registration pattern
function myExtension(api: ExtensionAPI): void {
  api.onCompactionStart?.((ctx) => { /* ... */ });
  api.onCompactionEnd?.((ctx) => { /* ... */ });
  api.onContextAssemble?.((ctx) => { /* ... */ });
}
```

**NOTE:** The actual ExtensionAPI interface methods are not publicly documented. The exact callback names need to be determined by inspecting the `@mariozechner/pi-coding-agent` package or the actual runtime behavior.

---

## How to Create Custom Extensions

### Step-by-Step Approach

1. **Study existing extensions** in `dist/plugin-sdk/src/agents/pi-hooks/`:
   - Study `compaction-safeguard.d.ts` and its implementation
   - Study `context-pruning.d.ts` and its implementation

2. **Create extension file** in a workspace or custom location:
   ```typescript
   // my-extension.ts
   import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
   
   export default function myCustomExtension(api: ExtensionAPI): void {
     // Register callbacks via api
   }
   ```

3. **Package as JS** — Extensions must be compiled JS (not TS) since they're loaded via `ResourceLoader.reload()` which resolves paths to `.js` files

4. **Configure path** — Via `additionalExtensionPaths` in the agent session params

### Requirements

- Must export a **default function** accepting `ExtensionAPI`
- Must be valid JS (ESM or CJS)
- Must be loadable via `import()` by ResourceLoader
- Should handle errors gracefully (uncaught exceptions may break extension behavior without crashing the session)

### Configuration Integration

Extensions that need config would read from `agents.defaults` or custom config paths:

```typescript
// In extensions.ts
if (cfg?.agents?.defaults?.myExtension?.enabled) {
  paths.push(resolvePiExtensionPath("my-extension"));
}
```

---

## Problems & Limitations

### Problems

1. **No public SDK documentation** — Extension API types exist in `.d.ts` files but there's no user-facing docs explaining how to create custom extensions
2. **Internal API** — `ExtensionAPI` is from `@mariozechner/pi-coding-agent` (internal package), not a public OpenClaw API
3. **No discoverable extension points** — No registry or enumeration of available hooks
4. **TypeScript compilation required** — Extensions must be pre-compiled to JS
5. **Extension loading is static** — Paths must be known at session creation, no dynamic registration mid-session
6. **No error recovery** — If extension throws, behavior is undefined

### Limitations

1. **No cross-extension communication** — Each extension is isolated; session-manager-runtime-registry helps but is per-extension
2. **No hot-reload** — Changing an extension requires new session
3. **Disk-only session history** — Context pruning affects in-memory only; doesn't compact the actual session JSONL file
4. **Version coupling** — Extension API may change between pi-coding-agent versions (currently v0.64.0)

---

## Edge Cases

1. **Multiple extensions on same hook** — Execution order undefined; likely LIFO or insertion order
2. **Extension with same name as built-in** — Likely one overwrites the other based on path precedence
3. **Extension path doesn't exist** — ResourceLoader.reload() likely fails or silently skips
4. **Extension modifies session state incorrectly** — Could cause context overflow, tool call failures, or compaction loops
5. **Session reset clears extension state** — SessionManager runtime registry is per-session; reset clears it
6. **Subagent sessions** — Extensions may or may not be inherited; need to test

---

## Creative Uses

1. **RAG Context Enrichment** — Hook into context assembly to inject relevant documents from a vector store before each LLM call
2. **Custom Logging/Audit Trail** — Track all prompts, tool calls, and responses to a separate audit store
3. **Dynamic Tool Allowlist** — Modify tool policy based on session history or user context
4. **Conversation Analytics** — Track sentiment, topic changes, engagement metrics
5. **Adaptive Temperature/Temperature Override** — Adjust model parameters based on conversation phase
6. **Memory Injection Gateway** — Intercept context and inject relevant MEMORY.md content proactively
7. **Rate Limiting** — Throttle tool calls or message volume per session
8. **Content Filtering** — Scan context for sensitive content before LLM call
9. **Multi-modal Preprocessor** — Transform images/audio before injection
10. **Session Migration** — Export session state to external format on specific triggers

---

## New Questions Generated

1. **What are the exact `ExtensionAPI` callback method names?** — Need to inspect `@mariozechner/pi-coding-agent` runtime or source
2. **Can extensions be enabled/disabled per session or per agent?** — Config structure unclear
3. **What is the full lifecycle of a compaction event?** — When exactly do callbacks fire?
4. **Can extensions read/write to the session file?** — Would enable truly custom compaction strategies
5. **What is `resolvePiExtensionPath()` and how does it resolve paths?** — May be a standard location or config-driven
6. **Are there memory leaks from extension runtime registries?** — Need to understand cleanup
7. **Can extensions communicate via shared state?** — Beyond session-manager-runtime-registry
8. **What happens when extension throws in a callback?** — Is it caught, does it propagate?
9. **Can extensions modify the tool list dynamically?** — Would enable dynamic capability switching
10. **Is there a way to debug extension execution?** — No logs or traces mentioned

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/pi.md` — Pi Integration Architecture documentation
- `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/compaction-safeguard.d.ts` — Compaction safeguard type definitions
- `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/context-pruning.d.ts` — Context pruning type definitions
- `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/agents/pi-hooks/session-manager-runtime-registry.d.ts` — Session runtime registry
- `/usr/local/lib/node_modules/openclaw/dist/agents/pi-embedded-runner/extensions.ts` — Extension loading logic
- Backlog.md — L18 Custom Pi Extensions item

---

*Research by: Investigador Scout | 2026-04-23 01:55 CET*
