# Dossier ejecutivo corregido — mediterraneanfusion.es

> **🚨 VERSIÓN VIGENTE: v56, 2026-07-22 16:04.** Sustituye y RETRACTA la recomendación v51 de aplicar un redirect 301 wildcard. **No ejecutar un wildcard ni dejar expirar el dominio con la evidencia actual.**

## TL;DR

`mediterraneanfusion.es` no es solo un dominio histórico con URLs rotas: conserva un catálogo vivo. La auditoría v53 encontró **23/36 páginas de marca con contenido real**, mientras sus equivalentes en `mf3.es/{marca}/` devuelven 404. La comprobación independiente v54 en Wayback confirma que **20/23 (87,0 %) de esas páginas vivas ya tenían un 200 histórico**: 16 aparecen en capturas de 2024 y 4 en 2022.

Por tanto, el wildcard propuesto en v51 habría enviado páginas vivas a destinos inexistentes. La autoridad SEO exacta sigue siendo desconocida — Wayback prueba existencia histórica, no tráfico, backlinks ni PageRank —, pero el riesgo ya es suficiente para descartar la acción masiva.

**Recomendación vigente: B'' — migración selectiva y dividida por intención.** Mantener el dominio mientras se decide qué marcas siguen siendo estratégicas. El inventario exacto v56 corrige v55: hay **1.877 productos únicos** y **2.055 URLs únicas** anunciadas (2.058 entradas brutas). El **80,3 %** de los productos son iluminación, asientos, mesas o decoración: su intención comercial encaja mejor con el WooCommerce de `dindonliving.com` que con la página editorial/B2B `mf3.es/mobiliario/`. Por tanto, no debe preseleccionarse `mf3.es` como destino universal: catálogo transaccional → evaluar DinDon; páginas editoriales/servicios → evaluar MF3. Crear primero destinos equivalentes y solo después aplicar 301 individuales.

## Evidencia actual

| Auditoría | Resultado | Implicación |
|---|---:|---|
| v49 — persistencia | 14/16 paths de servicio seguían 404 | El redirect actual solo cubre la home; no hay consolidación global. |
| v50 — Wayback dominio | 509 URLs históricas con 200; 302 `/product/`, 42 `/product-category/` | El dominio tuvo un catálogo amplio; no puede tratarse como cascarón vacío. |
| v53 — GET actual | 23/36 páginas de marca vivas; 0/36 migradas a mf3.es; 9/36 404 en ambos | El catálogo sigue activo y no tiene destinos equivalentes en mf3.es. |
| v54 — Wayback páginas vivas | 20/23 (87,0 %) con 200 histórico exacto | La mayoría tiene existencia histórica independiente; no redirigir a ciegas. |
| v55 — sitemap con UA | 2.058 entradas anunciadas; muestra 474/474 respondió 200 en ese momento | El alcance real es de miles de URLs, no 23 páginas aisladas. |
| v56 — deduplicación + intención | 2.055 URLs únicas; 1.877 productos; 1.507/1.877 (80,3 %) son iluminación/asientos/mesas/decoración | El destino natural del catálogo puede ser DinDon, no MF3; migración dividida por intención. |

### Proxy histórico v54

- **20/23 páginas vivas** tienen registro histórico 200 exacto en Wayback.
- Distribución de la URL histórica colapsada: **16 en 2024 y 4 en 2022**.
- Tamaño de respuesta archivada: mediana **40.806 B**, rango **30.882–60.145 B**, total **852.931 B**.
- Tres páginas hoy vivas no aparecen en esa consulta colapsada: `/mobalco/`, `/mobitec/`, `/alivar/`; requieren validación manual, no eliminación automática.
- Límite metodológico: estos datos prueban vida histórica y contenido, **no autoridad SEO ni tráfico**. Para eso hacen falta GSC o un índice de backlinks.

Archivo de evidencia: `Research/L7/data/l7_v54_brand_wayback_proxy_2026-07-22.json`.

## Arquitectura descubierta en v56

