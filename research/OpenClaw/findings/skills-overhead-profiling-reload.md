# Skills Overhead Profiling & Reload Mechanisms — Research Findings

**Topic:** Can skills overhead be profiled in production? Is there a tool command to reload skills without file changes?
**Priority:** MED
**Date:** 2026-04-23 11:46 CET
**Research by:** Investigador Scout
**Status:** ✅ COMPLETE

---

## 1. WHAT IS — Definition & Core Concepts

### Skills Overhead Profiling

Skills overhead profiling is the ability to **measure, monitor, and debug** the token/character cost of the skills list in the system prompt. OpenClaw provides built-in introspection via `/context` slash commands rather than a dedicated profiler.

### Skills Reload Mechanisms

Skills reload is the ability to **refresh the skills snapshot** without waiting for natural watcher triggers or session restart. OpenClaw has **no dedicated reload command**, but skills refresh through multiple automatic mechanisms and limited manual triggers.

### Key Distinction

| Concept | Description |
|---------|-------------|
| Skills snapshot | Per-session cached list of eligible skills, built at session start |
| Skills watcher | File system monitor that triggers snapshot refresh on SKILL.md changes |
| Config hot-reload | System that applies config changes (including `skills.entries`) without restart |
| Snapshot bump | Programmatic increment of snapshot version forcing next-turn refresh |

---

## 2. HOW IT WORKS — Internal Mechanics

### A) Skills Overhead Profiling via `/context`

**Built-in profiling commands:**

```
/context        → quick summary
/context list  → breakdown: skills list chars + token estimate + count
/context detail → per-skill entry sizes (top skills shown individually)
/context json  → machine-readable format
```

**What `/context list` shows for skills:**
```
Skills list (system prompt text): 2,184 chars (~546 tok) (12 skills)
```

**What `/context detail` shows for skills:**
```
Top skills (prompt entry size):
- frontend-design: 412 chars (~103 tok)
- oracle: 401 chars (~101 tok)
… (+10 more skills)
```

**Token calculation formula (from skills.md):**
```
total_chars = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
rough_tokens ≈ total_chars / 4  (OpenAI-style estimate)
```

- **Base overhead:** 195 characters (~49 tokens) when ≥1 skill exists
- **Per skill:** 97 chars + XML-escaped field lengths (~24-45 tokens/skill)

### B) Skills Snapshot Mechanism

**When snapshot is built:**
1. Session starts → `buildWorkspaceSkillSnapshot()` called once
2. Snapshot stored in `sessionEntry.skillsSnapshot`
3. Reused for all subsequent turns in same session

**Snapshot refresh triggers:**
1. Skills watcher detects `add`/`change`/`unlink` on SKILL.md files
2. New eligible remote node appears (macOS node with skills)
3. Effective agent skill allowlist changes for that session
4. `bumpSkillsSnapshotVersion()` called programmatically

**Key files:**
- `/usr/local/lib/node_modules/openclaw/dist/skills-DYF-hmoJ.js` — `buildWorkspaceSkillSnapshot`
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher + `bumpSkillsSnapshotVersion`
- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Snapshot version checking

### C) Skills Watcher Implementation

```javascript
// From refresh-p9Dzo7mb.js
watcher.on("add", (p) => schedule(p));
watcher.on("change", (p) => schedule(p));
watcher.on("unlink", (p) => schedule(p));  // SKILL.md deleted
```

- Watch targets: skill folder directories (6 locations)
- Debounce: `watchDebounceMs` (default 250ms)
- `schedule(p)` calls `bumpSkillsSnapshotVersion()` on SKILL.md change

### D) Config Hot-Reload for Skills Entries

**Config changes that hot-reload without restart:**
- `skills.entries.<skill>.enabled` (set to `false` to disable)
- `skills.entries.<skill>.env` changes
- `skills.entries.<skill>.apiKey` changes

**How it works:**
1. User runs: `openclaw config set skills.entries.peek:enabled=false`
2. Config hot-reload fires
3. On next agent turn: `needsSkillsSnapshot` check sees new version
4. `buildWorkspaceSkillSnapshot()` rebuilds with disabled skill excluded

**NOT hot-reloaded:**
- `skills.load.extraDirs` changes (require restart)
- `skills.load.watch` changes (require restart)

---

## 3. USES — Practical Applications

### A) Profiling Skills Overhead in Production

**Scenario 1: Diagnose unexpected context size**
```
User: /context detail
→ Top skills shows "unused-skill: 800 chars"
→ Disable skill via: openclaw config set skills.entries.unused-skill:enabled=false
```

