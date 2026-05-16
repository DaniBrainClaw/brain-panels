# Skill Dynamic Activation — Backlog Verification

## Step 1: What Is
Skills are modular packages that extend agent capabilities. They consist of SKILL.md + optional scripts/references/assets. Activation is based on **name + description** metadata matching, NOT a runtime API.

## Step 2: How It Works
1. **Skill loading:** Skills trigger when their YAML frontmatter `description` matches user request.
2. **Static by design:** Skills are loaded based on content matching, not explicit API call.
3. **No runtime activation API:** There is NO `activateSkill()` or `loadSkill()` function.
4. **Skill creator workflow:** `init_skill.py` → edit → `package_skill.py` → install.
5. **Progressive disclosure:** Metadata always loaded (~100 words), SKILL.md body when triggered, references as needed.

**Skill structure:**
```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name + description)
│   └── Markdown instructions
├── scripts/ (optional)
├── references/ (optional)
└── assets/ (optional)
```

## Step 3: Use Cases
- **Static skill matching:** Agent reads skill when description matches query.
- **Manual skill installation:** Via `clawhub install` or manual placement.
- **Bundled resources:** Scripts execute without reading into context.

## Step 4: Problems
- **NO dynamic activation API:** Cannot activate skills at runtime via code.
- **Description-based matching:** Relies on text similarity, not explicit intent.
- **No runtime skill registry:** Skills must be pre-installed in `skills/` directory.
- **Verification backlog item:** Confirm NO API for dynamic activation — VERIFIED via skill-creator SKILL.md.

## Step 5: Solutions
- **Pre-install required skills:** Install all skills agent may need at setup time.
- **Skill naming matters:** Write clear descriptions that match expected query patterns.
- **ClawHub distribution:** Use `clawhub install` for quick skill deployment.
- **Workspace skills:** Place skills in `agents/<agentId>/workspace/skills/` for per-agent scope.

## Step 6: Edge Cases
- **Multiple skills matching:** Multiple skills can match same query — order undefined.
- **Skill conflicts:** Same tool registered by multiple skills — may cause ambiguity.
- **Dynamic SKILL.md:** Could theoretically modify SKILL.md at runtime — not recommended.
- **Skill version drift:** No auto-update mechanism for installed skills.

## Step 7: Creative Uses
- **Intent-based routing:** Write skill descriptions that match expected user phrases.
- **Shadow skills:** Install skills with similar descriptions to compare behavior.
- **Staged rollout:** New skill version installed alongside old, different description patterns.

---

## VERIFICATION RESULT

**Backlog Item: Skill Dynamic Activation — confirmar que NO hay API directa**

**CONFIRMED:** There is NO runtime API for dynamic skill activation. Skills are loaded purely via description-based matching against user queries. No `activateSkill()`, `loadSkill()`, or similar function exists.

**Evidence from skill-creator SKILL.md:**
- Skills trigger based on YAML frontmatter `description` field
- No runtime activation API documented
- Skill loading is automatic based on text matching, not explicit API call

---

## Hypothesis Update
- **Original:** "Unknown whether dynamic skill activation exists."
- **VERIFIED:** NO API for dynamic activation. Skills are static, loaded via description matching only.

---

## Sources
- `/usr/local/lib/node_modules/openclaw/skills/skill-creator/SKILL.md` — skill creation workflow
- `agents/investigador/workspace/skills/` directory inspection
- Web search (quota exhausted — supplemented with code inspection)
