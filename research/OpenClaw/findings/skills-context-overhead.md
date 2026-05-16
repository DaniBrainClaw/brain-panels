# Skills Per Agent Context Overhead — Research Findings

**Topic:** What is the maximum recommended number of skills per agent before context overhead becomes problematic?
**Priority:** MED
**Date:** 2026-04-23 08:02 CET
**Research by:** Investigador Scout
**Status:** ✅ COMPLETE

---

## 1. WHAT IS — Definition & Core Concept

### Definition

**Skills context overhead** is the token cost of injecting the skills list into the agent's system prompt. Unlike tool schemas (which are also in the prompt), skills have a compact XML representation that scales linearly with the number of skills.

The overhead comes from:
1. **Base overhead** — Fixed cost when ≥1 skill exists (195 characters)
2. **Per-skill overhead** — Scales with skill count (97 chars + XML-escaped name/description/location)

### Token Calculation Formula

```
total_chars = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
total_tokens ≈ total_chars / 4 (OpenAI-style estimate)
```

**Key formula components:**
- Base overhead: **195 characters** (~49 tokens)
- Per skill: **97 + field lengths** (~120-180 characters depending on field lengths)
- Per skill tokens: **~24-45 tokens** depending on field lengths

### XML Escaping Impact

XML escaping expands `& < > " '` into entities (`&amp;`, `&lt;`, etc.), which increases length:
- Skill names with underscores/hyphens: minimal escaping
- Skill descriptions with quotes/ampersands: significant escaping (2x in extreme cases)

---

## 2. HOW IT WORKS — Context Window & Runtime Cap Mechanics

### Two-Level Context Limits

1. **Model context window** — Hardware/model limit (e.g., 204,800 tokens for MiniMax M2.7)
2. **Runtime context cap** — `agents.defaults.contextTokens` setting (e.g., 200,000 for MiniMax M2.7)

The runtime cap is typically set **below** the model context window to leave room for:
- Output tokens
- Safety margins
- Provider-specific overhead

### Current System Configuration

| Model | Context Window | Runtime Cap | Setting |
|-------|---------------|-------------|---------|
| MiniMax M2.7 | 204,800 | 200,000 | `agents.defaults.contextTokens` |
| GPT-5.4 | 1,050,000 | 272,000 | `openai-codex` default |
| Gemini 2.5 Pro | ~1,000,000+ | Provider default | N/A |
| Gemini 2.5 Flash | ~128,000 | Provider default | N/A |

### Prompt Budget Breakdown

For MiniMax M2.7 (200,000 token runtime cap), typical budget allocation:

| Component | Typical Tokens | Notes |
|-----------|---------------|-------|
| System prompt core (tooling, safety, self-update, workspace, docs, time, runtime) | ~2,500-4,000 | Varies with thinking level |
| Skills list | Variable | ~24-45/skill |
| Bootstrap files (MEMORY.md, AGENTS.md, etc.) | ~1,000-15,000 | Controlled by `bootstrapMaxChars` |
| Conversation history | Variable | Grows with turns |
| Tool results | Variable | Depends on tool usage |
| **Available for new input + output** | ~170,000-190,000 | After fixed costs |

---

## 3. USES — Practical Skill Count Recommendations

### Conservative Recommendations (Safety Margin)

| Scenario | Max Skills | Rationale |
|----------|------------|-----------|
| MiniMax M2.7 (200K cap) — aggressive | **~200 skills** | 200 × 45 tokens = 9,000 tokens (~5% of budget) |
| MiniMax M2.7 (200K cap) — conservative | **~100 skills** | 100 × 45 tokens = 4,500 tokens (~2.5% of budget) |
| MiniMax M2.7 (200K cap) — minimal overhead | **~50 skills** | 50 × 45 tokens = 2,250 tokens (~1% of budget) |
| GPT-5.4 (272K cap) — conservative | **~300 skills** | Larger cap allows more |
| Gemini 2.5 Flash (~128K cap) | **~50 skills** | Smaller cap requires discipline |

### Formula for Maximum Skills

```
max_skills = (contextTokens - systemPromptTokens - bootstrapTokens - outputReserve) / tokensPerSkill
```

**Example for MiniMax M2.7:**
- contextTokens: 200,000
- systemPromptTokens: ~3,000
- bootstrapTokens: ~5,000 (with MEMORY.md)
- outputReserve: ~10,000 (for model output)
- tokensPerSkill: ~35 (average with description length)

```
max_skills = (200,000 - 3,000 - 5,000 - 10,000) / 35 ≈ 5,200 skills (theoretical)
```

**Practical limit is much lower** due to:
1. Conversation history growth
2. Tool results during session
3. Compaction overhead
4. Provider-specific overhead

### Realistic Production Recommendations

