# MiniMax M2.7 Analysis — Executive Index

## Research completed: 10 queries, 20+ sources

---

## 1. ¿Dónde es EXCELENTE MiniMax M2.7?

### Coding / Software Engineering
- **SWE-Pro**: 56.22% — igual que GPT-5.3-Codex, cerca de Claude Opus 4.6 (57%)
- **SWE-bench Verified**: 78% — **MEJOR que Opus 4.6 (55%)** — 23 puntos de ventaja
- **SWE Multilingual**: 76.5 — genuino cross-language engineering
- **VIBE-Pro**: 55.6% — end-to-end project delivery, no solo isolated patches
- **Terminal Bench 2**: 57.0% — ahead of GPT-5.2 (54%)
- **Kilo Bench**: 47% pass rate — 2nd among 89 tasks, solved problems others couldn't

### Agentic Workflows
- **GDPval-AA**: ELO 1495 — **HIGHEST among open-source models**
- **MMClaw**: 62.7% — close to Sonnet 4.6
- **Skill adherence**: 97% on 40 complex tasks (>2000 tokens each)
- **Agent Teams**: native multi-agent collaboration with stable role identity

### Professional Office
- Excel/PowerPoint/Word con high-fidelity multi-turn editing
- Complex document processing
- 97% skill adherence en tareas profesionales

### Cost Efficiency
- **$175** para Intelligence Index vs $547 (GLM-5) y $371 (Kimi K2.5) — **más barato a inteligencia equivalente**
- $0.30/M input, $1.20/M output — 8-17x más barato que Claude/GPT
- **Pareto frontier** en Intelligence vs Cost chart

### Hallucination Rate
- **34%** — mejor que Sonnet 4.6 (46%) y Gemini 3.1 (50%)
- Improved from M2.5 (-40) to +1 on AA-Omniscience

### ML Research
- **MLE-Bench Lite**: 66.6% medal rate — **tied with Gemini 3.1**

---

## 2. ¿Dónde necesita apoyo de otro modelo?

### Creative Writing
- **Regressed vs M2.5**: LMSys rank 79 → 108 (peor)
- No es general purpose — es "test maxer" en STEM
- Problemas con simple prompts outside coding domains
- **→ Usar Claude Sonnet o GPT-5.4 para writing**

### General Knowledge
- Lower que modelos más pequeños (Gemma 4 26B, Qwen3.5 34B)
- Muy focalizado en coding/STEM
- **→ Para knowledge general, usar otro modelo**

### Long Context (>200K tokens)
- **200K max** vs Gemini 3.1 Pro 1M
- Full attention = slow on long ctx
- **→ Usar Gemini 3.1 Flash para contexts enormes**

### Speed-Critical Tasks
- **44 TPS real** vs claimado 100 TPS
- 2.4x más lento que el promedio de su tier
- Timeouts en time-sensitive workflows
- **→ Usar Gemini 2.5 Flash o GPT-5.4 Mini para velocidad**

### Multimodal Tasks
- Text only — no images, audio, video
- **→ Usar Gemini 3.1 Pro para multimodal**

### Simple Tasks (overkill)
- Reasoning always on — no hay "fast mode"
- 4x más verbose que el promedio
- Costo innecesario para tasks triviales
- **→ Usar modelo más pequeño para tasks simples**

---

## 3. ¿Cuándo cambiar a fallback?

| Situación | Fallback sugerido |
|-----------|-----------------|
| Creative writing, storytelling | Claude Sonnet 4.6 o GPT-5.4 |
| Context >200K tokens | Gemini 3.1 Flash |
| Speed crítico | Gemini 2.5 Flash |
| Multimodal (imágenes, audio) | Gemini 3.1 Pro |
| General knowledge fuera de STEM | GPT-5.4 o Claude |
| Tasks muy simples (<100 tokens) | Gemini 3.1 Flash-Lite |
| Voice/video input | Gemini 3.1 Pro |

---

## 4. Puntos Fuertes vs Competencia

### M2.7 vs Claude Opus 4.6

| Aspect | M2.7 | Opus | Winner |
|--------|------|------|--------|
| SWE-Pro | 56.22% | ~57% | Tie |
| SWE-bench Verified | **78%** | 55% | **M2.7** |
| Cost | $0.30/$1.20 | $5/$25 | **M2.7** (17x) |
| Test coverage | 20 tests | 41 tests | Opus |
| Architecture | flat | modular | Opus |
| Speed | slow | faster | Opus |

**Verdict**: M2.7 para coding tasks donde importan resultados; Opus para arquitectura y thoroughness.

### M2.7 vs GPT-5.4

| Aspect | M2.7 | GPT-5.4 | Winner |
|--------|------|---------|--------|
| SWE-Pro | 56.22% | similar | Tie |
| Intelligence Index | **#1** | below | **M2.7** |
| Cost | **$0.30** | higher | **M2.7** |
| Context | 200K | 128K | **M2.7** |
| Multimodal | ❌ | ✅ | GPT-5.4 |

**Verdict**: M2.7 es mejor en cost-efficiency y context para coding.

### M2.7 vs Gemini 3.1 Pro

| Aspect | M2.7 | Gemini 3.1 Pro | Winner |
|--------|------|----------------|--------|
| Coding | **mucho mejor** | worse | **M2.7** |
| Cost | **$0.30** | $2.50 | **M2.7** |
| Context | 200K | **1M** | Gemini |
| Multimodal | ❌ | ✅ | Gemini |
| Speed | slow | faster | Gemini |

**Verdict**: M2.7 para coding, Gemini para context largo y multimodal.

---

## 5. Recomendaciones para BRAIN

### Mantener M2.7 como primario para:
- Coding tasks (bug fixing, feature development, code review)
- Agentic workflows (loops, tool use, multi-step tasks)
- Office productivity (Excel, Word, PPT manipulation)
- Tareas de costo-sensibles con contexto <=200K tokens
- Spanish conversations (soportado)

### Cambiar a Gemini 3.1 Flash cuando:
- Contexto >200K tokens
- Speed crítico (TTFT bajo)
- Tasks multimodales
- Tasks simples donde M2.7 es overkill

### Cambiar a Claude cuando:
- Creative writing o storytelling
- Arquitectura de software (módulo complejo)
- Tasks que requieren máxima thoroughness
- General knowledge fuera de STEM

---

## Archivos del estudio

```
Research/MiniMax_M2.7_analysis/
├── sources.md          — todas las URLs consultadas
├── index.md            — este resumen ejecutivo
├── SUMMARY_DANI.md     — versión en español para Dani
└── findings/
    ├── step_1.md   — Benchmark capabilities
    ├── step_2.md   — vs GPT-4/Claude comparison
    ├── step_3.md   — Language understanding strengths
    ├── step_4.md   — Code generation performance
    ├── step_5.md   — Context window limitations
    ├── step_6.md   — Pricing efficiency
    ├── step_7.md   — Creative writing (ALERTA)
    ├── step_8.md   — Reasoning chain capabilities
    ├── step_9.md   — vs Gemini comparison
    └── step_10.md  — Multilingual support
```