# Research Backlog — OpenClaw
**Last Updated:** 2026-04-23 08:02 CET

## Priority Queue (Highest → Lowest)

### HIGH Priority
1. **[HOOKS]** ~~Can hooks trigger infinite loops (hook A → hook B → A)? Is there protection?~~ **[RESOLVED ✅ 2026-04-23]** → NO protection exists; session:patch creates direct recursion; solution patterns documented
2. **[SKILLS]** ~~Could TERRACOTTA business procedures be encoded as skills for consistent execution?~~ **[RESOLVED ✅ 2026-04-23]** → YES with Master Skill Pattern; no native dependency system; manual sub-skill installation required
3. **[HOOKS]** ~~Can hooks access environment variables with secrets?~~ **[RESOLVED ✅ 2026-04-23]** → env vars injected only to host process for agent run, not accessible to hooks
4. **[SKILLS]** ~~Can malicious skill bypass dangerous-code scanner for skill installs?~~ **[RESOLVED ✅ 2026-04-23]** → Scanner blocks Gateway-backed installs; CLI bypasses scanner; real risk is post-install skill privileges
5. **[SKILLS]** ~~Does the dangerous-code scanner analyze SKILL.md content itself or only installer metadata?~~ **[RESOLVED ✅ 2026-04-23]** → Scanner ONLY scans code files (.js/.ts/.jsx/.tsx); SKILL.md is NEVER analyzed; critical security gap
6. **[SKILLS]** ~~Are skills sandboxed post-install or do they run with full agent privileges?~~ **[RESOLVED ✅ 2026-04-23]** → NO sandboxing; skills are text; sandboxing applies to TOOLS only; R-002 in threat model
7. **[SKILLS]** ~~Does scanner re-run on skill updates or only on fresh installs?~~ **[RESOLVED ✅ 2026-04-23]** → ONLY on fresh Gateway-backed installs; CLI installs (clawhub) bypass scanner
8. **[SKILLS]** ~~Can a skill with no installer metadata still execute malicious code via SKILL.md content?~~ **[RESOLVED ✅ 2026-04-23]** → YES - SKILL.md content is embedded in system prompt; scanner doesn't analyze it
9. **[SKILLS]** ~~Can skills declare dependencies on other skills (skill chaining)?~~ **[RESOLVED ✅ 2026-04-23]** → NO native dependency system; skills are TEXT only; model executes via slash commands
10. **[SKILLS]** ~~Can skills call other skills recursively?~~ **[RESOLVED ✅ 2026-04-23]** → NO technical blocking; skills are TEXT instructions; no recursion counter; potential infinite loops

