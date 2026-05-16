# Questions — OpenClaw Research

## OpenClaw Hooks System (NEW RESEARCH COMPLETED 2026-04-23)

### a) Definition & Scope
- [x] What is exact difference between internal hooks (5) vs plugin hooks (28+)? → TWO SYSTEMS: Internal=standalone dirs (4 bundled, registration order, NO prompt injection); Plugin=SDK registered (44+ provider runtime hooks, priority-based, controlled via PROMPT_INJECTION_HOOK_NAMES) **[RESOLVED ✅ 2026-04-23]**
- [x] How do workspace hooks (`<workspace>/hooks/`) differ from managed hooks (`~/.openclaw/hooks/`) in discovery precedence? → TWO-PHASE: sort by precedence (bundled<plugin<managed<workspace) then merge by override rules; managed (30) ALWAYS wins over workspace (40); workspace.canOverride=workspace only **[MED — RESOLVED 2026-04-23]**
- [x] What's the practical difference between `openclaw-managed` (extraDirs) and `openclaw-managed` (managedHooksDir)? → Both have same source identifier but different loading mechanisms; extraDirs from config, managedHooksDir from ~/.openclaw/hooks/ **[LOW — NEW]**
- [ ] Can a workspace hook be promoted to managed status? → No automatic migration path **[LOW]**
- [ ] Is there a hook naming collision detection tool? → `openclaw hooks status` shows conflicts but doesn't prevent them **[MED]**
- [ ] What happens when a plugin ships a hook with same name as a bundled hook? → Plugin (20) can override bundled (10) **[MED]**
- [x] What is `PROMPT_INJECTION_HOOK_NAMES` and which 2 hooks are in it? → `before_prompt_build` + `before_agent_start` only **[HIGH]**
- [ ] Can plugin hooks be dynamically registered/unregistered at runtime? **[MED]**
- [x] Can plugin hooks be dynamically registered/unregistered at runtime? → NO - plugin hooks tied to plugin lifecycle; no public API; internal hooks have register/unregister but only used during plugin load/unload; no dynamic runtime changes **[MED — RESOLVED 2026-04-23]**
- [ ] What is the exact difference between `before_install` and `after_install` hooks? **[LOW]**
- [ ] Can internal hooks use priority values like plugin hooks? **[LOW]**
- [ ] What happens when multiple plugins register for same claiming hook? **[MED]**

### b) Internal Mechanics
- [x] What is exact hook execution order when multiple hooks fire on same event? → Two-level sort: source precedence (bundled<plugin<managed<workspace) then priority+index; three execution modes: void (parallel), modifying (sequential+merge), claiming (first-wins) **[RESOLVED ✅ 2026-04-23]**
- [x] How does PROMPT_INJECTION_HOOK_NAMES provide security guarantees? → Only 2 hooks get prompt injection context **[HIGH]**
- [ ] Can hooks modify the `bootstrapFiles` array in agent:bootstrap event (dangerous)? → YES, documented **[MED]**
- [x] What happens when hook removes MEMORY.md from bootstrapFiles array? → Agent loses all persistent memory **[HIGH]**
- [ ] Are hook execution times logged anywhere? Can performance be tracked? **[LOW]**
- [ ] What is max recommended handlers per hook before performance degrades? **[LOW]**
- [ ] Can hook execution order be traced at runtime without debug mode? **[LOW]**
- [ ] Can plugins from different sources enforce ordering constraints? **[MED]**
- [ ] What happens to in-flight hook executions when gateway restarts? **[LOW]**
- [ ] Is there a performance benchmark for hook overhead? **[LOW]**
- [ ] Does claim-first-wins pattern support priority among claiming hooks? **[MED]**

### c) Use Cases
- [ ] Can hooks implement custom authentication/authorization flows? **[MED]**
- [ ] Maximum hooks per event before performance degrades? **[LOW]**
- [ ] Can hooks read/write to session store directly? What are risks? **[MED]**
- [ ] Can hooks trigger subagent runs? What are limitations? **[MED]**
- [ ] Can hooks implement rate limiting or throttling? **[MED]**

