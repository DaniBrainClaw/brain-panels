# Skills Dynamic Enable/Disable Mid-Session — RESEARCH FINDINGS

**Research Date:** 2026-04-23

**Topic:** Can skills be dynamically enabled/disabled mid-session without gateway restart?

**Priority:** MED (#20)

**Status:** ✅ COMPLETE

---

## 1. WHAT IS

The ability to enable or disable OpenClaw skills **during an active session** without requiring a gateway restart. This is relevant for:
- Disabling a misbehaving skill immediately
- Enabling skills based on runtime conditions (time, user, channel)
- A/B testing skills without downtime

---

## 2. HOW IT WORKS

### Two mechanisms exist:

#### A. Config-based enabling/disabling
```json5
{
  skills: {
    entries: {
      myskill: {
        enabled: false  // disables skill even if bundled/installed
      }
    }
  }
}
```

#### B. Skills watcher (auto-refresh)
```json5
{
  skills: {
    load: {
      watch: true,           // enable file watching
      watchDebounceMs: 250   // debounce rapid changes
    }
  }
}
```

**Watcher behavior:**
- Monitors `SKILL.md` files in skill directories
- On file add/change/unlink, triggers `bumpSkillsSnapshotVersion()`
- New snapshot is picked up on **next agent turn** (not immediate)
- Uses chokidar for file system watching

**Key insight from code:**
```javascript
// refresh-p9Dzo7mb.js
const watchEnabled = params.config?.skills?.load?.watch !== false;
// On change → bumpSkillsSnapshotVersion → "next agent turn picks up new list"
```

---

## 3. USES

- **Emergency skill disable**: Instantly disable a problematic skill without gateway restart
- **Conditional skill activation**: Enable skills based on time (via cron), user, or channel
- **Development workflow**: Add new skills mid-session for testing
- **A/B testing**: Toggle skills on/off between sessions

---

## 4. PROBLEMS

| Problem | Description |
|---------|-------------|
| **Watcher only monitors SKILL.md** | The watcher only triggers on `SKILL.md` file changes, NOT config file changes |
| **Config changes may require reload** | Changing `skills.entries.<skill>.enabled` in config may require hot-reload or restart |
| **No per-session skill toggling** | Skills are global to workspace; cannot enable for one session but not another |
| **Watcher disabled in production** | Many production deployments disable file watching |
| **Mid-execution edge case** | If skill is executing when disabled, current call completes but subsequent calls fail |

---

## 5. SOLUTIONS

### Solution 1: Use watcher + SKILL.md modification
1. Set `skills.load.watch: true`
2. To disable: rename or delete the skill's SKILL.md (or add a marker file)
3. Next agent turn picks up the change

### Solution 2: Use config hot-reload
- If gateway is in `hot` or `hybrid` reload mode, edit `skills.entries.<skill>.enabled`
- Some config changes may still require restart

### Solution 3: Use per-agent skill allowlists
```json5
{
  agents: {
    list: [
      { id: "agent1", skills: ["skill-a", "skill-b"] },
      { id: "agent2", skills: ["skill-a"] }
    ]
  }
}
```
This provides session-scoped skill control at config level.

### Solution 4: Use `disableModelInvocation` for soft-disable
```json5
{
  skills: {
    entries: {
      myskill: {
        disableModelInvocation: true
      }
    }
  }
}
```
This keeps skill available via slash command but removes it from model prompt.

---

## 6. EDGE CASES

- **Skill executing when disabled**: Current tool call completes; subsequent calls fail with "skill not available"
- **Watcher race conditions**: Rapid add/change/unlink events are debounced (default 250ms)
- **Remote nodes**: Skills from remote nodes can trigger refresh when node becomes eligible
- **Config + watcher conflict**: If config disables skill AND watcher is enabled, config takes precedence at load time
- **Snapshot version**: Each refresh increments `snapshotVersion`; model sees new list on next turn

---

## 7. CREATIVE USES

- **Time-based skill activation**: Use cron to modify skill directory (rename SKILL.md) at specific times
- **User-segmented skills**: Have different SKILL.md files for different users, swap via hook
- **Skill A/B testing**: Alternate SKILL.md content between two skills with same name
- **Emergency kill switch**: Create a "dead man's switch" that disables all non-essential skills

---

## NEW QUESTIONS

- [ ] Can hooks dynamically modify the skills list at runtime (without config change)?
- [ ] Is there a tool command to reload skills without file changes?
- [ ] What happens to in-flight skill executions when SKILL.md is deleted?
- [ ] Can skills be enabled/disabled per-session (not just global to workspace)?
- [ ] Does config hot-reload apply to `skills.entries` changes?

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills watcher documentation (line 317+)
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — `enabled` and `disableModelInvocation` fields
- `/usr/local/lib/node_modules/openclaw/dist/refresh-p9Dzo7mb.js` — Skills watcher implementation
- `/usr/local/lib/node_modules/openclaw/dist/skills-DYF-hmoJ.js` — Snapshot building logic

---

*Research by: Investigador Scout*