- **2.058 entradas brutas → 2.055 URLs únicas** tras deduplicar `/shop/`, `/product/lampara-colgante-frame/` y `/product/aplique-wheel/`.
- **1.877 productos únicos**, no 1.880 como resumía v55.
- **59 categorías de producto** (excluyendo `uncategorized`) que normalizan a **56 marcas/categorías distintas**.
- **49/56 (87,5 %) categorías normalizadas** tienen además una página editorial dedicada dentro del dominio antiguo: la migración es un grafo de categoría + página + productos, no una lista plana.
- Mezcla por slug: iluminación 696 (37,1 %), asientos 402 (21,4 %), decoración 205 (10,9 %) y mesas 204 (10,9 %). Juntas: **1.507/1.877 = 80,3 %**.
- **Implicación:** esos cuatro bloques son retail de mobiliario/iluminación y encajan semánticamente con DinDon Living. MF3 encaja con arquitectura, reformas, cocinas y páginas editoriales de servicio. La futura migración debe separar ambos destinos.

Evidencia reproducible: `Research/L7/scripts/l7_v56_sitemap_structure.py`, `Research/L7/data/l7_v55_sitemap_inventory_2026-07-22.json` y `Research/L7/data/l7_v56_sitemap_structure_2026-07-22.json`.

## Opciones corregidas

| Opción | Acción | Riesgo | Veredicto |
|---|---|---|---|
| **A — Mantener como está** | Conservar ambos dominios sin cambios inmediatos | Canibalización y mantenimiento duplicado, pero evita destruir URLs vivas | **Seguro como pausa**, no como solución final |
| **B'' — Migración selectiva dividida** ⭐ | Catálogo transaccional con equivalente real → evaluar `dindonliving.com`; páginas editoriales/servicios → evaluar `mf3.es`; 301 solo tras crear y validar el destino | Trabajo editorial/técnico; requiere mapa, GSC y QA | **Recomendada** |
| **C — Retirada selectiva** | Marcas obsoletas → destino de categoría realmente equivalente; si no existe, 404/410 controlado | Puede perder señales de URLs antiguas, pero evita soft-404 hacia home | Válida para catálogo sin valor comercial |
| **D — Wildcard o expiración** | Redirección masiva o pérdida del dominio | Puede romper 23 páginas vivas y sus señales históricas | **DESCARTADA por ahora** |

## Plan B' seguro

1. **No cambiar DonDominio todavía.** Mantener el dominio y sus URLs vivas.
2. Extraer el inventario completo del catálogo actual, no solo la muestra de 36.
3. Clasificar cada URL: marca vigente / marca obsoleta / servicio 404 / producto histórico.
4. Para cada marca vigente, asignar intención y destino: producto/categoría retail → posible equivalente en `dindonliving.com`; arquitectura/reforma/servicio/editorial → posible equivalente en `mf3.es`. Crear primero el destino con contenido, canonical y estado 200.
5. Aplicar **301 individual** antigua→nueva solo después de validar el destino.
6. Para páginas de servicio 404 (`/reformas/`, `/proyectos/`, `/contacto/`), redirigir únicamente si el equivalente en mf3.es existe y responde 200 con la misma intención.
7. Para contenido obsoleto sin equivalente, usar 404/410 o una categoría relevante; **no enviar todo a la home**.
8. QA previo y posterior: estado HTTP, cadena de redirects, canonical, sitemap, enlaces internos y cobertura GSC.

## Qué invalida esta versión del dossier v51

Quedan retractadas estas afirmaciones/instrucciones anteriores:

- ❌ “Mi recomendación: redirect 301 wildcard DonDominio”.
- ❌ “Riesgo mínimo”.
- ❌ “10 minutos y reversible” como solución completa.
- ❌ `*.mediterraneanfusion.es → https://mf3.es/$1` sin mapa previo.
- ❌ “El catálogo antiguo ya no aporta valor” sin validación comercial de Dani.
- ❌ “Coste SEO residual post-B = 0”.

La corrección no es cosmética: v53 demostró que el supuesto básico de v51 era falso. El sitio tiene un catálogo activo y mayoritariamente histórico.

