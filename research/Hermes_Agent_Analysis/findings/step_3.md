# Hermes Agent Analysis — Step 3: Self-Improvement Mechanism

**Fecha:** 2026-05-16

---

## Fuentes

1. **Self-Improving AI Guide** — hermes-agent.ai/blog/self-improving-ai-guide
2. **Inside Hermes Agent** — mranand.substack.com
3. **Five Pillars: Memory, Skills, Soul, Crons, Self-Improvement** — mindstudio.ai

---

## Qué es Self-Improvement en Hermes

### Definición:
> "Hermes improves at the **agent layer** — it gets better at choosing the right workflow, loading the right skill, respecting project conventions, and avoiding mistakes the user already corrected."

**No es fine-tuning del modelo base.** El modelo puede seguir siendo Claude, GPT, local, o cualquier provider. Hermes mejora la **capa agent** envolviendo ese modelo en memory, tools, skills, session recall, cron, y verification habits.

---

## El Ciclo de Mejora (Closed Learning Loop)

```
┌─────────────────────────────────────────────────────────┐
│                    EL LOOP                              │
│                                                          │
│  1. Understand task + inspect environment                │
│           ↓                                              │
│  2. Act with tools (no guessing)                        │
│           ↓                                              │
│  3. Verify result (tests, checks, output)               │
│           ↓                                              │
│  4. Save durable facts → MEMORY.md                      │
│           ↓                                              │
│  5. Convert procedures → Skills                         │
│           ↓                                              │
│  6. Load skills next time automatically                 │
│           ↓                                              │
│  7. Goto 1 (contexto mejorado)                         │
└─────────────────────────────────────────────────────────┘
```

---

## Periodic Nudge — El Trigger Automático

### Qué es:
Cada ciertos intervalos, Hermes recibe un **internal system-level prompt** que le pregunta:
> "¿Mirando hacia atrás, hay algo que vale la pena persistir?"

### Cómo funciona:
1. **Fire without user input** — no necesita que Dani le diga nada
2. El agente escanea actividad reciente
3. Si cruza threshold → escribe a MEMORY.md
4. Memory stays **curated**, no se convierte en dump de cada interacción

### Threshold triggers:
- 5+ tool calls en una tarea
- Recovery from error
- User correction (Dani le dice que no lo haga así)
- Non-obvious workflow that worked

---

## Skill Creation — De Experiencia a Skill

### Cuándo crea skills:
Después de completar una tarea, Hermes revisa si el path que usó merece documentarse.

### Criterios:
```
IF task involved:
  - 5+ tool calls, OR
  - Recovery from error, OR
  - User correction, OR
  - Non-obvious successful workflow
THEN:
  create skill in ~/.hermes/skills/
```

### El skill file:
```yaml
---
name: deployment-workflow
description: Deploy project via GitHub push
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [devops, deployment]
    category: workflow
---
# Deployment Workflow

## When to Use
User asks for landing page fix

## Procedure
1. Inspect repo structure
2. Edit correct file
3. Run lint and build
4. Commit and push

## Pitfalls
- Don't use hosting CLI directly
- Check lint before commit

## Verification
Run 'git log' to confirm push
```

