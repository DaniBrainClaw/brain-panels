# Agents - Intelligent Automation and Multi-Agent Orchestration for Claude Code

Source: https://github.com/wshobson/agents

A comprehensive production-ready system combining 185 specialized AI agents, 16 multi-agent workflow orchestrators, 153 agent skills, and 100 commands organized into 80 focused plugins for Claude Code.

## Architecture

- 80 Focused Plugins - Granular, single-purpose plugins optimized for minimal token usage
- 185 Specialized Agents - Domain experts across architecture, languages, infrastructure, quality, data/AI, business operations
- 153 Agent Skills - Modular knowledge packages with progressive disclosure
- 16 Workflow Orchestrators - Multi-agent coordination systems
- 100 Commands - Optimized utilities including project scaffolding, security scanning

## Example Plugins

- comprehensive-review: architect-review, code-reviewer, security-auditor
- javascript-typescript: javascript-pro, typescript-pro
- python-development: python-pro, django-pro, fastapi-pro
- security-scanning: SAST with security skill
- full-stack-orchestration: Multi-agent workflows

## Agent Teams

/pre install agent-teams@claude-code-workflows

Orchestrate multi-agent teams for parallel workflows:
- 7 Team Presets: review, debug, feature, fullstack, research, security, migration
- Parallel Code Review: /team-review src/ --reviewers security,performance,architecture
- Hypothesis-Driven Debugging: /team-debug "API returns 500" --hypotheses 3
- Parallel Feature Development: /team-feature "Add OAuth2 auth" --plan-first

## Three-Tier Model Strategy

| Tier | Model | Agents | Use Case |
|------|-------|--------|----------|
| Tier 1 | Opus 4.7 | 42 | Critical architecture, security, ALL code review |
| Tier 2 | Inherit | 42 | Complex tasks - user chooses model |
| Tier 3 | Sonnet | 51 | Support with intelligence |
| Tier 4 | Haiku | 18 | Fast operational tasks |

## Workflow Orchestration Example

/full-stack-orchestration:full-stack-feature "user authentication with OAuth2"

Coordinates 7+ agents: backend-architect → database-architect → frontend-developer → test-automator → security-auditor → deployment-engineer → observability-engineer

## Categories (25)

- Development (6): debugging, backend, frontend, multi-platform
- Documentation (4): code docs, API specs, diagrams
- Workflows (5): git, full-stack, TDD, Conductor, Agent Teams
- Testing (2): unit testing, QA orchestra
- Quality (3): comprehensive review, performance
- AI & ML (4): LLM apps, agent orchestration, context, MLOps
- Data (2): data engineering, data validation
- Database (2): database design, migrations
- Operations (4): incident response, diagnostics
- Infrastructure (5): cloud, Kubernetes