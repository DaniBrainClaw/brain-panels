# OpenClaw Config System — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23  
**Topic:** OpenClaw Config System (configuration-reference + configuration + skills-config)  
**Priority:** MEDIUM (from backlog.md L26)  
**Research Depth:** 6-Layer Exhaustive  

---

## TABLE OF CONTENTS
1. [What Is — Definition & Core Concept](#1-what-is--definition--core-concept)
2. [How It Works — Architecture & Mechanics](#2-how-it-works--architecture--mechanics)
3. [Uses — Practical Applications](#3-uses--practical-applications)
4. [Problems — Known Issues & Limitations](#4-problems--known-issues--limitations)
5. [Solutions — Best Practices & Workarounds](#5-solutions--best-practices--workarounds)
6. [Edge Cases — Unusual Scenarios](#6-edge-cases--unusual-scenarios)
7. [NEW Questions Opened by This Research](#7-new-questions-opened-by-this-research)
8. [Sources](#8-sources)

---

## 1. WHAT IS — Definition & Core Concept

### Definition

**OpenClaw Config System** is the centralized JSON5-based configuration subsystem that controls all aspects of the Gateway: channels, models, agents, skills, sandboxing, cron jobs, hooks, logging, auth profiles, secrets, and more. It lives in `~/.openclaw/openclaw.json` and is the single source of truth for OpenClaw behavior.

### Core Properties

| Property | Description |
|----------|-------------|
| **Format** | JSON5 (comments + trailing commas allowed) |
| **Location** | `~/.openclaw/openclaw.json` (primary); `~/.openclaw/` directory for related data |
| **Schema** | Strict validation via JSON Schema — unknown keys cause Gateway **refusal to start** |
| **Schema Tool** | `openclaw config schema` prints live schema with bundled/plugin/channel metadata merged |
| **Hot Reload** | Gateway watches `openclaw.json` and applies changes automatically |
| **Fallback** | If `openclaw.json` is missing, OpenClaw uses safe defaults for everything |
| **Includes** | `$include` directive supports splitting config into multiple files with deep-merge |

### Config vs Configuration

| Term | Meaning |
|------|---------|
| **Config** | The JSON5 file (`~/.openclaw/openclaw.json`) |
| **Configuration** | The total set of all settings controlling OpenClaw behavior |

### Top-Level Config Structure

```json5
{
  // Core
  $schema?: string,           // JSON Schema metadata
  gateway?: { ... },          // Gateway-level settings
  agents?: { ... },           // Agent defaults + agent list
  channels?: { ... },         // Channel configs (telegram, discord, whatsapp, etc.)
  
  // Automation
  cron?: { ... },             // Cron job configuration
  hooks?: { ... },            // Hook system config
  
  // AI/ML
  models?: { ... },           // Model providers + catalog
  auth?: { ... },             // Auth profiles + cooldowns
  
  // Tools/Skills
  skills?: { ... },           // Skills loading + per-skill config
  tools?: { ... },            // Tool-specific config
  
  // Security
  secrets?: { ... },          // Secret providers (env, file, exec, vault)
  
  // Observability
  logging?: { ... },          // Logging config
  diagnostics?: { ... },     // Diagnostics + OTEL export
  
  // Platform
  acp?: { ... },              // ACP runtime config
  cli?: { ... },              // CLI behavior
  
  // Meta
  wizard?: { ... },           // Metadata from guided setup flows
  update?: { ... },           // Auto-update channel + schedule
  
  // Experimental
  plugins?: { ... },          // Plugin entries + config
  broadcast?: { ... },        // Broadcast targets
}
```

### Configuration Reference vs Configuration Overview

| Document | Purpose |
|----------|---------|
| **configuration-reference.md** | Field-level schema semantics, every available key, all defaults |
| **configuration.md** | Task-oriented overview: common tasks, quick setup, links to reference |
| **configuration-examples.md** | Complete copy-paste configs for common scenarios |

---

## 2. HOW IT WORKS — Architecture & Mechanics

### Config Loading & Validation

**Startup sequence:**
1. Gateway reads `~/.openclaw/openclaw.json`
2. Validates against JSON Schema (STRICT — invalid config = Gateway won't boot)
3. If validation fails: only diagnostic commands work (`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)
4. On success: Gateway starts with resolved config

**Schema tooling:**
- `openclaw config schema` — prints live JSON Schema used by Control UI + validation
- `config.schema.lookup` — returns one path-scoped schema node for drill-down
- `pnpm config:docs:check` / `pnpm config:docs:gen` — validates config-doc baseline hash against schema surface

**Hot reload:**
- Gateway watches `openclaw.json` for changes
- Changes applied automatically without restart
- Some changes (hooks, skills) may require restart for full effect

### Config Includes (`$include`)

```json5
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
```

**Merge behavior:**
- Single file: replaces the containing object
- Array of files: deep-merged in order (later overrides earlier)
- Sibling keys: merged after includes (override included values)
- Nested includes: up to 10 levels deep
- Paths: resolved relative to the including file, but must stay inside the top-level config directory (`dirname` of `openclaw.json`)
- Errors: clear messages for missing files, parse errors, and circular includes
- `../` forms only allowed when still resolving inside config boundary

### SecretRef System

Secrets use an indirection layer to avoid plaintext credentials in config:

```json5
{ source: "env" | "file" | "exec", provider: "string", id: "string" }
```

**Validation rules:**
- `provider` pattern: `^[a-z][a-z0-9_-]{0,63}$`
- `source: "env"` id pattern: `^[A-Z][A-Z0-9_]{0,127}$`
- `source: "file"` id: absolute JSON pointer (e.g., `/providers/openai/apiKey`)
- `source: "exec"` id pattern: `^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`
- `source: "exec"` ids must NOT contain `.` or `..` path segments

**Secret providers:**

```json5
{
  secrets: {
    providers: {
      default: { source: "env" },
      filemain: { source: "file", path: "~/.openclaw/secrets.json", mode: "json" },
      vault: { source: "exec", command: "/usr/local/bin/openclaw-vault-resolver", passEnv: ["PATH", "VAULT_ADDR"] },
    },
    defaults: { env: "default", file: "filemain", exec: "vault" },
  },
}
```

**Resolution behavior:**
- Secret refs resolved at activation time into an in-memory snapshot
- Request paths read the snapshot only (not re-resolved on every access)
- Active-surface filtering: unresolved refs on enabled surfaces fail startup/reload
- Inactive surfaces skipped with diagnostics

### Auth Profiles

```json5
{
  auth: {
    profiles: {
      "anthropic:default": { provider: "anthropic", mode: "api_key" },
      "openai-codex:personal": { provider: "openai-codex", mode: "oauth" },
    },
    order: {
      anthropic: ["anthropic:default", "anthropic:work"],
      "openai-codex": ["openai-codex:personal"],
    },
    cooldowns: {
      billingBackoffHours: 5,
      billingMaxHours: 24,
      authPermanentBackoffMinutes: 10,
      // ... more cooldowns
    },
  },
}
```

- Per-agent profiles stored at `<agentDir>/auth-profiles.json`
- OAuth-mode profiles do NOT support SecretRef-backed auth-profile credentials
- Legacy OAuth imports from `~/.openclaw/credentials/oauth.json`

### Agent Configuration

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: { primary: "anthropic/claude-sonnet-4-6", fallbacks: ["openai/gpt-5.4"] },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "openai/gpt-5.4": { alias: "GPT" },
      },
      skills: ["github", "weather"],
      memorySearch: { provider: "openai", model: "text-embedding-3-small" },
      sandbox: { mode: "non-main", scope: "agent" },
      heartbeat: { every: "30m", target: "last" },
      imageMaxDimensionPx: 1200,
    },
    list: [
      { id: "main" },
      { id: "writer", skills: ["docs-search"] },
      { id: "locked-down", skills: [] },
    ],
  },
}
```

### Channel Configuration

Each channel starts automatically when its config section exists (unless `enabled: false`):

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",
      allowFrom: ["tg:123"],
      groups: { "*": { requireMention: true } },
    },
    discord: {
      enabled: true,
      token: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["1234567890"],
      guilds: { "123456789012345678": { slug: "my-guild" } },
    },
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15555550123"],
    },
  },
}
```

**DM policies:** `pairing` (default) | `allowlist` | `open` | `disabled`
**Group policies:** `allowlist` (default) | `open` | `disabled`

### Skills Configuration

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
      watch: true,
      watchDebounceMs: 250,
    },
    install: {
      preferBrew: true,
      nodeManager: "npm",
    },
    entries: {
      "image-lab": { enabled: true, apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" } },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

### Cron Configuration

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
    retry: {
      maxAttempts: 3,
      backoffMs: [30000, 60000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "timeout", "server_error"],
    },
    failureAlert: { enabled: false, after: 3, cooldownMs: 3600000 },
    failureDestination: { mode: "announce", channel: "last" },
  },
}
```

### Hooks Configuration

```json5
{
  hooks: {
    internal: {
      enabled: true,
      entries: {
        "session-memory": { enabled: true },
        "command-logger": { enabled: false },
        "bootstrap-extra-files": { enabled: true, paths: ["packages/*/AGENTS.md"] },
      },
      load: {
        extraDirs: ["/path/to/more/hooks"],
      },
    },
  },
}
```

### Logging Configuration

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty",
    redactSensitive: "tools",
    redactPatterns: ["\\bTOKEN\\b\\s*[=:]\s*(['\"]?)([^\s'\"]+)\1"],
  },
}
```

Default log file: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
Max file size: 500 MB (524288000 bytes), then writes suppressed

### Diagnostics + OTEL

```json5
{
  diagnostics: {
    enabled: true,
    flags: ["telegram.*"],
    stuckSessionWarnMs: 30000,
    otel: {
      enabled: false,
      endpoint: "https://otel-collector.example.com:4318",
      protocol: "http/protobuf",
      serviceName: "openclaw-gateway",
      traces: true,
      metrics: true,
    },
    cacheTrace: { enabled: false, filePath: "~/.openclaw/logs/cache-trace.jsonl" },
  },
}
```

### Config Editing Methods

| Method | Command/Action |
|--------|----------------|
| **Interactive wizard** | `openclaw onboard` or `openclaw configure` |
| **CLI one-liners** | `openclaw config get/set/unset` |
| **Control UI** | http://127.0.0.1:18789 → Config tab |
| **Direct edit** | Edit `~/.openclaw/openclaw.json` directly |

**CLI examples:**
```bash
openclaw config get agents.defaults.workspace
openclaw config set agents.defaults.heartbeat.every "2h"
openclaw config unset plugins.entries.brave.config.webSearch.apiKey
```

### Control UI Config Tab

- Renders a form from the live config schema
- Includes field `title`/`description` docs metadata
- Plugin and channel schemas merged when available
- Raw JSON editor as escape hatch
- `config.schema.lookup` for drill-down tooling

---

## 3. USES — Practical Applications

### Common Config Tasks

| Task | Config Section | Key Fields |
|------|---------------|------------|
| **Connect a channel** | `channels.<provider>` | `enabled`, `botToken`/`token`, `dmPolicy`, `allowFrom` |
| **Set default model** | `agents.defaults.model` | `primary`, `fallbacks[]`, `models{}` |
| **Configure memory search** | `agents.defaults.memorySearch` | `provider`, `model`, `query.hybrid`, `query.mmr` |
| **Set up skills** | `skills` + `agents.defaults.skills` | `entries{}`, `load.extraDirs`, per-agent `skills[]` |
| **Enable sandboxing** | `agents.defaults.sandbox` | `mode: "non-main"|"all"`, `scope: "agent"|"session"` |
| **Configure cron jobs** | `cron` | `enabled`, `maxConcurrentRuns`, `sessionRetention` |
| **Control logging** | `logging` | `level`, `file`, `consoleStyle`, `redactSensitive` |
| **Set up secrets** | `secrets.providers` | `source`, `path`/`command`, `passEnv` |
| **Configure auth profiles** | `auth.profiles` | `provider`, `mode: "api_key"|"oauth"` |
| **Enable OTEL telemetry** | `diagnostics.otel` | `enabled`, `endpoint`, `protocol`, `headers` |

### Config-Based Access Control

**Per-channel DM policy:**
- `pairing` (default): unknown senders get one-time pairing code; owner approves
- `allowlist`: only senders in `allowFrom` (or paired allow store)
- `open`: allow all DMs (requires `allowFrom: ["*"]`)
- `disabled`: ignore all DMs

**Per-channel group policy:**
- `allowlist` (default): only groups matching configured allowlist
- `open`: bypass group allowlists (mention-gating still applies)
- `disabled`: block all group/room messages

**Per-agent skill allowlists:**
```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" },           // inherits defaults → github, weather
      { id: "docs", skills: ["docs-search"] },  // replaces defaults
      { id: "locked-down", skills: [] },        // no skills
    ],
  },
}
```

### Model Configuration

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-5.4"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "openai/gpt-5.4": { alias: "GPT" },
      },
    },
  },
}
```

**Model refs:** `provider/model` format (e.g., `anthropic/claude-opus-4-6`)
**Model catalog:** `agents.defaults.models` acts as allowlist for `/model`

### Memory Search Configuration

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",        // auto-detected if omitted
        model: "text-embedding-3-small",
        fallback: "none",
        remote: { baseUrl, apiKey, headers },
        query: {
          hybrid: { vectorWeight: 0.7, textWeight: 0.3, mmr: { enabled: true, lambda: 0.7 } },
          temporalDecay: { enabled: true, halfLifeDays: 30 },
        },
        extraPaths: ["../team-docs"],
      },
    },
  },
}
```

### Cron Job Configuration

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
    retry: { maxAttempts: 3, backoffMs: [30000, 60000, 300000] },
    failureAlert: { enabled: true, after: 3, cooldownMs: 3600000, mode: "announce" },
    failureDestination: { mode: "announce", channel: "last" },
  },
}
```

