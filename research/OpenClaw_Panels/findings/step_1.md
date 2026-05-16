# OpenClaw Canvas & Panels — Query 1: Canvas Dashboard Tutorial

**Fecha:** 2026-05-16
**Query:** "openclaw canvas dashboard interactive panel tutorial"
**Resultados:** 18 found

---

## Fuentes Principales

1. **Documentación oficial Canvas** — docs.openclaw.ai/platforms/mac/canvas
2. **SKILL.md Canvas** — github.com/openclaw/openclaw/blob/main/skills/canvas/SKILL.md
3. **Web UI Guide** — ququ123.top/en/2026/02/openclaw-web-ui/
4. **Goldie Agency Dashboard** — goldie.agency/openclaw-dashboard/
5. **GitHub mudrii/openclaw-dashboard** — zero-dependency command center

---

## Arquitectura Canvas (del SKILL.md)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Canvas Host    │────▶│   Node Bridge     │────▶│  Node App   │
│  (HTTP Server)  │     │  (TCP Server)     │     │ (Mac/iOS/   │
│  Port 18793     │     │  Port 18790       │     │  Android)   │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

### Componentes:
1. **Canvas Host Server** — Serve static HTML/CSS/JS files
2. **Node Bridge** — Communica canvas URLs a nodes
3. **Node Apps** — Render content en WebView

---

## Cómo Funciona Canvas

### 1. Crear HTML content
```bash
# En canvas root directory (~/.openclaw/canvas/<session>/)
cat > ~/.openclaw/canvas/my-dashboard.html << 'HTML'
<!DOCTYPE html>
<html>
<head><title>My Dashboard</title></head>
<body>
  <h1>Hello Canvas!</h1>
</body>
</html>
HTML
```

### 2. Presentar content
```
canvas action:present node:<node-id> target:<url>
```

### 3. Acciones disponibles
- `present` — Show canvas
- `hide` — Hide canvas
- `navigate` — Navigate a URL
- `eval` — Execute JavaScript
- `snapshot` — Capture screenshot

---

## A2UI Protocol (Advanced)

Canvas supports **A2UI v0.8** commands:
- `beginRendering`
- `surfaceUpdate`
- `dataModelUpdate`
- `deleteSurface`

```bash
# Ejemplo A2UI push
openclaw nodes canvas a2ui push --node <id> --text "Hello from A2UI"
```

---

## Canvas Commands desde CLI

```bash
# Listar nodes
openclaw nodes list

# Presentar dashboard
openclaw nodes canvas present --node <id>

# Navigate
openclaw nodes canvas navigate --node <id> --url "/"

# Eval JS
openclaw nodes canvas eval --node <id> --js "document.title"

# Snapshot
openclaw nodes canvas snapshot --node <id>
```

---

## URL Path Structure

```
http://<host>:18793/__openclaw__/canvas/index.html
  → ~/.openclaw/canvas/index.html

http://<host>:18793/__openclaw__/canvas/dashboard/metrics.html
  → ~/.openclaw/canvas/dashboard/metrics.html
```

---

## Live Reload

Cuando `liveReload: true`:
- Watcher monitorea cambios en archivos
- Inyecta WebSocket client en HTML
- Auto-reload en canvas conectadas

**Perfecto para desarrollo!**

---

## Configuración

```json
{
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "/Users/tú/.openclaw/canvas",
    "liveReload": true
  },
  "gateway": {
    "bind": "auto"
  }
}
```

---

## Bind Modes (Tailscale/LAN)

| Bind | Server binds to | Canvas URL uses |
|------|-----------------|-----------------|
| loopback | 127.0.0.1 | localhost |
| lan | LAN interface | LAN IP |
| tailnet | Tailscale interface | Tailscale hostname |
| auto | Best available | Tailscale > LAN > loopback |

**Key insight:** Cuando usas Tailscale, el node recibe el hostname de Tailscale, no localhost!

---

## Control UI vs Canvas

| Característica | Control UI | Canvas |
|----------------|------------|--------|
| Propósito | Dashboard de gestión | Visual workspace |
| Contenido | Stats, config, logs | HTML/CSS/JS apps |
|Quién controla | Gateway | Agent |
| Acceso | Browser → :18789 | macOS/iOS/Android apps |

---

## Tips del SKILL.md

- Mantener HTML self-contained (inline CSS/JS)
- Usar default index.html como test page
- Canvas persiste hasta `hide`
- Live reload = desarrollo rápido
- A2UI JSON push es WIP — usar HTML por ahora

---

## Dashboard con OpenClaw

GitHub: **mudrii/openclaw-dashboard**
- Zero dependencies
- Muestra models, skills, git commits
- Command center para agentes

---

*Investigador — Query 1 completada.*