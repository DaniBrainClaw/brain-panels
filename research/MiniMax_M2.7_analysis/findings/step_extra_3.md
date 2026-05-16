# Extra Step 3: MiniMax M2.7 Coding Plan, Agents, Workflow

## Query
"MiniMax M2.7 coding plan agents workflow non-API"

## Fuentes consultadas
- https://platform.minimax.io/docs/guides/text-ai-coding-tools
- https://medium.com/data-science-in-your-pocket/minimax-m2-7-best-agentic-ai-llm-is-here-07e00857b29b
- https://www.analyticsvidhya.com/blog/2026/04/minimax-m2-7-goes-open-weight-to-let-you-run-agents-locally/
- https://developer.nvidia.com/blog/minimax-m2-7-advances-scalable-agentic-workflows-on-nvidia-platforms-for-complex-ai-applications/
- https://www.minimax.io/models/text/m27

---

## Hallazgos principales

### M2.7 Coding Plan de MiniMax

MiniMax ofrece un "Coding Plan" que NO es la API. Es un plan específico para coding con estas características:

- **Model name para Codex**: `codex-MiniMax-M2.7`
- **Optimizado para**: Claude Code, Cursor, Zed, VS Code, OpenCode
- **Compatible con**: Claude Code Extension for VS Code

**Integration**: Se configura via `~/.claude/settings.json` apuntando a `api.minimax.io/anthropic` con API key de MiniMax.

### Agentes que usan M2.7 nativamente

M2.7 está integrado en múltiples coding agents:

1. **Claude Code** — configuración directa documentada por MiniMax
2. **OpenCode** — M2.7 es preloaded built-in
3. **Cursor** — via API
4. **Kilo Code** — testing head-to-head con otros modelos
5. **Codex CLI** — recomendado usar `codex-MiniMax-M2.7`
6. **TokenRing Coder** — soporte oficial

### Agent Teams — Multi-agent collaboration

M2.7 soporta Agent Teams, donde múltiples roles trabajan juntos:
- Uno escribe código
- Otro hace review
- Otro testa y debug

Roles con identidad estable y decisión autónoma. No es prompting — está built-in.

### Terminal Bench 2 — System-level comprehension

M2.7 scored 57.0% en Terminal Bench 2. Esto demuestra:
- Deep understanding de operational logic
- No solo code generation
- Comprende sistemas complejos (logs, metrics, deployment timelines, database state)

### Production debugging capability

Ejemplo descrito en docs: M2.7 puede correlacionar:
- Logs + metrics + deployment timelines
- Database state + missing migrations
- Error patterns + system behavior

Y sugiere fixes priorizados (ej: apply non-blocking changes before deeper fixes).

**Resultado**: recovery time < 3 minutos en producción.

### Open-weight availability

M2.7 weights están disponibles en:
- HuggingFace: `MiniMaxAI/MiniMax-M2.7`
- ModelScope: `MiniMax/MiniMax-M2.7`
- NVIDIA NIM: endpoint dedicado

### Deployment options

1. **SGLang** — recommended por MiniMax
2. **vLLM** — alternative popular
3. **Transformers** — HuggingFace
4. **Local** — Ollama (2 días gratis M2.5)
5. **Cloud** — Together AI, OpenRouter, NVIDIA NIM

### vLLM con tool call parser

```bash
vllm serve MiniMaxAI/MiniMax-M2.7 \
  --tensor-parallel-size 4 \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2
```

### Skill adherence — 97% en 40 complex skills

Cada skill > 2000 tokens. M2.7 mantiene 97% adherence.

Esto es relevante para BRAIN porque significa que puede seguir instrucciones complejas de workflow.

### Agentic performance en números

- **MMClaw**: 62.7% (close to Sonnet 4.6)
- **GDPval-AA ELO**: 1495 (highest among open-source)
- **Skill adherence**: 97% on 40 complex tasks
- **Agentic Index**: 62.1 (alto para agentic workflows)

### Para BRAIN — cómo usar M2.7 como coding agent

El modelo está optimizado para:
1. **Multi-step tool use** — puede invocar tools sequentially
2. **Memory** — mantiene contexto across long workflows
3. **Self-correction** — analiza failure y modifica approach
4. **Code + system understanding** — no solo syntax, también operational logic

**Recomendación**: Para tareas de coding en BRAIN, usar M2.7 como agent (no solo chat). Configurar Claude Code o similar con M2.7 como backend.

---

## Resumen

M2.7 tiene un ecosystem robusto de coding tools:
- Coding Plan dedicado
- Integración nativa con Claude Code, OpenCode, Cursor, etc.
- Agent Teams para multi-role collaboration
- 97% skill adherence en tareas complejas
- Open-weight para local deployment

Para BRAIN: M2.7 es ideal como coding agent backend.