### Secrets Management Setup

```json5
{
  secrets: {
    providers: {
      default: { source: "env" },
      vault: { source: "exec", command: "/usr/local/bin/vault-resolver", passEnv: ["VAULT_ADDR"] },
    },
  },
}
```

### Split Config with $include

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  channels: { $include: ["./channels/telegram.json5", "./channels/discord.json5"] },
}
```

---

## 4. PROBLEMS — Known Issues & Limitations

### Strict Validation = All-or-Nothing

**Problem:** OpenClaw ONLY accepts configs that fully match the schema. Unknown keys, malformed types, or invalid values cause the Gateway to **refuse to start**.

**Impact:** 
- Gateway won't boot if config has ANY error
- Only diagnostic commands work (`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)

**Mitigation:**
- Run `openclaw doctor` to see exact issues
- Run `openclaw doctor --fix` (or `--yes`) to apply repairs
- Always validate locally before deploying

### No Partial Config Hot-Reload

**Problem:** Some config changes require full Gateway restart to take effect.

**Affected areas:**
- Hook handlers (must restart to reload handlers)
- Plugin enable/disable (some require restart)
- Skill binary requirements (checked at load time)

**Not affected:**
- Most channel configs (hot reloaded)
- Logging levels (hot reloaded)
- Cron settings (hot reloaded)

