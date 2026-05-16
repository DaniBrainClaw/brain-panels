# OpenClaw Panels & Avatares — INDEX

**Guía para crear paneles interactivos con BRAIN/OpenClaw**

**Última actualización:** 2026-05-16

---

## Tabla de Contenidos

1. [Arquitectura general](#1-arquitectura-general)
2. [Canvas — Cómo BRAIN presenta paneles](#2-canvas--cómo-brain-presenta-paneles)
3. [Acciones del Canvas tool](#3-acciones-del-canvas-tool)
4. [Crear HTML para Canvas](#4-crear-html-para-canvas)
5. [Dashboard externo vs Canvas](#5-dashboard-externo-vs-canvas)
6. [Virtual Office — OpenClaw Office](#6-virtual-office--openclaw-office)
7. [WebChat personalizado — PinchChat](#7-webchat-personalizado--pinchchat)
8. [Esquemas de bind y acceso remoto](#8-esquemas-de-bind-y-acceso-remoto)
9. [A2UI Protocol (avanzado)](#9-a2ui-protocol-avanzado)
10. [Solución de problemas](#10-solución-de-problemas)

---

## 1. Arquitectura General

OpenClaw tiene DOS tipos de paneles:

### Type A: Canvas (para agentes)
- El agente genera HTML/CSS/JS y lo presenta en nodes (Mac/iOS/Android)
- Communication: Canvas Host → Node Bridge → Node App (WebView)
- Puerto: 18793

### Type B: Dashboard/Control UI (para operadores)
- Dashboards externos que se conectan al Gateway WebSocket
- No requieren que el agente genere contenido
- Puerto default: 18789

```
┌──────────────────────────────────────────────────────┐
│              OpenClaw Gateway (:18789)                │
├────────────────────────┬─────────────────────────────┤
│  Control UI / WebChat  │  WebSocket API               │
│  (Browser UI)          │  (Dashboards externos)      │
└────────────────────────┴─────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐       ┌─────────────────┐
│   Canvas Host    │       │  openclaw-       │
│   (:18793)       │       │  dashboard       │
│   (Node Bridge) │       │  (puerto 8080)   │
└─────────────────┘       └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Node Apps      │
│  Mac/iOS/Android│
│  (WebView)      │
└─────────────────┘
```

---

## 2. Canvas — Cómo BRAIN presenta paneles

### Paso 1: Crear archivo HTML
```bash
mkdir -p ~/.openclaw/canvas/mi-panel
cat > ~/.openclaw/canvas/mi-panel/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>Mi Dashboard</title>
  <style>
    body { font-family: sans-serif; padding: 20px; }
    .card { border: 1px solid #ccc; padding: 16px; margin: 8px 0; }
  </style>
</head>
<body>
  <h1>Dashboard de Ventas</h1>
  <div id="content">Cargando...</div>
  <script>
    // Tu JavaScript aquí
    document.getElementById('content').innerText = '¡Listo!';
  </script>
</body>
</html>
EOF
```

### Paso 2: Encontrar el node ID
```bash
openclaw nodes list
# Anotar el node ID (ej: mac-63599bc4-b54d-4392-9048-b97abd58343a)
```

### Paso 3: Presentar desde BRAIN
```
canvas action:present node:<node-id> target:http://<hostname>:18793/__openclaw__/canvas/mi-panel/index.html
```

---

## 3. Acciones del Canvas tool

| Acción | Ejemplo | Retorna |
|--------|---------|---------|
| `present` | `canvas action:present node:<id> target:<url>` | Panel visible |
| `hide` | `canvas action:hide node:<id>` | Panel ocultado |
| `navigate` | `canvas action:navigate node:<id> url:<url>` | Navega a URL |
| `eval` | `canvas action:eval node:<id> js:<js>` | Resultado JS |
| `snapshot` | `canvas action:snapshot node:<id>` | IMAGE: + MEDIA: |
| `a2ui_push` | `canvas action:a2ui_push node:<id> text:<msg>` | A2UI message |
| `a2ui_reset` | `canvas action:a2ui_reset node:<id>` | Reset A2UI |

---

## 4. Crear HTML para Canvas

### Estructura básica self-contained:
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mi Panel</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }
    .card { background: #16213e; border-radius: 8px; padding: 16px; margin: 8px 0; }
    h1 { color: #e94560; }
  </style>
</head>
<body>
  <h1>Ventas</h1>
  <div class="card">
    <div id="counter">0</div>
  </div>
  <script>
    let count = 0;
    setInterval(() => {
      count++;
      document.getElementById('counter').innerText = count;
    }, 1000);
  </script>
</body>
</html>
```

### Live Reload:
Con `liveReload: true` en config, cada vez que guardes el archivo el canvas se actualiza automáticamente.

---

## 5. Dashboard externo vs Canvas

### Para qué sirve cada uno:

| Característica | Canvas | Dashboard externo |
|----------------|--------|-------------------|
| **Quién crea contenido** | Agente | Tú/dashboards |
| **Interactividad** | HTML/JS generado por IA | Dashboards pre-hechos |
| **Ideal para** | Mostrar resultados, visualizaciones | Monitorizar sistema |
| **Requiere node** | Sí (Mac/iOS/Android) | No |
| **Puerto** | 18793 | 8080 o custom |

### Instalar dashboard externo:
```bash
# opcionales
brew install mudrii/tap/openclaw-dashboard  # 12 panels
npx @ww-ai-lab/openclaw-office              # virtual office
docker run -p 3000:80 ghcr.io/marlburrow/pinchchat  # webchat custom
```

---

## 6. Virtual Office — OpenClaw Office

### Quick start:
```bash
npx @ww-ai-lab/openclaw-office
# Abre http://localhost:5180
```

### Qué incluye:
- **Virtual Office** — 2D SVG office con agent avatars animados
- **Chat Workspace** — Session management + streaming
- **Console** — Dashboard, Agents, Channels, Skills, Cron, Settings
- **Skill Workbench** — AI-assisted skills development

### Avatars de agentes:
- Generados determinísticamente desde agent ID
- Animaciones: idle, working, speaking, tool calling, error
- Collaboration lines muestran flujo de mensajes

---

## 7. WebChat personalizado — PinchChat

### Install Docker:
```bash
docker run -p 3000:80 ghcr.io/marlburrow/pinchchat:latest
# Abrir http://localhost:3000
```

### Características principales:
- Tool call visualization (colored badges + expandable)
- GPT-like interface con sessions sidebar
- Live streaming token by token
- Token usage tracking con progress bars
- Split view (2 sesiones lado a lado)
- Themes: Dark, Light, OLED Black

---

## 8. Esquemas de bind y acceso remoto

### Configuración de bind:
```json
{
  "gateway": { "bind": "auto" },
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "~/.openclaw/canvas",
    "liveReload": true
  }
}
```

### Bind modes:

| Mode | binds a | Canvas URL |
|------|---------|------------|
| `loopback` | 127.0.0.1 | localhost |
| `lan` | LAN IP | LAN IP |
| `tailnet` | Tailscale | Tailscale hostname |
| `auto` | mejor disponible | varies |

### Acceso remoto:

**Tailscale (recomendado):**
```bash
# Config en gateway
{ "gateway": { "tailscale": { "mode": "serve" } } }
# Acceder via https://your-tailnet-name.ts.net
```

**SSH tunnel:**
```bash
ssh -L 18789:localhost:18789 user@remote
# Luego http://localhost:18789
```

**Reverse proxy (Caddy):**
```
your-domain.com {
  reverse_proxy localhost:18789
}
```

---

## 9. A2UI Protocol (avanzado)

### Qué es:
Protocolo para que el Gateway envíe commands a la Canvas panel directamente.

### Versión actual: v0.8

### Comandos:
```bash
# Enviar mensaje simple
openclaw nodes canvas a2ui push --node <id> --text "Hello"

# Enviar JSON estructurado
openclaw nodes canvas a2ui push --jsonl /tmp/a2ui.jsonl --node <id>
```

### Formato JSON:
```json
{"surfaceUpdate":{"surfaceId":"main","components":[
  {"id":"root","component":{"Column":{"children":{"explicitList":["title"]}}}},
  {"id":"title","component":{"Text":{"text":{"literalString":"Title"},"usageHint":"h1"}}}
]}}
{"beginRendering":{"surfaceId":"main","root":"root"}}
```

**Nota:** `createSurface` (v0.9) no está soportado aún.

---

## 10. Solución de problemas

### Pantalla en blanco / No carga contenido:
**Causa:** URL mismatch entre server bind y expectativa del node

**Debug:**
```bash
# 1. Ver bind mode
cat ~/.openclaw/openclaw.json | jq '.gateway.bind'

# 2. Ver puerto
lsof -i :18793

# 3. Test URL
curl http://<hostname>:18793/__openclaw__/canvas/<file>.html
```

**Solución:** Usar el hostname completo que corresponda al bind mode.

---

### "node required" error:
 Siempre especifica `node:<node-id>`

---

### "node not connected" error:
 Node offline. Verificar con `openclaw nodes list`

---

### Content no actualiza:
1. Verificar `liveReload: true` en config
2. Asegurar que el archivo está en canvas root
3. Revisar logs por watcher errors

---

## Resumen rápido — Cómo hacer cada cosa

| Qué quieres | Cómo hacerlo |
|-------------|---------------|
| Crear panel HTML para BRAIN | Crear HTML en `~/.openclaw/canvas/<session>/` |
| BRAIN muestre dashboard | `canvas action:present node:<id> target:<url>` |
| Ver BRAIN trabajando en tiempo real | Instalar OpenClaw Office (`npx @ww-ai-lab/openclaw-office`) |
| Dashboard de métricas del sistema | Instalar openclaw-dashboard |
| Reemplazar WebChat con UI mejor | Usar PinchChat (Docker) |
| Ver avatares de agentes | OpenClaw Office o Clawfice |
| Acceso remoto | Tailscale o SSH tunnel |

---

*Investigador — INDEX.md creado.*