# Skills Dependencies & Chaining — Research Findings

**Topic:** Can skills declare dependencies on other skills (skill chaining)? Can skills call other skills recursively?

**Priority:** MED

**Date:** 2026-04-23 06:15 CET

**Research by:** Investigador Scout

**Status:** ✅ COMPLETED

---

## 1. WHAT IS — Definition & Core Concept

### Skill Dependencies
Skill dependencies refer to a skill that requires another skill to be present or enabled for its instructions to work correctly. Example: a "Madrid Wellness Report" skill might depend on a "Data Fetch" skill to retrieve member data.

### Skill Chaining
Skill chaining means a skill can invoke or trigger another skill as part of its execution. Example: a "Morning Ritual" skill chains the "Sauna Protocol" skill + "Cold Plunge Log" skill + "Membership Check" skill in sequence.

### Skill Recursion
Skill recursion means a skill that can call itself (directly or indirectly through a chain), creating potential infinite loops.

---

## 2. HOW IT WORKS — OpenClaw Skill System Architecture

### Built-in Dependency System: NONE EXISTS

**Finding:** OpenClaw has **NO native skill dependency system**. There is:
- ❌ No `dependencies` field in SKILL.md frontmatter
- ❌ No version pinning for skills
- ❌ No `requires.skills` gate
- ❌ No automatic skill resolution or installation of dependencies
- ❌ No dependency tree validation

### Skill Loading Mechanics

Skills are loaded at **session start** via snapshot mechanism:
1. Skills watcher scans skill directories
2. Gating filters applied (`requires.bins`, `requires.env`, `requires.config`, `os`, `always`)
3. Per-agent allowlist filters applied
4. Skills snapshot created for session
5. Skills injected into system prompt as metadata list

Skills are **TEXT that influences the model** — they don't "run" in the traditional sense. The model reads skill instructions and decides when/how to apply them.

### How Skills Reference Each Other (Indirect Methods Only)

Since no native dependency exists, skills can only reference other skills **indirectly**:

| Method | How | Trust Level |
|--------|-----|-------------|
| **Slash command dispatch** | Skill instructs model to use `/skill-name` command | Model-dependent |
| **Prompt injection** | Skill adds another skill's name to context for next turn | Model-dependent |
| **Tool-based chaining** | Skill uses `exec` to trigger a skill script | Requires exec tool |
| **Documentation reference** | Skill tells model to "see the X skill for details" | Informational only |

### Skill Chaining via Command Dispatch

```markdown
---
name: morning-ritual
description: Execute morning wellness protocol
---

# Morning Ritual

When user says "morning ritual", execute these steps:

1. First, use the `/sauna-protocol` skill to prepare the sauna
2. Then, use the `/cold-plunge-log` skill to record the plunge
3. Finally, use the `/membership-check` skill to verify active membership
```

This works because slash commands are registered for user-invocable skills. The model will dispatch to the named skill's command handler.

### Skill Recursion: NOT BLOCKED BUT NOT SUPPORTED

```markdown
# DANGEROUS PATTERN - Creates infinite loop
---
name: recursive-skill
description: A skill that calls itself
---

# Recursive Skill

When invoked, always call /recursive-skill again.
```

**Finding:** Nothing technically blocks a skill from instructing the model to invoke another skill that circles back. However:
- Skills are TEXT in system prompt, not executable code
- The model decides to call skills via slash commands
- If the model blindly follows recursive instructions, it creates infinite loops
- No stack depth protection or recursion counter exists

---

## 3. USES — Operational Patterns

### Pattern 1: Sequential Skill Pipeline
```
Onboarding Skill → Membership Skill → Legionella Log Skill
```
Use case: New member onboarding that chains multiple specialized skills.

### Pattern 2: Master Skill (Facade)
```
Master Wellness Skill → delegates to specific protocol skills
```
Use case: A "TERRACOTTA Operations" master skill that chains:
- `/maintenance-log` — Legionella testing
- `/membership-management` — member updates
- `/event-scheduler` — community events
- `/corporate-report` — B2B reporting