### SecretRef Complexity

**Problem:** SecretRef system is powerful but complex to configure correctly.

**Issues:**
- Id patterns have strict validation (env: `^[A-Z][A-Z0-9_]{0,127}$`, exec: no `.` or `..`)
- Secret refs resolved at activation time only — not re-resolved on every access
- Inactive surfaces skipped but can cause confusion
- No SecretRef support for OAuth-mode auth profile credentials

### Config Schema Drift

**Problem:** `docs/` config references can drift from actual schema.

**Detection:**
- `pnpm config:docs:check` detects drift between docs-facing config baseline and current schema surface
- `pnpm config:docs:gen` regenerates docs baseline

**Mitigation:** Run `pnpm config:docs:check` regularly in CI/CD

### No Config Validation in CI by Default

**Problem:** Schema validation only runs at Gateway startup.

**Gap:** No built-in `openclaw config validate` command for pre-deployment validation.

**Workaround:** Use `pnpm config:docs:check` or start Gateway in diagnostic mode

### Config Includes Path Security

**Problem:** `$include` paths must stay inside config directory.

**Restriction:** `../` forms only allowed when still resolving inside config directory boundary.

**Impact:** Cannot include files from outside `~/.openclaw/`

### Skill Env Injection Scope

**Problem:** `skills.entries.*.env` and `skills.entries.*.apiKey` inject secrets into **host** process for agent turn, NOT the sandbox.

