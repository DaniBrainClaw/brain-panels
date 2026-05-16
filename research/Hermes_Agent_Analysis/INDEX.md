# Hermes Agent Analysis — INDEX

**Fecha:** 2026-05-16  
**Repo:** github.com/NousResearch/hermes-agent (153K stars)  
**Versión actual:** v0.14.0

---

## Resumen Ejecutivo

Hermes Agent es un AI agentself-improving construido por Nous Research. A diferencia de otros agentes que solo recuerdan lo que pasó, Hermes extrae qué funcionó, lo escribe como skill reutilizable, y lo carga la próxima vez que surge un problema similar.

**BRAIN puede aprender de Hermes** — no necesita migrar, pero sí implementar features del closed learning loop.

---

## Estructura del Análisis

```
Research/Hermes_Agent_Analysis/
├── sources.md           ✅ Links y referencias
├── INDEX.md            ✅ Este archivo
├── SUMMARY_DANI.md     ✅ En español, qué интегрировать
└── findings/
    ├── step_1.md       ✅ Qué es Hermes (desde código)
    ├── step_2.md       ✅ Funcionalidades principales
    ├── step_3.md       ✅ Self-improvement mechanism
    └── step_4.md       ✅ Comparison con BRAIN
```

---

## Hallazgos Principales

### Lo que Hermes tiene que BRAIN NO:

| Feature | Qué hace | Priority |
|---------|----------|----------|
| **Periodic nudge** | Auto-memory curation cada X intervals | 🔴 Alta |
| **Autonomous skill creation** | Crea skills después de 5+ tool calls | 🔴 Alta |
| **Skill self-patching** | Mejora skills durante uso | 🟡 Media |
| **FTS5 session search** | Full-text search + LLM summarization | 🟡 Media |
| **4-layer memory** | Separated concerns (prompt, session, skills, project) | 🔴 Alta |
| **Adaptive reasoning** | Controla thinking depth por tarea | 🟡 Media |
| **Built-in cron** | Natural language scheduling | 🟡 Media |
| **Fallback skills** | Auto-show skill cuando tool unavailable | 🟢 Baja |
| **20+ platforms** | Un gateway para todo | 🟢 No aplica |

### Lo que BRAIN tiene bien (mejor que Hermes):

1. **Agente Investigador dedicado** — BRAIN tiene esto, Hermes no
2. **Simplicidad** — más fácil para caso de uso de Dani
3. **Setup ya funcional** — no empezar de cero

---

## El Self-Improvement Loop de Hermes

```
Understand → Act → Verify → Save Memory → Create Skills → Load Next Time
                           ↑                              ↓
                           └──────── NUDGE (periodic) ────┘
```

**No es fine-tuning** — es la capa agent que mejora, no el modelo base.

---

## Recommendation

**NO migrar a Hermes** — слишком много работы.

**SÍ implementar en BRAIN:**
1. Memory curation activa (límites en MEMORY.md)
2. Periodic self-review (semanal)
3. Skill creation trigger (después de 5+ tool calls)
4. FTS5 session search (investigar implementación)

---

## Fuentes

- Repo: https://github.com/NousResearch/hermes-agent
- Docs: https://hermes-agent.nousresearch.com/docs/
- Self-Improving Guide: https://hermes-agent.ai/blog/self-improving-ai-guide

---

*Investigador — INDEX completado.*