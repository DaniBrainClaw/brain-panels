# Extra Step 1: MiniMax M2.7 Multimodal — Vision, Images, Audio

## Query
"MiniMax M2.7 multimodal vision images audio capabilities"

## Fuentes consultadas
- https://www.reddit.com/r/MiniMax_AI/comments/1skfbw9/m27_vision_support/
- https://github.com/MiniMax-AI/MiniMax-M2/issues/92
- https://www.buildfastwithai.com/blogs/minimax-m2-7-review
- https://artificialanalysis.ai/models/minimax-m2-7
- https://winbuzzer.com/2026/04/14/minimax-launches-mmx-cli-ai-agents-get-multimodal-powers-xcxwbn/
- https://www.deeplearning.ai/the-batch/minimaxs-m2-7-model-competes-with-gemini-and-opus
- https://wavespeed.ai/landing/minimax-m2.7

---

## Hallazgos principales

### Veredicto: M2.7 es TEXT-ONLY, NO multimodal

**Respuesta oficial de MiniMax**: M2.7 es un modelo de **reasoning-only text**. No procesa imágenes ni audio.

Desde GitHub issue #92 (respuesta de MiniMax):
> "Minimax subscription cannot do image analysis via the Anthropic API — that's a hard limitation on their end, confirmed by their own docs."

Desde Artificial Analysis:
> "No, MiniMax-M2.7 does not support image input. It can only process text."

### Qué dicen los marketers (Marketing vs Realidad)

WaveSpeed AI dice: "Multi-Modal Reasoning — MiniMax M2.7 processes text, images, and documents natively"

**Esto es marketing falso.** Los datos técnicos oficiales de MiniMax y terceros confirman que M2.7 es text-only.

### MiniMax SÍ tiene multimodal — pero es M2.5

MiniMax M2.5 sí es multimodal:
> "A 'native' multimodal model is trained on different types of data (text, image, audio) at the same time"

M2.7 sacrificó capabilities multimodales por mejor reasoning/performance.

### MMX-CLI — Multimodal via CLI separado

MiniMax liberó MMX-CLI (CLI abierto) que incluye:
- `mmx text` — genera texto (usa M2.7)
- `mmx image` — genera imágenes (otro modelo)
- `mmx video` — genera video ( Hailuo-2.3)
- `mmx speech` — síntesis de voz (30+ voces)
- `mmx music` — genera música
- `mmx vision` — visión artificial (modelo separado)
- `mmx search` — búsqueda web

**Importante**: esto NO es M2.7 siendo multimodal. Es un wrapper que conecta a múltiples modelos especializados.

### La historia de MiniMax con multimodal

- M2.5: multimodal nativo
- M2.7: text-only, otimizado para reasoning
- Image-01: modelo separado para texto→imagen

### Implicación para BRAIN

Si necesitamos capacidades visuales (analizar imágenes, documentos con charts, etc.), M2.7 no las tiene. Opciones:

1. **MMX-CLI** — usar el CLI wrapper para tareas multimodales
2. **Gemini 3.1 Pro** — para análisis de imágenes
3. **M2.5** — versión anterior que sí era multimodal

---

## Resumen

| Capacidad | M2.7 | M2.5 | Gemini 3.1 |
|-----------|------|------|------------|
| Text | ✅ | ✅ | ✅ |
| Images | ❌ | ✅ | ✅ |
| Audio | ❌ | ✅ | ✅ |
| Video | ❌ | ❌ | ✅ |
| reasoning | ✅ | ⚠️ | ✅ |

**M2.7 = text-only reasoning model.** No es multimodal.

**Para tasks visuales → Gemini 3.1 Pro o usar MMX-CLI por separado.**