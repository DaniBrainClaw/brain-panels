# Channel System — Telegram Deep Research

## Step 1: What Is
OpenClaw's channel system connects the agent runtime to messaging platforms. Telegram is the primary channel configured, with support for multiple bot accounts, streaming modes, and sophisticated routing.

## Step 2: How It Works
1. **Channel plugin architecture:** Each platform (Telegram, Discord, etc.) has a plugin that translates messages to/from OpenClaw's unified format.
2. **Streaming modes:** `partial` (default), `block`, `progress`, or `full`.
3. **dmPolicy options:** `pairing` (default), `allowlist`, `open`, `disabled`.
4. **Group policies:** `allowlist` with `requireMention` for group chats.
5. **Multiple accounts:** Each bot token = separate account with own settings.

**Current Config Analysis:**
```json
"telegram": {
  "enabled": true,
  "dmPolicy": "pairing",
  "botToken": "8299166002:AAHiZY1Ye4ZuzgZ81QKzQwutz3zkf9z5ll4",
  "groups": { "*": { "requireMention": true } },
  "groupPolicy": "allowlist",
  "streaming": { "mode": "partial" },
  "accounts": {
    "default": { "dmPolicy": "pairing", "botToken": "...default..." },
    "organizacion": { "dmPolicy": "pairing", "botToken": "...organizacion..." }
  },
  "defaultAccount": "default"
}
```

## Step 3: Use Cases
- **Personal AI assistant:** Direct Telegram DMs with pairing code verification.
- **Multi-agent routing:** Different Telegram bots → different agents (via bindings).
- **Group chat automation:** Bot responds only when mentioned, white-list controlled.
- **Real-time briefing:** Streaming responses for immediate feedback.

## Step 4: Problems
- **Long polling lag:** Polls Telegram for updates → can introduce latency.
- **Webhooks require open ports:** Faster but requires public endpoint.
- **Multiple token management:** Each account needs separate bot token.
- **Pairing code expiry:** 6-digit codes expire after 1 hour.
- **NAT limitations:** Long polling works behind NAT; Webhooks don't.

## Step 5: Solutions
- **Use Webhooks when possible:** Faster than polling for production.
- **Pre-approve users:** Use `allowlist` dmPolicy after pairing.
- **Separate bots for separation:** Different token = clean isolation.
- **Monitor pairing codes:** Track code expiry to avoid locked-out users.

## Step 6: Edge Cases
- **Bot token exposure:** Bot tokens in config — if config leaked, attacker controls bot.
- **Group message floods:** `requireMention: true` prevents silent floods.
- **Streaming mode tradeoffs:** `partial` feels snappy but sends draft updates; `full` waits until complete.
- **Account switching:** `defaultAccount` determines which bot receives unaddressed DMs.

## Step 7: Creative Uses
- **Multi-tenant channels:** Separate bot tokens for separate user groups.
- **Hybrid routing:** DM to one agent, group mentions to another.
- **Shadow testing:** Route copy of messages to monitoring agent.
- **Cross-channel bridging:** Telegram ↔ Discord via agent routing.

---

## Current Gap in Coverage

**Channel system marked PARTIAL** — only Telegram is configured. No Discord, WhatsApp, Signal, etc.

**Agents with Heartbeat:**
| Agent | Heartbeat |
|-------|-----------|
| maintenance | yes (60m) |
| director-organizacion | yes (60m) |
| jobber | yes (60m) |
| memoria-corrector | yes (60m) |

**Only `director-organizacion` has explicit binding** to Telegram `organizacion` account.

---

## Hypothesis Update
- **Original:** "Channel system needs deeper research."
- **Finding:** Telegram channel well-configured with multi-account support. Key gap is channel system breadth (only Telegram active).

---

## Sources
- Web search: OpenClaw Telegram configuration
- `openclaw.json` channels.telegram inspection
