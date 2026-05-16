# OpenClaw Skill System — Research Findings

**Topic:** OpenClaw Skill System  
**Priority:** MED  
**Date:** 2026-04-23 04:25 CET  
**Research by:** Investigador Scout  
**Status:** ✅ COMPLETE

---

## 1. WHAT IS — Definition & Core Concept

### Definition

An **OpenClaw Skill** is a versioned bundle of files that teaches the agent how and when to use tools. Each skill is a directory containing a `SKILL.md` with YAML frontmatter and markdown instructions. Skills are the mechanism by which Dani and BRAIN define procedures that must be executed consistently, without variation, without forgetting steps, and without depending on memory.

### Key Principle (from skill-creator SKILL.md)

> Skills vs System Prompt: The system prompt can be ignored. The skill cannot. Skills guarantee consistency where memory fails and improvisation introduces variation.

### Skill Components

A skill directory contains:
- **`SKILL.md`** — Primary file with YAML frontmatter metadata + markdown body with instructions
- **Optional supporting files** — scripts, configs, or other files used by the skill
- **ClawHub metadata** — version, tags, install requirements for registry publishing

### Skill Format (SKILL.md)

```markdown
---
name: skill_name
description: "When to invoke this skill — one line"
metadata: { "openclaw": { ... } }
---

# Skill Name — What it does in one phrase

## CUÁNDO INVOCAR
[Exactly when to use this skill]

## QUÉ HACE
[What the skill does]

## PROCEDIMIENTO
1. Step 1
2. Step 2
3. Step 3

## FORMATO DE OUTPUT
[How output should look — if applicable]

## EJEMPLO
[Real example]

## REGLA DE ORO
[One critical negative rule]
```

### Key Metadata Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (snake_case) |
| `description` | Yes | One-line description shown to the agent |
| `metadata.openclaw.always` | No | If `true`, always include skill (skip other gates) |
| `metadata.openclaw.emoji` | No | Emoji for Skills UI |
| `metadata.openclaw.homepage` | No | URL for Skills UI |
| `metadata.openclaw.os` | No | OS filter (`["darwin"]`, `["linux"]`, etc.) |
| `metadata.openclaw.requires.bins` | No | Required binaries on PATH |
| `metadata.openclaw.requires.anyBins` | No | At least one binary must exist |
| `metadata.openclaw.requires.env` | No | Env var must exist or be in config |
| `metadata.openclaw.requires.config` | No | Required config keys |
| `metadata.openclaw.primaryEnv` | No | Env var for `skills.entries.<name>.apiKey` |
| `metadata.openclaw.install` | No | Installer specs for Skills UI |
| `metadata.openclaw.user-invocable` | No | If `false`, excluded from slash commands |
| `metadata.openclaw.disable-model-invocation` | No | Exclude from model prompt |
| `metadata.openclaw.command-dispatch` | No | If `tool`, bypass model and dispatch directly |
| `metadata.openclaw.command-tool` | No | Tool name for `command-dispatch: tool` |
| `metadata.openclaw.skillKey` | No | Override key under `skills.entries` |

---

## 2. HOW IT WORKS — Loading, Precedence & Execution

### 6 Load Locations (Precedence Order)

Highest to lowest:

| # | Location | Path | Scope |
|---|---------|------|-------|
| 1 | **Workspace skills** | `<workspace>/skills/` | Per-agent |
| 2 | **Project agent skills** | `<workspace>/.agents/skills/` | Per-workspace agent |
| 3 | **Personal agent skills** | `~/.agents/skills/` | Shared agent profile |
| 4 | **Managed/local skills** | `~/.openclaw/skills/` | All agents on machine |
| 5 | **Bundled skills** | Shipped with OpenClaw | Global |
| 6 | **ExtraDirs** | `skills.load.extraDirs` configured | Custom shared folders |

**Rule:** If same skill name exists in multiple locations, highest precedence wins (workspace overrides project overrides personal overrides managed overrides bundled overrides extraDirs).

