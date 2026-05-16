# Step 6: Pricing Efficiency

## Query
"MiniMax M2.7 pricing efficiency"

## Fuentes consultadas
- https://artificialanalysis.ai/articles/minimax-m2-7-everything-you-need-to-know
- https://pricepertoken.com/pricing-page/model/minimax-minimax-m2.7
- https://openrouter.ai/minimax/minimax-m2.7
- https://wavespeed.ai/blog/posts/minimax-m2-7-self-evolving-agent-model-features-benchmarks-2026/

---

## Hallazgos principales

### Pricing oficial

| Tipo | Costo por 1M tokens |
|------|---------------------|
| Input | $0.30 |
| Output | $1.20 |
| Cache (input) | $0.06 |
| Blended (3:1 ratio) | ~$0.45-$0.55 |

### Costo por inteligencia — el dato clave

M2.7 cuesta **$175** para correr el Artificial Analysis Intelligence Index completo.

Comparación a inteligencia equivalente:
- **GLM-5 (Reasoning)**: $547 (3x más)
- **Kimi K2.5 (Reasoning)**: $371 (2x más)
- **Gemini 3 Flash Preview**: $278 (1.5x más)
- **M2.7**: $175 ← el más barato

**M2.7 está en la Pareto frontier** del chart Intelligence vs Cost.

### Costo vs Claude Opus 4.6

| Aspecto | M2.7 | Claude Opus 4.6 |
|---------|------|-----------------|
| Input por 1M | $0.30 | $5.00 (~17x) |
| Output por 1M | $1.20 | $25.00 (~21x) |
| Costo Intelligence Index | $175 | significativamente más |

**No es 50x** (ese número era contra Opus 4.1). Contra Opus 4.6 es ~17x.

### Verbosity tax — la trampa

M2.7 usó **87M output tokens** para correr la evaluación de Artificial Analysis.
- M2.5 usó ~56M (55% menos)
- Median para modelos similares: ~26M
- **M2.7 es 3.35x más verboso que el promedio**

Esto significa que el costo real por tarea puede ser MUCHO mayor que el per-token rate sugiere.

**ECPT (Effective Cost Per Task)**: 
- Kilo Bench: M2.7 consumió 2.8M input tokens por trial
- Opus consumió 1.18M en el mismo PR
- **M2.7 lee 2.4x más contexto por tarea**

### Plan de tokens de MiniMax

| Plan | Precio | Requests/5h | Features |
|------|--------|-------------|----------|
| Starter | $10/mes | 1,500 | M2.7 solo |
| Plus | $20/mes | 4,500 | + speech, image |
| Max | $50/mes | 15,000 | + video, music |
| Plus-Highspeed | $40/mes | 4,500 | highspeed variant |
| Max-Highspeed | $80/mes | 15,000 | highspeed variant |
| Ultra-Highspeed | $150/mes | 30,000 | todo incluido |

### Mejores prácticas para costo

1. **Usar cache** — input cacheado a $0.06/M (vs $0.30/M)
2. **Prompt engineering claro** — reduce tokens desperdiciados
3. **System prompts cortos** — M2.7 puede terminate early cerca del límite
4. **Phased processing** — dividir tareas largas en ventanas
5. **Evitar verbose outputs** — especificar formato explícito

---

## Resumen pricing

✅ **Excellent cost efficiency** — mejor inteligencia/dólar de su tier
✅ **Cache automático** reduce costos en workloads repetitivos
⚠️ **Verbosity trap** — 3.35x más output que median
⚠️ **ECPT puede ser mayor que Opus** para tareas muy complejas
⚠️ **No es 50x más barato** — eso era contra Opus 4.1, no 4.6

**Best for**: tareas de volumen alto, coding tasks bounded, agent workloads
**Cuidado con**: tareas largas, contexts extremos, workflows que requieren outputs detallados