# Hermes Agent Analysis — Step 1: ¿Qué es Hermes?

**Fecha:** 2026-05-16
**Repo:** github.com/NousResearch/hermes-agent
**Stars:** 153K (152K en contexto original)
**Última versión:** v0.14.0 (Mayo 2026)

---

## Fuentes

1. **Hermes Agent GitHub** — github.com/NousResearch/hermes-agent
2. **Documentación oficial** — hermes-agent.nousresearch.com/docs/
3. **README.md** — raw.githubusercontent.com/NousResearch/hermes-agent/main/README.md

---

## Qué es Hermes Agent

**Hermes Agent** es un AI agentself-improving construido por **Nous Research** (el laboratorio detrás de Hermes, Nomos y Psyche models).

### Tagline:
> *"The agent that grows with you"*

### Características defining:

| Feature | Descripción |
|---------|-------------|
| **Self-improving** | Aprende de experiencias, crea skills, mejora durante uso |
| **Closed learning loop** | Memory con nudges periódicos, skill creation autonomous |
| **Cross-session recall** | FTS5 session search con LLM summarization |
| **User modeling** | Honcho dialectic user modeling |
| **Runs anywhere** | Local, Docker, SSH, Singularity, Modal, Daytona, Vercel |
| **20+ platforms** | CLI, Telegram, Discord, Slack, WhatsApp, Signal, etc. |

---

## Stack Técnico

### Modelos soportados:
- **Nous Portal** (propio)
- **OpenRouter** (200+ modelos)
- **NovitaAI**
- **NVIDIA NIM** (Nemotron)
- **Xiaomi MiMo**
- **z.ai/GLM**
- **Kimi/Moonshot**
- **MiniMax** (¡el mismo que usa BRAIN!)
- **Hugging Face**
- **OpenAI**
- **Tu propio endpoint**

### Plataformas de deployment:
```
Local │ Docker │ SSH │ Singularity │ Modal │ Daytona │ Vercel Sandbox
```

### Plataformas de messaging:
```
CLI │ Telegram │ Discord │ Slack │ WhatsApp │ Signal │ Matrix │ 
Mattermost │ Email │ SMS │ DingTalk │ Feishu │ WeCom │ 
Weixin │ QQ Bot │ Yuanbao │ BlueBubbles │ Home Assistant │ 
Microsoft Teams │ Google Chat
```

---

## Arquitectura de Memory

### Dos archivos de memory:

| File | Purpose | Char Limit |
|------|---------|------------|
| **MEMORY.md** | Agent's personal notes | 2,200 chars (~800 tokens) |
| **USER.md** | User profile | 1,375 chars (~500 tokens) |

### Características del sistema de memory:
- Persiste across sessions
- Curated y bounded (límites estrictos)
- Agent manages its own memory via `memory` tool
- Frozen snapshot pattern (capturado al inicio de sesión)

### Memory Tool Actions:
- **add** — Add new entry
- **replace** — Replace via substring matching
- **remove** — Remove via substring matching
- **No read** — memory se inyecta automáticamente en system prompt

---

## Skills System

### SKILL.md format:
```yaml
---
name: my-skill
description: Brief description
version: 1.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [python, automation]
    category: devops
---
# Skill Title

## When to Use
Trigger conditions

## Procedure
1. Step one
2. Step two

## Pitfalls
Known failure modes

## Verification
How to confirm
```

### Progressive disclosure (token-efficient):
```
Level 0: skills_list() → [{name, description, category}, ...]  (~3k tokens)
Level 1: skill_view(name) → Full content + metadata
Level 2: skill_view(name, path) → Specific reference file
```

### Conditional activation (fallback skills):
```yaml
fallback_for_toolsets: [web]    # Show ONLY when web toolsets unavailable
requires_toolsets: [terminal]   # Show ONLY when terminal available
```

---

## Personality System (SOUL.md)

### SOUL.md vs AGENTS.md:
- **SOUL.md** → identity, tone, style, communication defaults
- **AGENTS.md** → project architecture, coding conventions, repo-specific workflows

### Built-in personalities:
```
helpful │ concise │ technical │ creative │ teacher │ 
kawaii │ catgirl │ pirate │ shakespeare │ surfer │ 
noir │ uwu │ philosopher │ hype
```

### Personalities son session-level overlays sobre SOUL.md durable.

---

## Voice Mode

- Real-time voice interaction
- CLI, Telegram, Discord, Discord VC
- Requiere ffmpeg y dependencias de voz

---

## Tools & Toolsets

- **70+ built-in tools**
- Toolset system para organizar
- MCP integration para conectar servers externos
- Terminal backends: local, Docker, SSH, Singularity, Modal, Daytona

---

## Cron Scheduling

- Built-in cron scheduler
- Delivery a cualquier platform
- Natural language scheduling
- Daily reports, nightly backups, weekly audits

---

## Migration desde OpenClaw

```bash
hermes claw migrate  # Migrate from OpenClaw
```

**Esto es relevante para BRAIN** — Hermes tiene migración directa desde OpenClaw.

---

## Instalación

```bash
# Linux, macOS, WSL2, Termux
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Windows (early beta, PowerShell)
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

---

## Comparación Inicial con BRAIN

| Aspecto | BRAIN (OpenClaw) | Hermes |
|---------|------------------|--------|
| **Modelo** | MiniMax M2.7 | Cualquiera |
| **Memory** | MEMORY.md, USER.md, daily | MEMORY.md, USER.md (similar) |
| **Skills** | Skills system | Skills system + Hub + progressive disclosure |
| **Identity** | SOUL.md | SOUL.md |
| **Platforms** | Depends on config | 20+ platforms |
| **Self-improving** | No explicit | Yes — built-in learning loop |
| **Cron** | Cron jobs | Built-in cron scheduler |
| **Subagents** | Subagents | Isolated subagents + parallel workstreams |

---

*Investigador — Step 1 completado. Fuente: código fuente y documentación oficial.*