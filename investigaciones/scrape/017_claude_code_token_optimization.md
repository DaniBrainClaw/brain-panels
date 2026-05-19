# Claude Code Token Optimization: Full System Guide (2026)

Source: https://buildtolaunch.substack.com/p/claude-code-token-optimization

Two months ago, my Claude Code bill hit $1,600. I thought I was being cautious. But when that invoice arrived, it made sense.

Every file I asked Claude to read added its entire contents to the context window permanently. Every MCP tool response got the full JSON, not a summary. Every log Claude scanned. All of it stacking, invisibly.

## Why Claude Code Gets Expensive: The 3 Token Drains

1. Tool outputs accumulate - Every time Claude reads a file, runs a shell command, or calls an MCP server, the full output gets appended to context. A 10,000-line log file stays in context for every subsequent message.

2. Conversation history compounds - Claude re-reads the entire conversation from the top on every message. Message 50 costs more than message 5 not because you asked something harder, but because Claude is re-reading 49 prior messages first.

3. CLAUDE.md baseline - Your CLAUDE.md loads before Claude reads your code. A 5,000-token CLAUDE.md costs 5,000 tokens before you've typed a word. Every turn. Every session.

## One-Time Setup to Reduce Token Baseline

- .claudeignore: Control what Claude can read. node_modules/, .next/, dist/, build/, *.log, coverage/, .env*
- MCP servers: If you haven't used a server in a week, disconnect it
- CLAUDE.md: Should be under 500 tokens with project shape, not full documentation

## Session Habits That Cut Token Usage

- /clear: Wipes entire conversation for when switching tasks completely
- /compact: Summarizes conversation for when you still need the thread
- Be specific about which files to read
- Use shell scripts instead of asking Claude to read files you're going to read yourself
- Use CLI tools instead of MCP when available

## Claude Code's Three Main Models

Opus for architecture decisions, complex debugging. Sonnet for daily work. Haiku for simple tasks.