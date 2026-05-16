# Step 1: MiniMax M2.7 Model Capabilities Benchmark

## Query
"MiniMax M2.7 model capabilities benchmark"

## Fuentes consultadas
1. https://www.minimax.io/models/text/m27 — Página oficial del modelo
2. https://wavespeed.ai/blog/posts/minimax-m2-7-self-evolving-agent-model-features-benchmarks-2026/ — Análisis completo en WaveSpeed
3. https://openrouter.ai/minimax/minimax-m2.7/benchmarks — Benchmarks en OpenRouter
4. https://www.minimax.io/news/minimax-m27-en — Announcement oficial
5. https://huggingface.co/MiniMaxAI/MiniMax-M2.7 — HuggingFace page
6. https://artificialanalysis.ai/models/minimax-m2-7 — Artificial Analysis

---

## Hallazgos principales

### Specs básicas
- **Parámetros activados**: 10B (el más pequeño en Tier-1)
- **Contexto**: ~200K tokens
- **Velocidad**: 100 tokens/segundo
- **Input cost**: $0.30/M tokens
- **Output cost**: $1.20/M tokens
- **Cache blended**: $0.06/M tokens (con cache automático)

### Benchmark results

| Benchmark | M2.7 | Competitor |
|-----------|------|------------|
| SWE-Pro | 56.22% | ~57% (Claude Opus 4.6) |
| SWE-bench Verified | 78% | 55% (Claude Opus 4.6) |
| VIBE-Pro (end-to-end) | 55.6% | — |
| Terminal Bench 2 | 57.0% | — |
| GDPval-AA (Office) | ELO 1495 | Highest among open-source |
| MM Claw (Agent eval) | 62.7% | ~Sonnet 4.6 level |
| MLE-Bench Lite | 66.6% | Tied with Gemini 3.1 |
| Skill Adherence (40 tasks >2000 tokens) | 97% | — |

### SWE-bench Verified: 78% vs 55%
M2.7 outperforma significativamente a Claude Opus 4.6 en SWE-bench Verified (78% vs 55%). Esto es notable porque SWE-bench Verified es un benchmark de coding más moderno y completo que SWE-Pro.

### Agentic capabilities
- 97% skill adherence en 40 tareas complejas (>2000 tokens cada una)
- Near-Sonnet 4.6 en MMClaw (agente evaluation)
- Auto-mejora: 100+ iteraciones de optimización de scaffold durante training

### Software Engineering
- End-to-end project delivery (no solo isolated patches)
- Log analysis y debugging
- Code security review
- Machine learning pipeline development

### Office Suite
- Excel operations y formula generation
- PowerPoint creation y editing
- Word document manipulation
- Multi-turn modification support

---

## Notas
- M2.7 es 3x más rápido que Claude Opus (100 TPS vs ~33 TPS)
- 50x más barato que Opus en input ($0.30 vs $15 per million)
- 60x más barato en output ($1.20 vs $75 per million)
- Modelo con solo 10B parámetros iguala/rivaliza con modelos de 100B+