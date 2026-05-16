# Step 2: MiniMax M2.7 vs GPT-4 vs Claude Comparison

## Query
"MiniMax M2.7 vs GPT-4 vs Claude comparison"

## Fuentes consultadas
- https://aithinkerlab.com/minimax-m2-7-vs-gpt4-claude-benchmarks/
- https://blog.kilo.ai/p/we-tested-minimax-m27-against-claude
- https://thomas-wiegold.com/blog/minimax-m-2-7-review-is-it-worth-the-hype/
- https://medium.com/@tentenco/minimax-m2-7-vs-claude-opus-4-7-vs-gpt-5-4-which-coding-model-actually-wins-in-2026-ff415f6d6d75

---

## Hallazgos principales

### Pricing comparison

| Model | Input $/M | Output $/M | Ratio vs M2.7 |
|-------|-----------|-----------|---------------|
| MiniMax M2.7 | $0.30 | $1.20 | baseline |
| Claude Opus 4.6 | $5.00 | $25.00 | ~17x more expensive |
| GPT-5 (estimated) | higher | higher | ~30x+ more expensive |

**Nota**: "50x cheaper" comparaba contra Opus 4.1 ($15/M input), no contra Opus 4.6 actual ($5/M).

### Real-world test (Kilo Code - 3 TypeScript codebases)

Ambos modelos encontraron los 6 bugs y 10 vulnerabilidades. Diferencias:

| Aspect | M2.7 | Claude Opus 4.6 |
|--------|------|-----------------|
| Tests escritos | 20 unit tests | 41 integration tests |
| Arquitectura | Flat, fewer files | Modular directory structure |
| Fix quality | Good, simpler | More thorough + rollback logic |
| Costo total tarea | $0.27 | $3.67 |
| Quality ratio | 90% | 100% |
| **Cost ratio** | **7%** | **100%** |

**Conclusión Kilo**: M2.7 entrega ~90% de la calidad por 7% del costo.

### Donde M2.7 supera a Claude Opus

1. **SWE-bench Verified**: 78% vs 55% — gap de 23 puntos
2. **Currency fix**: usó integer math (cents) vs floats — solución técnicamente mejor
3. **SWE-bench multilingual**: 76.5 (genuine cross-language, no solo English)
4. **Unique task solutions**: resolvió problemas que otros modelos no pudieron (89-task eval, Kilo Bench)
5. **Hallucination rate**: 34% vs 46% (Sonnet 4.6) y 50% (Gemini 3.1) — más confiable en hechos

### Donde M2.7 queda por debajo

1. **Test coverage**: 20 vs 41 tests — menos cobertura
2. **Modular architecture**: flat structure vs proper separation of concerns
3. **Rollback logic**: no maneja partial failures en multi-item orders
4. **Security fix quality**: fixes menos completos (rate limiting parcial, SSRF validation only at delivery)
5. **BridgeBench**: dropped vs M2.5 — peor en vibe-coding/natural language to code

### Verbosity trap (importantísimo)

M2.7 genera 87M tokens de output en la evaluación de Artificial Analysis vs median de 26M — **3.35x más verboso**. Esto erosiona significativamente el ahorro de per-token pricing.

ECPT (Effective Cost Per Task): Para tareas complejas de ingeniería, M2.7 puede costar más por tarea que Opus porque:
- Lee mucho más contexto por tarea (2.8M input tokens en Kilo Bench vs 1.18M de Opus en mismo PR)
- Escribe mucho más output

**No бюджетируйте por per-token pricing — modelen ECPT.**

### Speed real

- Claimed: 100 TPS
- Actual (Artificial Analysis, standard variant): **45.7 TPS** vs median 109.7 TPS — **2.4x más lento que el promedio de su tier**
- Time to first token: 2.49s vs 1.84s median
- Full attention architecture → degrades further en long context

---

## Resumen

M2.7 es mejor que Opus en:
- SWE-bench Verified (78% vs 55%)
- Cost efficiency para tareas bounded
- Multilingual engineering
- Lower hallucination rate

Opus es mejor en:
- Architecture quality y test coverage
- Thoroughness de fixes
- Speed real (no claimado)
- Complex multi-step reasoning

**Recomendación**: Usar M2.7 para coding tasks bounded y de costo-efectividad. Usar Opus para arquitectura y tareas que requieren máxima thoroughness.