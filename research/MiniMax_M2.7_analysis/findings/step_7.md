# Step 7: Creative Writing Abilities

## Query
"MiniMax M2.7 creative writing abilities"

## Fuentes consultadas
- https://www.reddit.com/r/Anthropic/comments/1sjkcw1/is_minimax_27_as_good_as_sonnet_46_in_english/
- https://huggingface.co/MiniMaxAI/MiniMax-M2.7/discussions/17
- https://www.reddit.com/r/LocalLLaMA/comments/1pwyw36/minimaxaiminimaxm21_seems_to_be_the_strongest/

---

## Hallazgos principales — ALERTA IMPORTANTE

### M2.7 es un modelo "test maxer", NO general purpose

Desde HuggingFace discussion #17:
> "This LLM is a test maxer, not a general purpose AI model... It scores lower on broad knowledge tests, including my own, than much smaller general purpose AI models like Gemma 4 26b-a4b, and even Qwen3.5 34b-a3b."

### Regresión vs M2.5 en creative writing

En LMSys Arena (donde LOWER rank = mejor):
- **M2.5**: creative writing rank ~79
- **M2.7**: creative writing rank ~108 ← **REGRESIÓN significativa**
- Math: 60 → 91 (también empeoró)

Esto significa que M2.7 es PEOR que M2.5 en creative writing.

### Lo que los usuarios reportan

1. **Creative writing**: M2.7 no es tan bueno como Sonnet 4.6 para english long-form writing
2. **General knowledge**: muy bajo para su tamaño
3. **Endless thinking loops**: para prompts simples fuera de sus dominios overfit
4. **Hallucination generator**: fuera de STEM/coding, entra en bucles de pensamiento y alucina

### Lo que MiniMax dice sobre creative writing

La página oficial menciona "identity preservation and emotional intelligence" para aplicaciones de entretenimiento/interactive, pero NO claims específicos de creative writing como fortaleza.

### GDPval-AA — pero no es creative writing

GDPval-AA mide "office productivity tasks" (Excel, PowerPoint, Word), no creative writing.

---

## Resumen honesto

⚠️ **M2.7 NO es bueno para creative writing comparado con su competencia**

Fortalezas:
- Coding/engineering
- STEM/math
- Agentic workflows
- Office productivity

Debilidades:
- Creative writing ← no es su enfoque
- General knowledge ← bajo para su tier
- Long-form writing ← regressed vs M2.5
- Simple prompts outside STEM ← puede entrar en loops

**Si necesitas creative writing de alta calidad → usa Claude Sonnet 4.6 o GPT-5.4**