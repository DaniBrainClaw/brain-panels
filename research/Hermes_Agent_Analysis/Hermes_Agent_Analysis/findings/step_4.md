# Hermes Agent Analysis — Step 4: Comparison con BRAIN

**Fecha:** 2026-05-16

---

## Overview

BRAIN es un agente basado en OpenClaw con modelo MiniMax M2.7. Hermes es un agente auto-mejorante de Nous Research con soporte para 200+ modelos.

### Basic Info

| Aspecto | BRAIN | Hermes |
|---------|-------|--------|
| **Framework** | OpenClaw | Hermes (Nous Research) |
| **Modelo** | MiniMax M2.7 | 200+ modelos (OpenRouter, OpenAI, etc.) |
| **Stars GitHub** | N/A | 153K |
| **Self-improving** | No (manual) | Yes (built-in loop) |
| **Target user** | Dani (VPS, personal) | General, developers |

---

## Memory System

### BRAIN Memory
```
~/.openclaw/
├── MEMORY.md           # Long-term curated memory
├── USER.md             # User profile
├── memory/
│   └── YYYY-MM-DD.md   # Daily logs
└── AGENTS.md, SOUL.md, TOOLS.md
```

**Características:**
- 3 archivos principales + daily logs
- Escritura manual o automática
- Sin límites estrictos de chars
- Sin búsqueda full-text

### Hermes Memory (4 Layers)
```
~/.hermes/
├── memories/
│   ├── MEMORY.md       # 2,200 chars max
│   └── USER.md         # 1,375 chars max
├── sessions/          # SQLite + FTS5
├── skills/            # Procedural memory
└── project context    # AGENTS.md files
```

**Características:**
- Límites estrictos (3,575 chars total)
- Búsqueda FTS5 en sesiones
- LLM summarization para retrieval
- Periodic nudge automático

### Comparación

| Aspecto | BRAIN | Hermes | Ventaja |
|---------|-------|--------|---------|
| Memory layers | 2-3 | 4 | Hermes |
| Límites activos | No | Yes (curation) | Hermes |
| Session search | Basic | FTS5 + LLM | Hermes |
| Periodic nudge | No | Yes | Hermes |
| Auto-curation | No | Yes | Hermes |

---

## Skills System

### BRAIN Skills
- Skills directory con SKILL.md files
- Cargadas al inicio o bajo demanda
- No hay progressive disclosure
- Actualización manual

### Hermes Skills
- Progressive disclosure (3 levels)
- Conditional activation (fallback skills)
- Self-patching durante uso
- Autonomy creation después de tareas complejas
- Open standard (agentskills.io)

### Comparación

| Aspecto | BRAIN | Hermes | Ventaja |
|---------|-------|--------|---------|
| Skill loading | All at once | Progressive | Hermes |
| Auto-creation | No | Yes | Hermes |
| Self-patching | No | Yes | Hermes |
| Fallback skills | No | Yes | Hermes |
| Open standard | No | Yes | Hermes |

---

## Self-Improvement Loop

### BRAIN
- Mejora manual (Dani le dice qué corregir)
- Memory update después de errores
- Skills creados manualmente
- Sin loop automático

### Hermes
```
Understand → Act → Verify → Save Memory → Create Skills → Load Next Time
                              ↑                              ↓
                              └──────── NUDGE (periodic) ────┘
```

**Features:**
- Periodic nudge (cada ciertos intervals)
- Triggers: 5+ tools, errors, corrections, non-obvious workflows
- Skill creation after complex tasks
- Self-patching skills during use

### Comparación

| Aspecto | BRAIN | Hermes | Ventaja |
|---------|-------|--------|---------|
| Automatic loop | No | Yes | Hermes |
| Periodic nudge | No | Yes | Hermes |
| Trigger-based creation | No | Yes | Hermes |
| Skill self-improvement | No | Yes | Hermes |
| Verification requirement | Manual | Built-in | Hermes |

---

## Messaging Platforms

### BRAIN
- OpenClaw channels (Telegram, etc.)
- Depends on configuration

### Hermes
```
CLI │ Telegram │ Discord │ Slack │ WhatsApp │ Signal │ 
Matrix │ Mattermost │ Email │ SMS │ DingTalk │ Feishu │ 
WeCom │ Weixin │ QQ Bot │ Yuanbao │ BlueBubbles │ 
Home Assistant │ Microsoft Teams │ Google Chat
```
20+ platforms, un solo gateway.

### Comparación

| Aspecto | BRAIN | Hermes | Ventaja |
|---------|-------|--------|---------|
| Platform count | ~5-10 | 20+ | Hermes |
| Gateway unification | Partial | Full | Hermes |

