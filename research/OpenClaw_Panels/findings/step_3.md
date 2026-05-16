# OpenClaw Canvas & Panels — Query 3: Control UI, Panels & Embed HTML

**Fecha:** 2026-05-16
**Query:** "openclaw control UI panels embed HTML"
**Resultados:** 19 found

---

## Fuentes

1. **Control UI Official Docs** — docs.openclaw.ai/web/control-ui
2. **Web UI Guide (ququ123)** — ququ123.top/en/2026/02/openclaw-web-ui/
3. **GitHub openclaw/ui** — github.com/openclaw/openclaw/blob/main/ui/index.html
4. **GitHub mudrii/openclaw-dashboard** — zero-dependency command center
5. **GitHub TianyiDataScience/openclaw-control-center** — local control center

---

## Control UI — Official

**URL:** docs.openclaw.ai/web/control-ui
**Puerto default:** http://127.0.0.1:18789/

### Pages/Features:
| Feature | Description |
|---------|-------------|
| **Chat** | Message input, Markdown, code blocks |
| **Sessions** | List, details, reset, delete, export |
| **Config** | Edit config online, validation, hot reload |
| **Nodes** | List connected devices, status, pairing |
| **Logs** | Real-time streaming, filter, search, export |
| **Skills** | Install from ClawHub, configure, toggle |

### Config options:
```json
{
  "web": {
    "enabled": true,
    "port": 18789,
    "bind": "loopback",
    "auth": {
      "mode": "password",
      "password": "your-secure-password"
    },
    "theme": "dark"
  }
}
```

### Auth modes:
- **Token** — via `connect.params.auth.token`
- **Password** — `gateway.auth.mode: "password"`
- **Tailscale** — identity headers when `gateway.auth.allowTailscale: true`
- **Trusted-proxy** — identity headers from proxy

### Remote access:
- **Tailscale:** https://your-tailnet-name.ts.net
- **SSH tunnel:** `ssh -L 18789:localhost:18789 user@remote-server`
- **Reverse proxy:** Caddy/Nginx con `reverse_proxy localhost:18789`

---

## Dashboards Alternativos

### 1. openclaw-dashboard ⭐⭐⭐
**GitHub:** github.com/mudrii/openclaw-dashboard
**Autor:** mudrii

#### 12 Paneles:
1. **Top Metrics Bar** — CPU, RAM, swap, disk + OpenClaw version
2. **Header Bar** — Bot name, online/offline, auto-refresh countdown
3. **Alerts Banner** — High costs, failed crons, gateway offline
4. **System Health** — Gateway status, PID, uptime, memory, sessions
5. **Cost Cards** — Today's cost, all-time, projected monthly, breakdown
6. **Cron Jobs** — All scheduled jobs with status/schedule/last-next
7. **Active Sessions** — Recent sessions con model, type badges
8. **Token Usage & Cost** — Per-model breakdown, 7d/30d/all-time
9. **Sub-Agent Activity** — Runs con cost, duration, status
10. **Charts & Trends** — Cost trend line, model breakdown
11. **Bottom Row** — Available models, skills list, git log
12. **AI Chat** — Natural language queries sobre dashboard

#### Características:
- 6 built-in themes (3 dark + 3 light)
- Glass Morphism UI
- Responsive (desktop/tablet/mobile)
- Local only — no external deps
- Rate limiting en `/api/chat`
- Go backend + pure HTML/CSS/JS frontend

#### Install:
```bash
# Homebrew
brew install mudrii/tap/openclaw-dashboard
openclaw-dashboard --refresh
openclaw-dashboard

# Pre-built binary
curl -L https://github.com/mudrii/openclaw-dashboard/releases/latest/download/openclaw-dashboard-darwin-arm64.tar.gz | tar xz
./openclaw-dashboard --port 8080
```

---

### 2. openclaw-control-center
**GitHub:** github.com/TianyiDataScience/openclaw-control-center

**Descripción:** "Turn OpenClaw from a black box into a local control center you can see, trust, and control."

---

### 3. OpenClaw Office (de Query 2)
**GitHub:** github.com/WW-AI-Lab/openclaw-office

Ya documentado en step_2.md — incluye console completo + virtual office.

---

## Embed HTML en Control UI

### Building the UI
La documentación menciona que el Gateway sirve static files desde `dist/control-ui`. 

Para hacer embed de contenido custom en el Control UI:

1. **Crear archivo HTML** en el canvas root
2. **Presentar via Canvas tool** — `canvas.present`
3. **O navegar** — `canvas.navigate`

### Hosted Embeds
Desde docs.openclaw.ai:
```
El Control UI soporta hosted embeds vía:
- /__openclaw__/canvas/<file>.html
- Custom URL scheme: openclaw-canvas://<session>/<path>
```

---

## URLs de Interés

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:18789/ | Control UI default |
| http://127.0.0.1:18793/__openclaw__/canvas/ | Canvas host |
| ws://127.0.0.1:18789 | Gateway WebSocket |

---

## Resumen: Cómo Añadir Paneles a OpenClaw

### Opción 1: Canvas (para agentes)
```javascript
// El agente crea HTML y lo presenta
canvas action:present node:<node-id> target:<url>
// El agente puede hacer eval, snapshot, navigate
```

### Opción 2: Dashboard externo (para Dani)
```bash
# Instalar dashboard alternativas
brew install mudrii/tap/openclaw-dashboard
openclaw-dashboard --port 8080
# Abrir http://localhost:8080
```

### Opción 3: OpenClaw Office (visual completo)
```bash
npx @ww-ai-lab/openclaw-office
# Abre http://localhost:5180
# Incluye virtual office + console
```

---

*Investigador — Query 3 completada.*