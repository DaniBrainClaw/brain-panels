# Lossless-Claw Configuration — 7-Step Deep Research

## Step 1: What Is
Lossless-Claw (LCM) is an OpenClaw plugin providing permanent, searchable memory via a SQLite-backed DAG summarization system. It replaces the standard sliding-window context management.

## Step 2: How Works
LCM persists raw transcript messages into a SQLite DB (`lcm.db`). It uses incremental compaction to build a tree of summaries (DAG). Leaf nodes summarize raw tokens (`leafChunkTokens`), and condensed nodes group summaries (`condensedMinFanout`).

## Step 3: Use Cases
- Long-running autonomous research agents.
- Cross-session memory persistence.
- Proactive agent briefing (end-of-day audit).
- Searchable project history.

## Step 4: Problems
- **Compaction Stalls:** Default timeout (60-120s) often fails under high token load during summarization.
- **Summary Truncation:** If `summaryMaxOverageFactor` is triggered, content is lost.
- **Discrepancy:** Differences between `openclaw.json` (plugin config) and runtime CLI status (`/lossless`).

## Step 5: Solutions
- **Timeout Fix:** Increase `summaryTimeoutMs` and `delegationTimeoutMs` (e.g., 300s+).
- **Tuning:** Use `cacheAwareCompaction.enabled: true` to prevent redundant summarization of hot prompt cache.
- **Storage:** Explicitly configure `databasePath` to avoid SQLite location bugs on multi-user/multi-profile hosts.

## Step 6: Edge Cases
- **`/new` / `/reset`:** `/new` clears runtime context but keeps LCM row (`sessionKey` stable). `/reset` archives current row and starts a new one.
- **`statelessSessionPatterns`:** Matching patterns skip LCM entirely, useful for ephemeral sub-agents.
- **Timezones:** Summaries use the configured `timezone` (defaults to host TZ); inconsistent TZ across distributed nodes causes audit drift.

## Step 7: Creative Uses
- **Research Loops:** Scout (30m) + Synthesis (60m) cycle using `lightContext: true`.
- **Audit Trails:** `BRAIN end-of-day audit` job that appends to memory/YYYY-MM-DD.md.
- **Lightweight State:** Using `leafChunkTokens: 80000` to balance recall frequency vs summarization cost.

---

## Hypothesis Refinement
- **Original:** "Compaction is standard."
- **Revised:** "Compaction is context-aware and tunable." Tuning `leafChunkTokens` is the most significant lever for performance.
