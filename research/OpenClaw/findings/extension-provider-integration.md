# Extension Provider Integration

## What is it?

Extension Provider Integration allows extensions to dynamically register, override, or remove LLM model providers at runtime. This enables extensions to:

1. **Add new model providers** (e.g., a proxy extension that routes requests through a corporate gateway)
2. **Override existing provider URLs** (e.g., point `anthropic` at a proxy endpoint)
3. **Register OAuth-based providers** (enterprise SSO authentication)
4. **Unregister providers** (restore original built-in models)

## How it works

### Registration Flow

```
Extension.load()
  → pi.registerProvider(name, config)
    → runtime.registerProvider(name, config, extension.path)
      → pendingProviderRegistrations.push({ name, config, extensionPath })

ExtensionRunner.bindCore()
  → for each pending registration:
      → providerActions?.registerProvider(name, config)  [optional passthrough]
      → modelRegistry.registerProvider(name, config)
  → runtime.registerProvider = direct call (no longer queued)
```

**Phase 1 (Extension Loading):** Extensions call `pi.registerProvider()` during their factory function execution. Since the `ModelRegistry` isn't yet bound to the runtime, calls are queued in `pendingProviderRegistrations[]`.

**Phase 2 (bindCore):** Once the runner has the `ModelRegistry` reference, it flushes all pending registrations. The runtime's `registerProvider` is then replaced with a direct call that registers immediately, bypassing the queue.

### `before_provider_request` Event

The `before_provider_request` event fires just before any provider API call is made. Extensions can intercept and transform the request payload:

```ts
pi.on("before_provider_request", async (event, ctx) => {
    // Transform the payload before it goes to the provider
    return modifiedPayload; // Replaces event.payload for the actual call
});
```

**Event chain:** Each handler's return value becomes the payload for the next handler (chained transformation). If a handler returns `undefined`, the payload passes through unchanged.

### ProviderConfig Interface

```ts
interface ProviderConfig {
    baseUrl?: string;           // Required when defining models
    apiKey?: string;            // Required when defining models (unless oauth)
    api?: Api;                  // API type (required at provider or model level)
    streamSimple?: (model, context, options?) => AssistantMessageEventStream;
    headers?: Record<string, string>;
    authHeader?: boolean;       // If true, adds Authorization: Bearer header
    models?: ProviderModelConfig[];  // If provided, replaces all existing models
    oauth?: {                   // OAuth provider for /login support
        name: string;
        login(callbacks: OAuthLoginCallbacks): Promise<OAuthCredentials>;
        refreshToken(credentials: OAuthCredentials): Promise<OAuthCredentials>;
        getApiKey(credentials: OAuthCredentials): string;
        modifyModels?: (models, credentials) => Model[];
    };
}
```

### ProviderModelConfig Interface

```ts
interface ProviderModelConfig {
    id: string;                // e.g., "claude-sonnet-4-20250514"
    name: string;              // Display name
    api?: Api;                 // API type override for this model
    reasoning: boolean;        // Supports extended thinking
    input: ("text" | "image")[];
    cost: { input: number; output: number; cacheRead: number; cacheWrite: number };
    contextWindow: number;     // Max tokens in context
    maxTokens: number;         // Max output tokens
    headers?: Record<string, string>;
    compat?: Model<Api>["compat"];
}
```

### Unregister Flow

```ts
pi.unregisterProvider(name)
  → runtime.unregisterProvider(name)
    → if before bindCore: removes from pendingProviderRegistrations
    → if after bindCore: calls modelRegistry.unregisterProvider(name)
      → removes from registeredProviders
      → calls refresh() to restore built-in models
```

## Uses

1. **Corporate AI proxies** — Route API calls through enterprise proxies with custom auth
2. **Model gateway extensions** — Aggregate multiple providers under one extension
3. **SSO-protected providers** — Enterprise login with token refresh
4. **Custom API endpoints** — Point existing providers at different baseUrls (e.g., for testing)
5. **Dynamic provider switching** — Swap providers at runtime based on conditions

## Problems

1. **Double registration conflict** — If two extensions register the same provider name, the second overwrites the first silently
2. **No unregister confirmation** — No way to know if an unregister call actually removed something
3. **Validation only on register** — `validateProviderConfig` is only called during `registerProvider`, not `unregisterProvider`
4. **OAuth state persistence gap** — Credentials returned by `login()`/`refreshToken()` must be persisted by the extension; OpenClaw doesn't handle this automatically

## Solutions

1. **Conflict detection** — Could check `modelRegistry.registeredProviders.has(name)` before registering and warn
2. **Unregister result** — `unregisterProvider` could return `boolean` indicating whether something was removed
3. **Idempotent unregister** — Already works (returns early if not registered), but could be more explicit
4. **Credential storage** — Extensions should use `pi.appendEntry()` to persist OAuth credentials in session state

## Edge Cases

1. **Register during event handler** — After `bindCore`, calling `registerProvider` in a `tool_call` handler takes effect immediately (no reload needed)
2. **Register same provider twice** — Second call replaces the first; no merge of model lists
3. **Unregister non-existent provider** — No-op (silent)
4. **Register provider with only `baseUrl`** — Overrides URL for all existing models from that provider (doesn't replace models)
5. **`streamSimple` without `api`** — Throws validation error: `"Provider X: "api" is required when registering streamSimple."`
6. **OAuth without apiKey** — Allowed; `getApiKey` from credentials is used instead

## Creative Uses

1. **A/B testing proxy** — Route different percentages of requests to different provider endpoints
2. **Cost tracking extension** — Intercept `before_provider_request` to log token counts per request
3. **Request caching layer** — Inspect payload and return cached responses for identical requests
4. **Response transformation** — Transform provider responses (e.g., strip proprietary metadata) via `before_provider_request` return value
5. **Provider fallback chain** — On provider failure, automatically retry with a different provider registered in the same extension
6. **Dynamic model rotation** — Rotate through multiple model IDs from the same provider based on time or load

## Sources

- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/loader.js` — Provider registration queue (lines 113-120, 213-214)
- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/runner.js` — bindCore flush + direct call replacement (lines 144-177, emitBeforeProviderRequest)
- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/types.d.ts` — ProviderConfig, ProviderModelConfig, BeforeProviderRequestEvent (lines 396-397, 712, 836-974)
- `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/model-registry.js` — registerProvider/unregisterProvider implementation (lines 481-510)