# Manage Costs Effectively - Claude Code Docs

Source: https://code.claude.com/docs/en/costs

Claude Code charges by API token consumption. For subscription plan pricing (Pro, Max, Team, Enterprise), see claude.com/pricing. Per-developer costs vary widely based on model selection, codebase size, and usage patterns.

Across enterprise deployments, the average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users.

## Track Your Costs

Using the `/usage` command: provides detailed token usage statistics for your current session.

## Managing Costs for Teams

When using Claude API, you can set workspace spend limits on the total Claude Code workspace spend. Admins can view cost and usage reporting in the Console.

Rate limit recommendations per team size:
- 1-5 users: 200k-300k TPM per user, 5-7 RPM
- 5-20 users: 100k-150k TPM, 2.5-3.5 RPM
- 20-50 users: 50k-75k TPM, 1.25-1.75 RPM
- 50-100 users: 25k-35k TPM, 0.62-0.87 RPM
- 100-500 users: 15k-20k TPM, 0.37-0.47 RPM
- 500+ users: 10k-15k TPM, 0.25-0.35 RPM

## Agent Team Token Costs

Agent teams spawn multiple Claude Code instances, each with its own context window. Token usage scales with the number of active teammates.

To keep agent team costs manageable:
- Use Sonnet for teammates
- Keep teams small
- Keep spawn prompts focused
- Clean up teams when work is done

## Reduce Token Usage

Token costs scale with context size: the more context Claude processes, the more tokens you use. Claude Code automatically optimizes costs through prompt caching and auto-compaction.

Strategies to reduce token usage:
- Manage context proactively with /usage and /clear
- Choose the right model (Sonnet for most tasks, Opus for complex)
- Reduce MCP server overhead
- Install code intelligence plugins for typed languages
- Offload processing to hooks and skills
- Move instructions from CLAUDE.md to skills
- Adjust extended thinking
- Delegate verbose operations to subagents
- Write specific prompts
- Work efficiently on complex tasks using plan mode