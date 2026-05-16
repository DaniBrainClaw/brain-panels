# Custom SKILL.md Scanning via before_install Hooks — RESEARCH FINDINGS

**Research Date:** 2026-04-23
**Topic:** Can organizations implement custom scanner integration via before_install hooks that scans SKILL.md?
**Priority:** MED (#13)
**Status:** ✅ COMPLETE

---

## 1. WHAT IS
A custom scanner integration using the `before_install` hook in an OpenClaw plugin. This allows organizations to add a security gate that inspects `SKILL.md` content—which the built-in scanner ignores—before a skill is installed.

## 2. HOW IT WORKS
1. **Plugin Registration**: The plugin registers the `before_install` hook: `api.registerHook("before_install", ...)`.
2. **Event Payload**: When a skill install starts, the hook receives `PluginHookBeforeInstallEvent`, which contains `sourcePath` (the directory where the skill is located).
3. **Inspection**: The handler reads `SKILL.md` from `sourcePath/SKILL.md` and runs custom regex/logic to find malicious instructions.
4. **Enforcement**: If malicious content is found, the hook returns `{ block: true, blockReason: "Malicious SKILL.md patterns detected" }`, effectively blocking the installation.

## 3. USES
- **Enterprise Security Gate**: Ensure all skills installed in an organization conform to security standards.
- **Prompt Injection Defense**: Detect instructions in `SKILL.md` that attempt system prompt overrides.
- **Content Filtering**: Ensure skills don't request sensitive credentials or external network exfiltration.

## 4. PROBLEMS
- **CLI Bypass**: The `before_install` hook only runs for Gateway-backed installs. CLI-based installs (e.g., `clawhub install`, `openclaw update`) bypass this hook entirely.
- **Not a replacement**: It does not replace the built-in scanner; it only augments it.
- **Resource access**: Requires reading files from the system, which must be secured.

## 5. SOLUTIONS
- **Mandatory Policy Plugin**: Force-install a "Security Policy" plugin on all org nodes that includes this scanner.
- **Hash/Fingerprint Database**: Implement a known-good SKILL.md database to verify skills by fingerprint.
- **Multi-layering**: Pair this with sandbox tool policies to enforce security at the tool execution level.

## 6. EDGE CASES
- **Symlink attacks**: `sourcePath` might be a symlink to outside the intended directory.
- **Multi-file payloads**: Malicious instructions split across `SKILL.md` and other files.
- **Dynamic Updates**: Plugin-based scanning is install-time; it does not block post-install modifications.

## 7. CREATIVE USES
- **Marketplace Scores**: Compute a "Security Integrity Score" for skills based on how they pass custom scanning.
- **Adaptive Blocking**: Dynamically download and update pattern lists via the plugin hook to defend against zero-day injection attacks.

---

## NEW QUESTIONS
- [ ] Can we harden the `sourcePath` check to prevent directory traversal?
- [ ] How to efficiently maintain the pattern database for organizations?
- [ ] Can we integrate LLM-based SKILL.md analysis into this hook for higher intelligence?

---

*Research by: Investigador Scout*
