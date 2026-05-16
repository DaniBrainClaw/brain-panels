# GitHub + BRAIN Integration — Query 3: GitHub Pages Use Cases Beyond Static Websites

**Fecha:** 2026-05-16
**Query:** "github pages use cases beyond static websites"
**Resultados:** 20 found

---

## Fuentes

1. **GitHub Pages: Advanced Uses** — paulserban.eu (tutorial completo)
2. **What is GitHub Pages** — docs.github.com (oficial)
3. **GitHub Pages examples collection** — github.com/collections/github-pages-examples

---

## GitHub Pages — Qué es

Servicio de hosting estático de GitHub:
- Toma archivos HTML/CSS/JS directamente del repo
- Opcionalmente los procesa (Jekyll, etc.)
- Publica como website
- SSL gratis, CDN global

### Tipos de sitios:

| Tipo | URL default | Repo |
|------|-------------|------|
| **User/Org** | `https://<owner>.github.io` | `<owner>.github.io` |
| **Project** | `https://<owner>.github.io/<repo>` | cualquier repo |

---

## Use Cases Más Allá de Static Websites

### 1. Blogs con Jekyll
```bash
# Jekyll integrado nativamente en GitHub Pages
# Solo necesitas escribir en Markdown
# GitHub hace build y deploy automático
```

**Setup mínimo:**
```
_repo/
  _config.yml
  index.md
  posts/
    2026-05-16-first-post.md
```

### 2. Documentation Sites
```bash
# Docusaurus, MkDocs, VuePress
# Generan sitio searchable desde Markdown
```

**Ejemplo Docusaurus config:**
```javascript
module.exports = {
  url: 'https://DaniBrainClaw.github.io',
  baseUrl: '/my-docs/',
  organizationName: 'DaniBrainClaw',
  projectName: 'my-docs',
};
```

### 3. SPAs (Single Page Applications)
- React, Vue, JavaScript vanilla
- Client-side rendering
- GitHub Actions para build automático

**SPA Routing fix (404.html):**
```html
<script>
const redirectToIndex = () => {
  const path = location.pathname;
  if (path !== '/' && !path.endsWith('.html')) {
    location.replace('/index.html');
  }
};
redirectToIndex();
</script>
```

O usar hash routing: `HashRouter` en vez de `BrowserRouter`.

### 4. Portfolios y CVs online
- Gratis y versionado
- Deploy con push a main

### 5. Landing pages para negocios
- Carrd.co + GitHub Pages hosting
- Dominio custom gratis

### 6. API Documentation interactiva
- Swagger UI
- Stoplight
- Redoc

### 7. Dashboards (client-side)
- Datos de APIs externas
- Gráficos con Chart.js / D3.js
- Sin backend necesario

---

## GitHub Actions para GitHub Pages

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: npm install
        
      - name: Build
        run: npm run build
        
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

---

## Jekyll — Built-in en GitHub Pages

### _config.yml mínimo:
```yaml
title: Mi Blog
description: Blog de Dani
theme: minima
collections:
  posts:
    output: true
```

### Crear post:
```markdown
---
title: "Primer post"
date: 2026-05-16
---

Hola mundo desde GitHub Pages!
```

---

## Límites Importantes

| Aspecto | Límite |
|---------|--------|
| **Storage** | 1 GB soft, 5 GB hard |
| **Bandwidth** | 100 GB/month (soft) |
| **Deploys** | 10/hour (soft) |
| **Private repos** | Solo GitHub Pro/Team/Enterprise |

---

## Dominio Custom

GitHub Pages soporta dominio custom:
1. Settings → Pages → Custom domain
2. Configurar DNS en tu proveedor
3. SSL automático con Let's Encrypt

### DNS para apex domain (ej: dani.es):
```
@  A  185.199.108.153
@  A  185.199.109.153
@  A  185.199.110.153
@  A  185.199.111.153
www  CNAME  DaniBrainClaw.github.io
```

### DNS para subdomain (ej: blog.dani.es):
```
blog  CNAME  DaniBrainClaw.github.io
```

---

## Para BRAIN + Dani: Aplicaciones Prácticas

| Aplicación | Uso |
|------------|-----|
| **Portfolio** | mf3.es → redirige a GitHub Pages con portfolio |
| **Landing pages** | Páginas de venta para servicios de Dani |
| **Blog de negocio** | Blog técnico para Green Axis, etc. |
| **Dashboard público** | Stats de BRAIN visibles online |
| **Documentation** | Docs de habilidades y configuración |
| **CV online** | Portfolio profesional |

---

## Ejemplo: Dashboard Público con BRAIN

### Setup:
1. Crear repo `DaniBrainClaw.github.io`
2. BRAIN genera dashboard HTML con datos públicos
3. GitHub Actions hace deploy automáticamente

### GitHub Actions:
```yaml
name: Update Dashboard
on:
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate dashboard
        run: |
          curl -s http://localhost:18789/api/stats > public/data.json
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

---

## Alternativas a GitHub Pages (si creces)

| Plataforma | Ventaja | Precio |
|-----------|---------|--------|
| **Netlify** | Deploy automático, Forms, Functions | Gratis + paid |
| **Vercel** | Edge functions, Optimized images | Gratis + paid |
| **Cloudflare Pages** | Edge network, Free tier generous | Gratis + paid |

---

*Investigador — Query 3 completada.*