**Impact:** 
- Sandboxed runs don't inherit these env vars
- Must use `agents.defaults.sandbox.docker.env` or bake into custom image
- Security risk if skill env vars contain sensitive data that could leak

### Secret Storage Gap

**Problem:** No built-in encrypted secrets storage.

**Available options:**
- `source: "env"` — environment variables
- `source: "file"` — JSON file (not encrypted by default)
- `source: "exec"` — external vault/exec resolver

**Gap:** No native HashiCorp Vault, AWS Secrets Manager, or similar integration built-in

### Auth Profile Per-Agent Storage

**Problem:** Per-agent auth profiles stored at `<agentDir>/auth-profiles.json`.

**Implication:** If agent directory is lost/corrupted, auth profiles for that agent are lost

### Large Log File = Silent Failure

**Problem:** When `logging.file` exceeds `maxFileBytes` (default 500MB), writes are **silently suppressed**.

**Impact:** No logging after limit hit — hard to debug

**Mitigation:** Use external log rotation for production

---

## 5. SOLUTIONS — Best Practices & Workarounds

### Best Practice: Validate Before Deploy

```bash
# Always run doctor before restarting gateway
openclaw doctor

# Apply fixes automatically
openclaw doctor --fix --yes
```

### Best Practice: Use Config Includes for Modular Setup

