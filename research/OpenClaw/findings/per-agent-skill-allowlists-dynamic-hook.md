# Per-Agent Skill Allowlists & Dynamic Hook Modification — RESEARCH FINDINGS

**Research Date:** 2026-04-23
**Topic:** Can per-agent skill allowlists be changed dynamically via hook?
**Priority:** MED (#24)
**Status:** ✅ COMPLETE

---

## 1. WHAT IS

**Question:** Can hooks dynamically modify the per-agent skill allowlists at runtime without config changes?

This asks whether there's a mechanism for hooks to programmatically add, remove, or swap skills during an active session based on conditions like user identity, channel, time, or other runtime context.

---

## 2. HOW IT WORKS

### Skills Snapshot Timing

The skills snapshot is built in `agent-command-BRtqb5oD.js` during session preparation:

```javascript
// Line 1097-1102
const skillsSnapshotVersion = getSkillsSnapshotVersion(workspaceDir);
const currentSkillsSnapshot = sessionEntry?.skillsSnapshot;
const shouldRefreshSkillsSnapshot = !currentSkillsSnapshot || 
  shouldRefreshSnapshotForVersion(currentSkillsSnapshot.version, skillsSnapshotVersion) || 
  !matchesSkillFilter(currentSkillsSnapshot.skillFilter, skillFilter);

const skillsSnapshot = needsSkillsSnapshot ? buildWorkspaceSkillSnapshot(workspaceDir, {...}) : currentSkillsSnapshot;
```

### Hook Execution Order

The `before_prompt_build` hook runs in `pi-embedded-runner-CefZK1Pt.js` AFTER the skills snapshot is passed to the attempt:

```javascript
// Line 3573-3588
const promptBuildResult = params.hookRunner?.runBeforePromptBuild({
  prompt: params.prompt, 
  messages: params.messages
}, params.hookCtx);

// Hook returns only:
return {
  systemPrompt: promptBuildResult?.systemPrompt ?? legacyResult?.systemPrompt,
  prependContext: joinPresentTextSegments([...]),
  prependSystemContext: joinPresentTextSegments([...]),
  appendSystemContext: joinPresentTextSegments([...])
};
```

### Per-Agent Skill Filter Resolution

The per-agent skill filter is resolved from config in `agent-scope-D7mk_f98.js`:

```javascript
// Line 101-103
function resolveAgentSkillsFilter(cfg, agentId) {
  return resolveEffectiveAgentSkillFilter(cfg, agentId);
}
```

This reads from:
- `cfg.agents.defaults.skills` — default skill list for all agents
- `cfg.agents.list[].skills` — per-agent overrides

---

## 3. USES

If this were possible, use cases would include:
- **Context-aware skill activation**: Enable/disable skills based on user, channel, time
- **A/B testing skills**: Dynamically swap skills for experimentation
- **Emergency disable**: Disable misbehaving skills when error rate exceeds threshold
- **Progressive rollout**: Gradually enable new skills for expanding user groups

---

## 4. PROBLEMS

| Problem | Description |
|---------|-------------|
| **No direct API** | No hook or API can modify skills list at runtime |
| **Snapshot already built** | `before_prompt_build` fires AFTER skills snapshot decision |
| **Hook return values are limited** | Only `systemPrompt`, `prependContext`, `prependSystemContext`, `appendSystemContext` can be returned |
| **Config changes take next turn** | Modifying `context.cfg.skills` in hook affects FUTURE turns, not current |
| **No pre-preparation hook** | No hook runs BEFORE skills snapshot is computed |

---

## 5. SOLUTIONS

### Solution 1: Pre-planned Skill Sets (Static)

Design skills to cover all anticipated scenarios, with SKILL.md instructions to activate/deactivate based on context detection.

### Solution 2: Config Hot-Reload (Next Turn)

Modify `skills.entries.<skill>.enabled` in config file, then trigger hot-reload. Changes take effect on NEXT turn (current turn already has snapshot).

```javascript
// After modifying config file:
await gateway.reloadConfig(); // Triggers skills snapshot rebuild
```

### Solution 3: Workspace Skill Renaming (Watcher-Based)

Rename skill directories to enable/disable them. The watcher detects changes and bumps the snapshot version for the next turn.

```javascript
// Hook renames skill directory
await rename(skillPath, disabledPath); // e.g., "skill-name" → ".disabled-skill-name"
// Next turn: watcher picks up change, snapshot refreshes
```

### Solution 4: Prompt Injection via Hook

While you cannot modify the skills list, you can inject skill-like behavior via `appendSystemContext`:

```javascript
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    if (shouldUseSpecialSkill(event)) {
      return {
        appendSystemContext: `\n\n# ADDITIONAL CAPABILITIES\nWhen user asks about X, use the following approach...\n`
      };
    }
  }
});
```

---

## 6. EDGE CASES

### Edge Case 1: Modifying cfg.skills in before_prompt_build

**Scenario:** Hook modifies `event.context.cfg.skills` expecting immediate effect.

**Reality:** The snapshot was already built before this hook runs. The modification only affects FUTURE turns.

### Edge Case 2: Session Resume with Modified Skills

**Scenario:** Session resumes after skills were modified in config.

**Behavior:** On resume, `shouldRefreshSnapshotForVersion` checks if version changed. If version didn't change but filter did, old snapshot may be stale.

### Edge Case 3: Concurrent Session Access

**Scenario:** Multiple sessions of same agent running concurrently, one modifies skill enablement.

**Reality:** Each session has its own skills snapshot. Changes to config affect all NEW sessions or sessions that trigger snapshot refresh.

### Edge Case 4: Hook Returns Skills-Like Content

**Scenario:** Hook tries to simulate skill behavior via system prompt.

**Limitation:** This works for prompt injection but doesn't give the skill actual metadata/invocation mechanics (skill isn't in the skills list shown to model).

---

## 7. CREATIVE USES

### Creative Use 1: Conditional System Prompt

Use `appendSystemContext` to inject scenario-specific instructions without modifying skill list:

```javascript
// In before_prompt_build hook:
if (event.context.channelId === "alerts") {
  return {
    appendSystemContext: "# ALERT MODE\nYou are in alerts channel. Keep responses brief and actionable."
  };
}
```

### Creative Use 2: Skill Usage Detection

Use `before_prompt_build` to log which skills WOULD be used, for analytics:

```javascript
// Log skill access pattern (read-only, doesn't modify)
const skills = params.skillsSnapshot?.entries || [];
console.log(`Session ${sessionKey} using ${skills.length} skills`);
```

### Creative Use 3: Emergency Skill Purge

In `agent:bootstrap` hook, check for emergency conditions and remove bootstrap files:

```javascript
api.registerHook({
  events: ["agent:bootstrap"],
  handler: async (event) => {
    const isSecurityIncident = await checkSecurityStatus();
    if (isSecurityIncident) {
      // Remove all skills from bootstrap
      event.context.bootstrapFiles = event.context.bootstrapFiles.filter(
        f => !f.includes("skills")
      );
    }
  }
});
```

---

## 8. NEW QUESTIONS

- [ ] Is there a hook that runs BEFORE skills snapshot is computed (preparation hook)?
- [ ] Can workspace skill directory changes be detected and applied within same turn?
- [ ] What's the performance impact of frequent skills snapshot refreshes?
- [ ] Can skills be enabled/disabled per-session via session:patch?

---

## Sources

- `/usr/local/lib/node_modules/openclaw/dist/agent-command-BRtqb5oD.js` — Skills snapshot building logic
- `/usr/local/lib/node_modules/openclaw/dist/pi-embedded-runner-CefZK1Pt.js` — `before_prompt_build` hook execution
- `/usr/local/lib/node_modules/openclaw/dist/agent-scope-D7mk_f98.js` — `resolveAgentSkillsFilter` function
- `/usr/local/lib/node_modules/openclaw/dist/hook-runner-global-D9t7KsGJ.js` — Hook merge function (mergeBeforePromptBuild)
- `/usr/local/lib/node_modules/openclaw/docs/automation/hooks.md` — Hook documentation

---

*Research by: Investigador Scout | 2026-04-23 09:18 CET*
*Status: COMPLETE ✅*