---

## Deployment Options

### BRAIN
- VPS (current setup)
- Local
- Depends on OpenClaw

### Hermes
```
Local │ Docker │ SSH │ Singularity │ Modal │ Daytona │ Vercel
```
- Daytona/Modal: serverless persistence (hibernation)
- $5 VPS hasta GPU cluster

---

## Cron Scheduling

### BRAIN
- System cron jobs
- Requiere setup manual
- Bash scripts

### Hermes
- Built-in cron scheduler
- Natural language scheduling
- Delivery a cualquier platform

```bash
hermes cron "daily report at 9am"
hermes cron "backup every night at 3am"
```

---

## Subagents

### BRAIN
- Subagents capability
- Used for spawning isolated runs

### Hermes
- Spawn isolated subagents
- Parallel workstreams
- Programmatic tool calling via `execute_code`
- Zero-context-cost turns

---

## Voice Mode

### BRAIN
- Depende de config
- No built-in (requiere OpenClaw config)

### Hermes
- Real-time voice interaction
- CLI, Telegram, Discord, Discord VC
- Requiere ffmpeg + voice deps

---

## Model Support

### BRAIN
- MiniMax M2.7 (principal)
- OpenClaw model flexibility

### Hermes
- 200+ models vía OpenRouter
- Nous Portal, OpenAI, NVIDIA NIM, Xiaomi MiMo, Kimi, MiniMax, Hugging Face
- Switch con `hermes model` — no code changes

---

## Identidad / Personality

### BRAIN
- SOUL.md para personality
- AGENTS.md para instructions

### Hermes
- SOUL.md como primary identity (slot #1 in system prompt)
- `/personality` para session-level overlays
- Built-in personalities: helpful, concise, technical, creative, teacher, kawaii, catgirl, pirate, shakespeare, surfer, noir, uwu, philosopher, hype

---

## Lo que Hermes tiene que BRAIN NO

1. **Self-improving loop automático**
2. **Periodic nudge** para memory curation
3. **Autonomous skill creation**
4. **Skill self-patching during use**
5. **FTS5 session search + LLM summarization**
6. **4-layer memory architecture**
7. **Adaptive reasoning effort**
8. **Built-in natural language cron**
9. **Fallback skills system**
10. **20+ messaging platforms unificados**
11. **Progressive disclosure para skills**
12. **RL training pipeline (Atropos)**
13. **200+ model support**
14. **Serverless persistence (Daytona/Modal)**

---

## Lo que BRAIN tiene que Hermes NO (o menos)

1. **Simplicidad** — más fácil de setup para caso simple
2. **OpenClaw ecosystem** — skills, integrations existentes
3. **Investigador agent** — BRAIN tiene agente de investigación dedicado
4. **Dani's existing setup** — ya configurado y funcionando

---

## Migration Path

Hermes tiene migración directa desde OpenClaw:
```bash
hermes claw migrate
```

Esto significa que Dani podría migrar de BRAIN a Hermes si quisiera, aunque perdería:
- Su configuración actual
- Sus daily memory files
- Sus skills personalizados
- El agente Investigador

---

## Veredicto: ¿Debería Dani Migrar a Hermes?

### NO, por ahora — razones:

1. **Ya tiene BRAIN funcionando** —迁移 significa perder contexto
2. **El agente Investigador** — BRAIN tiene algo que Hermes no: agente de investigación dedicado
3. **Setup personalizado** — todo lo que tiene Dani está en su VPS
4. **MiniMax es suficiente** — no necesita 200+ modelos

### SÍ, solo si:

1. Quiere el self-improving loop automático
2. Necesita 20+ plataformas de messaging
3. Quiere explorar skill creation automático
4. Está dispuesto a migrar y reconfigurar

---

## Recomendación: Implementar en BRAIN

En vez de migrar, podemos **implementar features de Hermes en BRAIN**:

### High Priority (implementable):
1. **Memory curation activa** — limitar MEMORY.md a X chars
2. **Periodic self-review** — BRAIN revisa su memory semanalmente
3. **Skill creation trigger** — después de 5+ tool calls, sugerir skill
4. **FTS5 session search** — buscar en sesiones pasadas (complejo)
5. **Natural language cron** — crear wrapper para scheduling

### Medium Priority:
6. **Fallback skills** — implementar system de fallback skills
7. **Verification requirement** — antes de decir "listo", verificar

### Low Priority (no implementable fácilmente):
- RL training pipeline
- 200+ model support
- Serverless persistence
- 20+ platform gateway

---

*Investigador — Step 4 completado.*