# Encoding TERRACOTTA Business Procedures as Skills — Research Findings

**Topic:** Could TERRACOTTA business procedures be encoded as skills for consistent execution?

**Priority:** HIGH — Critical for operational scaling and consistency

**Date:** 2026-04-23 06:15 CET

**Research by:** Investigador Scout

**Status:** ✅ COMPLETED (updated with skill dependencies research)

---

## 1. WHAT IS — Definition & Core Concept

Encoding TERRACOTTA business procedures as skills means converting standard operating procedures (SOPs) into modular, versioned OpenClaw skill bundles. Instead of relying on human memory or static documents, the agent uses these skills as interactive "living manuals" to guide operations.

**CRITICAL FINDING:** OpenClaw has **NO native skill dependency system**. Skills are TEXT that influences the model — they don't "run" in the traditional sense. Each skill must be self-contained; chaining requires model cooperation via slash commands.

---

## 2. HOW IT WORKS — Operational Execution

### Skill Architecture for TERRACOTTA

Each TERRACOTTA procedure is a skill folder:
```
skills/terracotta/
├── SKILL.md (main operations index)
├── legionella-log/
│   └── SKILL.md (water testing procedure)
├── membership/
│   └── SKILL.md (onboarding/offboarding)
├── maintenance/
│   └── SKILL.md (facility maintenance)
├── events/
│   └── SKILL.md (community events)
└── corporate/
    └── SKILL.md (B2B reporting)
```

### How Skills Execute

1. **Skill is TEXT in system prompt** — skills are instructions the model reads
2. **Slash commands invoke skills** — `/legionella-log` triggers the skill's command handler
3. **Model follows skill instructions** — decides when/how to apply procedures
4. **No automatic chaining** — master skill must explicitly instruct model to use sub-skills
5. **No dependency resolution** — sub-skills must be manually installed

---

## 3. USES — Key Operational Domains

### TERRACOTTA Skill Map

| Domain | Skill Name | Slash Command | Description |
|--------|------------|---------------|-------------|
| **Maintenance** | `legionella-log` | `/legionella-log` | RD 865/2003 water testing, log results |
| **Maintenance** | `maintenance-daily` | `/maintenance-daily` | Daily facility checks |
| **Membership** | `membership-onboard` | `/membership-onboard` | New member welcome workflow |
| **Membership** | `membership-offboard` | `/membership-offboard` | Member cancellation/suspension |
| **Events** | `event-scheduler` | `/event-scheduler` | Community event creation |
| **Events** | `event-reminder` | `/event-reminder` | Automated reminders |
| **Corporate** | `corporate-proposal` | `/corporate-proposal` | B2B wellness proposal generation |
| **Corporate** | `corporate-report` | `/corporate-report` | ROI reporting for corporate partners |
| **Operations** | `operations-master` | `/terracotta-ops` | Master skill for all operations |

### Daily Operations Flow

```
Morning (9:00)
  → /maintenance-daily → Salt electrolysis check, water levels
  → /legionella-log → Record Legionella test results (if test day)

Onboarding (as needed)
  → /membership-onboard → Welcome message, tier selection, payment setup

Events (weekly)
  → /event-scheduler → Create/update community events
  → /event-reminder → Send reminders 24h before

Corporate (monthly)
  → /corporate-proposal → Generate B2B proposal for prospects
  → /corporate-report → Monthly usage report for existing contracts
```

---

## 4. PROBLEMS & LIMITATIONS

| Problem | Severity | Impact |
|---------|----------|--------|
| **No dependency system** | CRITICAL | Cannot declare that `/terracotta-ops` requires sub-skills; must manually install all |
| **No automatic resolution** | HIGH | Installing via ClawHub installs skills alphabetically, not by dependency |
| **No version pinning** | HIGH | Sub-skill updates may break master skill references |
| **Model-dependent chaining** | HIGH | Chaining relies on model following instructions; not guaranteed |
| **No error propagation** | MED | If sub-skill fails, master skill may not detect failure |
| **No transactional execution** | MED | Partial chain failure leaves inconsistent state |
| **No skill state isolation** | MED | Chained skills share session context without isolation |