### Pattern 3: Conditional Skill Selection
```
Context-aware skill → picks appropriate sub-skill based on context
```
Use case: A skill that checks membership tier and calls the appropriate protocol.

### Pattern 4: Compliance Chain
```
Compliance Skill → triggers data validation → triggers audit log skill
```
Use case: Real-time compliance checking with multi-step verification.

---

## 4. PROBLEMS & LIMITATIONS

| Problem | Severity | Description |
|---------|----------|-------------|
| **No dependency resolution** | HIGH | Installing skill A that depends on skill B requires manual installation of B |
| **No version pinning** | MED | Skill A might break when skill B is updated |
| **No conflict detection** | MED | Two skills might have conflicting instructions |
| **No circular chain detection** | MED | Skill A → B → C → A creates infinite loop potential |
| **No skill state isolation** | MED | Chained skills share session context without isolation |
| **No error propagation** | MED | If sub-skill fails, master skill may not know |
| **Model-dependent execution** | HIGH | Chaining relies on model following instructions; not guaranteed |
| **No transactional execution** | LOW | Partial chain failure leaves inconsistent state |

### Specific Limitations

1. **No `requires.skills` gate**: Cannot block skill loading when dependency is missing
2. **No skill version constraints**: `github` skill v2.0 might break `reports` skill that expects v1.0
3. **No installation ordering**: `clawhub install` installs skills alphabetically, not by dependency
4. **No skill API**: Skills cannot programmatically query "is skill X enabled?"
5. **No nested transaction**: Chain can't be rolled back if step 3 fails

---

## 5. SOLUTIONS & BEST PRACTICES

### Solution 1: Manual Dependency Documentation

```markdown
# SKILL.md for terracotta-maintenance

---
name: terracotta-maintenance
description: TERRACOTTA facility maintenance operations
metadata: {"openclaw": {"requires": {"bins": ["python3"]}}}
---

# TERRACOTTA Maintenance Skill

## Dependencies (MANUAL INSTALL REQUIRED)
This skill requires the following skills to be installed:
- `legionella-log` — for water testing documentation
- `membership-core` — for member data access

## Usage
When user asks about maintenance, use the appropriate sub-skill.
```

**Pros:** Simple, no technical changes needed
**Cons:** Manual, no enforcement, easy to break

### Solution 2: Master Skill Pattern

Create a "TERRACOTTA Operations" master skill that:
- Contains the orchestration logic
- References sub-skills via slash commands
- Includes error handling for missing sub-skills

```markdown
---
name: terracotta-operations
description: Master skill for TERRACOTTA business operations
---

# TERRACOTTA Operations Master Skill

## Available Operations

| Operation | Slash Command | Description |
|-----------|--------------|-------------|
| Legionella Log | `/legionella-log` | Water quality documentation |
| Membership | `/membership-management` | Member onboarding/offboarding |
| Event Planning | `/event-scheduler` | Community event coordination |
| Corporate B2B | `/corporate-report` | Corporate wellness reporting |

## Error Handling
If a sub-skill is not available, inform the user and suggest installing it.
```

**Pros:** Clear interface, discoverable operations
**Cons:** Still manual dependency management

### Solution 3: Hook-Based Skill Activation

Use `before_prompt_build` hook to inject skill context dynamically:

```typescript
// In a hook, inject skill reference based on context
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    // Detect which sub-skill context is needed
    if (event.context.userMessage.includes("legionella")) {
      event.context.systemPrompt += `\n\n[Use the /legionella-log skill for water testing.]`;
    }
  }
});
```

**Pros:** Dynamic, context-aware
**Cons:** Requires custom hook code, not pure skill solution

### Solution 4: Skill Grouping via Directory

