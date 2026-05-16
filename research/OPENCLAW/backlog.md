# OpenClaw Research Backlog

## Prioridad ALTA

### 1. Lossless-Claw Configuration Details ✅ COMPLETADO
- **Qué:** Configuración detallada del plugin lossless-claw
- **Hallazgo:** DAG-based memory con tuning crítico en `leafChunkTokens` y `cacheAwareCompaction`
- **Sources:** Docs técnicos de la extensión
- **Status:** **COMPLETADO** — Artifact: `findings/lossless-claw-config/STEP2-7_full_chain.md`
- **Realizado:** 2026-04-25 — 7-step chain completed in one iteration

### 2. Cron Jobs — Estado real vs jobs.json ✅ COMPLETADO
- **Qué:** Por qué hay discrepancy entre `openclaw cron list` (muestra jobs activos) y `jobs.json` (vacío)
- **Hallazgo clave:** jobs.json NO está vacío — tiene 20 jobs! El problema real es que muchos están broken/timing out
- **Sources:** jobs.json real + web search
- **Status:** **COMPLETADO** — Artifact: `findings/cron-jobs-state/STEP1_what_is.md`
- **Next step:** Limpiar jobs rotos (hay ~13 con timeout errors)
- **Realizado:** 2026-04-25 — 7-step chain completed in one iteration

### 3. MCP Server Configuration ✅ COMPLETADO
- **Qué:** NotebookLM MCP server configurado pero no documentado
- **Hallazgo clave:** mcp-adapter plugin NO está habilitado; servidor notebooklm configurado pero disconnected
- **Sources:** openclaw.json + web search
- **Status:** **COMPLETADO** — Artifact: `findings/mcp-server-config/STEP1_what_is.md`
- **Action needed:** Enable mcp-adapter plugin + authenticate nlm
- **Realizado:** 2026-04-25

## Prioridad MEDIA

### 4. Extension Tool Integration ✅ COMPLETADO
- **Qué:** ¿Pueden las extensiones Pi registrar tools que el LLM puede llamar?
- **Hallazgo:** YES — plugins register JSON-Schema tools via api.registerTool(); LCM provides canonical example
- **Sources:** openclaw.plugin.json inspection + web search
- **Status:** **COMPLETADO** — Artifact: `findings/extension-tool-integration/STEP1_what_is.md`
- **Realizado:** 2026-04-25

### 5. Extension Provider Integration ✅ COMPLETADO
- **Qué:** ¿Pueden las extensiones registrar model providers personalizados?
- **Hallazgo:** YES — api.registerProvider() confirma. Formatos: anthropic-messages u openai-completions
- **Sources:** openclaw.json providers + web search
- **Status:** **COMPLETADO** — Artifact: `findings/extension-provider-integration/STEP1_what_is.md`
- **Realizado:** 2026-04-25

### 6. Extension Security Model ✅ COMPLETADO
- **Qué:** ¿Las extensiones están sandboxed? ¿Puede una extensión maliciosa crashear el Gateway?
- **Hallazgo:** CRITICAL - investigación de CVEs: CVE-2026-25253 (CSRF token theft, CVSS 8.8), CVE-2026-32922 (privilege escalation, CVSS 9.9), CVE-2026-32046 (browser sandbox bypass). Sistema 2026.4.12 YA parcheado para los tres.
- **Sources:** Web search CVEs + openclaw.json version inspection
- **Status:** **COMPLETADO** — Artifact: `findings/extension-security-model/STEP1_what_is.md` + `findings/security-remediation-plan/STEP1_what_is.md`
- **Resultado:** Sistema v2026.4.12 está por encima de todas las versiones corregidas (2026.1.29, 2026.2.21, 2026.3.11). Remediation plan creado con verificación steps.
- **Realizado:** 2026-04-25

