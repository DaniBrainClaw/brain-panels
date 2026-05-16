# Tareas Largas Autonomas — Fuentes

**Fecha:** 2026-05-16

---

## Artículos Principales

| Recurso | URL |
|---------|-----|
| **Building AI Agents That Actually Complete Tasks** | https://atticusli.com/blog/posts/building-ai-agents-that-complete-tasks/ |
| **Long-running Agents** | https://addyosmani.com/blog/long-running-agents/ |
| **Microsoft: Agent Autonomous Batch Processing** | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/scenarios/agent-autonomous-batch |

---

## Patrones de Diseño

| Patrón | Descripción |
|--------|-------------|
| **Ralph Loop** | Geoffrey Huntley — bash script que itera sobre tareas con checkpointing |
| **ReAct** | Reason Then Act — después de cada acción, razona antes de continuar |
| **State Checkpoints** | Guardar estado cada N pasos para poder reanudar |
| **Bounded Retries** | Retry con approach modificado, máximo 3 intentos |

---

## Errores Comunes en Agentes Largos

1. **Infinite loops** — Repite misma acción
2. **Goal drift** — Pierde el objetivo original
3. **Context overflow** — Se queda sin contexto
4. **Over-confidence** — Dice "listo" sin verificar

---

## Links Adicionales

| Recurso | URL |
|---------|-----|
| **Claude Agent SDK - Long-running agents** | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents |
| **Cursor: Scaling long-running agents** | https://cursor.com/blog/scaling-agents |
| **METR Time Horizons** | https://metr.org/ |

---

*Investigador — Fuentes completadas.*