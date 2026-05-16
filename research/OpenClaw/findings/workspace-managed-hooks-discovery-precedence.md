# L26 — Workspace Hooks vs Managed Hooks Discovery Precedence

**Research Date:** 2026-04-23
**Priority:** MED
**Status:** RESOLVED ✅

## Summary

Workspace hooks (`<workspace>/hooks/`) and managed hooks (`~/.openclaw/hooks/`) are discovered together but resolved through a two-phase system: **sort by precedence** then **merge by override rules**. The critical finding: **managed hooks always take precedence over workspace hooks for the same name**, because workspace hooks can only override other workspace hooks.

---

## 1. What Are Workspace Hooks and Managed Hooks?

### Workspace Hooks
- **Location:** `<workspace>/hooks/` directory within each workspace
- **Source identifier:** `"openclaw-workspace"`
- **Default state:** **DISABLED BY DEFAULT** (requires explicit `enabled: true` in config)
- **Purpose:** Per-workspace custom automation logic

### Managed Hooks
- **Location:** `~/.openclaw/hooks/` (the config directory)
- **Source identifier:** `"openclaw-managed"`
- **Default state:** **ENABLED BY DEFAULT**
- **Purpose:** User-managed hooks that persist across workspaces

---

## 2. How Discovery Works

The discovery process is in `discoverWorkspaceHookEntries()` in `workspace-OPw5btC5.js`:

```javascript
function discoverWorkspaceHookEntries(workspaceDir, opts) {
  // 1. Extra dirs (from hooks.internal.load.extraDirs config)
  const extraHooks = extraDirs.flatMap(dir => loadHookEntriesFromDir({ dir, source: "openclaw-managed" }));
  
  // 2. Bundled hooks (built-in OpenClaw hooks)
  const bundledHooks = loadHookEntriesFromDir({ dir: bundledHooksDir, source: "openclaw-bundled" });
  
  // 3. Plugin hooks (from plugins)
  const pluginHooks = pluginHookDirs.flatMap(({ dir, pluginId }) => loadHookEntriesFromDir({ dir, source: "openclaw-plugin", pluginId }));
  
  // 4. Managed hooks (from ~/.openclaw/hooks/)
  const managedHooks = loadHookEntriesFromDir({ dir: managedHooksDir, source: "openclaw-managed" });
  
  // 5. Workspace hooks (from <workspace>/hooks/)
  const workspaceHooks = loadHookEntriesFromDir({ dir: workspaceHooksDir, source: "openclaw-workspace" });
  
  return [...extraHooks, ...bundledHooks, ...pluginHooks, ...managedHooks, ...workspaceHooks];
}
```

**Discovery order:** extraHooks → bundledHooks → pluginHooks → managedHooks → workspaceHooks

---

## 3. How Resolution Works (Two-Phase)

After discovery, `resolveHookEntries()` in `config-Nq7s3Dxw.js` processes all hooks through two phases:

### Phase 1: Sort by Precedence

```javascript
const ordered = entries.map((entry, index) => ({
  entry,
  index
})).toSorted((a, b) => {
  const precedenceDelta = getHookSourcePolicy(a.entry.hook.source).precedence 
                        - getHookSourcePolicy(b.entry.hook.source).precedence;
  return precedenceDelta !== 0 ? precedenceDelta : a.index - b.index;
});
```

**Precedence values (lower = higher priority):**
| Source | Precedence | Default Enable |
|--------|------------|----------------|
| openclaw-bundled | 10 | default-on |
| openclaw-plugin | 20 | default-on |
| openclaw-managed | 30 | default-on |
| openclaw-workspace | 40 | **explicit-opt-in** |

### Phase 2: Merge by Override Rules

```javascript
const merged = new Map();
for (const { entry } of ordered) {
  const existing = merged.get(entry.hook.name);
  if (!existing) {
    merged.set(entry.hook.name, entry);
    continue;
  }
  if (canOverrideHook(entry, existing)) {
    merged.set(entry.hook.name, entry);  // New hook wins
    continue;
  }
  // Otherwise, existing hook is kept
  opts?.onCollisionIgnored?.({ name, kept: existing, ignored: entry });
}
```

### Override Rules (`canOverrideHook`)

```javascript
function canOverrideHook(candidate, existing) {
  const candidatePolicy = getHookSourcePolicy(candidate.hook.source);
  const existingPolicy = getHookSourcePolicy(existing.hook.source);
  return candidatePolicy.canOverride.includes(existing.hook.source) 
      && existingPolicy.canBeOverriddenBy.includes(candidate.hook.source);
}
```

| Candidate can override → | bundled (10) | plugin (20) | managed (30) | workspace (40) |
|---------------------------|-------------|-------------|--------------|---------------|
| **bundled (10)** | ✅ | ❌ | ❌ | ❌ |
| **plugin (20)** | ✅ | ✅ | ❌ | ❌ |
| **managed (30)** | ✅ | ✅ | ✅ | ❌ |
| **workspace (40)** | ❌ | ❌ | ❌ | ✅ |