```json5
// ~/.openclaw/openclaw.json
{
  $include: "./base.json5",
  channels: { $include: "./channels.json5" },
  agents: { $include: "./agents.json5" },
}
```

**Benefit:** Teams can own their slice; reduces merge conflicts

### Best Practice: Use SecretRefs for All Credentials

```json5
// BAD: plaintext token
{ channels: { telegram: { botToken: "123:abc" } } }

// GOOD: SecretRef
{ 
  channels: { 
    telegram: { 
      botToken: { source: "env", provider: "default", id: "TELEGRAM_BOT_TOKEN" } 
    } 
  } 
}
```

### Best Practice: Hot Reload-Friendly Changes

**Changes that apply without restart:**
- Channel config tweaks
- Logging level changes
- Cron job config
- Model fallbacks
- Skill enable/disable

**Changes requiring restart:**
- New hooks
- Plugin enable/disable
- Sandbox mode changes
- Skills with binary requirements

### Best Practice: Config Backup + Version Control

```bash
# Backup before editing
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup-$(date +%Y%m%d)

# Use git
cd ~/.openclaw && git init && git add openclaw.json
```

### Best Practice: Use Control UI for Exploration

- Navigate to http://127.0.0.1:18789
- Use Config tab form view (validates as you fill)
- Switch to Raw JSON for direct editing
- Uses live schema with field documentation

