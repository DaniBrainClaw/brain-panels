# GitHub + BRAIN Integration — Query 5: GitHub API Programmatic File Storage Free Tier Limits

**Fecha:** 2026-05-16
**Query:** "github api programmatic file storage free tier limits"
**Resultados:** ~20 found

---

## Fuentes

1. **Repository limits** — docs.github.com (oficial)
2. **About storage and bandwidth usage** — docs.github.com (LFS)
3. **Rate limits for the REST API** — docs.github.com (oficial)

---

## Límites de Repository (GitHub Free)

| Recurso | Límite |
|---------|--------|
| **Repositorios** | Sin límite público, ilimitado privado (con Pro) |
| **Tamaño archivo** | 100 MB (soft limit), 10 GB recomendado |
| **Tamaño repo** | 100 GB (límite rígido) |
| **Ancho de banda** | 100 GB/month (soft), 1 TB (hard) |

### Nota importante:
- Free tier: repos públicos ilimitados, 1 private repo (con restricciones)
- Pro ($4/month): repos privados ilimitados

---

## Git LFS (Large File Storage)

### Free tier:

| Plan | Bandwidth | Storage |
|------|-----------|---------|
| **GitHub Free** | 10 GiB | 10 GiB |
| **GitHub Pro** | 10 GiB | 10 GiB |
| **GitHub Team** | 250 GiB | 250 GiB |
| **GitHub Enterprise** | 250 GiB | 250 GiB |

### Qué es Git LFS:
- Para archivos grandes (imágenes, videos, datasets)
- Lo guarda como pointer en Git, archivo real en LFS
- Descarga bajo demanda

### Cómo funciona:
```
# En vez de guardar 500MB en git, guarda solo pointer
# El archivo real está en LFS storage

git lfs track "*.psd"
git add large-file.psd
git commit -m "Add large file"
git push
```

### Límites de Git LFS:
- **Storage:** 10 GB gratis (facturado por hora)
- **Bandwidth:** 10 GB/month gratis
- **Si excedes storage (sin pago):** No puedes hacer push de nuevos archivos LFS
- **Si excedes bandwidth:** LFS deshabilitado hasta el siguiente mes

---

## Rate Limits — GitHub REST API

### Sin autenticar:
- **60 requests/hour**
- Solo datos públicos

### Con personal access token (autenticado):
- **5,000 requests/hour**
- Acceso a repos privados

### Con GitHub App (Enterprise Cloud):
- **15,000 requests/hour**

### Para Git LFS (separado):
- **3,000 requests/minute** (autenticado)
- **300 requests/minute** (sin autenticar)

### Search API (más restrictivo):
- **30 requests/minute**
- 10 requests/minute sin autenticar

---

## GraphQL API Limits

### Rate limit:
- **5,000 points per hour** (autenticado)
- Basado en complejidad de queries, no número de requests

### Límite de ejecución:
- **30 segundos** por query
- **10 minutos** para mutations

### Límite de resultado:
- **100 items** por request (paginar con `first`, `last`)

---

## Storage para Archivos Grandes — Alternativas

### Si Git LFS se queda corto:

| Opción | Storage | Costo | Notas |
|--------|---------|-------|-------|
| **GitHub Gists** | 100 MB por gist | Gratis | Bueno para snippets |
| **GitHub Releases** | 2 GB por release | Gratis | Para binaries |
| **Google Drive** | 15 GB gratis | Gratis | Para archivos grandes |
| **AWS S3** | 5 GB gratis | ~$0.023/GB | Para producción |
| **Backblaze B2** | 10 GB gratis | $0.006/GB | Más barato que S3 |

---

## Guía para BRAIN: Cuánto storage necesita

### Archivos de config (预期用):
- AGENTS.md, SOUL.md, USER.md, MEMORY.md → ~1 MB total
- Scripts y skills → ~10 MB
- **Total estimado:** < 50 MB

### Conclusión:
- **GitHub Free es suficiente** para backup de config de BRAIN
- No necesita Git LFS para archivos de texto
- Si necesita guardar datasets o archivos grandes, usar alternativa

---

## Límites por Plan — Resumen

| Recurso | Free | Pro | Team |
|---------|------|-----|------|
| Repos públicos | Ilimitados | Ilimitados | Ilimitados |
| Repos privados | 1 | Ilimitados | Ilimitados |
| Colaboradores | Ilimitados | Ilimitados | Ilimitados |
| Git LFS Storage | 10 GB | 10 GB | 250 GB |
| Git LFS Bandwidth | 10 GB/mo | 10 GB/mo | 250 GB/mo |
| API requests | 60/hr (no auth) / 5,000/hr (auth) | Same | Same |

---

## Recomendación para Dani

### Para uso normal de BRAIN:
- **GitHub Free es suficiente**
- Repo privado `brain-config-backup` con ~50 MB de config
- 5,000 API requests/hour es más que suficiente para automatización

### Para casos especiales:
- Si necesitas guardar archivos > 100 MB → usar Git LFS
- Si necesitas más de 10 GB storage → pagar Pro ($4/month) o usar S3
- Si necesitas más API calls → implementar cacheo o usar GraphQL

---

*Investigador — Query 5 completada. Investigación finalizada.*