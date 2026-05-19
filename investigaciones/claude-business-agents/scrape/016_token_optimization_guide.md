# Stop Burning Tokens: A Developer's Guide to Claude AI Token Optimization

Source: https://levelup.gitconnected.com/stop-burning-tokens-a-developers-guide-to-claude-ai-token-optimization-4c70c7c52ffb

You're probably paying 5x more than you need to. Here's how the token system actually works.

## The Hidden Mechanic: Claude Re-Sends Your Entire Conversation Every Single Message

Claude is stateless. It has no memory between API calls. Every time you hit send, the entire conversation history gets re-transmitted to the model.

Message 1: You send 500 tokens. Claude processes 500 tokens.
Message 5: Your prompt is 200 tokens, but Claude is now processing ~3,000 tokens.
Message 15: Your prompt is 100 tokens, but Claude is processing ~15,000-25,000 tokens.
Message 30: A simple "fix the bug on line 42" might cost 50,000+ tokens.

## Rule #1: Start New Chats Every 15-20 Messages

The single highest-impact optimization. Starting a new conversation resets the accumulated context to zero.

## Rule #2: Choose the Right Model for the Right Task

Claude Haiku 4.5: $1 input / $5 output per million tokens. Best for classification, extraction, quick fixes, boilerplate.

Claude Sonnet 4.6: $3 input / $15 output per million tokens. Best for most coding tasks, multi-file logic.

Claude Opus 4.6: $15 input / $75 output per million tokens. Best for complex architecture, deep debugging.

The 3-Tier Strategy saves 40-70% on token costs: Haiku for simple tasks, Sonnet for daily work, Opus for deep reasoning.

## Rule #3: Give the Right Context, Not All the Context

Use XML tags to structure your context. Claude responds exceptionally well to structured context.

## Rule #4: Disable Tools and Connectors You're Not Using

Every MCP connector loads its full tool definition into your context window on every single message.

## Rule #5: Optimize for Complete Project Generation

Use phased approach: Architecture (Opus), Core implementation (Sonnet), Module work (Sonnet, new chat), Integration and review (Opus).

## Rule #6: Use Prompt Caching (API Users)

Prompt caching reduces costs by up to 90% on repeated context. Cache read tokens cost only 0.1x.

## Rule #7: Use Batch API for Non-Urgent Work

50% discount on all models for non-urgent processing.