### Best Practice: Monitor Log Size

```bash
# Check current log size
ls -lh /tmp/openclaw/openclaw-*.log

# Set up external rotation (example: logrotate)
# /etc/logrotate.d/openclaw
/tmp/openclaw/openclaw-*.log {
  daily
  rotate 7
  compress
  delaycompress
  missingok
  notifempty
}
```

### Best Practice: Sandbox Skill Secrets

For sandboxed runs with skill env vars:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "agent",
        docker: {
          env: {
            GEMINI_API_KEY: "from-host-env-or-secrets",
          },
        },
      },
    },
  },
}
```

### Best Practice: Schema Validation in CI

```yaml
# .github/workflows/openclaw-config.yml
- name: Validate OpenClaw config
  run: |
    openclaw doctor || openclaw doctor --fix
    pnpm config:docs:check
```

### Best Practice: Use allowBundled for Controlled Skill Sets

```json5
{
  skills: {
    allowBundled: ["github", "weather", "docs-search"],
  },
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
  },
}
```

**Effect:** Only listed bundled skills eligible; workspace/managed skills unaffected

### Workaround: Config Edit Without Restart

For changes that SHOULD hot-reload but don't:

1. Edit `~/.openclaw/openclaw.json`
2. Wait for file watcher detection
3. If no effect: `openclaw gateway restart`

### Workaround: Diagnose Config Issues

```bash
# Full diagnostic
openclaw doctor

# Check specific config section
openclaw config get agents.defaults

