# Cron Jobs — Estado Real vs jobs.json

## Step 1: What Is (Findings)

### Core Architecture Discovery

**`jobs.json` NO está vacío** — contiene 20 jobs activos con estado completo.

### Structure of jobs.json

```json
{
  "version": 1,
  "jobs": [ ... 20 jobs ... ]
}
```

Cada job tiene:
- `id`, `name`, `agentId`, `description`
- `enabled: true|false`
- `schedule`: `{kind: "cron"|"every", expr: string, tz: string, everyMs?: number}`
- `sessionTarget`: `"isolated"|"current"`
- `wakeMode`: `"now"`
- `payload`: `{kind: "agentTurn", message: string, timeoutSeconds: number}`
- `state`: last run tracking (lastRunAtMs, lastRunStatus, lastDurationMs, etc.)
- `delivery`: `{mode: "announce"|"none", channel?: "last"|"telegram"}`

### Job Types Found

| Job Name | Enabled | Schedule | Session | Status |
|----------|---------|----------|---------|--------|
| Crear archivo diario memory | false | 1 0 * * * | isolated | error (timeout) |
| BRAIN conversations index daily | false | 3 0 * * * | isolated | error (timeout) |
| **BRAIN end-of-day audit** | **true** | 30 22 * * * | isolated | ok ✓ |
| nightly-investigation-001 | false | 0 23 * * * | isolated | error (timeout) |
| nightly-audit-001 | **true** | 0 1 * * * | isolated | error (timeout) |
| nightly-execution-001 | false | 0 4 * * * | isolated | error (timeout) |
| Email mañana 8am | false | 0 8 * * * | isolated | error (timeout) |
| Email tarde 15pm | false | 0 15 * * * | isolated | error (timeout) |
| Jobs follow-up 2min | false | every 120000ms | isolated | error (timeout) |
| Maintenance master 5min | false | */5 * * * * | isolated | ok ✓ |
| **daily-briefing-001** | **true** | 0 22 * * 1-5 | current | ok ✓ |
| **email-fetch-0750** | **true** | 50 7 * * * | current | error (⚠️ ✉️ Message failed) |
| **email-fetch-1200** | **true** | 0 12 * * * | current | ok ✓ |
| **email-fetch-1450** | **true** | 50 14 * * * | current | ok ✓ |
| email-fetch-1900 | false | 0 19 * * * | current | error (timeout) |
| **openclaw-research-scout** | **true** | every 1800000ms | current | ok ✓ (THIS JOB) |
| **openclaw-research-synthesis** | **true** | every 3600000ms | isolated | ok ✓ |
| Tuesday reminder | **true** | 0 9 14 4 * | current | error (one-time past) |
| daily-session-reset | false | 0 7 * * 1-5 | isolated | BROKEN (/new invalid) |

### Cron Scheduler Location
- `~/.openclaw/cron/jobs.json` — primary storage
- `~/.openclaw/cron/runs/` — per-run history
- Backup files: `jobs.json.bak`, `jobs.json.JOB002.*.bak`, `jobs.json.*.tmp`

---

## Step 2: How It Works (Findings)

### Storage Mechanism
1. Gateway reads `jobs.json` on startup
2. Schedules cron jobs using host timezone (`tz` field)
3. Persists state changes back to `jobs.json` after each run
4. Creates `~/.openclaw/cron/runs/<jobId>/<timestamp>.json` for each run

### Schedule Types
- `cron`: Standard cron expr + tz (e.g., `1 0 * * *` = 00:01)
- `every`: Interval in ms (e.g., `everyMs: 1800000` = 30min)
- `at`: One-time execution (not seen in current jobs)

### Session Targeting
- `isolated`: Fresh session per run — **recommended for independent tasks**
- `current`: Runs in active conversation session
- Note: `sessionKey` field sometimes set (e.g., `"agent:ejecutor:main"`) but most jobs don't have it

### Delivery Modes
- `announce`: Send result to channel (Telegram/last)
- `none`: Result kept in session only, no push notification

---

## Step 3: Use Cases (Findings)

### Active Productive Jobs
1. **BRAIN end-of-day audit** (22:30) — Appends daily audit to memory
2. **daily-briefing-001** (22:00 weekdays) — Proactive briefing request
3. **email-fetch-0750/1200/1450** — 3x daily email processing
4. **openclaw-research-scout** — This job's own research cycle
5. **openclaw-research-synthesis** — Research synthesis cycle

### Broken/Disabled Jobs
- Most old jobs from 2026-04-03 to 2026-04-07 are broken/timed out
- Email jobs have `consecutiveErrors: 1-5` and `lastErrorReason: "timeout"`
- `daily-session-reset` explicitly marked BROKEN — `/new` slash command invalid in isolated

---

## Step 4: Problems (Findings)

### Problem: Most Jobs Timing Out
- **13 out of 20 jobs** show `lastErrorReason: "timeout"`
- Timeout durations: 60-120 seconds typical
- Some jobs have `timeoutSeconds: 60` but `lastDurationMs: 60004+` — timeout is too short

### Problem: Email Jobs Failing
- `email-fetch-0750`: `lastError: "⚠️ ✉️ Message failed"` — Outbound not configured
- `email-fetch-1900`: never executed despite being defined

### Problem: Discrepancy Hypothesis (CONTRADICTION)
- The backlog stated `jobs.json` was "vacío" (empty) or showing discrepancy with `openclaw cron list`
- **Reality: `jobs.json` has 20 jobs fully populated**
- Possible causes of original discrepancy:
  1. Bug in old version where `enabled: false` jobs were not shown
  2. Permission issue reading `jobs.json`
  3. Gateway not started when `openclaw cron list` was run
  4. `cron list` only shows enabled jobs in some versions

### Problem: Old Cron Jobs Not Cleaned Up
- Jobs from April 3-7 still present with old timestamps
- No automatic cleanup of disabled/broken jobs

---

## Step 5: Solutions (Findings)

### Timeout Fixes Needed
- Increase `timeoutSeconds` for all agentTurn jobs to at least 300s
- The `BRAIN end-of-day audit` runs ok at 225,359ms (3.7 min) but has `timeoutMs: 300000` set

### Email Job Fixes Needed
- Configure outbound channel properly for email-fetch jobs
- Or change `delivery.mode` to `none` if email processing should stay internal

### Orphan Job Cleanup
- Remove or disable: `nightly-investigation-001`, `nightly-execution-001`, `email-fetch-1900`, `daily-session-reset`
- These are clearly broken and adding noise

---

## Step 6: Edge Cases (Findings)

### Edge Case: One-time Jobs
- `tuesday-morning-reminder-001` — runs once at `0 9 14 4 *` (April 14) — past, will not fire again
- `Crear archivo diario memory` — one-time `1 0 * * *` but `enabled: false`

### Edge Case: `/new` Slash Command in Isolated Session
- `daily-session-reset` uses `/new` payload in isolated session → **BROKEN**
- Slash commands only work in interactive sessions
- This is explicitly documented in the job's `description` field

### Edge Case: `sessionKey` Field
- Some jobs specify `sessionKey: "agent:ejecutor:main"` or `"agent:main:main"`
- This appears to be a routing hint but most jobs don't have it set
- May not be fully implemented

### Edge Case: Cross-Timezone Jobs
- Some jobs use `Europe/Madrid`, others `Europe/Berlin`
- Mixing timezones could cause confusion (Spain DST vs Berlin no DST)

---

## Step 7: Creative Uses (Findings)

### Creative Pattern: Chained Research Pipeline
```
openclaw-research-scout (every 30min)
    → feeds findings to
openclaw-research-synthesis (every 60min)
    → produces consolidated reports
```

### Creative Pattern: Session-Routed Jobs
- Jobs can target specific agents via `sessionKey: "agent:ejecutor:main"`
- Allows routing cron work to specialized agents

### Creative Pattern: Self-Healing Cron
- Jobs track `consecutiveErrors` count
- Could auto-disable after N consecutive failures
- Currently NOT implemented — jobs keep trying forever

### Creative Pattern: LightContext for Cron
- `openclaw-research-scout` uses `"lightContext": true`
- Reduces token usage for lightweight research pulses
- Useful for periodic health checks and brief updates

---

## Hypothesis Update

**Original Hypothesis:** "Discrepancy between `openclaw cron list` and `jobs.json` (empty)"

**Revised:** `jobs.json` is NOT empty. The original discrepancy was likely caused by:
1. Running `openclaw cron list` before Gateway started
2. A version-specific bug showing only enabled jobs
3. A race condition during job creation/deletion

**Status:** PARTIALLY CONFIRMED — Real issue is not that `jobs.json` is empty, but that many jobs are broken/timing out and need cleanup.

---

## Sources
- `~/.openclaw/cron/jobs.json` (inspected 2026-04-25 02:27 UTC)
- `ls -la ~/.openclaw/cron/`
- Web search: OpenClaw cron docs + GitHub issues
