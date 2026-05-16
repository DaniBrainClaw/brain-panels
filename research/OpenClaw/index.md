# OpenClaw Research Index

**Last Updated:** 2026-04-23 13:15 CET

## Completed Research

| ID | Topic | Priority | Date | Findings File |
|----|-------|----------|------|---------------|
| L18 | OpenClaw Hooks System | MEDIUM | 2026-04-23 | `findings/openclaw-hooks-system.md` |
| L19 | Custom Pi Extensions | MEDIUM | 2026-04-23 | `findings/custom-pi-extensions.md` |
| L20 | Hook Security Audit | **HIGH** | 2026-04-23 | `findings/hook-security-audit.md` |
| L21 | ExtensionAPI Callback Reference | HIGH | 2026-04-23 | `findings/extension-api-callback-reference.md` |
| L22 | Extension to Extension Communication | MED | 2026-04-23 | `findings/extension-to-extension-communication.md` |
| L23 | Extension Tool Integration | HIGH | 2026-04-23 | `findings/extension-tool-integration.md` |
| L24 | Extension Provider Integration | MED | 2026-04-23 | `findings/extension-provider-integration.md` |
| L25 | Extension Security Model | HIGH | 2026-04-23 | `findings/extension-security-model.md` |
| L26 | OpenClaw Config System | MED | 2026-04-23 | `findings/openclaw-config-system.md` |
| L27 | OpenClaw Skill System | MED | 2026-04-23 | `findings/openclaw-skill-system.md` |
| L28 | Dangerous-Code Scanner for Skill Installs | **HIGH** | 2026-04-23 | `findings/malicious-skill-bypass-scanner.md` |
| L29 | Hook Infinite Loops | **HIGH** | 2026-04-23 | `findings/hook-infinite-loops.md` |
| L30 | Skills Sandbox & Post-Install Privilege Model | **HIGH** | 2026-04-23 | `findings/skills-sandbox-post-install.md` |
| L31 | Scanner Scope: SKILL.md vs Installer Metadata | **HIGH** | 2026-04-23 | `findings/scanner-skillmd-content-analysis.md` |
| L32 | Skills Dependencies & Chaining | MED | 2026-04-23 | `findings/skill-dependencies-chaining.md` |
| L13 | Custom SKILL.md Scanner via before_install | MEDIUM | 2026-04-23 | `findings/custom-skill-md-scanner.md` |
| L14 | Hook Types Difference: Internal vs Plugin | MED | 2026-04-23 | `findings/hook-internal-vs-plugin-types.md` |
| L16 | Hook Execution Order | MED | 2026-04-23 | `findings/hook-execution-order.md` |
| L33 | Plugin Hook Dynamic Registration + State Access | MED | 2026-04-23 | `findings/plugin-hook-dynamic-registration.md` |
| L34 | Dangerous Code Scanner Patterns (Red-Teaming) | MED | 2026-04-23 | `findings/dangerous-code-scanner-patterns.md` |
| L35 | Skills Context Overhead | MED | 2026-04-23 | `findings/skills-context-overhead.md` |
| L36 | Skills Dynamic Enable/Disable | MED | 2026-04-23 | `findings/skills-dynamic-enable-disable.md` |
| **L37** | **Skills Persistent State & Hook Dynamic Modification** | **MED** | **2026-04-23** | `findings/skills-persistent-state-and-hook-dynamic-modification.md` |
| L38 | Per-Agent Skill Allowlists & Dynamic Hook Modification | MED | 2026-04-23 | `findings/per-agent-skill-allowlists-dynamic-hook.md` |
| **L39** | **Skills Overhead Profiling & Reload Mechanisms** | **MED** | **2026-04-23** | `findings/skills-overhead-profiling-reload.md` |
| **L40** | **Workspace Hooks vs Managed Hooks Discovery Precedence** | **MED** | **2026-04-23** | `findings/workspace-managed-hooks-discovery-precedence.md` |
| **L41** | **Hook Exception Handler Behavior** | **MED** | **2026-04-23** | `findings/hook-exception-handler-behavior.md` |
| **L42** | **Hook-to-Hook Communication** | **MED** | **2026-04-23** | `findings/hook-to-hook-communication.md` |

## Key Security Findings Summary (L20 + L25 + L28 + L30 + L31)

- **CRITICAL**: Hooks run IN-PROCESS with Gateway — NO sandboxing
- **CRITICAL**: Hooks can access `context.cfg` with ALL secrets/credentials
- **CRITICAL**: No audit logging for hook execution or credential access
- **CRITICAL**: Extensions run in-process with NO sandbox isolation
- **CRITICAL**: Extensions can read ALL secrets via ExtensionContext.cfg
- **CRITICAL**: No memory isolation between extensions
- **CRITICAL**: SKILL.md content is NEVER scanned by dangerous-code scanner — scanner only checks .js/.ts/.jsx/.tsx files **[L31]**
- **CRITICAL**: Malicious SKILL.md can instruct model to perform dangerous actions with zero scanner detection **[L31]**
- **HIGH**: `PROMPT_INJECTION_HOOK_NAMES` only restricts 2 hooks from prompt injection
- **HIGH**: `agent:bootstrap` hook can remove MEMORY.md — catastrophic
- **HIGH**: No permission system for extensions
- **HIGH**: Skills run with agent privileges — NO post-install sandboxing **[L30]**
- **HIGH**: CLI `openclaw skills install` bypasses dangerous-code scanner **[L28]**
- **HIGH**: Scanner runs ONLY on fresh Gateway-backed installs; CLI installs bypass scanner **[L30]**
- **HIGH**: `skills.entries.<skill>.apiKey` injects to HOST process.env, NOT to sandbox container **[L30]**
- **HIGH**: Security audit (`openclaw security audit --deep`) also doesn't scan SKILL.md content **[L31]**
- **MEDIUM**: No native skill state persistence — file-based workarounds required **[L37]**
- **MEDIUM**: No hook API to dynamically modify skills list at runtime **[L37]**
- **MEDIUM**: No native hook-to-hook communication API; only sequential modifying hooks with mergeResults **[L42]**
- **MEDIUM**: Per-agent skill allowlists CANNOT be changed dynamically via hooks — snapshot built before hook fires **[L38]**
- **MEDIUM**: Workspace hooks disabled by default but still risky when enabled
- **MITIGATION**: Minimize enabled hooks, never enable workspace hooks in production
- **MITIGATION**: Treat third-party skills as untrusted, use sandboxing for untrusted inputs

## Files

- `questions.md` — All research questions with status and priority
- `sources.md` — Documented sources for all research
- `findings/` — Full research findings documents

---
*Maintained by: Investigador Scout*
