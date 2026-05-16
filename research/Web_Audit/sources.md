# SOURCES — Web Audit Dani Businesses

**Fecha:** 2026-05-16
**Investigador:** Investigador
**Total URLs auditadas:** 7 dominios + ~40 páginas internas

---

## Webs Auditadas

### 1. mf3.es — Mediterranean Fusion
**URLs analizadas:**
- https://mf3.es/
- https://mf3.es/mobiliario/andreu-world/

**Búsqueda:** `site:mf3.es`
**Resultados:** 2 páginas indexadas

---

### 2. liv-ing.com — Living
**URLs analizadas:**
- https://liv-ing.com/
- https://liv-ing.com/cookies.html
- https://liv-ing.com/hazteunliving/

**Búsqueda:** `site:liv-ing.com`
**Resultados:** 2 páginas indexadas

---

### 3. dindonliving.com — Din Don Living
**URLs analizadas:**
- https://www.dindonliving.com/
- https://www.dindonliving.com/seleccion-de-sillones/
- https://www.dindonliving.com/seleccion-de-muebles/

**Búsqueda:** `site:dindonliving.com`
**Resultados:** 16 páginas indexadas

---

### 4. estudiovirtual.es — Estudio Virtual
**URLs analizadas:**
- http://www.estudiovirtual.es/
- http://www.estudiovirtual.es/infografias/

**Búsqueda:** `site:estudiovirtual.es`
**Resultados:** 4 páginas indexadas

---

### 5. gp3.es — Green Path
**URLs analizadas:**
- https://gp3.es/
- https://gp3.es/energia/
- https://gp3.es/construccion/
- https://gp3.es/reforma/

**Búsqueda:** `site:gp3.es`
**Resultados:** 0 páginas (direct fetch)

---

### 6. terracottavalladolid.com — Terracotta
**URLs analizadas:**
- https://terracottavalladolid.com/
- https://terracottavalladolid.com/carta/
- https://terracottavalladolid.com/eventos/

**Búsqueda:** `site:terracottavalladolid.com`
**Resultados:** 4 páginas indexadas

---

### 7. greenaxis.es — Green Axis
**URLs analizadas:**
- https://greenaxis.es/

**Búsqueda:** `site:greenaxis.es`
**Resultados:** 0 páginas (direct fetch)

---

### 8. fusionhouse.es — Fusion House
**Estado:** ❌ DOWN (reported as not accessible)

---

## Herramientas de Auditoría

### Brave Search
- Query: `site:[dominio]`
- Resultados por query: 20
- Filters: None

### Jina Reader (fetch limpio)
- URL format: `https://r.jina.ai/[URL]`
- maxChars: 5000-8000
- extractMode: markdown

### Análisis Manual
- Estructura del sitio (navegación, páginas)
- Contenido (propuesta de valor, CTAs, testo)
- SEO básico (SSL, meta, título)
- Trust signals (testimonials, certificaciones)
- UX/UI (diseño, velocidad, mobile)

---

## Hallazgos Principales

### Dominios sin SSL
- estudiovirtual.es — HTTP only (CRÍTICO)

### Multi-dominio
- mf3.es + mediterraneanfusion.es (confusión)

### Stats con valores "0"
- gp3.es — 0 Metros Construidos, 0 Reformas
- estudiovirtual.es — 0 Infografías, 0 M2 Modelados

### Sin dirección física
- greenaxis.es — solo WhatsApp

### Sin horarios
- terracottavalladolid.com — sin horarios de apertura

---

## Archivos Generados

```
Research/Web_Audit/
├── SUMMARY_DANI.md    (~150 líneas)
├── INDEX.md           (~180 líneas)
├── sources.md         (~100 líneas)
└── findings/
    ├── web_mf3.md           (~130 líneas)
    ├── web_living.md        (~140 líneas)
    ├── web_dindon.md        (~160 líneas)
    ├── web_estudiovirtual.md (~150 líneas)
    ├── web_greenpath.md     (~150 líneas)
    ├── web_terracotta.md   (~140 líneas)
    └── web_greenaxis.md    (~150 líneas)
```

---

*Investigador — completado.*