### TERRACOTTA-Specific Limitations

1. **Data Sensitivity**: Member data in system prompts poses risk — treat skills as untrusted code equivalent
2. **Compliance Chain Gaps**: If sub-skill for Legionella logging is missing, compliance chain breaks
3. **Multi-location Coordination**: Skills loaded per-agent; no shared skill state across TERRACOTTA locations
4. **Procedural Complexity**: Multi-step procedures (MIDRA massage flow) harder to encode as pure markdown

---

## 5. SOLUTIONS & BEST PRACTICES

### Solution 1: Master Skill Pattern (RECOMMENDED)

Create a `terracotta-operations` master skill that:
- Lists all available sub-skills with slash commands
- Provides error handling when sub-skills unavailable
- Documents manual installation dependency in SKILL.md

```markdown
---
name: terracotta-operations
description: Master skill for TERRACOTTA business operations
---

# TERRACOTTA Operations Master Skill

## Prerequisites (MANUAL INSTALL REQUIRED)
Install these skills first:
- `terracotta-maintenance` (legionella-log, maintenance-daily)
- `terracotta-membership` (membership-onboard, membership-offboard)
- `terracotta-events` (event-scheduler, event-reminder)
- `terracotta-corporate` (corporate-proposal, corporate-report)

## Operations Index

| Operation | Command | Description |
|-----------|---------|-------------|
| Daily Maintenance | `/maintenance-daily` | Facility check routine |
| Legionella Log | `/legionella-log` | Water quality documentation |
| Member Onboarding | `/membership-onboard` | New member welcome |
| Event Create | `/event-scheduler` | Create community event |
| Corporate Proposal | `/corporate-proposal` | Generate B2B proposal |

## Error Handling
If a sub-skill command is not found, inform user:
"Please ensure the [skill-name] skill is installed. Run: openclaw skills install [skill-name]"
```

### Solution 2: Compliance Hook Verification

Use `before_prompt_build` hook to verify compliance-critical skills are loaded:

```typescript
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    const sessionId = event.context.sessionId;
    const message = event.context.userMessage;
    
    if (message.includes("legionella") || message.includes(" Legionella")) {
      // Verify legionella-log skill is in system prompt
      const skills = event.context.skillsSnapshot || [];
      if (!skills.includes("legionella-log")) {
        event.context.systemPrompt += `\n\n⚠️ WARNING: legionella-log skill not detected. Compliance may be affected.`;
      }
    }
  }
});
```

### Solution 3: Centralized Git Repository

Manage all TERRACOTTA skills in single Git repo:
```
terracotta-skills/
├── maintenance/
│   ├── SKILL.md
│   └── procedures/
├── membership/
│   ├── SKILL.md
│   └── templates/
├── events/
│   └── SKILL.md
├── corporate/
│   └── SKILL.md
└── README.md
```

Benefits:
- Version control for all procedures
- Easy deployment to multiple agents
- Change tracking for compliance
- Rollback capability

### Solution 4: Hook-Based Skill Activation

For dynamic compliance enforcement:

```typescript
// In terracotta-compliance hook
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    // After any maintenance operation, verify log was written
    if (event.context.userMessage.includes("maintenance-daily")) {
      event.context.systemPrompt += `\n\n[After maintenance, verify /legionella-log was executed if today is a test day.]`;
    }
  }
});
```

---

## 6. EDGE CASES

### Edge Case 1: Master Skill Installed Without Sub-Skills
**Scenario:** User installs `terracotta-operations` but forgets sub-skills
**Result:** `/terracotta-ops` lists operations that don't exist as commands
**Mitigation:** Include dependency check in master skill instructions

