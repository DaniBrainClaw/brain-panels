# Claude Code Pricing: Optimize Your Token Usage & Costs

Source: https://claudefa.st/blog/guide/development/usage-optimization

Master Claude Code pricing and token optimization to reduce costs by 70%. Learn proven strategies to maximize value from your API or subscription.

Problem: Claude Code costs adding up fast, hitting usage limits, or unsure which subscription tier fits your workflow. Strategic model selection and usage tracking can cut costs by 70%.

Quick Win: Install ccusage to see exactly where your tokens go.

Claude Code requires at least a Pro subscription ($20/month) since the free tier lacks terminal access.

Claude Pro ($20/month) - 5x usage limits vs free, Sonnet access, ~45 messages per 5-hour window. Best for learning and hobby projects.

Claude Max 5x ($100/month) - 5x Pro limits (~225 messages/5hr), generous Opus access. Best for professional developers.

Claude Max 20x ($200/month) - 20x Pro limits (~900 messages/5hr), full Opus access. Best for heavy daily usage and complex engineering.

API Pay-per-Use - Sonnet: $3/$15 per million input/output tokens. Opus: $15/$75 per million tokens. Best for predictable high-volume work.

Model Switching with /model: Switch models based on task complexity to control costs. Start every session with Sonnet. Only switch to Opus when you need deep analysis or complex refactoring.

Context Control Commands: Long conversations consume more tokens with every message. Use /compact when you notice Claude losing track, and /clear when switching to completely different work.

Planning Mode (Shift+Tab): Press Shift+Tab twice in the terminal to enter plan mode before expensive operations. Planning first prevents costly rework.

The biggest hidden cost is context bloat from loading instructions that aren't relevant to the current task.

Environment variables for token spending control available.

Reduce Non-Essential Token Usage: disables model calls used for non-critical features.

Prompt Caching Controls: Claude Code uses prompt caching by default to reduce costs and latency.

The opusplan Strategy: Claude uses Opus during plan mode for complex reasoning and architecture decisions, then automatically switches to Sonnet for code generation.

Track weekly and adjust based on data. Most developers reduce costs 40-70% with these strategies.