### Open Standard:
Skills siguen [agentskills.io](https://agentskills.io/specification) — son **portables** across agents compatibles.

---

## Skill Self-Improvement — Patching, Not Rewriting

### El agente NO reescribe skills completo:
- Usa `patch` por default (no `edit`)
- Solo cambia la parte que mejoró
- Más token-efficient
- Menos risk de romper lo que ya funciona

### 6 skill actions:
```python
skill_manage(action="create")   # Nueva skill
skill_manage(action="patch")   # Actualizar parte (PREFERRED)
skill_manage(action="edit")    # Reescribir completo
skill_manage(action="delete")  # Borrar
skill_manage(action="write_file")   # Archivos adicionales
skill_manage(action="remove_file")  # Borrar archivos
```

---

## Memory Management — Curated, Not Unlimited

### Límites estrictos:
| Store | Limit | Typical entries |
|-------|-------|-----------------|
| memory | 2,200 chars | 8-15 entries |
| user | 1,375 chars | 5-10 entries |
| **Total** | **3,575 chars** | ~800 tokens |

### Por qué límites?
- Previene memory bloat
- Fuerza curación activa
- Mantiene token bill control

### Lo que NO se guarda:
- Temporary task progress
- PR numbers
- Stale run logs
- Raw secrets
- Anything that expires quickly

### Lo que SÍ se guarda:
- User communication preferences
- Stable environment paths
- Project deployment conventions
- Tool quirks and integration gotchas
- Corrections user should not repeat

---

## Session Archive — Episodic Memory

### Stack:
- **SQLite** como archive
- **FTS5** para full-text search
- **LLM summarization** antes de inject

### Cómo funciona:
1. Cada sesión se archivea
2. FTS5 index permite búsqueda
3. Agent busca cuando necesita contexto pasado
4. Retrieved results → LLM summarization
5. Solo lo **relevante** entra al contexto actual

### Deliberate vs Always-On:
- **Session search** = on-demand retrieval
- **Prompt memory** = always-on, every session

---

## Failure Modes — Qué sale mal

### Síntomas:
1. Agent cita stale facts después de un project change
2. Skills contienen comandos que ya no funcionan
3. Memory guarda temporary run logs en vez de stable preferences
4. Agent claims success sin testing

### Fix:
```bash
# Remove stale memories
memory(action="remove", old_text="stale fact")

# Patch skill immediately
skill_manage(action="patch", old_text="old command", new_text="new command")

# Require verification before completion
```

---

## Adaptive Reasoning Effort

### Concepto:
No todas las tareas requieren el mismo "thinking budget".

### Ejemplo:
- Small formatting edit → consume reasoning mínimo
- Multi-repo debugging → deep reasoning

### Beneficio:
- Token efficiency
- Speed para tareas simples
- Depth para tareas complejas

---

## Reinforcement Learning (Atropos)

### Qué es:
Research en training próximo generation de tool-calling models.

### Rol:
- Batch trajectory generation
- Trajectory compression
- RL training with Atropos

### Importante:
> "Most users do not need RL to benefit from self-improvement today."

Para day-to-day work, el path confiable es **structured memory + skills**.

---

##对比 BRAIN

### Qué tiene Hermes que BRAIN NO tiene (todavía):

| Feature | Hermes | BRAIN |
|---------|--------|-------|
| **Periodic nudge** | ✅ Auto-memoria curation | ❌ No existe |
| **Autonomous skill creation** | ✅ Crea skills después de complex tasks | ❌ Skills manuales |
| **Skill self-patching** | ✅ Mejora skills durante uso | ❌ No existe |
| **FTS5 session search** | ✅ Full-text search + LLM summary | ❌ Solo búsqueda básica |
| **4-layer memory** | ✅ Separated concerns | ❌ 2-3 archivos simples |
| **Adaptive reasoning** | ✅ Controla thinking depth | ❌ No existe |
| **Built-in cron** | ✅ Natural language scheduling | ❌ System cron |
| **Skill conditional activation** | ✅ Fallback skills system | ❌ No existe |
| **RL training pipeline** | ✅ Atropos research | ❌ No disponible |

---

## Qué puede BRAIN aprender de Hermes

### Implementable en BRAIN:

1. **Periodic nudge** — BRAIN podría hacer memory review periódico
2. **Skill auto-creation** — después de 5+ tool calls, sugerir crear skill
3. **Memory límites estrictos** — forzar curación activa
4. **Skill patching** — en vez de rewrite completo
5. **FTS5 session search** — buscar en sesiones pasadas

### NO implementable fácilmente:

1. **RL training** — requiere research infrastructure
2. **200+ model support** — BRAIN es MiniMax-focused
3. **20+ messaging platforms** — overkill para Dani

---

*Investigador — Step 3 completado.*