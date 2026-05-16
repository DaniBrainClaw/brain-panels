# Research Sources — OpenClaw

Documented sources for all OpenClaw research conducted by Investigador Scout.

## L38 — Per-Agent Skill Allowlists & Dynamic Hook Modification (2026-04-23)

**Topic:** Can per-agent skill allowlists be changed dynamically via hook?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Skills snapshot building logic (lines 1097-1122)
- `/usr/local/lib/node_modules/openclaw/dist/pi-embedded-runner-CefZK1Pt.js` — `before_prompt_build` hook execution (lines 3573-3588)
- `/usr/local/lib/node_modules/openclaw/dist/agent-scope-D7mk_f98.js` — `resolveAgentSkillsFilter` function (lines 101-103)
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook merge function (`mergeBeforePromptBuild`, lines 54-66)
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation

---

## L28 — Dangerous-Code Scanner for Skill Installs (2026-04-23)

**Topic:** Can malicious skill bypass dangerous-code scanner for skill installs?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — primary source for scanner behavior, Gateway-backed install pipeline, CLI install path difference
- `/usr/local/lib/node_modules/openclaw/docs/gateway/security/index.md` — security model, audit glossary (`skills.code_safety`), trust boundaries
- `/usr/local/lib/node_modules/openclaw/docs/security/THREAT-MODEL-ATLAS.md` — Critical residual risk: "Skills run with agent privileges"
- `/usr/local/lib/node_modules/openclaw/docs/tools/clawhub.md` — CLI install path documentation
- `/usr/local/lib/node_modules/openclaw/docs/tools/plugin.md` — `--dangerously-force-unsafe-install` flag (similar concept for plugins)
- `/usr/local/lib/node_modules/openclaw/docs/gateway/security/index.md` — `skills.code_safety` checkId definition

---

## L29 — Hook Infinite Loops (2026-04-23)

**Topic:** Can hooks trigger infinite loops?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/gateway/hooks.md` — hook system documentation
- OpenClaw source code analysis via exec grep on dist/ directory
- Gateway hook execution internals

---

## L30 — Skills Sandbox & Post-Install Privilege Model (2026-04-23)

**Topic:** Are skills sandboxed post-install? What sandboxing options exist?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/security/THREAT-MODEL-ATLAS.md` — Skill sandboxing recommendation R-002, "Skills run with agent privileges" residual risk
- `/usr/local/lib/node_modules/openclaw/docs/gateway/sandboxing.md` — Sandboxing architecture, shows sandbox applies to tools, not skill text
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — Skills config, env injection behavior, sandbox interaction notes
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Scanner behavior, install paths, Gateway-backed vs CLI

---

## L31 — Scanner Scope: SKILL.md vs Installer Metadata (2026-04-23)

**Topic:** Does the dangerous-code scanner analyze SKILL.md content itself or only installer metadata?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/skill-scanner-DKzA4y0J.js` — Scanner implementation: `SCANNABLE_EXTENSIONS` = .js/.ts/.jsx/.tsx/.mjs/.cjs/.mts/.cts (NOT .md); `scanSource()` applies LINE_RULES + SOURCE_RULES
- `/usr/local/lib/node_modules/openclaw/dist/install-security-scan.runtime-5cdnayzJ.js` — `scanSkillInstallSourceRuntime()` calls `scanDirectoryTarget()` which only scans code files
- `/usr/local/lib/node_modules/openclaw/dist/skills-install-BOrVGZan.js` — Skill install flow: `scanSkillInstallSource({ sourceDir: entry.skill.baseDir })`
- `/usr/local/lib/node_modules/openclaw/dist/audit-extra.async-GfHD3ETo.js` — `collectInstalledSkillsCodeSafetyFindings()` uses same scanner; SKILL.md only collected for symlink-escape checks, NOT content scanning
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills documentation: scanner runs on Gateway-backed installs only

---

## L32 — Skills Dependencies & Chaining (2026-04-23)

**Topic:** Can skills declare dependencies on other skills? Can skills call each other recursively?


**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skill loading, precedence, gating rules, no dependency system
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — Skill config schema
- `/usr/local/lib/node_modules/openclaw/docs/tools/creating-skills.md` — Skill creation workflow
- `/usr/local/lib/node_modules/openclaw/docs/tools/slash-commands.md` — Slash command dispatch for skill invocation
- OpenClaw source code analysis — skills snapshot mechanism, skill invocation flow

---

## Previous Sources

(Research sources for L20-L27 documented in their respective findings files.)

## L16 — Hook Execution Order (2026-04-23)

**Topic:** What is exact hook execution order when multiple hooks fire on same event?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/config-Nq7s3Dxw.js` — Hook source policy definitions (`HOOK_SOURCE_POLICIES`), precedence system, sorting algorithm
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook execution runner: `runVoidHook`, `runModifyingHook`, `runClaimingHook`, `getHooksForName`, priority sorting, failure policy
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation: registration order, error handling
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Official hooks documentation