Organize related skills under a single directory:
```
skills/terracotta/
  SKILL.md (main index)
  legionella-log/
    SKILL.md
  membership/
    SKILL.md
  events/
    SKILL.md
```

Use workspace precedence so `skills/terracotta/` overrides any conflicting skills.

**Pros:** Logical grouping, versioned together
**Cons:** No automatic dependency resolution

---

## 6. EDGE CASES

### Edge Case 1: Two Skills Both Depend on Each Other
```
Skill A instructions → "Use /skill-b"
Skill B instructions → "Use /skill-a"
```
**Result:** Potential infinite loop. Model alternates between skills until context limit hit.

### Edge Case 2: Master Skill Installed Before Sub-Skills
**Result:** Master skill references non-existent slash commands. Model reports skill not found. User must manually install sub-skills.

### Edge Case 3: Skill Updates Break Chain
Skill B v2.0 changes its slash command from `/membership` to `/member-manage`. Master skill A still references `/membership`.
**Result:** Chain breaks silently. No error notification.

### Edge Case 4: Concurrent Skill Modification
While Master Skill A is executing `/skill-b`, user updates skill B's SKILL.md.
**Result:** In-flight operation uses old skill B content while new session would use updated content. Inconsistent behavior.

### Edge Case 5: Skill Recursion Depth
```
Skill A → Skill B → Skill C → Skill D → Skill E → [context limit]
```
**Result:** No explicit stack limit. Chain runs until model decides to stop or context overflows.

---

## 7. CREATIVE USES

### Creative Use 1: Skill-Based Business Process Engine
```
TERRACOTTA Core Operations
├── Maintenance Protocols (Legionella, water quality)
├── Membership Lifecycle (onboarding → active → churned)
├── Marketing Automation (event announcement → follow-up)
└── Corporate B2B (proposal → contract → reporting)
```

Each sub-skill is a "module" that can be invoked independently or chained.

### Creative Use 2: Dynamic Skill Assembly
A meta-skill that generates other skills based on context:
```markdown
# Dynamic Protocol Generator

When user describes a new TERRACOTTA procedure:
1. Document the procedure in a new SKILL.md
2. Register it as a slash command
3. Add it to the operations index
```

### Creative Use 3: Skill-Based Compliance Engine
```
Compliance Check Skill
├── Validates against regulatory requirements
├── Chains to appropriate documentation skill
└── Logs compliance evidence
```

### Creative Use 4: Multi-Agent Skill Coordination
Skills that invoke sub-agents for complex tasks:
```markdown
# Corporate Report Skill

When generating a corporate wellness report:
1. Use `/data-fetch` to get member metrics
2. Spawn sub-agent for report generation
3. Deliver report via corporate channel
```

---

## NEW QUESTIONS FOR BACKLOG

### From Skill Dependencies Research

1. **[MED]** Could a skill manifest format with dependency declarations be added? Would require PR to OpenClaw core.
2. **[MED]** Can a before_prompt_build hook dynamically inject skill references based on session context?
3. **[MED]** What is the maximum recommended chain depth before context overhead becomes problematic?
4. **[LOW]** Can skills use the `exec` tool to invoke shell scripts that represent "sub-skills"?
5. **[LOW]** Could skill directories use a `_meta.json` for group-level metadata and dependencies?
6. **[MED]** Is there a way to implement skill "transactions" (all-or-nothing execution)?
7. **[MED]** Can skills be loaded conditionally based on other skill presence?
8. **[LOW]** What happens when two skills in a chain have conflicting instructions to the model?

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skill loading, precedence, gating rules
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — Skill config schema
- `/usr/local/lib/node_modules/openclaw/docs/tools/creating-skills.md` — Skill creation workflow
- `/usr/local/lib/node_modules/openclaw/docs/tools/slash-commands.md` — Slash command dispatch
- OpenClaw source code analysis — skills snapshot mechanism, skill invocation flow

---

*Research by: Investigador Scout | 2026-04-23 06:15 CET*
