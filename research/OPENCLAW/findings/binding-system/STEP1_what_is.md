# Binding System — 7-Step Deep Research

## Step 1: What Is
Bindings route incoming messages from channels to specific agents. Each binding is a match rule that maps channel + account conditions to an agentId.

## Step 2: How It Works
1. **Binding structure:** Array of `{ agentId, match: { channel, accountId, ... } }` entries in `openclaw.json`.
2. **Match evaluation:** Gateway evaluates bindings in order; first match wins.
3. **Routing:** When a message arrives from a channel, binding determines which agent handles it.
4. **Channel plugin integration:** Each channel plugin (Telegram, Discord, etc.) provides channel-specific match fields.

## Step 3: Use Cases
- **Multi-agent routing:** Different Telegram accounts → different agents (e.g., `director-organizacion` for organizacion account).
- **Channel separation:** Separate workflows per channel (Telegram vs Discord).
- **Account-based routing:** Same channel, different accounts → different agents.
- **Fallback routing:** Default agent when no specific binding matches.

## Step 4: Problems
- **Limited match fields:** Only `channel` and `accountId` currently visible in config.
- **No regex/pattern matching:** Exact match only, no wildcard routing.
- **No priority field:** Order in array determines precedence — implicit, not explicit.
- **No fallback binding:** Messages not matching any binding may be dropped or routed to default.

## Step 5: Solutions
- **Ordered binding array:** Place most specific bindings first.
- **Distinct accountIds:** Use separate bot tokens per account for clear routing.
- **Agent specialization:** Each agent handles specific channel/account combos.
- **Monitoring unmatched:** Log binding misses to catch dropped messages.

## Step 6: Edge Cases
- **Multiple channels:** Telegram, Discord, WhatsApp, etc. — each has own match schema.
- **Wildcard `*`:** Some configs use `*` for "any account" — behavior may vary.
- **Cross-channel identity:** Same agent can handle multiple channels if bound to each.
- **Binding evaluation order:** First match wins — cannot have multiple handlers per message.

## Step 7: Creative Uses
- **Multi-tenant routing:** One gateway, multiple bot personas via separate accounts.
- **Channel bridging:** Agent on one channel can send to another via bindings.
- **A/B testing:** Route some users to agent-A, others to agent-B via different accountIds.
- **Shadowing:** Route copies of messages to a monitoring agent alongside primary.

---

## Current Binding Configuration

```json
{
  "bindings": [
    {
      "agentId": "director-organizacion",
      "match": {
        "channel": "telegram",
        "accountId": "organizacion"
      }
    }
  ]
}
```

This routes all Telegram messages from the `organizacion` account to the `director-organizacion` agent.

**Current gap:** All other messages (default Telegram account) have no explicit binding — routed to default agent (`main`).

---

## Hypothesis Update
- **Original:** "Bindings route messages to agents — unknown mechanism."
- **Confirmed:** Binding is a simple match-based router. Current config has only 1 explicit binding; most messages route to default agent.

---

## Sources
- `openclaw.json` bindings array inspection
- Web search (quota exhausted — supplemented with config analysis)