### d) Best Practices
- [ ] What happens if hook handler throws uncaught exception - does it crash gateway? **[MED]**
- [x] Can hooks access gateway internal state (session store, config)? → YES - via context.cfg (full gateway config including all secrets) and context.sessionEntry (session metadata); no direct file system access to session store **[MED — RESOLVED 2026-04-23]**
- [ ] Should llm_input/llm_output always use fire-and-forget? **[HIGH]**
- [ ] Is there a recommended pattern for hook error handling and logging? **[MED]**
- [ ] Can hooks safely use async/await or should they be synchronous? **[LOW]**

### e) Problems & Limitations
- [ ] Is there a known issue with hook discovery not working after config hot-reload? **[MED]**
- [x] before_agent_start deprecation status - does it still work or is it broken? → Still works, legacy warning only **[HIGH]**
- [ ] Does gateway restart kill in-flight hooks? Is there cleanup guarantee? **[MED]**
- [ ] What happens when workspace hook has same name as bundled hook? **[MED]**
- [ ] Are there memory leaks from hook handlers not properly cleaning up? **[MED]**

### f) Solutions & Workarounds
- [ ] What's recommended approach for hook-to-hook communication? **[LOW]**
- [ ] Can hooks be dynamically enabled/disabled without gateway restart? **[MED]**
- [ ] How to chain hooks to ensure execution order? **[MED]**
- [ ] What's the best way to debug hook execution? **[MED]**

### g) Edge Cases
- [x] What happens when hook removes MEMORY.md from bootstrapFiles array? → Agent loses memory for entire session **[HIGH]**
- [x] Can hooks trigger infinite loops (hook A → hook B → A)? Is there protection? → **NO protection exists**; session:patch direct recursion, message cascade loops, compaction cycles; guard counter patterns needed **[HIGH]**
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

## PRIOR TOPICS (RESOLVED)

