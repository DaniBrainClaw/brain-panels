# Extension Tool Integration — 7-Step Deep Research

## Step 1: What Is
Extensions (plugins) in OpenClaw can register tools that the LLM can call. The `lossless-claw` plugin provides the canonical example with 4 recall tools (`lcm_grep`, `lcm_describe`, `lcm_expand_query`, `lcm_expand`).

## Step 2: How It Works
1. Plugin defines `openclaw.plugin.json` with tools registered via `api.registerTool()`.
2. Tools are JSON-Schema function definitions exposed to the LLM as typed functions.
3. Tools can be marked `optional: true` — require explicit allowlisting.
4. Global and per-agent allowlists/denylists control tool availability.
5. Plugin loader scans `extensions/` dirs and `~/.openclaw/extensions/` at runtime.

## Step 3: Use Cases
- **LCM Recall Tools:** `lcm_grep`, `lcm_describe`, `lcm_expand_query`, `lcm_expand` for compacted history search.
- **Model Switching:** `clawhub:openclaw-mode-switcher` — switch LLM mid-session.
- **QVeris Plugin:** Dynamic capability discovery via external API.
- **Custom Tools:** Any typed function (read, write, exec, web_search, etc.)

## Step 4: Problems
- **Optional Tools Need Allowlisting:** `optional: true` tools won't auto-enable.
- **Sandboxed Agent Restrictions:** Workspace-origin plugins may be disabled by default.
- **Tool Allowlist Gaps:** `lossless-claw` tools (`lcm_*`) are registered but may not be in agent's allowlist.
- **No Built-in Tool Registry Docs:** Plugin tool registration API is under-documented.

## Step 5: Solutions
- **Explicit Allowlisting:** Add tools to agent config's tool allowlist.
- **Plugin Enable Flag:** Ensure plugin has `"enabled": true` in `plugins.entries`.
- **Optional Tool Discovery:** Use `openclaw plugins list` to see registered tools.
- **Hook-based Approval:** Use `before_tool_call` hooks to require user approval.

## Step 6: Edge Cases
- **Docker Sandboxing:** Tool execution can be sandboxed in Docker containers to limit damage.
- **Workspace Plugins:** Located in `extensions/` directory, may have different security posture than installed plugins.
- **Hook Interception:** Hooks can rewrite tool parameters or block execution at `before_tool_call`.
- **Model Provider Tools:** Providers can expose provider-specific tools (e.g., image generation).

## Step 7: Creative Uses
- **Dynamic Tool Discovery:** Register tools at runtime based on active session context.
- **Capability Escalation:** Use mode-switcher to use stronger model only for complex tool orchestration.
- **Tool Chaining:** Chain plugin tools into TaskFlows for multi-step workflows.
- **Contextual Tool Activation:** Enable/disable tools based on time of day, user, or conversation type.

---

## Current Plugin Landscape

| Plugin | Tools Registered | Status |
|--------|-----------------|--------|
| lossless-claw | lcm_grep, lcm_describe, lcm_expand_query, lcm_expand | ✅ Enabled |
| brain-primary-model-override | None (model provider) | ✅ Enabled |
| mcp-adapter | MCP server tools | ❌ NOT enabled |

---

## Hypothesis Update
- **Original:** "Extensions can register tools — unknown capability."
- **Confirmed:** YES — plugins register JSON-Schema tools via `api.registerTool()`, LCM provides canonical example.
- **Critical Gap:** `mcp-adapter` plugin NOT enabled — MCP server tools not exposed to agents despite config.

---

## Sources
- Web search: OpenClaw plugin tool registration API
- `openclaw.plugin.json` inspection from lossless-claw and brain-primary-model-override
- `lossless-claw/docs/agent-tools.md` — LCM tool reference