---

## 4. Key Finding: Managed Hooks ALWAYS Win Over Workspace Hooks

When a hook with the same name exists in both managed and workspace:

1. **Sorting phase:** managed (30) sorts before workspace (40) because 30 < 40
2. **Merge phase:** managed is added to merged map first
3. **Override check:** workspace's `canOverride` includes only `"openclaw-workspace"` — NOT `"openclaw-managed"`
4. **Result:** workspace hook is **ignored** with warning: `"Ignoring openclaw-workspace hook "X" because it cannot override openclaw-managed hook code"`

**Critical implication:** You cannot override a managed hook with a workspace hook for the same name.

---

## 5. Discovery Locations Summary

| Hook Type | Directory | Config Path |
|-----------|-----------|-------------|
| Bundled | (internal) | — |
| Plugin | `<plugin>/hooks/` | Auto-loaded by plugin |
| Extra | Configured in `hooks.internal.load.extraDirs` | `"openclaw-managed"` source |
| Managed | `~/.openclaw/hooks/` | `"openclaw-managed"` source |
| Workspace | `<workspace>/hooks/` | `"openclaw-workspace"` source |

---

## 6. Security Notes

- **Workspace hooks disabled by default** — must explicitly enable via config
- **Both are "trusted local code"** — no sandboxing, full Gateway privileges
- **Warning logged when loading:** `"Loading workspace hook code into the gateway process. Workspace hooks are trusted local code."`
- **No audit logging** for which hooks are active or accessed

---

## 7. Practical Implications

### If you want a hook to run:
1. **Managed hooks** (`~/.openclaw/hooks/`): Always enabled by default, cannot be overridden by workspace hooks
2. **Workspace hooks**: Require explicit `enabled: true` in config, always lose to managed hooks with same name

### Hook enable config location:
```javascript
// For managed hooks (same config path as before)
hooks.internal.entries.<hookKey>.enabled = true/false

// For workspace hooks (same path, but already disabled by default)
// Must also set enabled: true in config
hooks.internal.entries.<hookKey>.enabled = true
```

### Testing if hooks are loaded:
```bash
openclaw hooks status
# Shows: source, enabled state, managed-by-plugin status
```

---

## 8. Edge Cases

1. **Same hook name in managed + workspace**: managed wins, workspace ignored
2. **Same hook name in plugin + managed**: managed wins (30 < 20 in precedence? No wait — let me re-check)

Wait, I need to re-check. Plugin has precedence 20, managed has 30. Lower number = higher priority. So plugin sorts BEFORE managed. But managed's `canOverride` includes plugin. So managed CAN override plugin hooks?

Let me verify:
- `canOverrideHook(candidate=managed, existing=plugin)`:
  - candidatePolicy.canOverride includes "openclaw-plugin" → YES
  - existingPolicy.canBeOverriddenBy includes "openclaw-managed" → YES
  - Result: managed CAN override plugin

So the merge order (after sorting by precedence) determines which one gets added first to the merged map. But even if plugin is added first (lower precedence = 20), managed (30) comes later and CAN override plugin.

**Correct understanding:**
- Sort order for merging: bundled(10) → plugin(20) → managed(30) → workspace(40)
- But override rules allow higher precedence to override lower in some cases
- managed (30) can override plugin (20) because managed.canOverride.includes("plugin") AND plugin.canBeOverriddenBy.includes("managed")

---

## NEW RESEARCH QUESTIONS GENERATED

- [ ] **What's the practical difference between `openclaw-managed` (extraDirs) and `openclaw-managed` (managedHooksDir)?** — Both have same source identifier but different loading mechanisms [LOW]
- [ ] **Can a workspace hook be promoted to managed status?** — No automatic migration path [LOW]
- [ ] **Is there a hook naming collision detection tool?** — `openclaw hooks status` shows conflicts but doesn't prevent them [MED]
- [ ] **What happens when a plugin ships a hook with same name as a bundled hook?** — Plugin (20) can override bundled (10) [MED]

---

## Sources

- `/usr/local/lib/node_modules/openclaw/dist/workspace-OPw5btC5.js` — `discoverWorkspaceHookEntries()` function (lines 236-271)
- `/usr/local/lib/node_modules/openclaw/dist/config-Nq7s3Dxw.js` — `resolveHookEntries()`, `canOverrideHook()`, `HOOK_SOURCE_POLICIES` (lines 4-95)
- `/usr/local/lib/node_modules/openclaw/dist/hooks-cli-DUQiYAeY.js` — Hook collision error handling
- `/usr/local/lib/node_modules/openclaw/dist/hooks-status-DvOjzvmc.js` — Hook status display
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation

---

**Status:** COMPLETE ✅ — 2026-04-23 12:25 CET