## L14 — Hook Types Difference: Internal vs Plugin Hooks (2026-04-23)

**Topic:** What is exact difference between internal hooks (5) vs plugin hooks (28+)?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Internal hooks documentation
- `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin architecture, provider runtime hooks (44+ hooks table)
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook execution runner implementation
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation
- `/usr/local/lib/node_modules/openclaw/dist/loader-DuIH27tS.js` — Hook registry: `registry.typedHooks.push()`

---

## L35 — Skills Context Overhead (2026-04-23)

**Topic:** What is the maximum recommended number of skills per agent before context overhead becomes problematic?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills overhead formula: 195 base chars + 97 chars/skill + XML-escaped field lengths
- `/usr/local/lib/node_modules/openclaw/docs/reference/token-use.md` — Token use breakdown, context window mechanics
- `/usr/local/lib/node_modules/openclaw/docs/concepts/system-prompt.md` — System prompt structure, skills section
- `/usr/local/lib/node_modules/openclaw/docs/concepts/context.md` — Context window vs tracked tokens
- `/usr/local/lib/node_modules/openclaw/docs/concepts/model-providers.md` — Model contextWindow metadata
- `~/.openclaw/openclaw.json` — Current system config (MiniMax M2.7: 204,800 contextWindow, 200,000 runtime cap)

## L36 — Skills Dynamic Enable/Disable (2026-04-23)

**Topic:** Can skills be dynamically enabled/disabled mid-session without gateway restart?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills watcher documentation (line 317+)
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — `enabled` and `disableModelInvocation` fields
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher implementation
- `/usr/local/lib/node_modules/openclaw/dist/skills-DYF-hmoJ.js` — Snapshot building logic

## L34 — Dangerous Code Scanner Patterns (Red-Teaming) (2026-04-23)

**Topic:** What is the complete list of patterns the dangerous-code scanner detects? What bypass techniques exist?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/skill-scanner-DKzA4y0J.js` — Scanner implementation: SCANNABLE_EXTENSIONS, LINE_RULES, SOURCE_RULES
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Scanner behavior documentation
- `/usr/local/lib/node_modules/openclaw/docs/gateway/security/index.md` — Security model, audit glossary

## L33 — Plugin Hook Dynamic Registration + State Access (2026-04-23)