# Print full schema
openclaw config schema
```

---

## 6. EDGE CASES — Unusual Scenarios

### Edge Case 1: Circular $include

**Scenario:** Config A includes B, B includes A

**Behavior:** Clear error message with circular include detection

**Impact:** Config fails to load

### Edge Case 2: $include Outside Config Directory

**Scenario:** `$include: "../other-config.json5"`

**Behavior:** Resolves only if still inside `~/.openclaw/` directory boundary

**Impact:** If `../` escapes boundary, load fails with clear error

### Edge Case 3: Unknown Keys in Config

**Scenario:** Accidental typo or deprecated key

**Behavior:** Gateway REFUSES to start (strict validation)

**Impact:** Only diagnostic commands work; must fix with `openclaw doctor --fix`

### Edge Case 4: Schema Mismatch After Upgrade

**Scenario:** Upgraded OpenClaw; new required fields or changed types

**Behavior:** Config no longer valid against new schema

**Impact:** Gateway won't start; `openclaw doctor` shows exact issues

### Edge Case 5: SecretRef to Missing Env Var

**Scenario:** `{ source: "env", provider: "default", id: "NONEXISTENT_VAR" }`

**Behavior:** Fails at activation time for enabled surfaces; inactive surfaces skip with diagnostics

**Impact:** Gateway may fail to start if secret is for enabled component

### Edge Case 6: Concurrent Config Writes

**Scenario:** Multiple processes writing to `openclaw.json` simultaneously

**Behavior:** No locking mechanism; last write wins

**Impact:** Potential config corruption or lost changes

**Mitigation:** Use atomic write pattern (write to temp file, then rename)

### Edge Case 7: Log File Size Limit Hit

**Scenario:** `logging.file` grows past `maxFileBytes` (500MB default)

**Behavior:** Writes silently suppressed; no logging after limit

**Impact:** Hard to debug — appears as if logging stopped

**Mitigation:** External log rotation; monitor file sizes

### Edge Case 8: Skills Watcher + Rapid Edits

**Scenario:** Rapidly editing `SKILL.md` files

**Behavior:** `watchDebounceMs` (default 250ms) debounces reloads

**Impact:** May miss changes or reload multiple times

### Edge Case 9: Per-Agent Skills Override

**Scenario:** `{ id: "writer", skills: ["docs-search"] }` (no skills property inherits)

**Behavior:** Explicit `skills[]` list REPLACES defaults (does not merge)

**Impact:** Agent has NO skills unless explicitly listed

**Mitigation:** Always include all needed skills in explicit list

### Edge Case 10: Auth Profile OAuth + SecretRef

**Scenario:** `{ provider: "openai-codex", mode: "oauth" }` with SecretRef credential

**Behavior:** OAuth-mode profiles do NOT support SecretRef-backed credentials

**Impact:** Must use other auth mechanism for OAuth providers

### Edge Case 11: Nested $include Depth

**Scenario:** 10+ levels of nested `$include`

**Behavior:** Error after 10 levels of nesting

**Impact:** Cannot modularize beyond 10 levels

### Edge Case 12: Hot Reload of Hooks

**Scenario:** Edit hook handler while Gateway running

**Behavior:** Hook changes NOT picked up without restart

**Impact:** Must restart Gateway for hook changes

**Note:** This is a known limitation; workspace hook enable/disable may also need restart

### Edge Case 13: Config Secrets in Logs

**Scenario:** `logging.redactSensitive: "tools"` only redact tools calls

**Behavior:** Other log lines may contain config values with secrets

**Impact:** Potential secret exposure in logs

**Mitigation:** `redactPatterns` for additional patterns; avoid logging raw config

### Edge Case 14: Skills Watcher Disabled

**Scenario:** `skills.load.watch: false`

**Behavior:** Skill changes require new session to take effect

**Impact:** Development workflow slower

**Mitigation:** Enable watcher during development

### Edge Case 15: Sandbox + Skills Binary Requirements

**Scenario:** Skill requires `bins: ["uv"]` but sandbox container doesn't have it

**Behavior:** Skill not eligible in sandboxed runs

**Impact:** Works on host, fails in sandbox

**Mitigation:** Use `agents.defaults.sandbox.docker.setupCommand` to install binaries in container

---

## 7. NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] What is exact validation difference between "strict" schema and "lenient" fallback? **[MED]**
- [ ] Can `$include` paths use symlinks? **[LOW]**
- [ ] What happens when two `$include` files define the same top-level key? **[MED]**

### b) Internal Mechanics
- [ ] Does `openclaw config schema` include plugin/channel schemas dynamically? **[HIGH]**
- [ ] What is exact order of `$include` merge (depth-first vs breadth-first)? **[MED]**
- [ ] Can SecretRef resolve from other SecretRef? **[MED]**
- [ ] What is the `config.schema.lookup` output format exactly? **[LOW]**

### c) Security
- [ ] Is there a built-in config audit log (who changed what)? **[HIGH]**
- [ ] Can malicious `$include` file escape directory boundary via symlink? **[HIGH]**
- [ ] Does `logging.redactPatterns` regex support有什么限制？ **[MED]**
- [ ] Are auth profiles encrypted at rest in `<agentDir>/auth-profiles.json`? **[MED]**
- [ ] Can a compromised config overwrite gateway-level security settings? **[HIGH]**

### d) Performance
- [ ] What is the memory impact of large `openclaw.json` with many `$include` files? **[LOW]**
- [ ] Does hot reload watch every `$include` file or just main config? **[MED]**
- [ ] What is the startup time impact of many secrets to resolve? **[LOW]**

### e) Tools & Automation
- [ ] Can `openclaw config` CLI export config as SecretRef-free (for sharing)? **[MED]**
- [ ] Is there an `openclaw config diff` command to compare configs? **[MED]**
- [ ] Can `openclaw config validate` be run without starting Gateway? **[MED]**
- [ ] Does `pnpm config:docs:check` run in CI automatically? **[LOW]**

### f) Integrations
- [ ] Can `$include` pull from remote URLs (http/https)? **[MED]**
- [ ] Is there a Vault provider template for secrets resolution? **[MED]**
- [ ] Can `auth.profiles` use SecretRef for `api_key` mode? **[HIGH]**
- [ ] Are there channel-specific config `$include` patterns? **[LOW]**

### g) Skills Config
- [ ] Can workspace skills override bundled skill binary requirements? **[MED]**
- [ ] What is exact precedence when skill exists in multiple locations? **[HIGH]**
- [ ] Can skills be dynamically enabled/disabled without restart? **[MED]**
- [ ] Does skills watcher handle rapid multi-file edits correctly? **[MED]**

### h) Troubleshooting
- [ ] What is the exact error message for "schema validation failed"? **[LOW]**
- [ ] How to recover from corrupted `openclaw.json`? **[MED]**
- [ ] Does `openclaw doctor --fix` ever make things worse? **[MED]**
- [ ] Can Gateway start with ONLY `$schema` key (all other config omitted)? **[MED]**

### i) Edge Cases
- [ ] What happens when `maxFileBytes` is set to 0? **[MED]**
- [ ] Can config hot reload trigger infinite restart loop? **[MED]**
- [ ] What is interaction between `skills.allowBundled` and per-agent `skills[]` allowlists? **[HIGH]**
- [ ] Does config merge preserve ordering of array items? **[MED]**

---

## 8. SOURCES

### Primary Sources (OpenClaw Docs)

1. `/usr/local/lib/node_modules/openclaw/docs/gateway/configuration-reference.md` — Full field-level config reference (3742 lines)
2. `/usr/local/lib/node_modules/openclaw/docs/gateway/configuration.md` — Task-oriented config overview
3. `/usr/local/lib/node_modules/openclaw/docs/gateway/configuration-examples.md` — Complete copy-paste configs
4. `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — Skills config schema + examples
5. `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills loading, precedence, gating rules
6. `/usr/local/lib/node_modules/openclaw/docs/tools/creating-skills.md` — Building custom skills
7. `/usr/local/lib/node_modules/openclaw/docs/reference/memory-config.md` — Memory search config reference
8. `/usr/local/lib/node_modules/openclaw/docs/cli/config.md` — CLI config commands
9. `/usr/local/lib/node_modules/openclaw/docs/cli/configure.md` — Interactive config wizard
10. `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hooks (related config under `hooks.internal`)

