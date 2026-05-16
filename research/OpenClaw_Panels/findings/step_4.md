# OpenClaw Canvas & Panels — Query 4: Canvas Actions (present, eval, snapshot) + WebChat Custom

**Fecha:** 2026-05-16
**Query:** "openclaw canvas present eval snapshot features" + "openclaw webchat panel custom embed"
**Resultados:** 15 + 17 found

---

## Canvas Actions — Documentación Oficial

### SKILL.md Canvas (source of truth)
**URL:** github.com/openclaw/openclaw/blob/main/skills/canvas/SKILL.md

### 5 Acciones disponibles:

| Action | Descripción |
|--------|-------------|
| `present` | Show canvas con target URL opcional |
| `hide` | Hide canvas |
| `navigate` | Navigate a URL (local, http(s), file://) |
| `eval` | Execute JavaScript en el canvas |
| `snapshot` | Capture screenshot → returns MEDIA: + image |

### Comandos CLI:
```bash
# Presentar dashboard
openclaw nodes canvas present --node <id>

# Navigate
openclaw nodes canvas navigate --node <id> --url "/"

# Eval JS
openclaw nodes canvas eval --node <id> --js "document.title"

# Snapshot
openclaw nodes canvas snapshot --node <id>

# A2UI push (WIP)
openclaw nodes canvas a2ui push --node <id> --text "Hello"
```

---

## Canvas Tool en Agentes

```javascript
// Sintaxis:
canvas action:present node:<node-id> target:<url>
canvas action:hide node:<node-id>
canvas action:navigate node:<node-id> url:<url>
canvas action:eval node:<node-id> js:<javascript>
canvas action:snapshot node:<node-id>
```

### Ejemplo práctico — Dashboard interactivo:
```
canvas action:present node:mac-63599bc4-b54d-4392-9048-b97abd58343a target:http://peters-mac-studio-1.sheep-coho.ts.net:18793/__openclaw__/canvas/dashboard.html
```

---

## WebChat — Official Docs

**URL:** docs.openclaw.ai/web/webchat

### Características:
- Native chat UI — no embedded browser
- Usa WebSocket del Gateway
- `chat.history`, `chat.send`, `chat.inject`
- Deterministic routing — replies siempre vuelven a WebChat
- Bounded history para estabilidad

### Quick Start:
1. Start gateway
2. Open WebChat UI (macOS/iOS) o Control UI chat tab
3. Valid gateway auth configurado

---

## Custom WebChat UIs

### 1. PinchChat ⭐⭐⭐
**GitHub:** github.com/MarlBurroW/pinchchat
**Demo:** marlburrow.github.io/pinchchat/
**Docker:** `docker run -p 3000:80 ghcr.io/marlburrow/pinchchat:latest`

#### Características TOP:
- **Tool call visualization** — colored badges, parameters, expandable results
- **GPT-like interface** — sessions sidebar
- **Live streaming** — token by token
- **Token usage tracking** — progress bars
- **Inline images** — render con lightbox
- **Thinking/reasoning display** — collapsible blocks
- **Split view** — 2 sessions side by side
- **Message search** — Ctrl+F
- **PWA support** — installable
- **6 accent colors + 3 themes** — Dark, Light, OLED Black
- i18n (English + French)

#### Install Docker:
```bash
docker run -p 3000:80 ghcr.io/marlburrow/pinchchat:latest
# Abrir http://localhost:3000
```

#### Install Source:
```bash
git clone https://github.com/MarlBurroW/pinchchat.git
cd pinchchat
npm install
cp .env.example .env
npm run dev
```

---

### 2. Reddit User Builds (Issue #6050)
**Feature request:** Add custom links to webchat control panel sidebar

**Config example:**
```json
{
  "webchat": {
    "customLinks": [
      { "label": "Dashboard", "url": "http://localhost:8080" },
      { "label": "OpenClaw Office", "url": "http://localhost:5180" }
    ]
  }
}
```

---

### 3. Open WebUI Integration
**URL:** docs.openwebui.com/getting-started/quick-start/connect-an-agent/openclaw/

Permite usar OpenClaw agentes en Open WebUI como bot user.

---

## Embed OpenClaw en otras plataformas

### Localtonet Blog — Self-Host + Remote Access
**URL:** localtonet.com/blog/how-to-self-host-openclaw

**Features:**
- Multi-User access
- WebChat embedding
- Remote access

### Ejemplo embed iframe:
```html
<iframe 
  src="http://localhost:18789/webchat"
  width="100%" 
  height="600px"
  frameborder="0"
></iframe>
```

---

## Canales soportados (del README)
- WhatsApp, Telegram, Slack, Discord
- Google Chat, Signal, iMessage, IRC
- Microsoft Teams, Matrix, Feishu, LINE
- Mattermost, Nostr, Twitch, WebChat

---

## Resumen: Opciones de Customización

| Nivel | Opción | Complexity |
|-------|--------|------------|
| **1. Tool** | Canvas actions (present/eval/snapshot) | Baja |
| **2. UI** | PinchChat (reemplaza WebChat) | Baja |
| **3. Dashboard** | openclaw-dashboard (12 panels) | Baja |
| **4. Office** | OpenClaw Office (virtual office) | Media |
| **5. Full control** | Custom build sobre WebSocket API | Alta |

---

*Investigador — Query 4 completada.*