### Edge Case 2: Skill Update Breaks Slash Command
**Scenario:** `legionella-log` v2.0 changes command from `/legionella-log` to `/log-legionella`
**Result:** Master skill references old command; model reports "skill not found"
**Mitigation:** Pin skill versions; test updates before production

### Edge Case 3: Compliance Audit Missing Logs
**Scenario:** Maintenance performed but `/legionella-log` not executed
**Result:** Compliance gap — operation done but not documented
**Mitigation:** Use hook-based verification; cross-check logs after maintenance

### Edge Case 4: Member Data in Skill Instructions
**Scenario:** `membership-onboard` skill instructs model to access member API with credentials
**Risk:** Credentials in SKILL.md enter system prompt — CRITICAL security gap
**Mitigation:** Use `skills.entries.<skill>.env` for secrets; never put credentials in markdown

### Edge Case 5: Multi-Location Skill Sync
**Scenario:** TERRACOTTA has 3 locations, skills updated but only 2 locations refreshed
**Result:** Inconsistent procedures across locations
**Mitigation:** Use Git repo with `clawhub sync --all` deployment

---

## 7. CREATIVE USES

### Creative Use 1: Skill-Based SOP Compliance System
```
TERRACOTTA Compliance Engine
├── Skill: legionella-log (RD 865/2003)
├── Skill: maintenance-daily (equipment checks)
├── Skill: membership-audit (data retention compliance)
└── Hook: before_prompt_build (verify operations documented)
```

### Creative Use 2: Dynamic Procedure Generation
A meta-skill that generates new procedures:
```markdown
# TERRACOTTA Procedure Builder

When Dani describes a new standard operating procedure:
1. Create a new skill directory under skills/terracotta/
2. Write SKILL.md with the procedure steps
3. Register slash command
4. Add to operations index
5. Document in MEMORY.md
```

### Creative Use 3: Corporate Wellness B2B Skill Chain
```
Corporate Onboarding (master skill)
├── /corporate-proposal → generate proposal document
├── /membership-onboard-bulk → batch member creation
├── /corporate-report → set up monthly reporting schedule
└── /event-scheduler-corporate → book wellness days
```

### Creative Use 4: Real-Time Voice Guidance
Skills that provide step-by-step guidance via TTS:
```markdown
# Sauna Protocol Skill

When guiding user through sauna session:
1. Check membership tier via /membership-check
2. Provide temperature recommendation
3. Guide timing: "Enter sauna for 15 minutes"
4. Trigger cold plunge reminder at interval
5. Log session to member record
```

---

## NEW QUESTIONS FOR BACKLOG (TERRACOTTA Specific)

1. **[HIGH]** Can OpenClaw skill manifest format be extended to support `dependencies` field? (Would need PR to core)
2. **[MED]** What Telegram bot platform best integrates with TERRACOTTA membership skill (Manychat vs custom)?
3. **[MED]** Can skills use webhook out to notify external systems (Mindbody/Vagaro) after operations?
4. **[MED]** What is the best way to handle skill credentials for Mindbody/Vagaro API integration?
5. **[LOW]** Can skills implement file-based state that persists member operations across sessions?
6. **[MED]** How to sync TERRACOTTA skills across multiple agents (multi-location setup)?
7. **[HIGH]** Can compliance hooks verify that critical operations (Legionella log) were executed after maintenance skill?

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skill loading, precedence, gating rules
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — Skill config schema
- `/usr/local/lib/node_modules/openclaw/docs/tools/creating-skills.md` — Skill creation workflow
- `/usr/local/lib/node_modules/openclaw/docs/tools/slash-commands.md` — Slash command dispatch
- Research/OpenClaw/findings/skill-dependencies-chaining.md — Skill chaining limitations
- Research/OpenClaw/findings/openclaw-skill-system.md — Full skill system reference

---

*Research by: Investigador Scout | 2026-04-23 06:15 CET*