### Skills Snapshot Mechanism

- Skills are snapshotted **per-session at load time** and reused for subsequent turns
- Changes to skills or config take effect on **next new session**
- Skills watcher (`skills.load.watch: true`) can refresh mid-session when `SKILL.md` files change
- Refreshed list is picked up on **next agent turn**
- If effective agent skill allowlist changes mid-session, snapshot refreshes to stay aligned

### Environment Injection Per Agent Run

When an agent run starts, OpenClaw:
1. Reads skill metadata
2. Applies `skills.entries.<key>.env` or `skills.entries.<key>.apiKey` to `process.env`
3. Builds system prompt with **eligible** skills
4. Restores original environment after run ends

**Scoped to agent run**, not global shell environment.

### Skills Watcher

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

Default: `watch: true`, debounce: 250ms. Triggers skills snapshot refresh when `SKILL.md` files change.

### Skills for System vs User

- **System skills** (bundled with OpenClaw): `/data/.openclaw/skills/`
- **User workspace skills**: `workspace/skills/` or `<workspace>/skills/`

### Agent Skill Allowlists

Per-agent skill visibility control:

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],  // baseline
    },
    list: [
      { id: "writer" },  // inherits defaults → github, weather
      { id: "docs", skills: ["docs-search"] },  // replaces defaults
      { id: "locked-down", skills: [] },  // no skills at all
    ],
  },
}
```

Rules:
- `agents.defaults.skills` omitted → unrestricted skills by default
- `agents.list[].skills` omitted → inherits from `agents.defaults.skills`
- `agents.list[].skills: []` → **no skills** for that agent
- Non-empty `agents.list[].skills` list is **final set** (does not merge with defaults)

### Per-Skill Configuration

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" },
        env: {
          GEMINI_API_KEY: "VALUE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

Rules:
- `enabled: false` disables even if bundled/installed
- `env` injected **only if** variable not already in `process.env`
- `apiKey` convenience for `primaryEnv` declared skills
- `config` optional bag for custom fields
- Keys match **skill name** by default; use `metadata.openclaw.skillKey` override

### Token Impact (Skills List in System Prompt)

`formatSkillsForPrompt` in pi-coding-agent produces compact XML list:

```
Base overhead (only when ≥1 skill): 195 chars
Per skill: 97 chars + XML-escaped name/description/location
```

XML escaping (`& < > " '` → entities) increases lengths.

Rough estimate: ~4 chars/token → **~24 tokens per skill** overhead plus actual field lengths.

### ClawHub Integration

