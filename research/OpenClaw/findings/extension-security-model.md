# Extension Security Model — COMPLETE RESEARCH FINDINGS

**Research Date:** 2026-04-23
**Topic:** L25 — Extension Security Model
**Priority:** HIGH
**Research Depth:** 6-Layer Exhaustive Analysis

---

## 1. WHAT IS — Definition

The **Extension Security Model** in OpenClaw defines the trust and isolation boundaries for custom `pi-hooks` (Pi extensions). Unlike many modern plugin systems, OpenClaw extensions are **not sandboxed**. They operate as first-class citizens within the Gateway process, granting them full access to the internal state, host file system, network, and secrets management.

---

## 2. HOW IT WORKS — Mechanics

- **In-Process Execution:** Extensions are loaded via `jiti` and execute within the same Node.js process as the OpenClaw Gateway.
- **Shared Memory:** There is no memory isolation. An extension can read/modify the `ExtensionContext` or `SessionManager` state of any other extension or the agent core itself.
- **Privilege Inheritance:** Extensions inherit the OS-level permissions of the Gateway process.
- **Credential Access:** Through `ExtensionContext` (specifically `sessionManager` and `modelRegistry`), extensions have programmatic access to API keys, OAuth credentials, and session tokens.
- **Event-Driven Hooks:** Security is reliant on event-based interception (e.g., `tool_call` events) rather than preemptive resource restriction.

---

## 3. USES — Applications

- **Deep Integration:** Building plugins that require real-time, low-latency access to the agent loop.
- **UI Customization:** Modifying the terminal UI (TUI) via `ExtensionUIContext` widgets, overlays, and custom editors.
- **Workflow Automation:** Orchestrating complex tasks that involve multiple tools and sessions.

---

## 4. PROBLEMS — Limitations

- **Critical Security Deficit:** Total lack of process/memory sandboxing means a single compromised extension can compromise the entire OpenClaw instance.
- **Exfiltration Risk:** Extensions can make outbound network calls, allowing for easy data exfiltration of any internal information (including session history or credentials).
- **No Least-Privilege:** There is no capability-based security model; extensions are either loaded or not.
- **Persistence Risks:** Malicious extensions can modify core agent files, inject malicious prompts into future sessions, or install persistent backdoors.

---

## 5. SOLUTIONS — Best Practices

- **Trusted Sources Only:** Treat third-party extensions as running arbitrary code with `sudo` equivalent permissions.
- **Code Review:** Manually audit any extension source code before loading it via `additionalExtensionPaths`.
- **Environment Separation:** Use separate OpenClaw Gateway instances (dev/prod) if testing unverified extensions.
- **Minimize Dependencies:** Audit the dependency tree of any extension, as malicious upstream packages pose the same risk as the extension itself.
- **Hook Hygiene:** Use only the minimum required events. Avoid `before_agent_start` or broad-reaching lifecycle hooks if unnecessary.

---

## 6. EDGE CASES

- **Dependency Attacks:** A seemingly safe extension could pull in a compromised npm package, giving the attacker in-process control.
- **Resource Exhaustion:** A poorly written extension could cause memory leaks or CPU spikes, affecting the stability of the Gateway process itself.
- **Hook Conflicts:** If multiple extensions register conflicting event handlers, the execution order is dictated by the load order, which may not be deterministic.

---

## 7. CREATIVE USES

- **Security Auditing Extension:** A "meta-extension" that hooks into all lifecycle events to log activity, detect prompt injection, or monitor for suspicious tool calls.
- **Compliance Enforcement:** Use extension hooks to force compliance by injecting mandatory system prompt guidelines at the start of every session.

---

## 8. NEW Questions Opened by This Research

- [ ] Can we implement a secondary "sandbox" runtime (e.g., WebAssembly or child process) for extensions?
- [ ] Is it feasible to provide a restricted `ExtensionAPI` sub-set for "untrusted" extensions?
- [ ] Could we add a manifest file (e.g., `manifest.json`) to extensions to declare requested capabilities/permissions?

---

## 9. Sources

1. `/usr/local/lib/node_modules/openclaw/node_modules/@mariozechner/pi-coding-agent/dist/core/extensions/types.d.ts`
2. `/usr/local/lib/node_modules/openclaw/docs/plugins/architecture.md`
3. `/usr/local/lib/node_modules/openclaw/docs/help/troubleshooting.md`