### MED Priority
11. **[SKILLS]** ~~What is the complete list of patterns the dangerous-code scanner detects? Useful for red-teaming~~ **[RESOLVED ✅ 2026-04-23]** → 8 patterns: LINE_RULES (dangerous-exec, dynamic-code-execution, crypto-mining, suspicious-network) + SOURCE_RULES (potential-exfiltration, obfuscated-code[hex/base64], env-harvesting)
12. **[SKILLS]** ~~Could SKILL.md scanning be added to the dangerous-code scanner? What patterns would it look for?~~ **[RESOLVED ✅ 2026-04-23]** → YES - proposed implementation: extend SCANNABLE_EXTENSIONS to .md, add MARKDOWN_PATTERNS
13. **[SKILLS]** ~~Can organizations implement custom scanner integration via before_install hooks that scans SKILL.md?~~ **[RESOLVED ✅ 2026-04-23]** → YES via before_install hook; reads SKILL.md directly; returns {block:true} to prevent install; CLI bypass remains
14. **[HOOKS]** ~~What is exact difference between internal hooks (5) vs plugin hooks (28+)?~~ **[RESOLVED ✅ 2026-04-23]** → TWO SYSTEMS: Internal=standalone dirs (4 bundled, registration order, NO prompt injection); Plugin=SDK registered (44+ provider runtime hooks, priority-based, controlled via PROMPT_INJECTION_HOOK_NAMES)
15. **[HOOKS]** ~~Can plugin hooks be dynamically registered/unregistered at runtime?~~ **[RESOLVED ✅ 2026-04-23]** → NO — plugin hooks tied to plugin lifecycle; no public API; internal hooks have register/unregister but only used during plugin load/unload
16. **[HOOKS]** ~~What is exact hook execution order when multiple hooks fire on same event?~~ **[RESOLVED ✅ 2026-04-23]** → Two-level sort: source precedence (bundled<plugin<managed<workspace) then priority+index; three execution modes: void (parallel), modifying (sequential+merge), claiming (first-wins)
17. **[HOOKS]** ~~What happens if hook handler throws uncaught exception - does it crash gateway?~~ **[RESOLVED ✅ 2026-04-23]** → Depends on failure policy: fail-open (log + continue, most hooks) or fail-closed (throw + halt, before_tool_call); handler errors caught individually
18. **[HOOKS]** ~~Can hooks access gateway internal state (session store, config)?~~ **[RESOLVED ✅ 2026-04-23]** → YES — via context.cfg (full config with all secrets) and context.sessionEntry (session metadata); no direct disk access to session store
19. **[SKILLS]** ~~What is maximum recommended number of skills per agent before context overhead becomes problematic?~~ **[RESOLVED ✅ 2026-04-23]** → ~50-100 (conservative), ~200 (aggressive) for MiniMax M2.7; ~24-45 tokens/skill; recommendations documented
20. **[SKILLS]** ~~Can skills be dynamically enabled/disabled mid-session without gateway restart?~~ **[RESOLVED ✅ 2026-04-23]** → YES with watcher + SKILL.md changes (picked up next turn), or config hot-reload; watcher only monitors SKILL.md files; `disableModelInvocation` for soft-disable; no per-session toggle
21. **[SKILLS]** ~~Can skills implement persistent state across sessions (file-based)?~~ **[RESOLVED ✅ 2026-04-23]** → NO native mechanism; skills are TEXT only; file-based state possible via workspace files + skill instructions to read/write; race conditions with concurrent sessions; session store stores skillsSnapshot (not arbitrary state)
22. **[SKILLS]** ~~What is maximum recommended chain depth for skill chaining patterns?~~ **[RESOLVED ✅ 2026-04-23]** → NO recursion counter; model executes via slash commands; no automatic resolution; potential infinite loops if model follows recursive instructions
23. **[SKILLS]** ~~What is recommended skill description length to minimize overhead?~~ **[RESOLVED ✅ 2026-04-23]** → Keep under 100 characters; 195 base chars + 97/skill overhead
41. **[SKILLS]** ~~Can hooks dynamically modify the skills list at runtime (without config change)?~~ **[RESOLVED ✅ 2026-04-23]** → NO direct API; before_prompt_build fires AFTER snapshot decision; changes affect NEXT turn only; watcher-based renaming is workaround
24. **[SKILLS]** ~~Can per-agent skill allowlists be changed dynamically via hook?~~ **[RESOLVED ✅ 2026-04-23]** → NO — hook fires AFTER snapshot built; can only modify systemPrompt/prependContext; config changes affect NEXT turn
25. **[SKILLS]** ~~Can skills overhead be profiled in production?~~ **[RESOLVED ✅ 2026-04-23]** → YES via /context list/detail; NO dedicated profiler command; manual tracking required**

41. **[SKILLS]** ~~Can hooks dynamically modify the skills list at runtime (without config change)?~~ **[RESOLVED ✅ 2026-04-23]** → NO direct API; before_prompt_build fires AFTER snapshot decision; changes affect NEXT turn only; watcher-based renaming is workaround
42. **[SKILLS]** ~~Is there a tool command to reload skills without file changes?~~ **[RESOLVED ✅ 2026-04-23]** → NO dedicated reload command; workarounds: touch SKILL.md, rename folder, config hot-reload for enable/disable**
43. **[SKILLS]** ~~What happens to in-flight skill executions when SKILL.md is deleted?~~ **[RESOLVED ✅ 2026-04-23]** → In-flight turn completes; next turn excludes skill; model cannot re-read deleted SKILL.md**
44. **[SKILLS]** ~~Can skills be enabled/disabled per-session (not just global to workspace)?~~ **[RESOLVED ✅ 2026-04-23]** → NO per-session toggle; changes are global to workspace; new sessions use updated config**
45. **[SKILLS]** ~~Does config hot-reload apply to `skills.entries` changes?~~ **[RESOLVED ✅ 2026-04-23]** → YES for enable/disable/env/apiKey changes; NO for extraDirs/watch settings (require restart)**