**Topic:** Can plugin hooks be dynamically registered/unregistered at runtime? Can hooks access gateway internal state?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hooks implementation: `registerInternalHook`, `unregisterInternalHook`, `clearInternalHooks`
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Plugin hook runner: no dynamic registration API, `getHooksForName` reads from immutable-at-runtime registry
- `/usr/local/lib/node_modules/openclaw/dist/loader-DuIH27tS.js` — Plugin loader: `registerHook` during plugin load, `unregisterInternalHook` only at plugin unload
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook event context structure (context.cfg, context.sessionEntry)
- `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin architecture, load pipeline, registry model
- `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/src/plugins/types.d.ts` — Plugin SDK types: `registerHook` API (no unregister counterpart)

---

## L26 — Workspace Hooks vs Managed Hooks Discovery Precedence (2026-04-23)

**Topic:** How do workspace hooks (`<workspace>/hooks/`) differ from managed hooks (`~/.openclaw/hooks/`) in discovery precedence?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/workspace-OPw5btC5.js` — `discoverWorkspaceHookEntries()` function (lines 236-271): discovery order, hook loading from 5 sources (extraDirs, bundled, plugin, managed, workspace)
- `/usr/local/lib/node_modules/openclaw/dist/config-Nq7s3Dxw.js` — `resolveHookEntries()`, `canOverrideHook()`, `HOOK_SOURCE_POLICIES` (lines 4-95): two-phase resolution (sort by precedence then merge by override rules), override rules matrix
- `/usr/local/lib/node_modules/openclaw/dist/hooks-cli-DUQiYAeY.js` — Hook collision warning: `"Ignoring openclaw-workspace hook "X" because it cannot override openclaw-managed hook code"`
- `/usr/local/lib/node_modules/openclaw/dist/hooks-status-DvOjzvmc.js` — Hook status display with managed-by-plugin detection
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation

---

## L37 — Skills Persistent State & Hook Dynamic Modification (2026-04-23)
**Topic:** Can skills implement persistent state across sessions (file-based)? Can hooks dynamically modify the skills list at runtime?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/session-updates-3NulUPmS.js` — `persistSessionEntryUpdate` with skillsSnapshot persistence
- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Skills snapshot building and session entry update
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher implementation, `bumpSkillsSnapshotVersion`
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook event types, `before_prompt_build` modifying merge, `session:patch` context
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills loading, watcher behavior
- `/usr/local/lib/node_modules/openclaw/docs/plugins/sdk-runtime.md` — `saveSessionStore` API
- `/usr/local/lib/node_modules/openclaw/dist/skills-DYF-hmoJ.js` — `buildWorkspaceSkillSnapshot` implementation
- `/usr/local/lib/node_modules/openclaw/dist/skills-CUMOpDXe.js` — Skills snapshot related exports
- OpenClaw source code analysis via exec grep on dist/ directory for session management and skills loading

---

## L39 — Skills Overhead Profiling & Reload Mechanisms (2026-04-23)

**Topic:** Can skills overhead be profiled in production? Is there a tool command to reload skills without file changes?

**Sources:**
- `/usr/local/lib/node_modules/openclaw/docs/concepts/context.md` — `/context detail` documentation, per-skill breakdown, context window mechanics
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills snapshot, watcher, hot reload documentation, token overhead formula
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — `skills.entries.*` config fields, hot-reload behavior, watcher config
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher implementation: `watcher.on("add/change/unlink")`, `bumpSkillsSnapshotVersion`
- `/usr/local/lib/node_modules/openclaw/dist/skills-DYF-hmoJ.js` — `buildWorkspaceSkillSnapshot` implementation
- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Snapshot version checking, rebuild logic, `needsSkillsSnapshot` check
- `/usr/local/lib/node_modules/openclaw/dist/commands-handlers.runtime-qpU8MeZd.js` — `/context` command handlers: list/detail/json/deep modes
- `/usr/local/lib/node_modules/openclaw/docs/reference/token-use.md` — Token use reference, `/context` commands
## L41 — Hook Exception Handler Behavior (2026-04-23)
**Topic:** What happens if hook handler throws uncaught exception - does it crash gateway?
**Sources:**
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Plugin hook runner: exception handling, failure policies, `shouldCatchHookErrors`, `handleHookError`, `runVoidHook`, `runModifyingHook`, `runClaimingHook`
- `/usr/local/lib/node_modules/openclaw/dist/internal-hooks-2legcEEL.js` — Internal hook trigger: `triggerInternalHook` with per-handler try/catch
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation
