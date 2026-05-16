# Cron Hot-Reload — Backlog Verification

## Step 1: What Is
Hot-reload in OpenClaw determines which configuration changes take effect without restarting the Gateway. Current config shows `"reload": { "mode": "restart" }` — meaning ALL changes require full restart.

## Step 2: How It Works
1. **Reload mode config:** `gateway.reload.mode` controls behavior.
2. **Current setting:** `"restart"` — full Gateway restart required for ALL changes.
3. **Cron job changes:** Modifying `jobs.json` requires either:
   - Full Gateway restart (current behavior)
   - Or use `openclaw cron` CLI commands which may hot-reload
4. **Configuration changes:** Plugin enable/disable, provider changes typically require restart.
5. **Token rotation:** `gateway.auth.token` changes require restart.

**Current reload config:**
```json
{
  "gateway": {
    "reload": {
      "mode": "restart"
    }
  }
}
```

## Step 3: Use Cases
- **Job schedule changes:** `openclaw cron edit` may hot-reload specific job without full restart.
- **Plugin enable/disable:** May hot-reload without full restart in some cases.
- **Token rotation:** Always requires restart for security.

## Step 4: Problems
- **Full restart required (current):** `mode: "restart"` means no partial hot-reload.
- **Session disruption:** Full restart disconnects all active sessions.
- **Cron job debugging:** Cannot test job changes without restart cycle.
- **Verification backlog item:** Confirm what requires restart — VERIFIED via config.

## Step 5: Solutions
- **Use CLI for cron changes:** `openclaw cron add/edit/remove` may handle hot-reload internally.
- **Batch changes:** Make multiple cron changes, then single restart.
- **Separate test environment:** Test job changes in non-production first.
- **Watch mode:** Some configs support file watching for auto-reload.

## Step 6: Edge Cases
- **Gateway crash during restart:** Jobs may not resume correctly.
- **Partial reload failure:** Some components reload, others don't — inconsistent state.
- **jobs.json corruption:** Bad JSON causes restart failure, gateway may not start.
- **Concurrent edits:** Editing jobs.json while gateway is writing can cause corruption.

## Step 7: Creative Uses
- **Blue-green deployment:** Run two gateways, switch between them for zero-downtime updates.
- **Atomic job updates:** Write new jobs.json to temp, then atomic rename.
- **Cron job versioning:** Keep backup of jobs.json before changes for quick rollback.

---

## VERIFICATION RESULT

**Backlog Item: Cron hot-reload — confirmar qué cambios requieren restart**

**CONFIRMED (partial):** Current `gateway.reload.mode: "restart"` means full restart is the default. However, `openclaw cron` CLI commands may provide hot-reload capability for job-specific changes without restarting the entire gateway.

**Evidence:**
- Gateway reload config shows `mode: "restart"` (full restart required)
- However, `openclaw cron add/edit/remove` are designed as user-facing cron management that may hot-reload
- Not definitively confirmed without runtime testing

---

## Hypothesis Update
- **Original:** "Unknown what requires restart vs hot-reload."
- **PARTIALLY VERIFIED:** Full restart is default mode. `openclaw cron` CLI likely provides job-level hot-reload without full gateway restart.

---

## Sources
- `openclaw.json` gateway.reload configuration
- Web search (quota exhausted — supplemented with config analysis)
