# Extension Provider Integration — 7-Step Deep Research

## Step 1: What Is
Extensions can register custom model providers via `api.registerProvider()`. This allows OpenClaw to use LLMs beyond the standard built-in providers (OpenAI, Anthropic, Google, etc.).

## Step 2: How It Works
1. Plugin exports `register(api)` function with `api.registerProvider()` call.
2. Provider defines `baseUrl`, `api` format (`anthropic-messages` or `openai-completions`), and `models` array.
3. Provider implementations are npm packages implementing the standard Provider interface.
4. Providers can be published to npm and installed via `openclaw plugins install`.

## Step 3: Use Cases
- **Custom LLM Endpoints:** Register internal/specialized LLMs not in standard providers.
- **Proxy Providers:** Wrap third-party APIs with custom authentication.
- **Aggregators:** OpenRouter-style aggregation of multiple providers.
- **Model Override:** `brain-primary-model-override` plugin forces specific model (MiniMax M2.7).

## Step 4: Problems
- **Provider Interface Under-Documented:** Exact Provider interface specification is unclear.
- **No Public Provider Examples:** Few open-source provider implementations to reference.
- **API Format Constraints:** Must use `anthropic-messages` or `openai-completions` — limits provider flexibility.
- **npm Security:** Installing providers from npm requires trust — lifecycle scripts execute during install.

## Step 5: Solutions
- **Use `openai-completions` format:** More flexible, works with many OpenAI-compatible APIs.
- **Provider npm Packages:** Publish custom providers as npm packages for reuse.
- **Version Pinning:** Pin provider versions to avoid supply chain attacks.
- **Provider Allowlisting:** Only install from trusted npm packages.

## Step 6: Edge Cases
- **OAuth Providers:** Runtime-managed OAuth supported for providers like `openai-codex` and `github-copilot`.
- **API Key Rotation:** Provider API keys should be rotatable without redeployment.
- **Context Window Mismatch:** Custom providers may report wrong context window sizes.
- **Cost Tracking:** Custom providers may not report costs correctly to OpenClaw's billing.

## Step 7: Creative Uses
- **Internal LLM Gateway:** Wrap internal company LLMs behind a provider plugin.
- **Multi-Provider Fallback:** Register multiple providers with different cost/latency profiles.
- **Specialized Models:** Register fine-tuned models for specific domains (code, legal, medical).
- **Model Discovery:** Auto-discover available models from provider at startup.

---

## Current Provider Landscape

| Provider | Format | Base URL |
|----------|--------|----------|
| google | — | generativelanguage.googleapis.com |
| minimax | anthropic-messages | api.minimax.io/anthropic |
| nvidia_ext | openai-completions | integrate.api.nvidia.com |
| openai-codex | openai-codex-responses | chatgpt.com/backend-api |

---

## Hypothesis Update
- **Original:** "Extensions can register model providers — unknown mechanism."
- **Confirmed:** YES — `api.registerProvider()` in plugin `register(api)` function.
- **Current Implementation:** `brain-primary-model-override` is a provider-hook plugin (not a provider itself), forcing MiniMax as primary.

---

## Sources
- Web search: OpenClaw provider registration API
- `openclaw.json` provider configuration inspection
- `openclaw.plugin.json` from brain-primary-model-override plugin