## Decisión que necesita Dani

No hace falta actuar hoy en DonDominio. La decisión útil es:

1. ¿Qué marcas del catálogo siguen siendo comerciales para MF3?
2. ¿Quiere consolidarlas en mf3.es o mantener ese vertical separado?
3. ¿Puede facilitar acceso de solo lectura a GSC o un export de backlinks para ordenar la migración por valor real?

**Mi voto actual:** mantener el dominio sin cambios mientras preparo el inventario comercial y el mapa selectivo. Ejecutar luego B'' por lotes pequeños con QA: DinDon para catálogo transaccional cuando exista equivalente real; MF3 para servicios/editorial. Nunca wildcard.


---

## Anexo técnico v66 — 2026-07-28 22:04 — Validación oficial Google Search Central

**Origen:** `Research/L7/data/l7_v66_google_redirect_official_guidance_2026-07-28.json`. La opción **B'' — Migración selectiva dividida** (recomendada arriba) se valida 1:1 contra la documentación oficial de Google Search Central para site-move con cambio de dominio.

### Documentos canónicos citados

- `developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes` — *"Domain name changes such as example.com to example.net or merging multiple domains or hostnames"* (caso mediterraneanfusion.es → mf3.es documentado textualmente).
- `developers.google.com/search/docs/crawling-indexing/301-redirects` — 301/308 = *permanent redirects* que usa **la pipeline de indexación como señal fuerte de canonicidad**; 302/307/303 son temporales y NO consolidan señales.
- `developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls` — orden de señales canónicas: **(1) Redirects > (2) rel="canonical" > (3) sitemap**. *"Use redirects when you want to get rid of existing duplicate pages."*

### Por qué el approach B'' encaja con la guía

| Práctica B'' del dossier | Lo que dice Google | Estado |
|---|---|---|
| URL→URL mapping manual antes del redirect | *"Prepare URL mapping → Create a mapping of old to new URLs"* | ✅ Coincide |
| 301 server-side, no 302 | *"the indexing pipeline uses the redirect as a signal that the redirect target should be canonical"* | ✅ Coincide |
| Validación HTTP+canonical antes/después | *"Update all URL details on the new site"* (canonicals, sitemap, hreflang) | ✅ Coincide |
| Por lotes pequeños + QA | *"Monitor traffic"* con Search Console 28-90 días | ✅ Coincide |

### Por qué opciones descartadas se confirman inválidas

- ❌ **Wildcard**: rompe /mobalco1/ y /firmas/ con contenido vivo (v60) **+** Google no prescribe regex para site-move; exige mapeos.
- ❌ **Soft-404 (404→home)**: ningún patrón prescrito; diluye PageRank, confunde al crawler, sin consolidar nada en el destino.
- ❌ **302/307** como "más conservador": NO conservan PageRank — son temporales por definición y NO consolidan.

### Si Dani confirma expirar (opción A) — cambio de dirección formal

Si la decisión A es no-redirect (dejar expirar el dominio sin migrar), Google sigue requiriendo traspaso de propiedad:

1. *Change of Address tool* en Search Console (solo si existe GSC-property del dominio antiguo) para consolidar señales residuales.
2. Validar con `curl -sI` que el dominio deja de resolver y que ningún backlink apunta a un parking que robe tráfico.
3. Comunicar a partners estratégicos (FácilReformas `facilreformas.es/mediterraneanfusion` confirmado vivo v59) el corte del dominio.

### Checklist verificación post-B'' (si se ejecuta)

- Antes: `curl -sI -L <origen>` → debe devolver 200 o 404, nunca 302 a home.
- Después (mapping aplicado): `curl -sI -L <origen>` → debe devolver **un único 301** que apunte al destino y **200 final** con `rel="canonical"` apuntando a sí mismo o al destino.
- Regenerar sitemap `mf3.es` (o `dindonliving.com`) sin las URLs viejas.
- Monitorizar GSC 28 días por caídas de clics, aparición de soft-404 ocanicas equivocadas.
