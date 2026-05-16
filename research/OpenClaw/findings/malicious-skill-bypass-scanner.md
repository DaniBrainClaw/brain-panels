# Finding: Dangerous-Code Scanner for Skill Installs — Can a Malicious Skill Bypass It?

**Researcher:** Investigador (Scout session cron:1b91a4c2-6345-42b5-a911-484281391be5)  
**Date:** 2026-04-23  
**Topic:** Can malicious skill bypass dangerous-code scanner for skill installs?  
**Priority:** HIGH  
**Status:** ✅ RESOLVED

---

## 1. What Is the Dangerous-Code Scanner?

The dangerous-code scanner is a **built-in static analysis tool** that OpenClaw runs against skill installer metadata before executing any installer commands. It is part of the Gateway's skill install pipeline.

From skills.md:
> "Gateway-backed skill dependency installs (`skills.install`, onboarding, and the Skills settings UI) run the built-in dangerous-code scanner before executing installer metadata."

Key characteristics:
- Runs **before** installer metadata is executed
- Scans for **dangerous or suspicious patterns** in installer specs
- Has two finding severity levels: `critical` and `suspicious`
- `critical` findings **block by default**
- `suspicious` findings **warn only**

---

## 2. How It Works

The scanner is invoked during **Gateway-backed skill dependency installs** — specifically these three entry points:

1. **`skills.install`** — programmatic skill install via Gateway API
2. **Onboarding** — first-run skill setup flow
3. **Skills settings UI** — interactive UI for managing skills

When any of these triggers a skill install that has `metadata.openclaw.install` array in its SKILL.md, the Gateway:

1. Extracts the installer spec from the skill's SKILL.md
2. Runs the dangerous-code scanner against the installer metadata
3. If `critical` findings are found → **block the install by default**
4. If `suspicious` findings are found → **warn but allow the install**
5. Only if the caller explicitly sets `dangerouslyForceUnsafeInstall` → override critical blocks
6. If scan fails (error) → block by default

The scanner analyzes the **installer metadata** (the install spec array in SKILL.md), NOT the entire SKILL.md. It looks for patterns like:
- Dangerous shell commands
- Suspicious network calls
- Credential exfiltration patterns
- File system manipulation that could be harmful

From the security audit glossary (`gateway/security/index.md`):
> `skills.code_safety` | warn/critical | Skill installer metadata/code contains suspicious or dangerous patterns

---

## 3. What the Scanner Does NOT Cover

### `openclaw skills install <slug>` bypasses the scanner

The documentation explicitly states:
> "`openclaw skills install <slug>` is different: it downloads a ClawHub skill folder into the workspace and does not use the installer-metadata path above."

This means:
- The CLI command `openclaw skills install <slug>` downloads a skill folder directly
- It does **NOT** run through the Gateway-backed installer pipeline
- It does **NOT** invoke the dangerous-code scanner
- The downloaded SKILL.md is placed in `<workspace>/skills/` but the install process does not execute installer metadata

### Skill content after installation is not continuously scanned

Once installed, the skill's SKILL.md content and any associated scripts are not subject to continuous scanning. Only the **installer metadata** (the `metadata.openclaw.install` array) is scanned at install time.

---

## 4. Can a Malicious Skill Bypass the Scanner?

### For Gateway-backed installs (`skills.install`, onboarding, UI): **LOW RISK of bypass**

The scanner runs **before** any installer is executed. A skill cannot bypass it during the install trigger because:
1. The scanner is invoked by the Gateway before any installer code runs
2. `critical` findings block by default — no override is possible without explicit `dangerouslyForceUnsafeInstall`
3. Scan failures block by default

**However, theoretical bypass vectors exist:**

### Vector 1: Scanner evasion via complex encoding
A skilled attacker might try to encode malicious patterns in ways that evade the scanner's pattern matching. The scanner is static analysis — it could miss:
- Obfuscated commands
- Indirect execution (e.g., chaining through intermediate scripts)
- Environment-dependent behavior that behaves differently when scanned vs. executed

### Vector 2: Time-of-check to time-of-use (TOCTOU)
If the scanner validates the installer metadata but the file changes before execution, a race condition could theoretically allow malicious content to execute. This would require a very specific race condition in the Gateway's install pipeline.

### Vector 3: Before_install hooks (NOT the scanner)
The scanner does NOT block `before_install` hook policy. Hooks have their own block/suspend mechanism. A skill could theoretically use hooks for malicious purposes, but this is a separate security boundary.

