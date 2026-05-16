# MiniMax M2.7 — Resumen para Dani

**Fecha**: 2026-05-15
**Investigación**: 10 queries, 20+ fuentes consultadas

---

## ¿Qué es MiniMax M2.7?

Es nuestro modelo primario — el que usa BRAIN por defecto. Es un modelo de razonamiento lanzado en marzo 2026 por MiniMax (empresa china de IA). Su característica principal: **es el modelo #1 en inteligencia al menor costo** del mercado.

**Costes**: $0.30/M tokens input, $1.20/M output. De los más baratos para su nivel.

---

## ✅ DÓNDE DESTACA (y es mejor que la competencia)

### Coding / Ingeniería de Software
- **78% en SWE-bench Verified** — outperforms Claude Opus 4.6 (55%) por 23 puntos
- **56.22% en SWE-Pro** — igual que GPT-5.3, cerca de Opus
- **97% skill adherence** en 40 tareas complejas
- Encuentra bugs que otros modelos no pueden (Kilo Bench)
- multilingual coding (76.5% en SWE Multilingual) — funciona bien en español

### Agente y workflows
- **GDPval-AA ELO 1495** — el más alto entre modelos open-source
- **MMClaw 62.7%** — casi al nivel de Sonnet 4.6
- Lee archivos, analiza dependencias, traza call chains antes de escribir código
- Excelente para tareas de múltiples pasos con tools

### Costo-beneficio
- **$175** para correr el test completo de inteligencia
- Competidores con inteligencia similar: GLM-5 ($547), Kimi K2.5 ($371)
- **8-17x más barato que Claude Opus o GPT-5**

### Factual accuracy
- **34% hallucination rate** — mejor que Sonnet 4.6 (46%) y Gemini 3.1 (50%)
- Mejoró mucho desde M2.5 (-40 en omniscience → +1)

---

## ⚠️ DÓNDE NECESITA RESPALDO DE OTRO MODELO

### Creative Writing / Escritura creativa
**ALERTA**: M2.7 es PEOR que su predecesor M2.5 en escritura creativa.
- Regressed desde rank 79 → 108 en LMSys (más bajo = peor)
- Es un modelo "test maxer" enfocado en STEM, no general purpose
- Para historias, blogs, writing → usar Claude Sonnet 4.6

### Contextos muy largos (>200K tokens)
- Su máximo es 204,800 tokens (input+output)
- Usa full attention — se vuelve lento en contexts largos
- **Para documentos enormes → Gemini 3.1 Flash** (1M context)

### Speed crítico
- **44 tokens/segundo real** (no 100 como dicen)
- 2.4x más lento que el promedio de su categoría
- Para tasks que necesitan respuesta inmediata → Gemini 2.5 Flash

### Multimodal (imágenes, audio, video)
- **Solo texto** — no procesa imágenes ni audio
- **Para multimodal → Gemini 3.1 Pro**

### Tareas simples (overkill)
- Siempre tiene razonamiento activo — no hay modo "rápido"
- 4x más verbose que el promedio — gasta tokens innecesarios
- Para tasks triviales → Gemini 3.1 Flash-Lite

---

## 📊 ¿CUÁNDO USAR QUÉ?

| Situación | Modelo |
|-----------|--------|
| Coding (bug fixing, features, review) | **M2.7** ✅ |
| Tareas de agente / tools / multi-step | **M2.7** ✅ |
| Office (Excel, Word, PPT) | **M2.7** ✅ |
| Conversación general en español | **M2.7** ✅ |
| Writing creativo / storytelling | **Claude Sonnet 4.6** |
| Documentos >200K tokens | **Gemini 3.1 Flash** |
| Speed crítico | **Gemini 2.5 Flash** |
| Imágenes / Audio / Video | **Gemini 3.1 Pro** |
| Conocimiento general fuera de STEM | **Claude o GPT-5.4** |

---

## 🎯 RESUMEN EJECUTIVO

**MiniMax M2.7 es excelente para:**
- Coding profesional (mejor que Opus en SWE-bench Verified)
- Agentes y workflows complejos
- Office productivity
- Costo-sensibilidad (es el más barato por inteligencia)

**No es bueno para:**
- Escritura creativa (regressed vs M2.5)
- Contextos muy largos (se ralentiza)
- Speed (es lento)
- Multimodal (solo texto)

**En BRAIN lo usamos bien** — es la elección correcta para coding y agente. Para writing o contexts largos, ya tenemos fallback configurado.

---

*Investigación completada. Archivos en `/data/.openclaw/agents/investigador/workspace/Research/MiniMax_M2.7_analysis/`*