**Site:** [clawhub.ai](https://clawhub.ai)

Skills can be published to ClawHub for discovery, versioning, and installation:

```bash
# Search
clawhub search "postgres backups"

# Install into workspace
clawhub install my-skill

# Update installed
clawhub update --all

# Publish
clawhub skill publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0

# Sync all local skills
clawhub sync --all
```

Native OpenClaw commands also work:
```bash
openclaw skills search "calendar"
openclaw skills install <skill-slug>
openclaw skills update --all
```

`openclaw skills install` installs into `<workspace>/skills/`. ClawHub CLI installs into `./skills` under current working directory.

**ClawHub Security:**
- GitHub account must be ≥1 week old to publish
- Skills with >3 unique reports auto-hidden
- Moderators can hide/unhide/delete/ban users

---

## 3. USES — What Skills Are Used For

### Primary Use Cases

| Use Case | Example | Skill Name |
|---------|---------|-----------|
| **Procedures that must be consistent** | Log errors, compliance checks | `log-error`, `compliance-check` |
| **Complex tool workflows** | Image generation, browser automation | `image-lab`, `browser` |
| **API integrations** | GitHub, weather, web search | `github`, `weather` |
| **Coding assistance** | Claude CLI, code review | `claude-cli` |
| **File processing** | Summarize, PDF analysis | `summarize` |
| **Custom procedures** | Nightly routines, report generation | `buenas-noches` |

### Skill Categories

1. **Bundled skills** — Ship with OpenClaw (github, weather, etc.)
2. **Managed/local skills** — User-installed in `~/.openclaw/skills/`
3. **Workspace skills** — Per-agent in `<workspace>/skills/`
4. **Plugin skills** — Shipped inside plugins (lowest precedence)
5. **ExtraDirs skills** — Shared across agents via config

### Real-World Skill Examples

#### Skill: weather
```markdown
---
name: weather
description: Get current weather and forecasts via wttr.in or Open-Meteo.
---

# Weather — Current weather and forecasts

## CUÁNDO INVOCAR
When user asks about weather, temperature, or forecasts for any location.

## QUÉ HACE
Fetches current weather and forecasts via wttr.in or Open-Meteo.

## PROCEDIMIENTO
1. Use wttr.in for basic weather (no API key needed)
2. Fall back to Open-Meteo if wttr.in fails
3. Return temperature, conditions, forecast summary
```

#### Skill: skill-creator
```markdown
---
name: skill-creator
description: "OBLIGATORIO — Cuando Dani y BRAIN definen algo que debe hacerse siempre de la misma manera, BRAIN DEBE crear una skill con ese procedimiento."
---

# Skill Creator — Metodología para crear skills

## CUÁNDO INVOCAR
When Dani says "esto debe hacerse siempre así" or defines a new procedure.

## PROCEDIMIENTO
1. Define procedure with Dani (exact steps, format, outputs)
2. Name skill (verb + object, e.g., log-error, compliance-check)
3. Write SKILL.md with required structure
4. Place in correct location (/data/.openclaw/skills/ or workspace/skills/)
5. Verify with Dani
```

### Plugin Skills

Plugins can ship skills via `openclaw.plugin.json`:

```json
{
  "skills": ["skills-dir-relative-to-plugin-root"]
}
```

Plugin skills merge into same low-precedence path as `skills.load.extraDirs`. Bundled/managed/agent/workspace skills with same name override plugin skills.

---

## 4. PROBLEMS — Issues & Limitations

### Critical Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| **Skills run in-process** | CRITICAL | Like hooks/plugins, skills execute with full Gateway privileges. Untrusted skill code = same risk as malicious plugin. |
| **No sandbox isolation for skill processes** | CRITICAL | `skills.entries.<skill>.env` applies to **host** process, not sandbox. Sandbox does NOT inherit host `process.env`. |
| **skills.entries.env bypasses sandbox** | HIGH | Env injection for skills goes to host process env. For sandboxed sessions, must use `agents.defaults.sandbox.docker.env` or bake into custom image. |
| **Token overhead** | MEDIUM | Skills list adds ~195 base + ~97/skill chars to system prompt. Large skill lists = significant context cost. |
| **No hot reload without watcher** | MEDIUM | Without `skills.load.watch: true`, skill changes require new session or gateway restart. |
| **skills snapshot is load-time** | MEDIUM | Even with watcher, snapshot refreshes on next turn — not immediate. Real-time updates not possible. |
| **Workspace skills win precedence** | MEDIUM | Workspace skills override all lower-precedence copies. Can shadow critical bundled skills silently. |
| **No version pinning from ClawHub** | MEDIUM | `clawhub install` gets latest unless `--version` specified. Can lead to unexpected behavior after updates. |

### Confirmed Bugs/Limitations from Docs

| Issue | Status | Description |
|-------|--------|-------------|
| Skills watcher default | ⚠️ | `watch: true` is default, but depends on `skills.load.watch` config |
| Snapshot isolation | ⚠️ | Skills snapshot is per-session — cross-session skill state requires file-based mechanism |
| Bundle skills lowest precedence | ⚠️ | Plugin-shipped skills are lowest precedence — overridden by everything |
| `skills.install.nodeManager` | ⚠️ | Affects skill installs only, not Gateway runtime (still Node, bun not recommended for WhatsApp/Telegram) |

### Security Considerations

| Concern | Risk | Mitigation |
|---------|------|------------|
| Third-party skills as untrusted code | CRITICAL | Treat third-party skills as untrusted. Review code before enabling. Prefer sandboxed runs. |
| `skills.entries.*.apiKey` exposes secrets | HIGH | `apiKey` and `env` injection goes to **host process** for that agent turn, not sandbox. Keep secrets out of prompts/logs. |
| `skills.install` gateway-backed installs | HIGH | Runs built-in dangerous-code scanner before executing installer metadata. `critical` findings block by default unless caller sets dangerous override. |
| Workspace skill shadowing | MEDIUM | Workspace skills can shadow bundled skills with same name. Can be used for local patches/testing but also silent override risk. |
| `skills.allowBundled` only affects bundled | LOW | Does not restrict managed/workspace/extraDirs skills — only bundled allowlist. |

### Known Gaps

| Gap | Description |
|-----|-------------|
| **No native skill versioning** | Skills don't have automatic version tracking. ClawHub provides versioning for published skills only. |
| **No built-in skill dependency system** | Skills declare `requires.bins` but no formal dependency declaration. |
| **Skills watcher single debounce** | `watchDebounceMs: 250` applies to all skill folders — no per-skill debounce. |
| **No skill execution timeout** | Skills are instructions to model — no runtime execution timeout like tools. |
| **Skills vs hooks interaction unclear** | Hooks run AFTER skills are injected. No direct hook-to-skill activation API. |

---

## 5. SOLUTIONS — Best Practices & Workarounds

### For Secrets in Skills

**DO:**
```json5
// Use SecretRef for API keys
skills: {
  entries: {
    "image-lab": {
      apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }
    }
  }
}
```

**DON'T:**
```markdown
<!-- Never put plaintext API keys in SKILL.md -->
# BAD SKILL
Your API key is: sk-1234567890abcdef
```

### For Sandbox Environment

```json5
agents: {
  defaults: {
    sandbox: {
      docker: {
        env: {
          GEMINI_API_KEY: "from-config"
        }
      }
    }
  }
}
```

OR bake env into custom sandbox image.

### For Token Optimization

1. **Use per-agent skill allowlists** — Don't load all skills for all agents
2. **Disable unneeded skills:**
```json5
skills: {
  entries: {
    "large-schema-skill": { enabled: false }
  }
}
```
3. **Use `contextInjection: "continuation-skip"`** — Skip bootstrap re-injection on safe continuation turns
4. **Consider smaller models for simple tasks** — Less context window pressure

### For Skill Development Workflow

```bash
# 1. Create skill in workspace
mkdir -p ~/.openclaw/workspace/skills/my-skill

# 2. Write SKILL.md
cat > ~/.openclaw/workspace/skills/my-skill/SKILL.md << 'EOF'
---
name: my_skill
description: "When to use this skill"
---

# My Skill
...
EOF

# 3. Test with new session
openclaw agent --message "test my skill"

# 4. Publish to ClawHub when ready
clawhub skill publish ./my-skill --slug my-skill --version 1.0.0
```

### For Skills Watcher Performance

```json5
skills: {
  load: {
    watch: true,
    watchDebounceMs: 500,  // Increase if many skills
  }
}
```

### For Multi-Agent Skill Sharing

Put shared skills in `~/.openclaw/skills/` (managed) for all agents on machine. Or use `skills.load.extraDirs` for explicit shared folders.

### For Plugin Skill Override

Since plugin skills are lowest precedence, to override a plugin skill:
1. Create same-named skill in `<workspace>/skills/`
2. Or in `~/.openclaw/skills/`
3. Or in `~/.agents/skills/`

---

## 6. EDGE CASES — Corner Cases & Unexpected Behaviors

### Edge Case: Skill Name Conflicts

When same skill name in multiple locations:
- Workspace skills (`<workspace>/skills/`) **always win** over project, personal, managed, bundled, extraDirs
- This is intentional for local patches but can cause silent shadowing of critical skills

### Edge Case: Sandbox + Skill Env Injection

When session is **sandboxed**, skill processes run **inside Docker**. The sandbox does **NOT** inherit host `process.env`.

Options:
1. `agents.defaults.sandbox.docker.env` (or per-agent `agents.list[].sandbox.docker.env`)
2. Bake env into custom sandbox image
3. Use workspace-mounted secrets

### Edge Case: Skill Binary Requirements

`requires.bins` checked on **host** at skill load time. If agent is **sandboxed**, binary must also exist **inside container**.

Install via:
```json5
agents: {
  defaults: {
    sandbox: {
      docker: {
        setupCommand: "apt-get install -y some-binary"
      }
    }
  }
}
```

Requires: network egress, writable root FS, root user in sandbox.

### Edge Case: Installer Preference

When multiple installers listed, OpenClaw picks **single preferred option**:
1. Homebrew if available + `skills.install.preferBrew: true`
2. `uv`
3. Configured node manager (npm/pnpm/yarn/bun)
4. Go or download

### Edge Case: Empty skills.allowBundled

```json5
skills: {
  allowBundled: []  // Empty array = NO bundled skills eligible
}
```

Only affects **bundled** skills. Managed/workspace/extraDirs skills unaffected.

### Edge Case: Skill with `disable-model-invocation: true`

Skill still available via user invocation (slash command) but **excluded from model system prompt**. Model cannot invoke autonomously — only user can trigger.

### Edge Case: Skill with `command-dispatch: tool`

Slash command **bypasses the model** and dispatches directly to a tool. Tool invoked with:
```typescript
{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }
```

### Edge Case: ClawHub Sync with No Skills Found

`clawhub sync` scans workdir first. If no skills found, falls back to legacy locations (`~/openclaw/skills`, `~/.openclaw/skills`).

### Edge Case: Skill Load with Missing Binary

If `requires.bins` binary not found → skill excluded from eligible set (not an error). Agent doesn't see the skill.

### Edge Case: skills.entries vs skill name with hyphens

```json5
skills: {
  entries: {
    // Must quote key — JSON5 allows it
    "my-skill-name": { enabled: true }
  }
}
```

### Edge Case: Installer Multiple Options

If all installers are `download`, OpenClaw surfaces **all download options** instead of collapsing to one preferred option.

---

## 7. CREATIVE USES — Novel Applications

### Creative Use 1: Procedure Enforcement Layer

Use skills to enforce procedures that system prompt alone cannot guarantee:
- `compliance-check` skill: Before sending ANY response, check against compliance rules
- `log-error` skill: When BRAIN makes a mistake, immediately log structured error
- `skill-creator` skill: When Dani defines a procedure, immediately create the skill

### Creative Use 2: Contextual Skill Activation

Combine `before_prompt_build` hook + skill pattern for dynamic enforcement:

```typescript
// Hook injects enforcement context
api.registerHook({
  events: ["before_prompt_build"],
  handler: async (event) => {
    event.context.systemPrompt += `\n\n# Active Context:\nUse: compliance-check skill`;
  }
});
```

### Creative Use 3: Multi-Agent Procedure Library

Create `~/.openclaw/skills/` as shared procedure library across all agents:
- Standard log-error format
- Compliance check procedure
- Research methodology
- Curation process

Each agent inherits consistent procedures without copy-paste.

### Creative Use 4: Skill-Based Memory

Use skills as structured memory with enforced formats:
- `memory-update` skill: Structured way to update MEMORY.md
- `memory-search` skill: Standard query format for memory_search
- `daily-note` skill: Format for memory/YYYY-MM-DD.md entries

### Creative Use 5: Temporary Skill Injection

For one-off complex tasks, create temporary workspace skill:
1. Generate skill via subagent
2. Write to `<workspace>/skills/temp-task-skill/`
3. Next turn triggers skill watcher → skill becomes eligible
4. Task runs using skill
5. Delete skill after completion

### Creative Use 6: Skill Version Pinning

For production stability, pin skill versions:
```bash
# Install specific version
clawhub install my-skill --version 1.2.3