### Internal Sources (from this workspace)

11. `Research/OpenClaw/index.md` — Research index showing L26: OpenClaw Config System as pending
12. `Research/OpenClaw/findings/openclaw-hooks-system.md` — Hooks system (related config under `hooks.internal`)
13. `Research/OpenClaw/findings/extension-security-model.md` — Extension security model (related to secrets/config access)

### Key Findings Summary

| Aspect | Finding |
|--------|---------|
| Config format | JSON5, strict schema validation, unknown keys fail startup |
| Config location | `~/.openclaw/openclaw.json` |
| Hot reload | Yes, Gateway watches file; some changes need restart |
| Includes | `$include` with deep-merge, up to 10 levels, must stay in config dir |
| SecretRef | 3 sources: env/file/exec; resolved at activation, not per-request |
| Schema tooling | `openclaw config schema`, `config.schema.lookup`, `pnpm config:docs:check` |
| Per-agent config | `agents.list[].skills[]` replaces defaults (doesn't merge) |
| Skills locations | 6 locations with precedence: workspace > .agents > ~/.agents > ~/.openclaw > bundled > extraDirs |
| Logging | Default `/tmp/openclaw/openclaw-YYYY-MM-DD.log`, 500MB max then silent failure |
| Auth profiles | Per-agent at `<agentDir>/auth-profiles.json`, OAuth + SecretRef NOT supported |
| OTEL | Built-in OTEL export via `diagnostics.otel` config |
| Control UI | http://127.0.0.1:18789 Config tab with live schema form |

---

*Research by: Investigador Scout*  
*Date: 2026-04-23 03:45 CET*  
*Status: COMPLETE*