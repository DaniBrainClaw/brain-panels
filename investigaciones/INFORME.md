# Investigación: Agentes AI para Empresas

**Fecha:** 2026-05-20  
**Fuente:** 15 archivos scrapeados de GitHub + web  
** Carpeta:** `investigaciones/claude-business-agents/scrape/`

---

## Resumen Ejecutivo

Encontrados **3 grandes tipos** de soluciones:

| Tipo | Qué es | Relevancia |
|------|--------|------------|
| **185 agentes especializados** | Sistema completo con plugins, skills, orchestrators | ⭐⭐⭐ Muy alto |
| **Marketing automation suite** | 14 comandos para auditar, generar copy, emails, SEO | ⭐⭐ Alto |
| **Optimización de tokens** | Guía para reducir costes 40-70% | ⭐⭐⭐ Crítico para BRAIN |

---

## 1. AGENTES ESPECIALIZADOS — wshobson/agents

**Repo:** https://github.com/wshobson/agents

### Arquitectura
- **185 agentes especializados** — domain experts (arquitectura, lenguajes, infra, QA, datos, business)
- **80 plugins** — granular, single-purpose, optimizado para mínimo token usage
- **153 agent skills** — modular knowledge packages
- **16 workflow orchestrators** — coordinación multi-agente

### Modelo de 3 tiers
| Tier | Modelo | # Agentes | Uso |
|------|--------|-----------|-----|
| Tier 1 | Opus 4.7 | 42 | Arquitectura crítica, security, code review |
| Tier 2 | User choice | 42 | Tareas complejas |
| Tier 3 | Sonnet | 51 | Soporte inteligente |
| Tier 4 | Haiku | 18 | Tareas operativas rápidas |

### Ejemplo de workflow
```
full-stack-feature "user authentication with OAuth2"
→ backend-architect → database-architect → frontend-developer 
→ test-automator → security-auditor → deployment-engineer 
→ observability-engineer
```
Coordina 7+ agentes en paralelo.

### Team presets
- `review` — code review paralelo (security, performance, architecture)
- `debug` — hypothesis-driven debugging
- `feature` — parallel feature development
- `fullstack` — app completa
- `research` — investigación
- `security` — audit completo
- `migration` — migración de código

---

## 2. MARKETING AUTOMATION — ai-marketing-claude

**Repo:** https://github.com/zubair-trabzada/ai-marketing-claude

### Comandos disponibles
```
/market audit <url>     — Full marketing audit (5 agentes en paralelo)
/market quick <url>      — 60-second snapshot
/market copy <url>      — Generate optimized copy
/market emails <topic>   — Email sequences completos
/market social <topic>    — 30-day content calendar
/market ads <url>        — Ad creatives para todas plataformas
/market funnel <url>      — Sales funnel analysis
/market competitors <url> — Competitive intelligence
/market landing <url>    — Landing page CRO analysis
/market brand <url>      — Brand voice analysis
/market seo <url>        — SEO content audit
/market report <url>      — Full report (Markdown)
```

### Scoring del marketing audit
- Content & Messaging: 25%
- Conversion Optimization: 20%
- SEO & Discoverability: 20%
- Competitive Positioning: 15%
- Brand & Trust: 10%
- Growth & Strategy: 10%

---

## 3. OPTIMIZACIÓN CLAUDE — Token Optimization Guide

**Fuente:** levelup.gitconnected.com/stop-burning-tokens

### Reglas clave

**Regla #1: Nueva conversación cada 15-20 mensajes**
```
Message 1:   500 tokens
Message 5:   ~3,000 tokens (acumulado)
Message 15:  ~15,000-25,000 tokens
Message 30:  50,000+ tokens para "fix the bug on line 42"
```
**Ahorro:** 40-70% en costes de tokens

**Regla #2: Modelo correcto para tarea correcta**
| Modelo | Coste/M tokens | Uso |
|--------|---------------|-----|
| Haiku | $1 in / $5 out | Clasificación, quick fixes, boilerplate |
| Sonnet | $3 in / $15 out | Coding tasks, multi-file logic |
| Opus | $15 in / $75 out | Arquitectura compleja, deep debugging |

**Regla #3: Contexto estructurado con XML tags**
Claude responde mejor a contexto estructurado que a contexto largo.

**Regla #4: Desactivar tools no usadas**
Cada MCP connector carga su full tool definition en cada mensaje.

**Regla #5: Phased approach para proyectos grandes**
1. Architecture (Opus)
2. Core implementation (Sonnet)
3. Module work (Sonnet, new chat)
4. Integration + review (Opus)

**Regla #6: Prompt caching**
Cache read tokens cuestan 0.1x — ahorro de hasta 90%.

**Regla #7: Batch API para trabajo no urgente**
50% descuento en todos los modelos.

---

## 4. CLAUDE PARA PEQUEÑA EMPRESA — Weekend Guide

**Fuente:** medium.com/@sebuzdugan/how-to-use-claude-to-automate-your-small-business-in-a-weekend

### Capas de implementación
1. **Cero código** — Web app, Team/Pro plans
2. **API básico** — Integraciones simples
3. **API automation** — Cuando realmente hace falta

### Lo que realmente necesita una pyme
- Menos tabs abiertos
- Menos tareas repetitivas
- Menos "Can you quickly draft this?" en Slack

### Modelos disponibles
- Claude 3 Opus — contexto largo, mejor lenguaje
- Claude 3 Sonnet — balance
- Claude 3 Haiku — rápido, barato

---

## 5. OTROS ENCONTRADOS

### VoltAgent/awesome-claude-code-subagents
**Repo:** https://github.com/VoltAgent/awesome-claude-code-subagents

**100+ subagents categorizados:**
- `voltagent-core-dev` — api-designer, backend-developer, frontend-developer, fullstack-developer
- `voltagent-lang` — typescript-pro, python-pro, golang-pro, rust-engineer, etc.
- `voltagent-infra` — azure-infra, kubernetes-specialist, terraform-engineer, security-engineer
- `voltagent-qa-sec` — accessibility-tester, security-auditor, code-reviewer, penetration-tester

### nisonco.com/claude-code-business-guide
- MCP como "USB-C for AI"
- CLAUDE.md como employee handbook
- 84% developers usan AI tools

---

## Aplicabilidad para BRAIN

### Qué podemos usar ahora

| recurso | Aplicación | Prioridad |
|---------|-----------|----------|
| wshobson/agents | Inspiración para arquitectura multi-agente | Alta |
| ai-marketing-claude | Auditar webs de Dani | Media |
| Token optimization | Reducir costes BRAIN | Alta |
| VoltAgent subagents | Extender capacidades BRAIN | Baja |

### Qué NO aplicar
- La mayoría son para Claude Code / desarrollo de software
- BRAIN es asistente personal, no coding agent
- Los marketing agents son para vender servicios, no para gestionar empresa

---

## Recomendación

**Para BRAIN como sistema multi-agente:**

1. **Optimización tokens** → Implementar regla: sesiones nuevas cada 15-20 mensajes
2. **wshobson/agents** → Estudiar su arquitectura de 185 agentes para posible implementación en BRAIN
3. **ai-marketing-claude** → Crear skill de auditoría web para Dani's businesses

**No prioritario:** Los subagents de VoltAgent son muy desarrollo-software-centric.

---

*Datos crus guardados en `scrape/001-025`*  
*Investigación: subagent `cc92f71e` — sesión nueva*