### LOW Priority
26. **[HOOKS]** How do workspace hooks differ from managed hooks in discovery precedence? **[MED — RESOLVED ✅ 2026-04-23]**
27. **[HOOKS]** What's recommended approach for hook-to-hook communication? **[MED — RESOLVED ✅ 2026-04-23]**
28. **[SKILLS]** How does skills watcher handle nested directory changes (subdirectories)? **[MED]**
29. **[SKILLS]** What triggers skills snapshot refresh — only SKILL.md changes or any file in skill directory? **[MED]**
30. **[HOOKS]** What is max recommended handlers per hook before performance degrades? **[MED]**
31. **[HOOKS]** Can hook execution order be traced at runtime without debug mode? **[MED]**
32. **[HOOKS]** Can plugins from different sources enforce ordering constraints? **[MED]**
33. **[HOOKS]** What happens to in-flight hook executions when gateway restarts? **[MED]**
34. **[HOOKS]** Is there a performance benchmark for hook overhead? **[MED]**
35. **[HOOKS]** Does claim-first-wins pattern support priority among claiming hooks? **[MED]**
36. **[HOOKS]** Is there any audit logging for hooks accessing `context.cfg`? **[MED]**
37. **[HOOKS]** Can hooks modify gateway configuration at runtime (write-back to cfg)? **[MED]**
38. **[HOOKS]** What is performance impact of passing full config object to every hook? **[MED]**
39. **[HOOKS]** Can workspace hooks be dynamically enabled/disabled per-agent without affecting other agents? **[MED]**
40. **[HOOKS]** Can hooks access session store files directly on disk (not just in-memory context)? **[MED]**
41. **[HOOKS]** Is there a way to scope hook config access to only necessary fields (principle of least privilege)? **[MED]**

### NEW QUESTIONS FROM L26 RESEARCH
42. **[HOOKS]** What's the practical difference between `openclaw-managed` (extraDirs) and `openclaw-managed` (managedHooksDir)? → Both have same source identifier but different loading mechanisms **[LOW]**
43. **[HOOKS]** Can a workspace hook be promoted to managed status? → No automatic migration path **[LOW]**
44. **[HOOKS]** Is there a hook naming collision detection tool? → `openclaw hooks status` shows conflicts but doesn't prevent them **[MED]**
45. **[HOOKS]** What happens when a plugin ships a hook with same name as a bundled hook? → Plugin (20) can override bundled (10) **[MED]**

---

## In Progress
- None currently

## Completed (Recent)
- L41: Hook Exception Handler Behavior ✅ (2026-04-23 12:40)
- L39: Skills Overhead Profiling & Reload Mechanisms ✅ (2026-04-23 11:46)
- L40: Workspace Hooks vs Managed Hooks Discovery Precedence ✅ (2026-04-23 12:30)
- L34: Dangerous Code Scanner Patterns (Red-Teaming) ✅ (2026-04-23 07:41)
- L33: Plugin Hook Dynamic Registration + State Access ✅ (2026-04-23 07:09)
- L14: Hook Types Difference ✅ (2026-04-23 06:48)
- L16: Hook Execution Order ✅ (2026-04-23 06:31)
- L32: Skills Dependencies & Chaining ✅ (2026-04-23 06:15)
- L33: Terracotta Business Procedures as Skills ✅ (2026-04-23 06:15)
- L31: Scanner Scope: SKILL.md vs Installer Metadata ✅ (2026-04-23 05:50)
- L30: Skills Sandbox & Post-Install Privilege Model ✅ (2026-04-23 05:25)
- L27: OpenClaw Skill System ✅ (2026-04-23 04:25)
- L26: OpenClaw Config System ✅ (2026-04-23 03:45)
- L25: Extension Security Model ✅ (2026-04-23 03:30)
- L22: Extension to Extension Communication ✅ (2026-04-23 03:30)

---

## Notes
- backlog.md cleaned up 2026-04-23 06:48 — duplicate entries removed, numbering fixed
- All HIGH priority items now resolved
- Next research candidate: MED #27 (hook-to-hook communication) or MED #28 (skills watcher nested dirs) or MED #30 (hook performance)
