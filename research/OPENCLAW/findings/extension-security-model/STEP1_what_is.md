# Extension Security Model — 7-Step Deep Research

## ⚠️ CRITICAL SECURITY FINDINGS ⚠️

## Step 1: What Is
OpenClaw's security model is built on a "personal assistant" paradigm — single trusted operator per gateway. Native plugins run **in-process** within the OpenClaw Gateway, treated as trusted code. There is **NO built-in sandboxing** for plugins themselves.

## Step 2: How It Works
1. **In-Process Execution:** Native plugins run directly in Gateway process — no process isolation.
2. **Plugin Allowlisting:** Only allowlisted plugins in `plugins.allow` array can load.
3. **Tool Execution:** Can be sandboxed in Docker containers (optional, not default).
4. **Workspace Plugins:** Auto-load from `extensions/` directory without trust verification (pre-2026.3.12).
5. **Hooks System:** `before_tool_call` hooks can intercept and modify tool execution.

## Step 3: Use Cases
- **Tool Sandboxing:** Docker containers isolate tool execution from host system.
- **Hook-based Approval:** Require user confirmation before dangerous tools execute.
- **Read/Write Separation:** Distinguish low-risk read tools from high-risk write tools.
- **MicroVM Isolation:** Docker sandbox uses separate kernel per sandbox, not just container.

## Step 4: Problems — CRITICAL CVEs

### Active Vulnerabilities (System on 2026.4.12 — MISSING PATCHES)

| CVE | CVSS | Severity | Affects | Fixed In |
|-----|------|----------|---------|----------|
| CVE-2026-25253 | 8.8 | HIGH | < 2026.1.29 | 2026.1.29+ |
| CVE-2026-32922 | 9.9 | CRITICAL | < 2026.3.11 | 2026.3.11+ |
| CVE-2026-32046 | — | HIGH | < 2026.3.12 | 2026.3.12+ |
| Permission bypass | — | HIGH | < 2026.3.31 | 2026.3.31+ |

**Current system: 2026.4.12 — VULNERABLE to all above**

### Specific Issues:
1. **CVE-2026-25253:** WebSocket origin validation missing — token theft via malicious webpage
2. **CVE-2026-32922:** Pairing token → full admin + RCE (CVSS 9.9!)
3. **CVE-2026-32046:** `--no-sandbox` flag enabled by default
4. **Pre-2026.3.12:** Plugins auto-loaded from `extensions/` without trust verification
5. **Many exposed instances** running without authentication

## Step 5: Solutions
- **UPDATE IMMEDIATELY:** Upgrade to 2026.4.14+ (latest stable)
- **Bind to localhost:** Never expose gateway to public internet
- **Strong auth tokens:** Enforce on all connections
- **VPN/Tailscale:** For remote access instead of public exposure
- **Plugin code audit:** Review before install (npm lifecycle scripts can execute during install)
- **Extension allowlisting:** Explicit `plugins.allow` list only
- **Docker sandbox:** Enable for agent tool execution
- **Firewall rules:** Restrict network access

## Step 6: Edge Cases
- **Malicious Plugin can crash Gateway:** No process isolation = crash = gateway down
- **Workspace plugins as attack vector:** Pre-2026.3.12 auto-loads without verification
- **Token theft via WebSocket:** CVE-2026-25253 — visiting malicious page steals auth token
- **Privilege escalation:** Pairing token → full admin access (CVE-2026-32922)
- **Docker-in-Docker risks:** Privilege escalation if not properly configured
- **No bug bounty program:** As of Feb 2026, no dedicated security team

## Step 7: Creative Uses
- **SecureClaw:** Security auditing tool with OWASP-aligned rules
- **MicroVM over Container:** Use microVMs (separate kernel) instead of containers for stronger isolation
- **Read-only Workspace:** Mount workspace read-only except for specific files
- **Credential Proxy:** Inject API keys via host-side proxy, never direct to VM

---

## CRITICAL ACTION ITEM

**System Version: 2026.4.12 — PATCHES MISSING**

Required actions:
1. `openclaw gateway update` or manual upgrade to 2026.4.14+
2. Audit current plugin list
3. Check if gateway is exposed to internet
4. Review authentication tokens

---

## Hypothesis Update
- **Original:** "Unknown whether extensions are sandboxed."
- **Answer:** NO — plugins are NOT sandboxed. They run in-process. Docker sandbox is optional for tool execution, not for plugins themselves.
- **Critical Gap:** System is running vulnerable version (2026.4.12) missing critical security patches (CVE-2026-25253, CVE-2026-32922, CVE-2026-32046).

---

## Sources
- Web search: OpenClaw CVE vulnerabilities 2026
- Web search: OpenClaw plugin security model Docker sandbox
- `openclaw.json` version inspection
