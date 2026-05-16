# OpenClaw Research — Source Registry

## Official Sources

| Source | URL/Path | Status | Last Verified | Confidence |
|--------|----------|--------|--------------|------------|
| OpenClaw Docs | `/usr/local/lib/node_modules/openclaw/docs/` | ✅ Available | 2026-04-23 | HIGH |
| Hooks Architecture | `docs/automation/hooks.md` | ✅ Reviewed | 2026-04-23 | HIGH |
| Plugin Architecture | `docs/plugins/architecture.md` | ✅ Reviewed | 2026-04-23 | HIGH |
| OpenClaw GitHub | (not accessed yet) | ❌ Pending | — | — |
| Changelogs | (not accessed yet) | ❌ Pending | — | — |

## Repository / Code Sources

| Source | Path | Status | Notes |
|--------|------|--------|-------|
| OpenClaw Core | `/usr/local/lib/node_modules/openclaw/dist/` | ✅ Reviewed | Hook runner, agent core |
| Pi Agent | `node_modules/@mariozechner/pi-coding-agent/` | ✅ Reviewed | Model registry, extensions |
| Internal Hooks | `dist/internal-hooks-*.js` | ✅ Reviewed | Session-memory, boot-md |
| Hook Runner | `dist/hook-runner-global-*.js` | ✅ Reviewed | Global hook execution |

## Issues / Discussions

| Source | Topic | Status | Notes |
|--------|-------|--------|-------|
| GitHub Issues (PR #69549) | exec security strip | ✅ Known | DRAFT - silent cron failures |
| GitHub Issues (#69404) | Sessions OOM fix | ✅ Resolved | Fixed in v2026.4.20 |
| GitHub Issues (#69538) | OpenRouter bug | ✅ Resolved | Fixed in v2026.4.12 |

## Community Sources

| Source | Topic | Status | Notes |
|--------|-------|--------|-------|
| OpenClaw Discord | General | ❌ Not accessed | Community support |
| clawhub.com | Skills/Plugins | ✅ Available | Third-party extensions |

## Secondary Sources

| Source | Use | Status |
|--------|-----|--------|
| Web search (Tavily/Exa) | Discovery only | Optional |
| Forums | Last resort | Not recommended |

---

## Source Quality Rules

1. **Official > Code > Issues > Community > Secondary**
2. Community sources: use for discovery, NOT as primary evidence
3. Each critical claim needs official OR 2 independent non-official sources
4. Mark all sources with: verification date, confidence level

---

## Pending Source Access

- [ ] OpenClaw GitHub repository (full)
- [ ] Official changelogs (version history)
- [ ] Discord community (searchable threads)
- [ ] Third-party plugin registry

---

*Sources registry created: 2026-04-23*