**Scenario 2: Budget planning before adding skills**
```
Calculation:
- 100 skills × 35 tokens/skill = 3,500 tokens
- Current system prompt: ~3,000 tokens
- Bootstrap files: ~5,000 tokens
- Output reserve: ~10,000 tokens
- Available for history + new input: ~181,000 tokens
```

**Scenario 3: Track skills overhead over time**
```
/context list → note skills list size
After adding skills:
/context list → compare new size
```

### B) Reloading Skills Without File Changes

**Workaround 1: Touch SKILL.md file**
```bash
touch /path/to/skill/SKILL.md
# Watcher detects change → bumps snapshot version → next turn uses new snapshot
```

**Workaround 2: Rename skill folder**
```bash
mv my-skill my-skill-temp
mv my-skill-temp my-skill
# Watcher detects add+unlink → refreshes snapshot
```

**Workaround 3: Config hot-reload (for enable/disable only)**
```bash
openclaw config set skills.entries.my-skill:enabled=false
# Next turn: skill excluded from snapshot
```

**Workaround 4: Via remote node reconnection**
```bash
# Disconnect/reconnect macOS node with skills
# Node reconnection triggers skills snapshot refresh
```

### C) Monitoring In-Flight Skill Executions

**When SKILL.md is deleted mid-execution:**
1. Watcher detects `unlink` event
2. `bumpSkillsSnapshotVersion()` called
3. **In-flight execution continues** (no immediate interruption)
4. **Next agent turn** uses new snapshot (skill excluded)

**Important context:**
- Skills are TEXT (SKILL.md content) — they don't "run" independently
- Model reads SKILL.md when invoked via slash command
- If model is mid-execution reading a skill's instructions:
  - Current turn continues with its snapshot
  - Next turn sees the deletion
  - Model cannot re-read deleted SKILL.md

---

## 4. PROBLEMS — Limitations & Issues

### Problem 1: No Dedicated Profiler

| Issue | Impact | Workaround |
|-------|--------|------------|
| No `openclaw skills profile` command | Can't get historical trends | Manual `/context` tracking |
| `/context detail` only shows top N skills | May not see all skills | Run multiple times with different views |
| No token breakdown by skill metadata field | Can't pinpoint overhead source | Manual calculation using formula |
| No alerting on overhead threshold | May not notice bloat | External monitoring + `/context` cron |

### Problem 2: No Dedicated Reload Command

| Issue | Impact | Workaround |
|-------|--------|------------|
| No `openclaw skills reload` command | Must use file hacks | Touch SKILL.md or rename folder |
| Watcher only monitors SKILL.md files | Config changes may not trigger | Use config set instead of file edit |
| Remote node trigger is fragile | Relies on node connection | Manual session restart |

### Problem 3: Snapshot Refresh Race Conditions

| Issue | Impact | Workaround |
|-------|--------|------------|
| In-flight turn uses old snapshot | Changes not immediate | Accept delay or restart session |
| Concurrent sessions may see different snapshots | State inconsistency | Per-session state files |
| Snapshot version bump without file change | Confuses debugging | Document workaround usage |

### Problem 4: Config Hot-Reload Limits

| Issue | Impact | Workaround |
|-------|--------|------------|
| `skills.load.extraDirs` requires restart | Can't add skill folders hot | Restart gateway |
| `skills.load.watch` requires restart | Can't toggle watcher hot | Restart gateway |
| Per-agent `skills` array changes don't hot-reload | Must start new session | Use session-specific config |

### Problem 5: In-Flight Execution Deletion Edge Case

| Issue | Impact | Workaround |
|-------|--------|------------|
| SKILL.md deleted while model reading it | Model gets incomplete context | Don't delete mid-execution |
| Snapshot rebuild during session | Brief inconsistency window | Avoid deletions during active work |
| Skills watcher may miss nested changes | Some changes not detected | Use top-level SKILL.md only |

---

## 5. SOLUTIONS — Mitigations & Best Practices

### Solution 1: Establish Skills Overhead Budget

```json5
{
  agents: {
    defaults: {
      contextTokens: 200000,
      // Reserve 5% for skills overhead
      // Max ~100 skills at 35 tokens each = 3,500 tokens = 1.75%
    }
  }
}
```

**Monitoring cron:**
```
# Run /context list weekly, log skills overhead
# Alert if >10% of context budget
```

