# Sources — Cron Jobs State Research

## Web Sources
1. docs.openclaw.ai (cron jobs docs) — 404 during fetch
2. site:github.com/openclaw openclaw cron jobs.json gateway — Gemini web search
3. site:github.com/openclaw openclaw cron list vs jobs.json empty discrepancy active memory — Gemini web search

## Local Sources
4. `~/.openclaw/cron/jobs.json` — Inspected 2026-04-25 02:27 UTC — Primary source with all 20 jobs
5. `ls -la ~/.openclaw/cron/` — Directory listing showing files and timestamps

## Key Findings
- `jobs.json` is fully populated (20 jobs)
- `openclaw cron list` likely showed enabled=true only in some versions
- Many jobs broken due to timeout issues (60-120s too short for agentTurn tasks)
- Email jobs failing with "Message failed" and timeout errors

## Contradiction with Original Hypothesis
- Original: "jobs.json vacía / discrepancy with cron list"
- Actual: jobs.json has 20 detailed job entries, not empty
- Resolution: The original observation was likely from gateway not running or version bug