### Watchdog Timeout Root Cause
- [RESOLVED] Cron spin loop bug (PR #66019/#66083) + session route pollution (PR #66073) — Fixed in v2026.4.12

### Sessions OOM Prevention
- [RESOLVED] PR #69404 enforces load-time maintenance + prune by default — Fixed in v2026.4.12

### MCP STDIO RCE
- [RESOLVED] Only notebooklm stdio server active; LOW risk; STDIO exec is intentional design

### Hook System
- [RESOLVED] 4 bundled internal hooks + 28+ plugin hooks; PROMPT_INJECTION_HOOK_NAMES restricts prompt context; before_agent_start deprecated
- Full findings: `Research/OpenClaw/findings/openclaw-hooks-system.md`

### Vault Memory
- [RESOLVED] Not configured in current setup

---

*Last updated: 2026-04-23 01:30 CET*
*Research by: Investigador Scout*

---

## NEW: Custom Pi Extensions (L19-L21) — Research Complete 2026-04-23

### L19 — Custom Pi Extensions ✅
- [x] What are pi-hooks vs gateway hooks — pi-hooks operate INSIDE Pi agent runtime (not gateway layer) **[HIGH]**
- [x] Two built-in extensions: compaction-safeguard (compaction quality) + context-pruning (cache-ttl microcompact) **[HIGH]**
- [x] Loaded via additionalExtensionPaths → ResourceLoader.reload() → ExtensionAPI callbacks **[HIGH]**
- [x] Extension API from @mariozechner/pi-coding-agent (internal package, not public) **[MED]**
- [x] session-manager-runtime-registry allows per-session state sharing **[MED]**
- [x] How to create: compile to JS, export default function(api), add to additionalExtensionPaths **[MED]**
- [x] Extensions affect in-memory context only (not session JSONL file) **[MED]**
- ✅ COMPLETADO (2026-04-23 01:55)

### L20 — Hook Security Audit ✅
- [x] ¿Pueden los hooks acceder a datos sensibles de otros plugins? → SÍ, via context.cfg **[HIGH]**
- [x] ¿Hay auditoría de acceso a credenciales via hooks? → NO, no existe **[MED]**
- [x] ¿Cuál es el security model para workspace hooks vs managed hooks? → Ambos tienen el mismo privilegio que core **[HIGH]**
- [x] ¿Pueden plugins maliciosos usar hooks para exfiltración? → SÍ, acceso completo a context.cfg **[HIGH]**
- [x] Mitigaciones existentes en el código → Minimal: solo PROMPT_INJECTION_HOOK_NAMES **[MED]**
- [x] Hooks ejecutan IN-PROCESS, NO sandboxed → Riesgo crítico **[CRITICAL]**
- [x] Can hooks access environment variables with secrets? → SÍ, via config env injection **[HIGH]**
- [x] Audit logging for hook execution? → NO, none **[CRITICAL]**
- ✅ COMPLETADO (2026-04-23 02:00) — Full findings: `Research/OpenClaw/findings/hook-security-audit.md`

### L21 — ExtensionAPI Callback Reference
- [ ] ¿Cuáles son los métodos exactos de ExtensionAPI (onCompactionStart, etc)? **[HIGH]**
- [ ] ¿Se puede hacer hot-reload de extensiones sin reiniciar? **[MED]**
- [ ] ¿Hay memory leaks en session-runtime-registry? **[MED]**
- [ ] ¿Pueden extensiones comunicar entre sí via shared state? **[LOW]**
- [ ] ¿Qué pasa cuando una extensión lanza excepción? **[MED]**
- [ ] ¿Pueden extensiones modificar la tool list dinámicamente? **[MED]**
- Pendiente de investigación

### L22 — Skill Dynamic Activation from Hooks
- [ ] ¿Pueden los hooks activar skills dinámicamente en tiempo de ejecución? **[MED]**
- [ ] Integración hook-skill para compliance en tiempo real **[MED]**
- [ ] ¿Se puede hacer skill activation basada en contexto de sesión? **[LOW]**
- Pendiente de investigación

### L21 — ExtensionAPI Callback Reference ✅
- [x] ExtensionAPI source: @mariozechner/pi-coding-agent (internal v0.64.0) **[HIGH]**
- [x] 30+ events: session/agent/turn/message/tool/model **[HIGH]**
- [x] Tool registration via api.registerTool() **[HIGH]**
- [x] Provider registration via api.registerProvider() **[HIGH]**
- [x] Extensions affect in-memory context ONLY (NOT JSONL on disk) **[CRITICAL]**
- [x] No hot reload — requires Gateway restart **[MED]**
- [x] Memory leak risk in session-manager-runtime-registry **[MED]**
- [x] Full ExtensionAPI reference documented (30+ page types, 15+ API methods) **[HIGH]**
- ✅ **COMPLETADO** (2026-04-23 02:15) — Full findings: `findings/extension-api-callback-reference.md`

### L22 — Extension to Extension Communication ✅
- [x] Can extensions communicate via EventBus? → SÍ, all extensions share same EventBus instance **[HIGH]**
- [x] Can extensions share session state via registry? → SÍ, via runtime.appendEntry() to session store **[MED]**
- [x] Is there priority ordering for handlers? → NO, insertion order only **[MED]**
- [x] Handler chaining: handler returning non-undefined replaces payload for next handler **[HIGH]**
- [x] Error isolation: each handler wrapped in try/catch individually **[HIGH]**
- [x] 20+ event types: session/agent/turn/message/tool/model lifecycle events **[MED]**
- [x] No pub/sub acknowledgment: publishing extension has no way to know if handled **[MED]**
- [x] Session-scoped: events don't persist across sessions **[LOW]**
- ✅ **COMPLETADO** (2026-04-23 03:30) — Full findings: `findings/extension-to-extension-communication.md`


### L25 — Extension Security Model ✅
- [x] Are extensions sandboxed from each other? → NO, no sandboxing, in-process with full Gateway privileges **[HIGH]**
- [x] Can extensions access process.env directly? → SÍ, inherit Gateway process env including secrets **[HIGH]**
- [x] Can malicious extension crash Gateway? → SÍ, unhandled exceptions can crash Gateway **[HIGH]**
- [x] Is there a permission system for extensions? → NO, no permission model **[MED]**
- [x] Extensions can read context.cfg with ALL secrets/credentials via ExtensionContext **[CRITICAL]**
- [x] Extensions inherit OS-level permissions of Gateway process **[HIGH]**
- [x] No memory isolation between extensions **[CRITICAL]**
- [x] No audit logging for extension execution or credential access **[CRITICAL]**
- ✅ **COMPLETADO** (2026-04-23 03:30) — Full findings: `findings/extension-security-model.md`

---

## L26 — OpenClaw Config System ✅
- [x] What is JSON5 config format + strict schema validation? → JSON5 with STRICT validation, unknown keys fail startup **[HIGH]**
- [x] What is `$include` directive for config splitting? → Deep-merge up to 10 levels, must stay in config directory **[HIGH]**
- [x] What is SecretRef system? → 3 sources (env/file/exec), resolved at activation, active-surface filtering **[HIGH]**
- [x] What are config editing methods? → CLI (`config get/set/unset`), Control UI, direct edit; hot reload most changes **[HIGH]**
- [x] What is skills load precedence (6 locations)? → workspace > .agents > ~/.agents > ~/.openclaw > bundled > extraDirs **[HIGH]**
- [x] What is auth profile storage? → Per-agent at `<agentDir>/auth-profiles.json`; OAuth + SecretRef NOT supported **[HIGH]**
- [x] What is logging file default + max size? → `/tmp/openclaw/openclaw-YYYY-MM-DD.log`; 500MB max then silent failure **[HIGH]**
- [x] What is schema tooling? → `openclaw config schema`, `config.schema.lookup`, `pnpm config:docs:check` **[MED]**
- [x] What config changes require restart? → Hooks, plugins, sandbox mode; most other changes hot reload **[MED]**
- [x] Is there config audit log? → NO, no built-in audit logging for config changes **[HIGH]**
- [x] Can workspace skills override bundled skill binary requirements? → YES, workspace wins precedence **[MED]**
- [x] What happens when per-agent skills list is explicit? → REPLACES defaults (does not merge) **[HIGH]**
- [x] Can `$include` escape config directory via `../`? → Only if still inside `~/.openclaw/` boundary **[HIGH]**
- [x] Does `logging.redactPatterns` regex have limits? → Standard JS regex; redactSensitive only affects tools **[MED]**
- [x] Are auth profiles encrypted at rest? → NO, stored as plaintext JSON **[MED]**
- ✅ **COMPLETADO** (2026-04-23 03:45) — Full findings: `findings/openclaw-config-system.md`

## L27 — OpenClaw Skill System ✅
- [x] What is a skill in OpenClaw? → Versioned bundle of files teaching agent how/when to use tools; SKILL.md with YAML frontmatter + markdown instructions **[HIGH]**
- [x] What is skills load precedence (6 locations)? → workspace > .agents > ~/.agents > ~/.openclaw > bundled > extraDirs **[HIGH]**
- [x] How does skills snapshot mechanism work? → Per-session at load time; watcher can refresh mid-session on SKILL.md change **[HIGH]**
- [x] What is environment injection for skills? → `skills.entries.<key>.env` injected to host process for agent run; sandbox does NOT inherit host process.env **[HIGH]**
- [x] What is skill allowlist per-agent? → `agents.defaults.skills` baseline; `agents.list[].skills: []` = no skills; explicit list REPLACES defaults **[HIGH]**
- [x] What is skills token overhead? → 195 base chars + 97 chars/skill + XML-escaped field lengths; ~4 chars/token estimate **[MED]**
- [x] Can plugins ship skills? → YES via `openclaw.plugin.json` skills array; lowest precedence (overridden by all) **[MED]**
- [x] What is ClawHub skill lifecycle? → `clawhub install` → workspace; `clawhub sync --all` → backup/publish; `--version` for pinning **[MED]**
- [x] What are skill security risks? → Skills run in-process (like hooks/plugins); third-party skills = untrusted code; `apiKey`/`env` goes to HOST process **[CRITICAL]**
- [x] Can sandboxed sessions use skill env injection? → Only via `agents.defaults.sandbox.docker.env` or custom image; NOT from host process.env **[HIGH]**
- [x] What are skill metadata gating filters? → `requires.bins`, `requires.anyBins`, `requires.env`, `requires.config`, `os`, `always` **[MED]**
- [x] What is skill watcher debounce? → Default 250ms via `skills.load.watchDebounceMs`; applies to all skill folders **[MED]**
- [x] What happens on skill name conflict? → Highest precedence wins (workspace overrides all) **[MED]**
- [x] What is `command-dispatch: tool` in skills? → Slash command bypasses model, dispatches directly to tool with `{command, commandName, skillName}` **[MED]**
- [x] Can skills declare custom skillKey for config? → YES via `metadata.openclaw.skillKey` override **[LOW]**
- [x] What is `disable-model-invocation: true`? → Skill excluded from model prompt but still available via user invocation **[MED]**
- [x] What is skills watcher behavior on nested dirs? → Watches skill folders; triggers snapshot refresh when SKILL.md changes **[MED]**
- [x] Can skills implement persistent state? → Only via file-based mechanism; no native state persistence **[MED]**
- [x] What is `skills.install.nodeManager` scope? → Affects skill installs only; Gateway still Node (bun not recommended for WhatsApp/Telegram) **[LOW]**
- ✅ **COMPLETADO** (2026-04-23 04:25) — Full findings: `findings/openclaw-skill-system.md`

---

## NEW RESEARCH QUESTIONS (from Skill System research 2026-04-23)

### a) Definition & Scope
- [ ] Can skills declare dependencies on other skills (skill chaining)? **[MED]**
- [x] What is maximum recommended number of skills per agent before context overhead becomes problematic? → ~50-100 (conservative), ~200 (aggressive) for MiniMax M2.7; 24-45 tokens/skill **[MED — RESOLVED 2026-04-23]**
- [x] Can skills be dynamically enabled/disabled mid-session without gateway restart? → **YES** with watcher + SKILL.md changes (picked up next turn), or config hot-reload; watcher only monitors SKILL.md files; `disableModelInvocation` for soft-disable; no per-session toggle **[MED — RESOLVED 2026-04-23]**
- [ ] What is recommended skill description length to minimize overhead? **[MED]**
- [x] Can per-agent skill allowlists be changed dynamically via hook? → **NO** — hook fires AFTER skills snapshot is built; can only modify system prompt fields; config changes affect NEXT turn only **[MED — RESOLVED 2026-04-23]
- [ ] Can skills overhead be profiled in production? **[MED]**


### b) Internal Mechanics
- [ ] How does skills watcher handle nested directory changes (subdirectories)? **[LOW]**
- [ ] What triggers skills snapshot refresh — only SKILL.md changes or any file in skill directory? **[LOW]**
- [x] Can skills declare dependencies on other skills (skill chaining)? → **NO native dependency system exists**; no `dependencies` field; skills are TEXT only; model executes via slash commands; no automatic resolution **[MED — RESOLVED 2026-04-23]**
- [x] Can skills call other skills recursively? → **NO technical blocking**; skills are TEXT instructions to model; model may invoke via slash commands; no recursion counter or stack limit; potential infinite loops if model follows recursive instructions **[MED — RESOLVED 2026-04-23]**
- [ ] Can two skills with same name be loaded from different locations simultaneously? **[LOW]**

### c) Use Cases
- [ ] Can skills implement persistent state across sessions (file-based)? **[MED]**
- [ ] Can skills call other skills recursively? **[MED]**
- [ ] What is recommended pattern for skill that generates other skills? **[MED]**

### d) Best Practices
- [ ] What happens if skill's `requires.bins` binary exists on host but not in sandbox? **[MED]**
- [ ] Can skills use `skills.entries.<skill>.env` for secrets already in `process.env`? **[MED]**
- [ ] Should skills that need API keys prefer `apiKey` or `env` injection? **[LOW]**


### e) Problems & Limitations
- [ ] Is there known issue with skills watcher consuming excessive CPU on large directories? **[MED]**
- [ ] Does skills snapshot refresh trigger compaction or memory flush? **[MED]**
- [x] Can malicious skill bypass dangerous-code scanner for skill installs? → Scanner blocks Gateway-backed installs; CLI path bypasses scanner but also bypasses installer execution; real risk is post-install skill running with agent privileges **[HIGH - RESOLVED 2026-04-23]**

### NEW RESEARCH QUESTIONS (from Skills Dynamic Enable/Disable research 2026-04-23)
- [x] Can hooks dynamically modify the skills list at runtime (without config change)? → **NO direct API**; `before_prompt_build` fires AFTER snapshot decision; changes affect NEXT turn only **[MED — RESOLVED 2026-04-23]**
- [x] Is there a tool command to reload skills without file changes? → **NO** — workarounds: `touch SKILL.md`, rename folder, config hot-reload for enable/disable **[MED — RESOLVED 2026-04-23]**
- [x] What happens to in-flight skill executions when SKILL.md is deleted? → In-flight turn completes; next turn excludes skill; model cannot re-read deleted SKILL.md **[MED — RESOLVED 2026-04-23]**
- [x] Can skills be enabled/disabled per-session (not just global to workspace)? → **NO per-session toggle**; changes are global to workspace **[MED — RESOLVED 2026-04-23]**
- [x] Does config hot-reload apply to `skills.entries` changes? → **YES** for enable/disable/env/apiKey; NO for extraDirs/watch (require restart) **[MED — RESOLVED 2026-04-23]**

### f) Solutions & Workarounds
- [x] Are skills sandboxed post-install or do they run with full agent privileges? → NO sandboxing — skills are TEXT that influences model; sandbox applies only to TOOL EXECUTION; skill sandboxing is R-002 in threat model (not implemented) **[HIGH — RESOLVED 2026-04-23]**
- [x] What sandboxing options exist for skills? → Tool-level sandbox (docker/ssh/openshell) exists; skill-level sandbox does NOT; skills instruct model which uses tools within sandbox constraints **[HIGH — RESOLVED]**
- [x] Does dangerous-code scanner re-run on skill updates or only on fresh installs? → ONLY on fresh Gateway-backed installs (openclaw skills install, Skills UI); CLI installs (clawhub, update --all) bypass scanner **[MED-HIGH — RESOLVED]**


### f) Solutions & Workarounds
- [ ] Can skills implement their own sandboxing via skill-level Docker execution? **[MED]**
- [ ] What's best way to debug skill loading issues? **[MED]**
- [ ] Can skills be loaded from remote URLs (not local files)? **[MED]**


### g) Edge Cases
- [ ] What happens when skill name conflicts with built-in tool name? **[MED]**
- [ ] Can skills declare `metadata.openclaw.requires.config` for config paths that don't exist? **[LOW]**
- [ ] What happens to in-flight agent runs when skills snapshot refreshes mid-session? **[MED]**
- [ ] Can a skill with no installer metadata still execute malicious code via SKILL.md content at load/invoke time? **[MED]**
- [ ] What is the complete list of patterns the dangerous-code scanner detects? **[MED — useful for red-teaming]**

### h) Creative Uses
- [ ] Could skills implement real-time collaboration protocol (shared skills across users)? **[LOW]**
- [ ] Can skills be used as plugin system (skills that register new tools/hooks)? **[MED]**
- [ ] Could TERRACOTTA business procedures be encoded as skills for consistent execution? **[HIGH — business relevance]**
- [ ] Can organizations implement custom scanner integration via `before_install` hooks with different pattern sets? **[MED]**

---

## L30 — Skills Sandbox & Post-Install Privilege Model ✅ (2026-04-23)
- [x] Are skills sandboxed post-install or do they run with full agent privileges? → NO sandboxing exists; skills are text that influence model; real sandboxing applies to TOOLS only; R-002 in threat model; apiKey/env injection goes to HOST not sandbox **[HIGH]**
- [x] What sandboxing options exist for skills? → Tool-level sandbox exists; skill-level sandbox does NOT; skills can instruct model which then uses tools within sandbox constraints **[HIGH]**
- [x] What happens to skills.entries.<skill>.apiKey in sandboxed sessions? → Injected to HOST process.env, NOT to Docker container; sandbox does NOT inherit host env **[HIGH]**
- [x] Does scanner re-run on skill updates or only on fresh installs? → ONLY on fresh Gateway-backed installs; CLI installs (clawhub, update --all) bypass scanner **[HIGH]**
- [x] Can skill instruct model to bypass sandbox? → Skill text doesn't "run" — it instructs model; model calls tools; sandbox applies to tool execution; skill influence itself is not sandboxed **[HIGH]**
- [x] Is there audit trail linking tool calls to skills that instructed them? → NO; skill content is in system prompt; no correlation mechanism exists **[MED]**
- [x] Could sandbox + tool policy + exec approvals approximate skill sandboxing? → YES as defense-in-depth; treat untrusted skills as untrusted code equivalent **[HIGH]**
- [x] Does scanner analyze SKILL.md content or only installer metadata? → Unknown — needs further research (L31) **[HIGH]**
- [x] Can a skill with no installer metadata still execute malicious code via SKILL.md content? → SKILL.md content enters system prompt; skill instructs model; model calls tools; sandbox/policy/approvals apply to tools; no direct code execution **[MED]**
- ✅ **COMPLETADO** (2026-04-23 05:25) — Full findings: `findings/skills-sandbox-post-install.md`

---

## L31 — Scanner Scope: SKILL.md vs Installer Metadata ✅ (2026-04-23)
- [x] Does the dangerous-code scanner analyze SKILL.md content itself or only installer metadata (install.sh, etc.)? → **NO - SKILL.md NEVER scanned**; scanner only looks at code files (.js/.ts/.jsx/.tsx/.mjs/.cjs/.mts/.cts); this is a CRITICAL security gap **[HIGH — RESOLVED]**
- [x] Can a malicious SKILL.md evade scanner patterns? → **YES - trivially**; SKILL.md is not scanned at all; any malicious instructions embedded in SKILL.md bypass scanner completely **[HIGH — RESOLVED]**
- [x] What is the complete list of patterns the dangerous-code scanner detects? → **8 patterns**: LINE_RULES (dangerous-exec, dynamic-code-execution, crypto-mining, suspicious-network) + SOURCE_RULES (potential-exfiltration, obfuscated-code x2, env-harvesting); SKILL.md NEVER scanned **[MED — RESOLVED]**
- [x] Could SKILL.md scanning be added to the dangerous-code scanner? → YES - extend SCANNABLE_EXTENSIONS to include .md, add MARKDOWN_PATTERNS array with prompt-injection/shell-instruction/credential-request patterns, implement before_install hook for custom scanning **[MED — RESOLVED]**
- ✅ **COMPLETADO** (2026-04-23 05:45) — Full findings: `findings/scanner-skillmd-content-analysis.md`

## L34 — Dangerous-Code Scanner Patterns (Red-Teaming) ✅ (2026-04-23)
- [x] What is the complete list of patterns the dangerous-code scanner detects? → **8 patterns**: LINE_RULES (dangerous-exec, dynamic-code-execution, crypto-mining, suspicious-network) + SOURCE_RULES (potential-exfiltration, obfuscated-code[hex], obfuscated-code[base64], env-harvesting); detailed regex patterns documented **[MED — RESOLVED 2026-04-23]**
- [x] Could SKILL.md scanning be added to the dangerous-code scanner? → YES - proposed implementation: extend SCANNABLE_EXTENSIONS, add MARKDOWN_PATTERNS, use before_install hooks for custom scanning, consider behavioral sandboxing **[MED — RESOLVED 2026-04-23]**
- [x] What bypass techniques exist against current scanner patterns? → YES - dynamic function references (const c="exec"; c()), string concatenation, multi-stage attacks, unicode obfuscation, cross-file context separation **[HIGH — RESOLVED 2026-04-23]**
- ✅ **COMPLETADO** (2026-04-23 07:41) — Full findings: `findings/dangerous-code-scanner-patterns.md`

## L35 — Skills Context Overhead ✅ (2026-04-23)
- [x] What is the maximum recommended number of skills per agent before context overhead becomes problematic? → ~50-100 skills (conservative), ~200 skills (aggressive) for MiniMax M2.7 with 200K context; overhead is ~24-45 tokens/skill depending on description length; formula: 195 base chars + 97 + field lengths per skill **[MED — RESOLVED 2026-04-23]**
- [x] What is the token overhead formula for skills? → total_chars = 195 + Σ(97 + len(name) + len(description) + len(location)); ~4 chars/token → 24-45 tokens/skill **[MED — RESOLVED 2026-04-23]**
- [x] How does per-agent skill allowlists affect overhead? → Only eligible skills appear in list; use `agents.defaults.skills` and `agents.list[].skills` to control **[MED — RESOLVED 2026-04-23]**
- [x] What is recommended skill description length? → Keep under 100 characters to minimize overhead **[MED — RESOLVED 2026-04-23]**
- ✅ **COMPLETADO** (2026-04-23 08:02) — Full findings: `findings/skills-context-overhead.md`

## L36 — Skills Persistent State & Hook Dynamic Modification ✅ (2026-04-23)
- [x] Can skills implement persistent state across sessions (file-based)? → **NO native mechanism**; skills are TEXT only; file-based state via workspace files + skill instructions; race conditions with concurrent sessions; session store stores skillsSnapshot not arbitrary state **[MED — RESOLVED 2026-04-23]**
- [x] Can hooks dynamically modify the skills list at runtime (without config change)? → **NO direct API**; `before_prompt_build` fires AFTER snapshot decision; changes affect NEXT turn only; `session:patch` is read-react only; watcher-based SKILL.md renaming workaround **[MED — RESOLVED 2026-04-23]**
- [x] Is there race condition risk when multiple sessions write same workspace skill state file? → YES — concurrent sessions can corrupt shared state files; per-session state files (state-{sessionKey}.json) mitigate **[MED — RESOLVED 2026-04-23]**
- ✅ **COMPLETADO** (2026-04-23 09:20) — Full findings: `findings/skills-persistent-state-and-hook-dynamic-modification.md`

## NEW RESEARCH QUESTIONS (from Skills Overhead Profiling & Reload research 2026-04-23)
- [ ] Can snapshot version be inspected at runtime without debug mode? **[LOW]**
- [ ] Is there a way to export skills overhead data to external monitoring systems? **[MED]**
- [ ] Can skills overhead be included in `/status` output automatically? **[MED]**
- [ ] Does watcher consume significant CPU on large skill directories? **[LOW]**
- [ ] Is there a known issue where snapshot doesn't refresh after config hot-reload? **[MED]**
- [ ] Can a custom hook simulate `openclaw skills reload` functionality? **[MED]**
- [ ] What's the best way to test skills overhead changes before deploying? **[MED]**
- [ ] Could a skill self-report its overhead via a hook at load time? **[LOW]**
- [ ] Can skills overhead drive automatic skill pruning (remove lowest-use skills)? **[MED]**
