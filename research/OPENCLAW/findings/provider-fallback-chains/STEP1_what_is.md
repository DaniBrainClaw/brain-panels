# Provider Fallback Chains — 7-Step Deep Research

## Step 1: What Is
Provider fallback chains define what happens when the primary model/provider fails. OpenClaw supports model-level fallback chains defined in `agents.defaults.model.fallbacks` array.

## Step 2: How It Works
1. **Fallback chain:** Array of `provider/model` strings tried in order when primary fails.
2. **Primary first:** `minimax/MiniMax-M2.7` is primary.
3. **Fallback order:** nvidia_ext/minimax-m2.5 → nvidia_ext/z-ai/glm5 → nvidia_ext/nemotron-3-super → google/gemini-3.1-flash-lite.
4. **Provider-level fallback:** Built into `models.providers` definitions.
5. **Per-provider models:** Each provider can have multiple models listed.
6. **Cost optimization:** Fallbacks allow cheaper models for non-critical tasks.

**Current Configuration:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax/MiniMax-M2.7",
        "fallbacks": [
          "nvidia_ext/minimaxai/minimax-m2.5",
          "nvidia_ext/z-ai/glm5",
          "nvidia_ext/nvidia/nemotron-3-super-120b-a12b",
          "google/gemini-3.1-flash-lite"
        ]
      }
    }
  }
}
```

## Step 3: Use Cases
- **Reliability:** Automatic switch when primary model is down.
- **Cost optimization:** Use cheaper fallback models for simple tasks.
- **Latency optimization:** Use faster models when speed matters more than quality.
- **Model diversity:** Test different models for same task.
- **Capacity scaling:** Multiple providers handle load spikes.

## Step 4: Problems
- **No explicit retry count:** How many times to retry each fallback is unclear.
- **Provider-specific failures:** Whole provider may be down, not just one model.
- **Context window mismatch:** Fallback models may have different context limits.
- **Cost tracking:** Token usage across fallback chain may not be tracked cleanly.
- **No circuit breaker:** Continues trying even when provider is consistently failing.

## Step 5: Solutions
- **Explicit fallback ordering:** Put most reliable/capable fallbacks first.
- **Monitor provider health:** Track failure rates per provider.
- **Provider-level disable:** Disable provider entirely if consistently failing.
- **Custom fallback chains:** Define different chains per task type.
- **Cost alerts:** Set budget alerts for fallback-heavy usage.

## Step 6: Edge Cases
- **Identical provider fallbacks:** All nvidia_ext models go through same API — if one fails, others likely fail too.
- **Mixed API formats:** `anthropic-messages` (minimax) vs `openai-completions` (nvidia_ext) — may have different response formats.
- **Cache invalidation:** Switching models may invalidate prompt cache.
- **Token limit mismatch:** Fallback to smaller context model may truncate conversation.
- **Rate limit cascading:** Hitting rate limit on primary may cascade to fallbacks.

## Step 7: Creative Uses
- **Tiered fallback strategy:** Strong model → medium → weak (cost gradient).
- **Geographic fallback:** Provider with lower latency for your region as primary.
- **Specialized fallback:** Primary is general; fallback is specialized for specific domain.
- **A/B testing fallback:** Rotate which fallback is primary to collect comparative metrics.

---

## Current Provider Landscape

| Provider | Format | Models |
|----------|--------|--------|
| minimax | anthropic-messages | MiniMax-M2.7 (primary) |
| nvidia_ext | openai-completions | 3 models (fallback chain) |
| google | — | 7 models (last resort) |

**Gap:** Google provider has no fallbacks configured — if all other providers fail, Google is last resort but has no defined fallback of its own.

---

## Hypothesis Update
- **Original:** "Fallback chains handle provider failures — behavior unclear."
- **Confirmed:** Fallback chain is array-based, first-fail-then-next. Current chain has 4 levels. Google's models serve as de facto final fallback.

---

## Sources
- `openclaw.json` agents.defaults.model configuration
- `openclaw.json` models.providers configuration
