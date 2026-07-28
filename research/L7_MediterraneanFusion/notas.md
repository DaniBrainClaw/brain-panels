

## Pulso 2026-07-29 00:04 — L7 v67: redirect strategy oficial Google
**Pregunta:** ¿cómo aplicar B-refinado a mediterraneanfusion.es sin wildcard destructivo?

- Google Search Central mantiene que los redirects permanentes (301/308) son la señal adecuada para consolidar URLs antiguas hacia nuevas; el destino debe ser equivalente y estable.
- La guía de canonicalización recomienda señales coherentes (redirect, canonical, sitemap y enlaces internos); un redirect global a la home no es equivalente para la mayoría de rutas.
- Aplicación L7: B-refinado = mapear cada ruta histórica con destino temáticamente equivalente en mf3.es; las rutas sin equivalente deben responder 404/410, no enviarse a la home. Mantener `/mobiliario/` como caso especial requiere decisión explícita porque hay contenido paralelo.
- Fuentes oficiales consultadas (28-jul-2026): Google Search Central, `301-redirects`; `consolidate-duplicate-urls`.

**Siguiente:** construir, solo como propuesta para Dani, una tabla URL-a-URL de las 16 rutas auditadas y marcar qué destinos necesitan confirmación humana antes de tocar DonDominio.
