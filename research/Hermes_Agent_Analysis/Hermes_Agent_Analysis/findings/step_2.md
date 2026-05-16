# Hermes Agent Analysis — Step 2: Funcionalidades Principales

**Fecha:** 2026-05-16

---

## Fuentes

1. **Self-Improving AI Guide** — hermes-agent.ai/blog/self-improving-ai-guide
2. **Inside Hermes Agent: How a Self-Improving AI Agent Actually Works** — mranand.substack.com
3. **Documentación oficial** — hermes-agent.nousresearch.com/docs/

---

## Sistema de Memory — 4 Layers

Hermes usa 4 capas de memory, cada una con un propósito específico:

### Layer 1: Prompt Memory (Always-On)
- Se inyecta al inicio de **cada sesión**
- 2 archivos: `MEMORY.md` + `USER.md`
- Límite total: 3,575 chars (curated, no grows infinitamente)
- El agente lo gestiona via `memory` tool

### Layer 2: Session Archive
- Cada sesión se guarda en SQLite con FTS5 (full-text search)
- El agente puede buscar sesiones pasadas
- Results pasan por LLM summarization antes de entrar al contexto
- Solo lo relevante entra en el contexto actual

### Layer 3: Skills (Procedural Memory)
- El agente crea skills desde experiencia
- Se guardan en `~/.hermes/skills/`
- Formato: [agentskills.io](https://agentskills.io/specification) open standard
- Portable across agents compatibles

### Layer 4: Project Context Files
- AGENTS.md, context files por proyecto
- Se cargan cuando el proyecto está activo

---

## Self-Improvement Loop — Cómo Funciona

### El Loop Completo:

```
1. Understand task + inspect environment
2. Act with tools (no guessing)
3. Verify result (tests, browser checks, command output)
4. Save durable facts as memory
5. Convert reusable procedures into skills
6. Load those skills automatically next time
```

### Periodic Nudge (El Trigger):
- Cada ciertos intervalos, el agente recibe un "nudge" interno
- El nudge pregunta: "¿Hay algo worth persisting?"
- El agente escanea actividad reciente
- Si cruza threshold → escribe a MEMORY.md

### Triggers para crear skills:
- 5+ tool calls en una tarea
- Recovery from error
- User correction
- Non-obvious workflow that worked

### Skills se actualizan solos:
- El agente usa `patch` (no full rewrite)
- Solo cambia lo que mejoró
- Más token-efficient, menos risk de romper

---

## Skill Management — 6 Acciones

```python
skill_manage(action="create")   # Nueva skill
skill_manage(action="patch")    # Actualizar parte (default)
skill_manage(action="edit")    # Reescribir completo
skill_manage(action="delete")  # Borrar
skill_manage(action="write_file")   # Archivos adicionales
skill_manage(action="remove_file")  # Borrar archivos
```

### Progressive Disclosure para Skills:
```
Level 0: skills_list() → [{name, description, category}, ...]  (~3k tokens)
Level 1: skill_view(name) → Full content + metadata
Level 2: skill_view(name, path) → Specific reference file
```

---

## Session Search — FTS5 + LLM Summarization

### Cómo funciona:
1. Sesiones se guardan en SQLite archive
2. FTS5 index para búsqueda full-text
3. Agent busca cuando necesita contexto pasado
4. Results → LLM summarization → solo lo relevante entra

### Diferencia con prompt memory:
| Aspecto | Prompt Memory | Session Search |
|---------|---------------|----------------|
| Carga | Always-on, cada sesión | On-demand, cuando agent decide |
| Contenido | Permanente, para todas las future sessions | Específico, para topic actual |
| Size | Fijo (3,575 chars) | Variable |

---

## Adaptive Reasoning Effort

Hermes puede controlar **cuánto razonamiento gastar** en cada tarea:

- Tarea pequeña (formato) → poco reasoning
- Tarea compleja (debug multi-repo) → reasoning profundo

No todas las tareas consumen el mismo presupuesto de tokens.

---

## Crons — Scheduled Automations

```bash
# Built-in cron scheduler
# Natural language scheduling
hermes cron "daily report at 9am"
hermes cron "backup every night at 3am"
hermes cron "weekly audit every Monday"
```

### Características:
- Delivery a cualquier platform (Telegram, Discord, etc.)
- No necesita intervención
- Natural language scheduling

---

## Subagents — Parallel Workstreams

```bash
# Spawn isolated subagents
hermes delegate "research this topic"
```

### Características:
- Aislados entre sí
- Parallel workstreams
- Zero-context-cost turns (programmatic tool calling)

---

## Voice Mode

- Real-time voice interaction
- CLI, Telegram, Discord, Discord VC
- Requiere: ffmpeg + voice dependencies

---

## Gateway — Messaging Platform

Un solo gateway process conecta a 20+ plataformas:
```
CLI │ Telegram │ Discord │ Slack │ WhatsApp │ Signal │ 
Matrix │ Mattermost │ Email │ SMS │ DingTalk │ Feishu │ 
WeCom │ Weixin │ QQ Bot │ Yuanbao │ BlueBubbles │ 
Home Assistant │ Microsoft Teams │ Google Chat
```

---

## Tool System — 70+ Tools

### Herramientas built-in:
- Terminal (local, Docker, SSH, Singularity, Modal, Daytona)
- Web search, browse, extract
- Vision (image analysis)
- Image generation
- TTS
- File operations
- Code execution

### Toolset system:
- Organizes tools logically
- Conditional activation (fallback skills)
- MCP integration para tools externos

---

## Migration desde OpenClaw

```bash
hermes claw migrate
```

Hermes tiene migración directa para usuarios de OpenClaw.

---

## Comparison con BRAIN/OpenClaw

| Feature | BRAIN (OpenClaw) | Hermes |
|---------|------------------|--------|
| Memory layers | MEMORY.md, USER.md, daily files | 4 layers (prompt, session, skills, project) |
| Session search | Basic | FTS5 + LLM summarization |
| Skill creation | Skills system | Autonomous skill creation after complex tasks |
| Skill updates | Manual | Self-patching during use |
| Periodic nudge | No | Yes — automatic memory curation |
| Adaptive reasoning | No | Yes — controls thinking depth |
| Cron | Via system cron | Built-in natural language cron |
| Subagents | Subagents | Isolated + parallel workstreams |
| Voice mode | Depends on config | Built-in |
| Messaging gateway | OpenClaw channels | 20+ platforms unified |
| Model-agnostic | MiniMax M2.7 | 200+ models via OpenRouter |

---

*Investigador — Step 2 completado.*