| Use Case | Recommended Max | Rationale |
|----------|-----------------|-----------|
| General purpose agent | **50-100 skills** | Leave room for conversation growth |
| Research-heavy agent | **30-50 skills** | Need room for large tool results |
| Memory-intensive agent | **20-30 skills** | MEMORY.md + history consume budget |
| Lightweight/embedded agent | **10-20 skills** | Minimal context footprint |

### Current System Skill Count

| Location | Count |
|----------|-------|
| Bundled (`openclaw/skills/`) | ~17 skills |
| Managed (`~/.openclaw/skills/`) | 7 skills |
| Workspace (`workspace/skills/`) | 1 skill |
| **Total visible** | **~25 skills** |
| **Effective (with gating)** | **~10-15** (some gated by requirements) |

**Current overhead:** ~25 skills × ~35 tokens = ~875 tokens (~0.4% of 200K budget)

---

## 4. PROBLEMS — When Context Overhead Becomes Problematic

### Warning Signs

| Symptom | Threshold | Indication |
|---------|-----------|------------|
| Frequent `context overflow` errors | >85% context usage | Skills list + history too large |
| Slow compaction triggers | >75% context usage | Model context filling up |
| Token cost spikes | Unexpectedly high | Skills list growing unchecked |
| `/context detail` shows skills >10% | Context budget concern | Reduce skill count |

### Failure Modes

1. **Context overflow errors** — Model rejects input when context full
2. **Compaction thrashing** — Excessive compaction degrades session quality
3. **Memory pressure** — High context = high memory for session
4. **Cost inflation** — More context = higher token costs per turn

### Causes of Excessive Overhead

| Cause | Solution |
|-------|----------|
| Too many skills enabled globally | Use per-agent `skills` allowlist |
| Skills with long descriptions | Keep descriptions concise (<100 chars) |
| Skills in all locations loaded | Restrict via `skills.load.extraDirs` |
| No skill gating/filters | Use `requires.bins`, `requires.env` to auto-filter |
| Bootstrap files too large | Set `bootstrapMaxChars`, `bootstrapTotalMaxChars` |

---

## 5. SOLUTIONS — Managing Skills Context Overhead

### Strategy 1: Per-Agent Skill Allowlists

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],  // Small baseline
    },
    list: [
      { id: "research", skills: ["github", "weather", "web-research", "continuous-improvement"] },
      { id: "minimal", skills: [] },  // No skills
    ],
  },
}
```

**Benefit:** Only load skills needed for each agent

### Strategy 2: Skill Description Optimization

**BAD (long description):**
```markdown
---
name: my-skill
description: "This skill does X, Y, Z and handles edge cases A, B, C when used in context of D and E scenarios"
---
```

**GOOD (concise description):**
```markdown
---
name: my-skill
description: "When to use X and Y"
---
```

### Strategy 3: Skill Gating with Metadata

```markdown
---
name: docker-build
requires:
  bins: ["docker"]
---
```

Skills with unmet requirements are **automatically excluded** from the eligible set, reducing overhead.

### Strategy 4: Disable Unused Skills

```json5
{
  skills: {
    entries: {
      "unused-skill": { enabled: false }
    }
  }
}
```

### Strategy 5: Runtime Context Cap Adjustment

```json5
{
  agents: {
    defaults: {
      contextTokens: 150000,  // Lower cap = less context pressure
    }
  }
}
```

**Trade-off:** Less room for conversation history

### Strategy 6: Use Smaller Models for Simple Tasks

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "minimax/MiniMax-M2.7",
        fallbacks: ["google/gemini-3.1-flash-lite"]  // Use smaller for simple tasks
      }
    }
  }
}
```

---

## 6. EDGE CASES — Unexpected Behaviors

### Edge Case: Skill Name Conflicts

When same skill exists in multiple locations:
- Only **one** entry appears in the skills list (highest precedence wins)
- Other copies are ignored
- **Overhead is per-unique-skill-name**, not per-location

### Edge Case: `disable-model-invocation: true`

Skills with this flag are **excluded from the model prompt** but still available via user invocation (slash commands). This means:
- **Zero token overhead** for model-visible skills list
- Available only when user explicitly invokes

### Edge Case: Skills with `command-dispatch: tool`

Slash command **bypasses the model** for dispatch. Still appears in skills list but:
- Model doesn't read SKILL.md for invocation
- Tool invoked directly

### Edge Case: Skill Gating Removes Most Skills

If 100 skills are installed but only 5 meet gating criteria:
- **Only 5 appear in the skills list**
- Overhead is based on eligible count, not installed count

### Edge Case: Compaction Changes Skill Overhead Ratio

As session grows and gets compacted:
- Historical context shrinks (compressed)
- Skills list stays constant
- Skills overhead **percentage increases** over time

### Edge Case: `agents.defaults.skills` vs `agents.list[].skills`

