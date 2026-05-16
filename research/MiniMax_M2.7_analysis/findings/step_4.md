# Step 4: Code Generation Performance

## Query
"MiniMax M2.7 code generation performance"

## Fuentes consultadas
- https://kilo.ai/models/minimax-m27
- https://minimaxm27.net/
- https://www.minimax.io/news/minimax-m27-en

---

## Hallazgos principales

### Coding Benchmarks — Resumen completo

| Benchmark | M2.7 | Competitors |
|-----------|------|-------------|
| SWE-Pro | 56.22% | ~57% Opus 4.6, 55.6% GPT-5.3 |
| SWE-bench Verified | 78% | 55% Opus 4.6 |
| VIBE-Pro (repo-level) | 55.6% | ~Opus 4.6 level |
| Terminal Bench 2 | 57.0% | 59.1% Claude Code, 54.0% GPT-5.2 |
| PinchBench | 71.2% | — |
| GDPval-AA (Office) | ELO 1495 | 1633 Claude Code, 1462 GPT-5.2 |

### Unique strengths

1. **End-to-end project delivery** (VIBE-Pro 55.6%) — no solo isolated patches
2. **Multilingual coding**: SWE Multilingual 76.5 — genuine cross-language engineering
3. **Bug hunting**: encuentra bugs que otros modelos no encuentran (89-task Kilo Bench)
4. **Security audit**: encuentra las 10 vulnerabilidades planted como Opus

### Real-world test (Kilo Code - 3 TypeScript codebases)

| Metric | M2.7 | Claude Opus 4.6 |
|--------|------|-----------------|
| Bugs encontrados | 6/6 | 6/6 |
| Vulnerabilidades encontradas | 10/10 | 10/10 |
| Tests escritos | 20 (unit) | 41 (integration) |
| Costo por tarea | $0.27 | $3.67 |
| Quality ratio | 90% | 100% |

**M2.7 tuvo fix técnicamente mejor para currency bug** (integer math vs floats).

### Donde Opus gana en code generation

1. **Test coverage**: 41 integration tests vs 20 unit tests
2. **Architecture**: modular directory structure vs flat
3. **Rollback logic**: maneja partial failures
4. **Security fixes**: más completos (rate limiting por endpoint vs single)

### Coding tool compatibility
- Claude Code ✅
- Cursor ✅
- Cline ✅
- Codex CLI ✅
- OpenCode ✅
- Roo Code ✅
- Kilo Code ✅
- Droid ✅
- TRAE ✅
- Grok CLI ✅

### Speed
- Standard: 45.7 TPS (2.4x más lento que el promedio de su tier)
- Highspeed: claimado 100 TPS (no verificado independientemente)

### Context window for coding
- 204,800 tokens total (input + output)
- Recommended: mantener input+output dentro de 200K
- Full attention architecture → degrada en contexts largos

---

## Resumen

M2.7 es **excelente para coding** por costo-beneficio:
- Encuentra todos los bugs que Opus
- Fixes técnicamente correctos
- 90% de la calidad por 7% del costo

**No es ideal para**:
- Proyectos que requieren arquitectura modular (usar Opus)
- Tasks que necesitan muchos tests de integración (usar Opus)
- Vibe-coding / natural language to code (BridgeBench regressed vs M2.5)