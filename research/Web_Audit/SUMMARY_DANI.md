# SUMMARY_DANI — Auditoría Web del Grupo Mediterranean Fusion

**Fecha:** 2026-05-16
**Auditada por:** Investigador
**Tiempo de investigación:** ~45 minutos
**Webs auditadas:** 7 de 8 (fusionhouse.es reported as down)

---

## TL;DR

**Tienes 7 webs. La mayoría necesitan mejoras críticas.**
La mejor: **greenaxis.es** (7.5/10)
La peor: **mf3.es** y **gp3.es** (5/10)

**Problema #1:** estudiovirtual.es NO tiene SSL — CRÍTICO
**Problema #2:** gp3.es tiene estadísticas "0" — mata credibilidad
**Problema #3:** mf3.es tiene multi-dominio confusión

---

## Los Números

| Web | Score | Prioridad |
|-----|-------|-----------|
| greenaxis.es | 7.5/10 | Baja |
| liv-ing.com | 6.5/10 | Media |
| dindonliving.com | 6.5/10 | Media |
| terracottavalladolid.com | 6.5/10 | Media |
| estudiovirtual.es | 5.5/10 | ALTA 🔴 |
| gp3.es | 5/10 | ALTA 🔴 |
| mf3.es | 5/10 | ALTA 🔴 |

---

## Acciones Inmediatas (Esta Semana)

### 🔴 CRÍTICO — Arreglar YA

**1. estudiovirtual.es — Instalar SSL (30 min)**
```text
Este sitio está en HTTP puro. Sin certificado.
Esto significa:
- Chrome marca como "no seguro"
- Datos de clientes en riesgo
- SEO penalizado por Google

ACCIÓN: Comprar e instalar certificado SSL
(Hoy día es gratis con Let's Encrypt)
```

**2. gp3.es — Quitar estadísticas "0" (5 min)**
```text
"91 KW Instalados" ✅ (bien)
"0 Metros Construidos" ❌ (crédito)
"0 Reformas Realizadas" ❌ (crédito)

Esto destruye tu credibilidad.
El usuario ve "91" y luego "0" y piensa:
"si tienen 91 KW por qué no tienen ni un metro construido?"

ACCIÓN: Poner números reales o QUITAR los contadores
```

**3. mf3.es — Consolidar multi-dominio**
```text
mf3.es → web principal
mediterraneanfusion.es → submarcas

El usuario se confunde. Visitas mf3.es y luego
encuentras mediterraneanfusion.es con contenido diferente.

ACCIÓN: Decidir cuál es el principal y unificar
```

---

## Acciones Rápidas (1 hora total)

| Web | Qué hacer | Tiempo |
|-----|-----------|--------|
| terracottavalladolid.com | Añadir horarios de apertura | 5 min |
| greenaxis.es | Añadir dirección física en footer | 5 min |
| Todas | Añadir meta description | 15 min |
| Todas | Fix URLs (www统一) | 10 min |
| dindonliving.com | Comprimir imágenes banners | 25 min |

---

## El Diagnóstico Completo

### ✅ Lo que funciona bien
- **Green Axis** — mejor web. Propuesta clara, testimonials reales, proceso definido
- **Terracotta** — carta muy completa y detallada
- **Din Don Living** — ecommerce funcional con carrito
- **Living** — propuesta de valor clara con método

### ❌ Lo que NO funciona
- **estudiovirtual.es** — Sin SSL (arreglar YA)
- **gp3.es** — Stats="0" = sin credibilidad
- **mf3.es** — Sin CTAs, navegación confusa
- **Todas** — Sin meta descriptions, sin Schema markup
- **Todas** — Sin testimonials (excepto Green Axis)

---

## El Grupo Empresarial

Todas las webs están relacionadas:

```
Plaza Martí y Monsó, 1, Valladolid
├── MF3 (Arquitectura) ← mf3.es
├── Living (Consultora hogar) ← liv-ing.com
├── Green Path (Construcción) ← gp3.es
├── Green Axis (Mantenimiento) ← greenaxis.es ⭐
├── Din Don Living (Tienda muebles) ← dindonliving.com
├── Estudio Virtual (Render 3D) ← estudiovirtual.es
└── Terracotta (Restaurante) ← terracottavalladolid.com
```

**Fusion House** (fusionhouse.es) — reported as DOWN

---

## Siguiente Paso

**¿Qué quieres automatizar primero?**

Opciones:
1. **Centralizar atención** — WhatsApp Business + respuestas automáticas
2. **Capturar leads** — Forms de contacto optimizados para cada web
3. **SEO técnico** — Schema markup + meta descriptions
4. **CRM básico** — Seguimiento de clientes y prospects

La auditoría está en `Research/Web_Audit/`
Las auditorías detalladas en `Research/Web_Audit/findings/`

**Decide qué priorizamos.**