# OpenClaw Canvas & Panels — Query 5: A2UI Protocol & Advanced Canvas Features

**Fecha:** 2026-05-16
**Query:** "openclaw a2ui surface components protocol" + "openclaw canvas node present hide"
**Resultados:** ~15 found

---

## A2UI Protocol (Advanced User Interface)

**Documentación:** docs.openclaw.ai/platforms/mac/canvas#a2ui-in-canvas

### Qué es A2UI:
Es un protocolo para que el Gateway envíe comandos a la Canvas panel en nodes. Actualmente v0.8.

### Comandos A2UI v0.8:

| Comando | Descripción |
|---------|-------------|
| `beginRendering` | Inicia renderizado de surface |
| `surfaceUpdate` | Actualiza componentes en surface |
| `dataModelUpdate` | Actualiza modelo de datos |
| `deleteSurface` | Elimina surface |

**NO soporado aún:** `createSurface` (v0.9)

### Ejemplo A2UI push:
```bash
cat > /tmp/a2ui-v0.8.jsonl <<'EOFA2'
{"surfaceUpdate":{"surfaceId":"main","components":[
  {"id":"root","component":{"Column":{"children":{"explicitList":["title","content"]}}}},
  {"id":"title","component":{"Text":{"text":{"literalString":"Canvas (A2UI v0.8)"},"usageHint":"h1"}}},
  {"id":"content","component":{"Text":{"text":{"literalString":"If you can read this, A2UI push works."},"usageHint":"body"}}}
]}}
{"beginRendering":{"surfaceId":"main","root":"root"}}
EOFA2

openclaw nodes canvas a2ui push --jsonl /tmp/a2ui-v0.8.jsonl --node <id>
```

### Quick smoke test:
```bash
openclaw nodes canvas a2ui push --node <id> --text "Hello from A2UI"
```

---

## Canvas Node Commands

### Desde CLI:
```bash
# Listar nodes
openclaw nodes list

# Presentar content
openclaw nodes canvas present --node <id>

# Navigate (local path, http(s), file://)
openclaw nodes canvas navigate --node <id> --url "/"
openclaw nodes canvas navigate --node <id> --url "http://example.com"

# Eval JavaScript
openclaw nodes canvas eval --node <id> --js "document.title"

# Snapshot
openclaw nodes canvas snapshot --node <id>

# A2UI push
openclaw nodes canvas a2ui push --node <id> --text "Hello"
```

### Desde Herramienta (agente):
```
canvas action:present node:<node-id> target:<url>
canvas action:hide node:<node-id>
canvas action:navigate node:<node-id> url:<url>
canvas action:eval node:<node-id> js:<javascript>
canvas action:snapshot node:<node-id>
canvas action:a2ui_push node:<node-id> text:<text>
canvas action:a2ui_reset node:<node-id>
```

---

## Canvas — Security Notes

### Desde docs.openclaw.ai:

1. **Canvas scheme blocks directory traversal**
   - Files deben vivir bajo session root
   - No puedes acceder a archivos fuera del canvas root

2. **Local Canvas content usa custom scheme**
   - No requiere loopback server

3. **External http(s) URLs**
   - Solo permitido cuando explícitamente navegas

### Bind modes:
| Mode | Server binds to | Canvas URL uses |
|------|-----------------|-----------------|
| `loopback` | 127.0.0.1 | localhost |
| `lan` | LAN interface | LAN IP |
| `tailnet` | Tailscale interface | Tailscale hostname |
| `auto` | Best available | Tailscale > LAN > loopback |

---

## Live Reload

### Config:
```json
{
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "/path/to/canvas",
    "liveReload": true
  }
}
```

### Cómo funciona:
1. Canvas host watcher monitorea cambios en archivos (usa chokidar)
2. Inyecta WebSocket client en HTML files
3. Auto-reload en canvases conectadas

**Perfecto para desarrollo!**

---

## URL Path Structure

```
Canvas Host: http://<host>:18793/__openclaw__/canvas/

index.html → ~/.openclaw/canvas/index.html
dashboard.html → ~/.openclaw/canvas/dashboard.html
games/snake.html → ~/.openclaw/canvas/games/snake.html
```

---

## Canvas Components desde la guía ququ123

### Text Component:
```javascript
canvas.text({
  content: "Hello, World!",
  style: { fontSize: "24px", color: "#333", fontWeight: "bold" }
})
```

### Button Component:
```javascript
canvas.button({
  label: "Click Me",
  onClick: () => { console.log("Button clicked!"); },
  style: { background: "#3b82f6", color: "white" }
})
```

### List Component:
```javascript
canvas.list({
  items: ["Item 1", "Item 2", "Item 3"],
  onSelect: (item) => { console.log(`Selected: ${item}`); }
})
```

