# Cost Limits & Budgeting — Deep Research

## Step 1: What Is
OpenClaw's cost management is driven entirely by AI model API usage. OpenClaw itself is free/open-source, but operational costs come from LLM tokens + server hosting.

## Step 2: How It Works
1. **Token-based pricing:** Every agent action triggers API calls consuming tokens.
2. **Model tiers:** Budget models ($0.05-$0.60/M tokens) vs premium ($5-$25/M tokens).
3. **Heartbeat system:** Continuous monitoring agents consume tokens faster.
4. **Cron job costs:** Each LLM invocation = cost per run × frequency.
5. **No built-in cost controls:** OpenClaw relies on provider-level billing limits.

**Cost Factors:**
| Factor | Range |
|-------|-------|
| AI Model (budget) | $0.05-$0.60/M tokens |
| AI Model (mid) | $1-$10/M tokens |
| AI Model (premium) | $5-$25/M tokens |
| Server hosting | $5-$50/month |
| Storage/bandwidth | $1-$10/month |

**Typical OpenClaw interaction:** ~1,500 tokens

## Step 3: Use Cases
- **Personal/hobby:** $6-$16/month (budget models, local laptop)
- **Small business:** $25-$50/month (mixed model routing)
- **Heavy automation:** $100-$300+/month (premium models, complex workflows)
- **Cron job budgeting:** Job running every minute = ~$432/month

## Step 4: Problems
- **No built-in cost controls:** OpenClaw doesn't enforce per-agent or global spend limits.
- **Heartbeat drain:** Continuous heartbeat agents accumulate tokens rapidly.
- **Context window bloat:** Long sessions accumulate tokens fast.
- **Frequency risk:** High-frequency cron jobs can spike costs unexpectedly.
- **No real-time tracking:** Native dashboard for cost monitoring is minimal.

## Step 5: Solutions
1. **Set provider billing limits:** Hard limits at Anthropic/OpenAI/Google.
2. **Smart model routing:** Route simple tasks to budget models (60-80% savings).
3. **Budget alerts:** 50%, 75%, 90% thresholds.
4. **Frequency audit:** Review cron job frequencies, especially LLM-invoking jobs.
5. **Prompt optimization:** Shorter prompts + batching = fewer tokens.

## Step 6: Edge Cases
- **Minute-level cron jobs:** Running every minute = $432+/month.
- **Provider outage during budget spike:** Could waste tokens on retries.
- **Model fallback cascade:** Falling through 4-level provider chain = multiplied cost.
- **Concurrent sessions:** Multiple agents × sessions = multiplicative token usage.

## Step 7: Creative Uses
- **Cost allocation by client:** Route different clients to different model tiers.
- **Budget pool:** Single API key with pool of budget for different agents.
- **Shadow cost monitoring:** Run parallel tracking of actual vs expected costs.
- **Dynamic throttling:** Reduce cron frequency when approaching budget limits.

---

## Current System Analysis

**Provider Configuration:**
- Primary: `minimax/MiniMax-M2.7`
- Fallbacks: `nvidia_ext/minimax-m2.5` → `nvidia_ext/z-ai/glm5` → `nvidia_ext/nemotron-3-super` → `google/gemini-3.1-flash-lite`

**Hourly budget target in ledger:** 50 tokens/hour (very low)

**OpenClaw cost status:** MINIMAL coverage in research — this is an operational gap.

---

## Hypothesis Update
- **Original:** "Cost limits = minimal coverage."
- **Finding:** Confirmed — OpenClaw has NO built-in cost enforcement. Relies entirely on provider-level limits and user discipline.

---

## Sources
- Web search: OpenClaw cost management and budgeting
- `openclaw.json` provider configuration
- `ledger.json` hourly_budget_target setting