### Solution 2: Use `disable-model-invocation` for Rare Skills

```markdown
---
name: emergency-skill
description: "For emergencies only"
disable-model-invocation: true
---
```

**Benefits:**
- Zero token overhead in model prompt
- Available via user slash command only
- Useful for skills used <1/week

### Solution 3: Controlled Reload via File Touch

```bash
# Force snapshot refresh without visible file change
touch /workspace/skills/my-skill/SKILL.md
```

**Script for clean reload:**
```bash
#!/bin/bash
# reload-skill.sh — force snapshot refresh
SKILL_PATH="$1/SKILL.md"
if [ -f "$SKILL_PATH" ]; then
  touch "$SKILL_PATH"
  echo "Snapshot refresh triggered for $1"
else
  echo "SKILL.md not found at $SKILL_PATH"
fi
```

### Solution 4: Per-Agent Skill Control Without Restart

```json5
{
  agents: {
    defaults: { skills: ["core-1", "core-2"] },
    list: [
      { id: "research", skills: ["core-1", "core-2", "web-research"] },
      { id: "minimal", skills: ["core-1"] },
    ]
  }
}
```

**Change takes effect:** Next session for that agent

### Solution 5: Skills Overhead Debugging Workflow

```typescript
// Hook to log skills overhead at session start
api.registerHook({
  events: ["before_agent_start"],
  handler: async (event) => {
    const skills = event.visibleSkills;
    const overhead = 195 + skills.reduce((sum, s) => {
      return sum + 97 + s.name.length + s.description.length + s.location.length;
    }, 0);
    console.log(`Skills overhead: ${overhead} chars (~${Math.round(overhead/4)} tokens)`);
  }
});
```

---

## 6. EDGE CASES — Unexpected Behaviors

### Edge Case: Snapshot Version Without File Change

When `bumpSkillsSnapshotVersion()` is called programmatically (no SKILL.md change):
- Snapshot version increments
- `needsSkillsSnapshot` check triggers rebuild
- Next turn uses new snapshot
- **No visible change** unless you know to look for version bump

### Edge Case: Concurrent Watcher Events

When multiple SKILL.md files change in rapid succession:
- Watcher debounce (250ms default) coalesces events
- Single snapshot rebuild at end of debounce window
- All changes reflected in one refresh

### Edge Case: Skills Snapshot vs. Session Store

The snapshot is stored in session entry:
```
sessionEntry.skillsSnapshot = {
  version: "v42",
  skills: [...],
  timestamp: Date
}
```

Changes to snapshot do NOT affect:
- Session transcript (past interactions)
- Compaction summaries already written
- Session store file on disk

### Edge Case: Remote Node Skills and Snapshot Refresh

When macOS node connects with unique skills:
- `primeRemoteSkillsCache()` called
- Snapshot version bumped
- Skills from node become eligible
- **Without node, these skills invisible** — no error, just graceful fallback

### Edge Case: Watcher Disabled but Snapshot Still Refreshes

When `skills.load.watch: false`:
- File watcher inactive
- BUT: remote node changes still trigger snapshot refresh
- AND: programmatic `bumpSkillsSnapshotVersion()` still works
- AND: config changes still trigger rebuild at turn boundary

---

## 7. CREATIVE USES — Novel Applications

### Creative Use 1: Skills Overhead Budget Monitor

```typescript
const OVERHEAD_WARNING_THRESHOLD = 5000; // tokens

api.registerHook({
  events: ["before_agent_start"],
  handler: async (event) => {
    const skills = event.visibleSkills;
    const overhead = calculateSkillsOverhead(skills);
    if (overhead > OVERHEAD_WARNING_THRESHOLD) {
      console.warn(`⚠️ Skills overhead ${overhead} tokens exceeds ${OVERHEAD_WARNING_THRESHOLD} threshold`);
    }
  }
});
```

### Creative Use 2: Skills Overhead Auto-Reduction

```typescript
const MAX_SKILLS = 50;

api.registerHook({
  events: ["before_agent_start"],
  handler: async (event) => {
    if (event.visibleSkills.length > MAX_SKILLS) {
      console.warn(`Limiting skills from ${event.visibleSkills.length} to ${MAX_SKILLS}`);
      event.agentConfig.skills = event.visibleSkills
        .slice(0, MAX_SKILLS)
        .map(s => s.name);
    }
  }
});
```

### Creative Use 3: Snapshot Version Telemetry

