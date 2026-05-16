# Step 5: Context Window Limitations

## Query
"MiniMax M2.7 context window limitations"

## Fuentes consultadas
- https://platform.minimax.io/docs/token-plan/best-practices
- https://huggingface.co/nvidia/MiniMax-M2.7-NVFP4/discussions/2
- https://artificialanalysis.ai/models/minimax-m2-7

---

## Hallazgos principales

### Context window specs
- **Total**: 204,800 tokens (input + output combined)
- **Max output**: 131,072 tokens
- **Recommended usable**: ~200K tokens (input + output juntos)
- **Official recommendation**: keep total input+output within 200k tokens

### Full attention = performance degradation
**Importante**: M2.7 usa full attention across its entire context window. Esto significa:
- Performance degrades significativamente en long-context workloads
- Lo hace más lento que modelos con attention más eficiente
- Communities en llama.cpp han identificado esto: "Minimax applied full attention, thus it's so slow in long ctx"

### NVIDIA version context issue
 Algunos usuarios reportan que la versión NVFP4 de M2.7 solo alcanza ~88K context en local (vs los 196K esperados). Posible problema de量化 o configuración.

### Best practices oficiales de MiniMax

1. **Phased processing**: usar múltiples ventanas en lugar de un solo context muy largo
2. **State tracking**: M2.7 tiene good state tracking — puede mantener coherence en long sequences
3. **Maximize context**: hacer full use del context window antes de continuar a siguiente ventana
4. **Compression tools**: si usas tools como Claude Code que soportan context compression, controlar el system prompt size

### Warning crítico de documentación oficial

> "When using tools that support context compression (such as Claude Code), it's recommended to control the number of tokens in system prompts. M2.7 may terminate tasks early when approaching context capacity thresholds."

Esto es relevante para nuestro uso en OpenClaw — el system prompt de BRAIN es largo (~4K tokens), lo que reduce el context efectivo disponible.

### Recommended system prompt para tasks largos

```
This is a very lengthy task. It's recommended that you make full use of the complete output context to handle it—keep the total input and output tokens within 200k tokens. Make full use of the context window length to complete the task thoroughly and avoid exhausting tokens.
```

---

## Limitaciones documentadas

1. **No images/audio/video** — solo text input
2. **Full attention = slow** en contexts largos
3. **Approaching limit = early termination** — possible cut-off de tareas
4. **Long context = degraded performance**
5. **No cache para output tokens** — cache solo para input

---

## Comparación con competencia

| Model | Context Window | Attention |
|-------|---------------|-----------|
| M2.7 | 205K | Full (slow on long) |
| Claude Opus 4.6 | 200K | Más eficiente |
| GPT-5.2 | 128K | — |
| Gemini 3.1 Pro | 2M | — |

M2.7 tiene más context que GPT-5.2 pero mucho menos que Gemini 3.1 Pro.

---

## Implicaciones para BRAIN

1. **System prompt largo = context perdido** — BRAIN tiene ~4K de system prompt + memory
2. **Tasks largos de coding** pueden requerir phased approach (dividir en ventanas)
3. **Long conversations** eventually degraded — usar compression o restart después de ~150K tokens
4. **Para tareas que requieren máximo context** → cambiar a Gemini 3.1 Flash o similar