### For `openclaw skills install` CLI: **NO SCANNER PROTECTION**
The `openclaw skills install <slug>` command does not use the Gateway-backed installer pipeline and therefore does not invoke the scanner at all. A user running this command could install a malicious skill that has dangerous installer metadata, because the CLI path:
1. Downloads the skill folder
2. Places SKILL.md in the workspace
3. Does NOT execute the installer metadata (that's only done via Gateway-backed install)
4. Does NOT scan the installer metadata

Wait — actually, the CLI installs into `<workspace>/skills/` but the installer metadata (install array) is NOT executed during `openclaw skills install`. The installer is only executed when the Gateway needs to install a dependency (e.g., a binary required by the skill). So the dangerous window is when `skills.install` is called via Gateway API, not when using the CLI.

---

## 5. Problems Identified

### Problem 1: No scanner on CLI install path
`openclaw skills install` does not go through the scanner. While it doesn't execute installer metadata either, the skill file is downloaded and placed in the workspace without any scan.

**Severity:** LOW — because the CLI path doesn't execute installer metadata, the immediate risk is lower. However, if that skill is later installed via Gateway-backed path, the scanner would catch it.

### Problem 2: Scanner is pattern-based — potential evasion
Static scanners can be evaded by sophisticated attackers using encoding, indirect execution, or environmental triggers.

**Severity:** MEDIUM — for advanced attackers targeting specific systems.

### Problem 3: Skills run with agent privileges post-install
From THREAT-MODEL-ATLAS.md: "Skills run with agent privileges" — this is a **Critical residual risk**. The scanner only protects the install phase. Once installed, a skill runs with whatever privileges the agent has.

**Severity:** HIGH — the scanner is one layer, but post-install skill behavior is not sandboxed from agent privileges.

### Problem 4: No sandboxing for skills
Skills are not sandboxed — they execute with the agent's full context. The scanner provides protection only at install time.

**Severity:** HIGH — for untrusted third-party skills.

---

## 6. Solutions / Mitigations

### For Operators:
1. **Treat third-party skills as untrusted** — explicitly documented in skills.md:
   > "Treat third-party skills as untrusted code. Read them before enabling."
2. **Use sandboxing** for untrusted inputs and risky tools
3. **Use the CLI `openclaw skills install`** when you want to inspect a skill before it goes through the Gateway-backed install path
4. **Never combine shared DMs with broad tool access** — skills have agent privileges

### For OpenClaw (potential improvements not currently implemented):
1. **Extend scanner to cover skill content** at load time (not just installer metadata)
2. **Add optional scanner for CLI install path** as a warning layer
3. **Consider skill sandboxing** — isolated execution for untrusted skills

---

## 7. Edge Cases

1. **Bundled skills** — bundled skills are pre-scanned by OpenClaw team. Their installer metadata would have been reviewed. However, bundled skill overrides in workspace still follow precedence rules.

2. **Skill updates** — when a skill is updated, does the scanner re-run? This depends on whether the update triggers a fresh `skills.install` or just replaces the SKILL.md file. If the update path goes through Gateway-backed install again, the scanner re-runs. If it just replaces the file, no scan occurs.

3. **Skills with no installer metadata** — skills that just provide SKILL.md guidance (no binaries to install) would not trigger the scanner's full check because there's no installer metadata to scan. However, they still have agent privileges when invoked.

4. **Installer spec changes after scan** — if SKILL.md is edited after scanner runs but before execution, this is a potential TOCTOU. Unclear if the Gateway re-validates.

---

## 8. Creative Uses

1. **Trust verification workflow** — use `openclaw skills install` to download a skill, manually review the SKILL.md, then trigger Gateway-backed install only after approval.

2. **Scanner audit trail** — logs from `openclaw security audit --deep` include `skills.code_safety` check results, providing audit trail for compliance.

3. **Custom scanner integration** — organizations with advanced threat models could implement a custom `before_install` hook that performs additional scanning with different pattern sets.

---

## 9. New Questions Generated (Added to Backlog)

1. **MEDIUM** — Does the dangerous-code scanner run on skill updates/overwrites, or only on fresh installs?
2. **MEDIUM** — Can a skill with no installer metadata still execute malicious code via its SKILL.md content at load/invoke time?
3. **HIGH** — What is the complete list of patterns the dangerous-code scanner detects? (Could be useful for red-teaming)
4. **LOW** — Does `openclaw skills install` perform any scan or only download?
5. **HIGH** — Are there documented cases of scanner evasion attempts?
6. **MEDIUM** — How does the scanner interact with `before_install` hooks? Is there ordering/escalation?
7. **HIGH** — What sandboxing options exist for skill execution post-install?

---

## 10. Sources

- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — primary source for scanner behavior
- `/usr/local/lib/node_modules/openclaw/docs/gateway/security/index.md` — security model and audit glossary
- `/usr/local/lib/node_modules/openclaw/docs/security/THREAT-MODEL-ATLAS.md` — threat model including "Skills run with agent privileges" (Critical residual risk)
- `/usr/local/lib/node_modules/openclaw/docs/tools/clawhub.md` — CLI install path documentation
- Plugin.md reference for `--dangerously-force-unsafe-install` flag (similar concept for plugins)

---

## 11. Conclusion

**Can a malicious skill bypass the dangerous-code scanner for skill installs?**

**Answer: For Gateway-backed installs — unlikely for casual attacks, possible for sophisticated adversaries.** The scanner runs before any installer executes, and `critical` findings block by default. However, the scanner is static analysis and could theoretically be evaded by advanced attackers using encoding, indirect execution, or environmental triggers.

**For the `openclaw skills install` CLI path — the scanner is not invoked at all**, but this path also doesn't execute installer metadata, so the risk is different.

**The bigger risk** is that the scanner only covers install-time validation. Once installed, skills run with full agent privileges and are not sandboxed. This is the Critical residual risk documented in the threat model.

**Recommendation:** Treat third-party skills as untrusted. Use sandboxing for untrusted inputs. Use the CLI path to inspect skills before Gateway-backed installation.