### 7. TaskFlow System — Deep Dive ✅ COMPLETADO
- **Qué:** Cómo crear, ejecutar y monitorizar TaskFlows
- **Hallazgo:** Durable parent-child orchestration con revision-safe state. wait/resume pattern. Lobster authoring.
- **Sources:** taskflow/SKILL.md + examples
- **Status:** **COMPLETADO** — Artifact: `findings/taskflow-system/STEP1_what_is.md`
- **Realizado:** 2026-04-25

## Prioridad BAJA (exploración futura)

### 10. Channel System — Telegram ✅ COMPLETADO
- **Qué:** Cómo funciona el sistema de canales Telegram multi-account con streaming y dmPolicy
- **Hallazgo:** dmPolicy=pairing, streaming=partial, 2 cuentas (default + organizacion), groupPolicy=allowlist
- **Sources:** openclaw.json channels.telegram + web search
- **Status:** **COMPLETADO** — Artifact: `findings/channel-system-telegram/STEP1_what_is.md`
- **Realizado:** 2026-04-25

### 8. Binding System — Detalles completos ✅ COMPLETADO
- **Qué:** Cómo funcionan exactamente los bindings routing
- **Hallazgo:** Match-based router (channel + accountId), first-match-wins, only 1 explicit binding
- **Sources:** openclaw.json bindings inspection
- **Status:** **COMPLETADO** — Artifact: `findings/binding-system/STEP1_what_is.md`
- **Realizado:** 2026-04-25

### 9. Provider Fallback Chains — Comportamiento real ✅ COMPLETADO
- **Qué:** Cómo se comporta el fallback cuando un provider falla
- **Hallazgo:** 4-level array-based fallback: minimax→nvidia_ext(3 models)→google. First-fail-then-next.
- **Sources:** openclaw.json model configuration
- **Status:** **COMPLETADO** — Artifact: `findings/provider-fallback-chains/STEP1_what_is.md`
- **Realizado:** 2026-04-25

### 10. Channel System — Telegram ✅ COMPLETADO
- **Qué:** Sistema de canales Telegram multi-account con streaming y dmPolicy
- **Hallazgo:** dmPolicy=pairing, streaming=partial, 2 cuentas (default + organizacion), groupPolicy=allowlist
- **Sources:** openclaw.json channels.telegram + web search
- **Status:** **COMPLETADO** — Artifact: `findings/channel-system-telegram/STEP1_what_is.md`
- **Realizado:** 2026-04-25

### 11. Cost Limits & Budgeting ✅ COMPLETADO
- **Qué:** Gestión de costos de LLM en OpenClaw
- **Hallazgo:** NO hay controles internos - depende de límites del provider. Cron jobs = riesgo de costo.
- **Sources:** Web search + config analysis
- **Status:** **COMPLETADO** — Artifact: `findings/cost-limits-budgeting/STEP1_what_is.md`
- **Realizado:** 2026-04-25

---

## Backlog de verificación (revisar hechos existentes)

- [x] Hook Security: CONFIRMADO — context.cfg NO tiene auditoría. Custom hook requerido.
- [x] Skill Dynamic Activation: CONFIRMADO — NO hay API directa. Skills son estáticos.
- [x] Cron hot-reload: CONFIRMADO parcial — reload.mode=restart es default. CLI openclaw cron provee job-level reload.

---

**RESUMEN INVESTIGACIÓN COMPLETA (2026-04-25):**

11 temas de backlog COMPLETADOS + 3 items de verificación completados.
Hallazgo CRÍTICO: Sistema 2026.4.12 VULNERABLE a CVE-2026-25253, CVE-2026-32922, CVE-2026-32046.

---

## Criterios depriorización

1. **Valor operativo:** ¿Ayuda a resolver un problema actual?
2. **Cobertura:** ¿Llena un gap en las 19+ secciones de OPENCLAW_EXPERT.md?
3. **Verificabilidad:** ¿Se puede confirmar con fuentes oficiales o código?
4. **Novedad:** ¿Aporta algo que no esté ya documentado?

---

*Última actualización: 2026-04-23*
