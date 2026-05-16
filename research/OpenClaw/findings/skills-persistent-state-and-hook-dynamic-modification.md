# Skills Persistent State & Hook Dynamic Modification — RESEARCH FINDINGS

**Research Date:** 2026-04-23

**Topic:** Can skills implement persistent state across sessions (file-based)? + Can hooks dynamically modify the skills list at runtime?

**Priority:** MED (#21 + #41)

**Status:** ✅ COMPLETE

---

## 1. WHAT IS

Two related questions:

**Q21: Can skills implement persistent state across sessions (file-based)?**
Skills are instruction bundles that guide the model. The question is whether a skill can retain information from one session to another without relying on memory systems like `memory_search` or `MEMORY.md`.

**Q41: Can hooks dynamically modify the skills list at runtime (without config change)?**
Hooks run at specific lifecycle events. The question is whether a hook can programmatically add, remove, or swap skills during an active session without editing config files or triggering the watcher.

---

## 2. HOW IT WORKS

### Skills Persistent State — Mechanics

**No native state mechanism exists.** Skills are text bundles — they don't have runtime state storage. However, the skills infrastructure provides hooks into existing systems:

#### A. Workspace file-based state (skill writes files)
A skill can use the workspace directory (`context.workspaceDir` via hook context) to read/write state files:
```
<workspaceDir>/
  .skills/
    my-skill/
      SKILL.md
      state.json       ← skill can read/write this
```

The skill's **instructions** can include steps like "read state from `~/.openclaw/workspace/.skills/my-skill/state.json`". Since the workspace is persistent across sessions, files written there survive between sessions.

#### B. Skills snapshot persistence
The skills snapshot (`sessionEntry.skillsSnapshot`) is persisted in the **session store**:
```javascript
// session-updates-3NulUPmS.js
const skillSnapshot = !current.skillsSnapshot || shouldRefreshSnapshot 
  ? buildSnapshot() 
  : current.skillsSnapshot;
await persistSessionEntryUpdate({
  ...sessionEntry ?? { skillsSnapshot: skillSnapshot },
  skillsSnapshot: skillSnapshot
});
```

This means **which skills were eligible** for a session is recorded in the session store JSONL file. However, this is the *result* of skill loading, not arbitrary custom state.

#### C. Skill state via hook session:patch
The `session:patch` hook fires when session properties are modified. The patch only contains changed fields. This cannot directly add skill state to the snapshot, but a hook could write a workspace file that a skill reads on next execution.

### Hook Dynamic Skills Modification — Mechanics

**No direct API for runtime skills list modification exists.** Here's what the system actually supports:

#### A. before_prompt_build hook (modifying mode)
The `before_prompt_build` hook uses `mergeResults` mode — handlers are called sequentially, each can modify the result for the next. It runs on:
```javascript
return runModifyingHook("before_prompt_build", event, ctx, { mergeResults: mergeBeforePromptBuild });
```

The hook receives `context.cfg` (full config with all secrets). Modifying `context.cfg.skills` **at this hook level** does NOT cause the skills snapshot to rebuild in the current turn — the snapshot is already built before this hook runs.

#### B. Hook execution order context
The hook runs AFTER the skills snapshot decision is made for the turn. The flow is:
1. Session resolution → skills snapshot loaded/built
2. `before_prompt_build` hook fires (modifying merge)
3. System prompt assembled with current skills list
4. Agent run starts

So modifying `context.cfg` in `before_prompt_build` affects **future turns**, not the current one.

#### C. Watcher + SKILL.md modification
The skills watcher triggers on `SKILL.md` file changes:
```javascript
// refresh-p9Dzo7mb.js
const watchEnabled = params.config?.skills?.load?.watch !== false;
// On change → bumpSkillsSnapshotVersion → "next agent turn picks up new list"
```

A hook could theoretically rename/move `SKILL.md` files to dynamically enable/disable skills. This works but requires the watcher to be enabled and changes take effect on the **next turn**.

#### D. session:patch hook
The `session:patch` event fires when `session:patch` is called with changed fields. The context includes:
- `context.sessionEntry` — current session metadata
- `context.patch` — only changed fields
- `context.cfg` — full config

This hook cannot modify which skills are in the snapshot. It can only react to patch events.

---

## 3. USES

### For Skills Persistent State

- **Counters and accumulators**: Skill tracks "how many times I've executed X" in a local file
- **Configuration persistence**: Skill preferences set by user survive across sessions
- **Caching**: Skill caches API results to workspace files instead of recomputing
- **Workflow state machines**: Multi-step workflows can store progress in JSON state files
- **Audit logs**: Skills can append to structured log files in workspace

### For Hook Dynamic Skills Modification

- **Conditional skill activation**: Enable/disable skills based on time, user identity, or channel
- **A/B testing skills**: Hook swaps skill directories mid-session for experimentation
- **Emergency disable**: Hook disables misbehaving skill when error rate exceeds threshold
- **Progressive skill rollout**: Hook enables new skills for gradually expanding user groups
- **Context-aware skills**: Hook adds situation-specific skills based on message content

---

## 4. PROBLEMS

### For Skills Persistent State

| Problem | Description |
|---------|-------------|
| **No native mechanism** | Skills have no built-in state storage; must use workspace files manually |
| **No isolation** | Skill state files are in shared workspace; poorly behaved skills could corrupt each other's state |
| **Race conditions** | Two concurrent agent turns writing same state file could corrupt it |
| **Session store doesn't help** | `sessionEntry.skillsSnapshot` is not arbitrary key-value storage; it stores which skills were eligible, not custom skill data |
| **Security concern** | Workspace is accessible to skills and hooks; state files could contain sensitive data |

### For Hook Dynamic Skills Modification

| Problem | Description |
|---------|-------------|
| **No direct API** | No hook or API call can directly add/remove skills from the current session's skills list |
| **Snapshot already built** | `before_prompt_build` fires after snapshot decision; changes affect NEXT turn |
| **Watcher dependency** | Dynamic enable/disable requires `skills.load.watch: true` — often disabled in production |
| **No per-session toggle** | Skills are workspace-global; cannot enable for one session but not another |
| **Config hot-reload required** | Modifying `skills.entries.<skill>.enabled` may require hot-reload to take effect |
| **session:patch is read-react** | The `session:patch` hook only reacts to patches; it cannot initiate changes |

---

## 5. SOLUTIONS

### Solution 1: File-Based State Pattern for Skills

```javascript
// In skill instructions (SKILL.md):
// ## STATE FILE
// Location: <workspace>/.skills/my-skill/state.json
// Format: { "count": 0, "lastRun": "ISO timestamp" }

// Skill procedure:
// 1. Read state.json from <workspace>/.skills/my-skill/state.json
// 2. If not exists, initialize with defaults
// 3. Increment count, update lastRun
// 4. Write state.json back
// 5. Proceed with main logic using state
```

The skill must include file read/write instructions explicitly in its SKILL.md content.

### Solution 2: Hook-Driven Skills Toggle (Next Turn)

```javascript
// In a plugin hook handler:
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    const hour = new Date().getHours();
    if (hour >= 18 || hour < 9) {
      // Disable non-essential skills outside business hours
      event.context.cfg.skills = event.context.cfg.skills || {};
      // Note: This only affects next turn after watcher picks up changes
    }
  }
});
```

**Reality check:** This requires file modification + watcher trigger. The hook can't directly change the in-memory skills list.

### Solution 3: Skill Activation via session:patch

```javascript
// Hook that responds to session:patch events
api.registerHook({
  events: ["session:patch"],
  handler: async (event) => {
    if (event.context.patch?.activatedSkill) {
      // Write marker file that skill reads on next invocation
      const fs = await import('fs/promises');
      const statePath = `${event.context.workspaceDir}/.skills/active-skill.txt`;
      await fs.writeFile(statePath, event.context.patch.activatedSkill);
    }
  }
});
```

### Solution 4: Per-Agent Skill Allowlists (Static Control)

```javascript
// In openclaw.json
{
  agents: {
    defaults: { skills: ["essential", "critical"] },
    list: [
      { id: "researcher", skills: ["essential", "research", "web-search"] },
      { id: "simple", skills: ["essential"] }
    ]
  }
}
```

This is static and requires config change + restart, but provides clean isolation.

### Solution 5: Workspace Skill Renaming (Watcher-Based)

```javascript
// A cron job or hook renames skill directories to enable/disable
import { rename, access } from 'fs/promises';

async function disableSkill(skillName) {
  const skillPath = `${workspaceDir}/skills/${skillName}`;
  const disabledPath = `${workspaceDir}/skills/.disabled-${skillName}`;
  await access(skillPath).catch(() => { return; }); // skip if doesn't exist
  await rename(skillPath, disabledPath);
}

async function enableSkill(skillName) {
  const disabledPath = `${workspaceDir}/skills/.disabled-${skillName}`;
  const skillPath = `${workspaceDir}/skills/${skillName}`;
  await access(disabledPath).catch(() => { return; });
  await rename(disabledPath, skillPath);
}
```

The watcher picks up the directory change, bumps snapshot version, next turn uses new list.

---

## 6. EDGE CASES

### Edge Case: Concurrent Session State

If two sessions of the same agent run concurrently (both writing to `<workspace>/.skills/my-skill/state.json`), file corruption is possible. 

**Mitigation:** Use file locking or per-session state files (e.g., `state-{sessionKey}.json`).

### Edge Case: Session Store Contains Stale Skills Snapshot

If a session was created with skill X enabled, then X is deleted from disk, the session store still has the old `skillsSnapshot`. On session resume, `shouldRefreshSnapshotForVersion` is checked — if version changed, snapshot rebuilds. If version didn't change (X still exists in new location), old snapshot is reused.

### Edge Case: Hook Modifies cfg Before Snapshot Build

The `before_prompt_build` hook fires AFTER the skills snapshot is built for the current turn. So even if a previous hook modified `context.cfg.skills`, the current turn's snapshot is already computed.

### Edge Case: Skills Snapshot Version Collision

If watcher bumps version and hook in same turn also bumps, version numbers must be unique enough to trigger refresh. Uses timestamp-based version.

### Edge Case: Skill State File Lost on Workspace Reset

If workspace is reset or deleted, all skill state files are lost. Skills relying on workspace files for state must document this recovery procedure.

### Edge Case: session:patch Without Privileged Client

Only "privileged clients" can trigger `session:patch` events. A regular message cannot programmatically patch session state. Only gateway-internal or authenticated ACP clients can do this.

---

## 7. CREATIVE USES

### Creative Use 1: Skill-State-Aware Instructions
A skill that adjusts its own instructions based on accumulated state:
```
If state.json shows "mode: strict", add extra validation steps.
If "mode: relaxed", skip optional checks.
```

### Creative Use 2: Hook-Based Skill Roulette
A `before_prompt_build` hook randomly selects one skill from a pool for the current session, giving variety without config changes.

### Creative Use 3: Cross-Session Skill Memory
A dedicated skill (`skill-memory`) that other skills call via a standard protocol to read/write structured data. All skills use `skill-memory` instead of managing their own files.

### Creative Use 4: Emergency Skill Purge
A `session:patch` handler monitors for security incidents and, on detection, can trigger workspace skill directory renaming to disable potentially compromised skills.

### Creative Use 5: Session-Aware Skill Loading
Use `context.sessionEntry` in `before_prompt_build` to check which skills were used in previous turns of this session, then dynamically add complementary skills.

---

## NEW QUESTIONS

- [ ] Can skills use `context.workspaceDir` to read/write files without hook mediation? (Skills instructions could tell model to use exec tool)
- [ ] Is there a race condition risk when multiple sessions write to same workspace skill state file?
- [ ] Can a hook directly call `bumpSkillsSnapshotVersion()` to force refresh?
- [ ] What's the maximum skills snapshot version before wraparound/collision risk?
- [ ] Can session:patch be used to store custom skill data in session store (not just skillsSnapshot)?
- [ ] Does skills watcher also monitor subdirectories or only top-level skill folders?
- [ ] Can skills snapshot be disabled entirely for ultra-light sessions?

---

## Sources

- `/usr/local/lib/node_modules/openclaw/dist/session-updates-3NulUPmS.js` — `persistSessionEntryUpdate` with skillsSnapshot persistence
- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Skills snapshot building and session entry update
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher implementation, `bumpSkillsSnapshotVersion`
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook event types, `before_prompt_build` modifying merge, `session:patch` context
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills loading, watcher behavior
- `/usr/local/lib/node_modules/openclaw/docs/plugins/sdk-runtime.md` — `saveSessionStore` API

---

*Research by: Investigador Scout | 2026-04-23 09:20 CET*
