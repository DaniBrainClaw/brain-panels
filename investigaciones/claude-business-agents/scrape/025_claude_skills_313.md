# Claude Skills - 313+ Skills for Claude Code

Source: https://github.com/alirezarezvani/claude-skills

313 production-ready Claude Code skills, plugins, and agent skills for 12 AI coding tools. Also works with OpenAI Codex, Gemini CLI, Cursor, and 7 more coding agents.

## Skills Overview

Skills cover engineering, DevOps, marketing (incl. AEO - Answer Engine Optimization), security, compliance, C-level advisory, productivity, and research.

Each skill includes:
- SKILL.md — structured instructions, workflows, decision frameworks
- Python tools — ~402 CLI scripts (stdlib-only, zero pip installs)
- Reference docs — templates, checklists, domain knowledge

## Installation

```bash
# Clone
git clone https://github.com/alirezarezvani/claude-skills.git

# Add marketplace
/plugin marketplace add alirezarezvani/claude-skills

# Install by domain
/plugin install engineering-skills@claude-code-skills
/plugin install marketing-skills@claude-code-skills
/plugin install c-level-skills@claude-code-skills
```

## Skills by Domain

| Domain | Skills | Highlights |
|-------|--------|------------|
| Engineering — Core | 32 | Architecture, frontend, backend, fullstack, QA, DevOps, SecOps, AI/ML |
| Engineering — POWERFUL | 45 | Agent designer, RAG architect, database designer, security auditor, MCP builder |
| Product | 13 | Product manager, agile PO, strategist, UX researcher |
| Marketing | 45 | 8 pods: Content, SEO+AEO, CRO, Channels, Growth, Intelligence, Sales |
| Productivity | 4 | capture, email pair, reflect |
| Research | 8 | research orchestrator, pulse, litreview, grants, dossier, patent, syllabus |
| Project Management | 9 | Senior PM, scrum master, Jira, Confluence |
| Regulatory & QM | 14 | ISO 13485, MDR, FDA, ISO 27001, GDPR, SOC 2 |
| C-Level Advisory | 28 | Full C-suite (10 roles) + board meetings + culture |
| Business & Growth | 5 | Customer success, sales engineer, revenue ops |
| Finance | 3 | Financial analyst, SaaS metrics, investment advisor |

## Personas

Pre-configured agent identities with curated skill loadouts and distinct communication styles:

- Startup CTO: Engineering + Strategy for architecture decisions
- Growth Marketer: Marketing + Growth for content-led growth
- Solo Founder: Cross-domain for one-person startups

## Orchestration Patterns

- Solo Sprint: Switch personas across project phases
- Domain Deep-Dive: One persona + multiple stacked skills
- Multi-Agent Handoff: Personas review each other's output
- Skill Chain: Sequential skills for repeatable checklists