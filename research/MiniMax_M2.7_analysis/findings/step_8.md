# Step 8: Reasoning Chain Capabilities

## Query
"MiniMax M2.7 reasoning chain capabilities"

## Fuentes consultadas
- https://computertech.co/minimax-m2-7-review/
- https://www.mindstudio.ai/blog/what-is-minimax-m27-self-evolving-model
- https://artificialanalysis.ai/models/minimax-m2.7

---

## Hallazgos principales

### M2.7 es un reasoning model nativo

No es un modelo separado — tiene chain-of-thought integrado que activa automáticamente en tareas complejas.

### Características del reasoning

1. **Extended thinking / chain-of-thought** — trabaja problemas complejos antes de responder
2. **No se puede ajustar la profundidad** — todas las tareas (incluso simples) reciben el tratamiento completo
3. **Genera 87M tokens de output** en la evaluación de Intelligence Index — 4x el promedio
4. **La verbosidad es inevitable** — no hay modo "fast" con reasoning reducido

### Comportamiento en coding — deep reading antes de escribir

Kilo.ai highlight: M2.7 "reads extensively before writing" — pulling in adjacent files, analyzing dependencies, tracing call chains antes de tocar código.

Esto llevó a:
- 47% pass rate en Kilo Bench (2do lugar entre 89 tareas)
- Resolvió problemas que otros modelos no pudieron
- **Pero**: causa timeouts en workflows sensibles al tiempo

### Speed / reasoning tradeoff

| Aspect | M2.7 | Promedio reasoning models |
|--------|------|--------------------------|
| Speed | 44 TPS | ~110 TPS |
| TTFT | alto | bajo |
| Reasoning depth | máximo siempre | ajustable |

M2.7 no tiene "fast reasoning mode" — si necesitas velocidad, usa el highspeed variant.

### Self-evolving training — cómo mejora su reasoning

El reasoning de M2.7 viene de un proceso de RL donde:
1. Un agente autónomo observa training runs
2. Detecta failures, diagnosis, aplica fixes
3. Recibe feedback basado en si sus intervenciones mejoran el modelo
4. El agente se mejora con el tiempo — meta-learning

Esto es lo que MiniMax claims como "self-evolution" — el modelo participa en mejorar su propio training.

### Benchmark scores relevantes para reasoning

| Benchmark | Score | Notes |
|-----------|-------|-------|
| GPQA Diamond | 87.4% | Graduate-level scientific reasoning |
| HLE | 28.1% | Humanity's Last Exam — tareas muy duras |
| SciCode | 47% | Scientific computing |
| TerminalBench Hard | 39.4% | Agentic terminal tasks |

---

## Resumen reasoning

✅ **Excelente para problemas complejos que requieren análisis profundo**
✅ **Lee y analiza exhaustivamente antes de responder**
✅ **Resuelve problemas que otros modelos no pueden**
⚠️ **No hay control sobre profundidad de reasoning**
⚠️ **Muy lento (44 TPS vs 110 TPS promedio)**
⚠️ **Verboso — 4x más output que el promedio**
⚠️ **Puede timeout en workflows de baja latencia**

**Best for**: coding tasks complejos, debugging, análisis profundo
**Cuidado con**: tasks rápidos, respuestas cortas, workflows time-sensitive