### Chart Component:
```javascript
canvas.chart({
  type: "bar",
  data: {
    labels: ["Jan", "Feb", "Mar"],
    datasets: [{ label: "Revenue", data: [100, 200, 150] }]
  }
})
```

### Form Component:
```javascript
canvas.form({
  fields: [
    { name: "username", type: "text", label: "Username" },
    { name: "email", type: "email", label: "Email" },
    { name: "submit", type: "submit", label: "Submit" }
  ],
  onSubmit: (data) => { console.log("Form submitted:", data); }
})
```

---

## Ejemplo: Dashboard Renderizado

```javascript
canvas.render(`
  <Dashboard>
    <Header title="Sales Dashboard" />
    <Row>
      <Card title="Total Revenue" value="$125,430" trend="+12%" />
      <Card title="Active Users" value="3,245" trend="+5%" />
      <Card title="Conversion Rate" value="4.2%" trend="-1%" />
    </Row>
    <Row>
      <Chart type="line" data={revenueData} title="Revenue Trend" />
      <Chart type="bar" data={usersData} title="User Growth" />
    </Row>
  </Dashboard>
`)
```

---

## Ejemplo: Interactive Calculator

```javascript
canvas.render(`
  <Calculator>
    <Display value={display} />
    <Keypad>
      <Button onClick={() => input('7')}>7</Button>
      <Button onClick={() => input('8')}>8</Button>
      <Button onClick={() => input('9')}>9</Button>
      <Button onClick={() => input('/')}>/</Button>
    </Keypad>
  </Calculator>
`)

const state = { display: '0' }
function input(value) {
  state.display = calculate(state.display, value)
  canvas.update()
}
```

---

## Ejemplo: System Monitor

```javascript
canvas.render(`
  <Monitor>
    <Header title="System Monitor" />
    <Metrics>
      <Metric label="CPU Usage" value={cpuUsage} threshold={80} unit="%" />
      <Metric label="Memory" value={memoryUsed} threshold={90} unit="GB" />
      <Metric label="Disk I/O" value={diskIO} unit="MB/s" />
    </Metrics>
    <Chart type="line" data={historyData} realtime />
  </Monitor>
`)

// Update data periodically
setInterval(() => {
  cpuUsage = getCpuUsage()
  memoryUsed = getMemoryUsed()
  diskIO = getDiskIO()
  canvas.update()
}, 1000)
```

---

## Canvas Skill en Skills Marketplace

**URL:** lobehub.com/skills/openclaw-openclaw-canvas

### Ejemplo de uso:
```
canvas action:present node:mac-63599bc4-b54d-4392-9048-b97abd58343a target:http://peters-mac-studio-1.sheep-coho.ts.net:18793/__openclaw__/canvas/snake.html
```

---

## OpenClaw Canvas: Real-Time HTML Preview Skill

**URL:** mcpmarket.com/tools/skills/openclaw-canvas-1

### Features:
1. Interactive control via JavaScript evaluation
2. Visual debugging con automated canvas snapshot
3. Real-time HTML preview

---

## Troubleshooting Canvas

### White screen / content no carga:
**Causa:** URL mismatch entre server bind y node expectation

**Debug:**
```bash
# Check server bind
cat ~/.openclaw/openclaw.json | jq '.gateway.bind'

# Check port
lsof -i :18793

# Test URL directly
curl http://<hostname>:18793/__openclaw__/canvas/<file>.html
```

### "node required" error:
Siempre especificar `node:<node-id>`

### "node not connected" error:
Node offline. Usar `openclaw nodes list` para ver nodes online.

### Content not updating:
1. Check `liveReload: true` en config
2. Asegurar que file está en canvas root directory
3. Check for watcher errors in logs

---

## Canales - OpenClaw Docs

**URL:** openclaw-ai.com/en/docs/tools/index

### Canvas tool summary:
| Action | Returns |
|--------|---------|
| `present` | Canvas shown |
| `hide` | Canvas hidden |
| `navigate` | Canvas navigated |
| `eval` | JavaScript executed |
| `snapshot` | IMAGE: + MEDIA:<path> |
| `a2ui_push` | A2UI message sent |
| `a2ui_reset` | A2UI reset |

**Usa:** `gateway node.invoke` por debajo

---

## Resumen: Canvas Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Canvas Host    │────▶│   Node Bridge     │────▶│  Node App   │
│  (HTTP Server)  │     │  (TCP Server)     │     │ (Mac/iOS/   │
│  Port 18793     │     │  Port 18790       │     │  Android)   │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

1. Canvas Host sirve static files
2. Node Bridge comunica URLs a nodes
3. Node Apps renderizan en WebView

---

*Investigador — Query 5 completada.*