```typescript
// Log snapshot refresh events for debugging
api.registerHook({
  events: ["session:patch"],
  handler: async (event) => {
    if (event.patch.skillsSnapshotVersion) {
      console.log(`Snapshot version bump: ${event.patch.skillsSnapshotVersion}`);
    }
  }
});
```

### Creative Use 4: Skills Reload Webhook

```typescript
// Expose skills reload via webhook
api.registerHook({
  events: ["before_agent_start"],
  handler: async (event) => {
    // Check for reload flag in session context
    if (event.context.needsSkillsReload) {
      bumpSkillsSnapshotVersion();
    }
  }
});
```

### Creative Use 5: Skills Overhead Attribution

```typescript
// Track which skill categories consume most overhead
const CATEGORIES = {
  "coding": ["github", "coding-agent", "code-review"],
  "research": ["web-research", "continuous-improvement"],
  "communication": ["himalaya", "message"]
};

api.registerHook({
  events: ["before_agent_start"],
  handler: async (event) => {
    const overhead = { total: 0, byCategory: {} };
    for (const skill of event.visibleSkills) {
      const cat = Object.entries(CATEGORIES).find(([_, skills]) => 
        skills.includes(skill.name)
      )?.[0] ?? "other";
      overhead.byCategory[cat] = (overhead.byCategory[cat] ?? 0) + skillOverhead(skill);
      overhead.total += skillOverhead(skill);
    }
    console.table(overhead.byCategory);
  }
});
```

---

## Summary: Quick Reference

| Question | Answer |
|----------|--------|
| Can skills overhead be profiled? | **YES** — `/context list` and `/context detail` show per-skill sizes |
| Is there a skills reload command? | **NO** — must use file workaround (touch SKILL.md) |
| What triggers snapshot refresh? | File watcher + remote nodes + config changes + `bumpSkillsSnapshotVersion()` |
| Does config hot-reload apply to skills.entries? | **YES** — enable/disable via `openclaw config set` hot-reloads |
| What happens when SKILL.md deleted mid-execution? | In-flight turn completes; next turn excludes skill |
| Can skills be enabled/disabled per-session? | **NO** — global to workspace; new sessions use new config |
| Is there a token breakdown by skill field? | **PARTIAL** — `/context detail` shows per-skill total only |
| Can watcher be disabled? | YES — `skills.load.watch: false` (requires restart to set) |

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/concepts/context.md` — `/context detail` documentation, per-skill breakdown
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills snapshot, watcher, hot reload documentation
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — `skills.entries.*` config fields, hot-reload behavior
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher implementation: `watcher.on("add/change/unlink")`, `bumpSkillsSnapshotVersion`
- `/usr/local/lib/node_modules/openclaw/dist/skills-DYF-hmoJ.js` — `buildWorkspaceSkillSnapshot` implementation
- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Snapshot version checking, rebuild logic
- `/usr/local/lib/node_modules/openclaw/dist/commands-handlers.runtime-qpU8MeZd.js` — `/context` command handlers

---

## NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] Can snapshot version be inspected at runtime without debug mode? **[LOW]**
- [ ] Is there a way to export skills overhead data to external monitoring systems? **[MED]**

### b) Internal Mechanics
- [ ] Does `bumpSkillsSnapshotVersion()` require watcher to be enabled? **[LOW]**
- [ ] Can multiple snapshot versions coexist across concurrent sessions? **[LOW]**
- [ ] What is the maximum snapshot version before rollover? **[LOW]**

### c) Use Cases
- [ ] Can skills overhead be included in `/status` output automatically? **[MED]**
- [ ] Is there a way to schedule skills enable/disable at specific times? **[MED]**

### d) Problems & Limitations
- [ ] Does watcher consume significant CPU on large skill directories? **[LOW]**
- [ ] Is there a known issue where snapshot doesn't refresh after config hot-reload? **[MED]**

### e) Solutions & Workarounds
- [ ] Can a custom hook simulate `openclaw skills reload` functionality? **[MED]**
- [ ] What's the best way to test skills overhead changes before deploying? **[MED]**

### f) Edge Cases
- [ ] What happens when snapshot version overflows (wraps around)? **[LOW]**
- [ ] Can two concurrent sessions have different snapshot versions? **[LOW]**

### g) Creative Uses
- [ ] Could a skill self-report its overhead via a hook at load time? **[LOW]**
- [ ] Can skills overhead drive automatic skill pruning (remove lowest-use skills)? **[MED]**

---

*Research by: Investigador Scout | 2026-04-23 11:46 CET*