```json5
{
  agents: {
    defaults: { skills: ["base"] },  // Baseline for all agents
    list: [
      { id: "extra", skills: ["base", "extra"] },  // REPLACES defaults
    ]
  }
}
```

- `skills: ["base", "extra"]` **replaces** defaults, does not merge
- `skills: []` means **no skills**
- No skills in either → all visible skills eligible

---

## 7. CREATIVE USES — Novel Applications

### Creative Use 1: Dynamic Skill Loading by Context

Combine `before_prompt_build` hook to dynamically adjust skill allowlist based on conversation topic:

```typescript
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    const topic = event.context.recentTopics?.[0];
    if (topic === "code") {
      event.agentConfig.skills = ["github", "coding-agent", "code-review"];
    } else if (topic === "research") {
      event.agentConfig.skills = ["web-research", "continuous-improvement"];
    }
  }
});
```

### Creative Use 2: Skill Overhead Budget Monitor

Create a hook that warns when skills overhead exceeds threshold:

```typescript
api.registerHook({
  events: ["before_agent_start"],
  handler: async (event) => {
    const skillsOverhead = calculateSkillsOverhead(event.visibleSkills);
    if (skillsOverhead > 5000) {  // 5K tokens
      console.warn(`High skills overhead: ${skillsOverhead} tokens`);
    }
  }
});
```

### Creative Use 3: Context-Aware Skill Subsetting

For memory-intensive sessions, temporarily reduce skills:

```json5
{
  agents: {
    list: [{
      id: "heavy-memory",
      contextTokens: 180000,  // Lower cap
      skills: ["core-only"]   // Fewer skills
    }]
  }
}
```

### Creative Use 4: Skill-Based Context Budget Allocation

Use skills as a way to budget context:
- Keep skill descriptions under 100 characters
- Use `disable-model-invocation: true` for rarely-used skills
- Only load essential skills per agent

---

## NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] What triggers `context overflow` errors — skills alone, or skills + history? **[MED]**
- [ ] Does `/context detail` show per-skill token breakdown? **[MED]**
- [ ] How does compaction affect skills list visibility? **[LOW]**

### b) Internal Mechanics
- [ ] Can skills list be paginated or collapsed for very large skill sets (>500)? **[MED]**
- [ ] What is exact overhead of `disable-model-invocation: true` skill? Zero or still listed? **[MED]**
- [ ] Does `skills.load.extraDirs` add to visible skill count even if skills are gated out? **[LOW]**

### c) Use Cases
- [ ] Can per-agent skill allowlists be changed dynamically via hook? **[MED]**
- [ ] Is there a cost difference between 50 short-description skills vs 50 long-description skills? **[LOW]**

### d) Best Practices
- [ ] What is recommended skill description length to minimize overhead? **[MED]**
- [ ] Should rarely-used skills use `disable-model-invocation: true`? **[MED]**
- [ ] What is better: many small skills or few comprehensive skills? **[MED]**

### e) Problems & Limitations
- [ ] Does high skill count affect model startup time (loading SKILL.md)? **[LOW]**
- [ ] Is there a known issue with skills list not refreshing when `agents.defaults.skills` changes? **[MED]**

### f) Solutions & Workarounds
- [ ] Can skills be loaded from remote URLs to reduce local overhead? **[MED]**
- [ ] Is there a way to profile skills overhead in production? **[MED]**

---

## Summary: Quick Reference

| Question | Answer |
|----------|--------|
| Token overhead per skill | ~24-45 tokens (depending on field lengths) |
| Base overhead | ~49 tokens (195 chars) |
| Recommended max skills (MiniMax M2.7) | **50-100 conservative, 200 aggressive** |
| Recommended max skills (GPT-5.4 272K) | **150-300 conservative** |
| Recommended max skills (Gemini 2.5 Flash) | **30-50 conservative** |
| Skills overhead % of 200K budget (100 skills) | ~2.5% |
| Skills overhead % of 200K budget (200 skills) | ~5% |
| Way to reduce overhead | Per-agent allowlists, short descriptions, `disable-model-invocation` |

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills overhead formula, base + per-skill costs
- `/usr/local/lib/node_modules/openclaw/docs/reference/token-use.md` — Token use breakdown, context window mechanics
- `/usr/local/lib/node_modules/openclaw/docs/concepts/system-prompt.md` — System prompt structure, skills section
- `/usr/local/lib/node_modules/openclaw/docs/concepts/context.md` — Context window vs tracked tokens
- `/usr/local/lib/node_modules/openclaw/docs/concepts/model-providers.md` — Model contextWindow metadata
- `~/.openclaw/openclaw.json` — Current system config (MiniMax M2.7: 204,800 contextWindow, 200,000 runtime cap)
- `/usr/local/lib/node_modules/openclaw/dist/` — Source analysis for skills loading

---

*Research by: Investigador Scout | 2026-04-23 08:02 CET*
