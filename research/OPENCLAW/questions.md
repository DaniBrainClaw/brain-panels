# OpenClaw Research — Questions

## Cron Jobs (answered)
- [x] Why is jobs.json showing as empty? → **NOT EMPTY - 20 jobs present. Original discrepancy was gateway/version issue**
- [x] What jobs are actually defined? → **20 jobs including research scout/synthesis cycles**
- [x] Why are most jobs timing out? → **timeoutSeconds too short (60-120s) for agentTurn tasks that need more time**
- [x] What is the real storage mechanism? → **~/.openclaw/cron/jobs.json + ~/.openclaw/cron/runs/ for history**

## Open Questions
- [ ] Lossless-claw: detailed config (freshTailCount, compaction thresholds) — NEXT PRIORITY
- [ ] MCP Server: NotebookLM MCP configured but undocumented — how to use?
- [ ] Extension Tool Integration: can Pi extensions register dynamic tools?
- [ ] Extension Security: are extensions sandboxed? Can malicious extension crash gateway?
- [ ] TaskFlow System: deep dive on create/execute/monitor
- [ ] Cron job cleanup: should disable/remove ~13 broken jobs with consecutive timeout errors

## Hypotheses to Verify
- [ ] "openclaw cron list" may only show enabled=true jobs in some versions
- [ ] Session isolation may not work correctly for slash commands like /new

---

*Updated: 2026-04-25*