# Or lock via lockfile
# .clawhub/lock.json tracks installed versions
```

Then `clawhub update --all` only updates within compatible range.

### Creative Use 7: Cross-Platform Skill Bundles

Use `skills.load.extraDirs` for organization-wide skill bundles:
```json5
{
  skills: {
    load: {
      extraDirs: [
        "~/company/skills/security/",
        "~/company/skills/compliance/",
        "~/company/skills/productivity/"
      ]
    }
  }
}
```

Different directories for different skill categories.

---

## NEW QUESTIONS OPENED BY THIS RESEARCH

### a) Definition & Scope
- [ ] Can skills declare dependencies on other skills (skill chaining)? **[MED]**
- [ ] What is the maximum recommended number of skills per agent before context overhead becomes problematic? **[MED]**
- [ ] Can skills be dynamically enabled/disabled mid-session without gateway restart? **[MED]**

### b) Internal Mechanics
- [ ] How does the skills watcher handle nested directory changes (subdirectories)? **[LOW]**
- [ ] What triggers skills snapshot refresh — only SKILL.md changes or any file in skill directory? **[LOW]**
- [ ] Can two skills with same name be loaded from different locations simultaneously (one for model, one for user invocation)? **[LOW]**

### c) Use Cases
- [ ] Can skills implement persistent state across sessions (file-based)? **[MED]**
- [ ] Can skills call other skills recursively? **[MED]**
- [ ] What is recommended pattern for skill that generates other skills? **[MED]**

### d) Best Practices
- [ ] What happens if a skill's `requires.bins` binary exists on host but not in sandbox — does skill load or fail silently? **[MED]**
- [ ] Can skills use `skills.entries.<skill>.env` for secrets that are also in `process.env` (override vs preserve)? **[MED]**
- [ ] Should skills that need API keys prefer `apiKey` or `env` injection? **[LOW]**

### e) Problems & Limitations
- [ ] Is there a known issue with skills watcher consuming excessive CPU on large skill directories? **[MED]**
- [ ] Does skills snapshot refresh trigger compaction or memory flush? **[MED]**
- [ ] Can malicious skill bypass dangerous-code scanner for skill installs? **[HIGH]**

### f) Solutions & Workarounds
- [ ] Can skills implement their own sandboxing via skill-level Docker execution? **[MED]**
- [ ] What's best way to debug skill loading issues? **[MED]**
- [ ] Can skills be loaded from remote URLs (not local files)? **[MED]**

### g) Edge Cases
- [ ] What happens when skill name conflicts with built-in tool name? **[MED]**
- [ ] Can skills declare `metadata.openclaw.requires.config` for config paths that don't exist? **[LOW]**
- [ ] What happens to in-flight agent runs when skills snapshot refreshes mid-session? **[MED]**

### h) Creative Uses
- [ ] Could skills implement a real-time collaboration protocol (shared skills across users)? **[LOW]**
- [ ] Can skills be used as a plugin system (skills that register new tools/hooks)? **[MED]**
- [ ] Could TERRACOTTA business procedures be encoded as skills for consistent execution? **[HIGH — business relevance]**

---

## Sources

- `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` — Skills loading, precedence, gating rules
- `/usr/local/lib/node_modules/openclaw/docs/tools/creating-skills.md` — Skill creation workflow, SKILL.md format
- `/usr/local/lib/node_modules/openclaw/docs/tools/skills-config.md` — Skills config schema reference
- `/usr/local/lib/node_modules/openclaw/docs/tools/clawhub.md` — ClawHub registry, CLI commands, publish/sync workflows
- `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md` — Plugin capability model (skills shipped via plugins)
- `/data/.openclaw/skills/skill-creator/SKILL.md` — Internal skill creation methodology (skill about creating skills)

---

*Research by: Investigador Scout | 2026-04-23 04:25 CET*
