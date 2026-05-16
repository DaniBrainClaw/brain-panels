# MCP Server Configuration — 7-Step Deep Research

## Step 1: What Is
MCP (Model Context Protocol) is an open standard enabling AI models to connect to external data sources and tools via a universal "USB-C port" interface. OpenClaw supports MCP servers through the `mcp-adapter` plugin.

## Step 2: How It Works
1. OpenClaw's `mcp-adapter` plugin connects to MCP servers on startup.
2. It discovers available tools and registers them as native OpenClaw agent tools.
3. Servers communicate via `stdio` or `http` transport protocol.
4. Configuration lives in `~/.openclaw/openclaw.json` under `mcp.servers`.

## Step 3: Use Cases
- **NotebookLM Integration:** Query notebooks, manage sources, generate audio overviews.
- **External Tool Access:** Databases, file systems, web search, browser automation.
- **Enterprise Workflows:** Google Slides, WordPress, Atlassian products.
- **Multi-Account Rotation:** Managing multiple NotebookLM accounts.

## Step 4: Problems
- **No Official API:** Google hasn't released a public NotebookLM API; community MCP servers rely on browser automation.
- **Authentication Drift:** MCP servers often require OAuth/browser login that can expire.
- **NotebookLM MCP Not Enabled:** Current config has `notebooklm` server defined but no `mcp-adapter` plugin enabled in `plugins.entries`.

## Step 5: Solutions
- **Enable mcp-adapter:** Add to `plugins.entries` with `"enabled": true`.
- **Tool Allowlist:** For sandboxed agents, add `mcp-adapter` to tool allowlist.
- **Auto-Reconnect:** The adapter automatically reconnects if connections drop.
- **npx notebooklm-mcp@latest:** For NotebookLM CLI login and tool access.

## Step 6: Edge Cases
- **Transport Types:** `stdio` (local CLIs like `nlm`) vs `http` (remote servers).
- **Multi-Instance Mode:** `OPENCLAW_INSTANCES` env var for orchestrating multiple gateways from single MCP server.
- **Headless Deployments:** NotebookLM MCP optimized for headless with anti-detection.
- **OAuth2 + PKCE:** Required for custom MCP connectors (Claude.ai compatible).

## Step 7: Creative Uses
- **Research Pipeline:** Agent queries NotebookLM sources → synthesizes with OpenClaw → sends Telegram briefing.
- **Automated Audio Briefs:** Generate NotebookLM audio overview from day's research artifacts, deliver via cron.
- **Multi-Source Synthesis:** Pull from NotebookLM + web search + memory → create comprehensive daily audit.

---

## Current Config Analysis

**In `openclaw.json`:**
```json
"mcp": {
  "servers": {
    "notebooklm": {
      "command": "nlm",
      "args": ["mcp", "server"],
      "env": {}
    }
  }
}
```

**ISSUE:** No `mcp-adapter` plugin enabled. The `notebooklm` server is defined but not connected through the adapter.

**ISSUE:** No authentication token (`env: {}`) — `nlm login` required before tools work.

---

## Hypothesis Update
- **Original:** "NotebookLM MCP server configured but not documented."
- **Revised:** MCP server IS configured but **mcp-adapter plugin is NOT enabled** — tools are not exposed to agents. Also missing authentication setup.
- **Action Needed:** Enable `mcp-adapter` plugin + authenticate `nlm` + test tool discovery.

---

## Sources
- Web search: OpenClaw MCP configuration 2026
- Web search: NotebookLM MCP server capabilities
- `openclaw.json` current config inspection
