# OpenClaw Canvas & Panels — Query 2: Agent Avatars & Office Simulation

**Fecha:** 2026-05-16
**Query:** "openclaw agent avatar office simulation interface"
**Resultados:** 20 found

---

## Proyectos Encontrados

### 1. OpenClaw Office ⭐ (RECOMENDADO)
**GitHub:** github.com/WW-AI-Lab/openclaw-office
**Autor:** WW-AI-Lab
**Demo:** FuenteForge mirror disponible

#### Características:
- **Virtual Office** — 2D floor plan SVG con oficina isométrica
- **Agent Avatars** — SVG generados determinísticamente desde agent IDs
- **Status animations** — idle, working, speaking, tool calling, error
- **Collaboration Lines** — Líneas visuales de flujo entre agentes
- **Speech Bubbles** — Markdown text streaming en tiempo real
- **Side Panels** — Agent details, token charts, cost pie charts, activity heatmaps

#### Tech Stack:
- Vite 6 + React 19
- SVG + CSS Animations
- Zustand 5 + Immer
- Tailwind CSS 4
- Recharts
- i18next

#### Quick Launch:
```bash
# Directo (no necesita clonar)
npx @ww-ai-lab/openclaw-office

# O global
npm install -g @ww-ai-lab/openclaw-office
openclaw-office
```

#### Auto-detecta token del Gateway:
```bash
# Auto-configuración
openclaw-office
# Detecta automáticamente desde ~/.openclaw/openclaw.json
```

---

### 2. Pixel Office OpenClaw
**GitHub:** github.com/neomatrix25/pixel-office-openclaw
**Descripción:** "Pixel art office for AI agents"

#### Características:
- Cada agent tiene character animado
- Walking, sitting at desks
- Real-time status como ellos ejecutan tasks
- Click any agent para ver detalles

#### Status: README 404, puede estar deprecated

---

### 3. ClawOffice (SaaS)
**URL:** www.productcool.com/product/clawoffice
**Descripción:** "Browser-based 3D virtual office platform"

#### Características:
- 3D virtual office
- SaaS
- Deploy y manage OpenClaw agents

---

### 4. ClawHarbor
**URL:** www.clawharbor.work/
**Descripción:** "Virtual Office for OpenClaw Agents"

#### Características:
- Watch agents work
- Click NPCs to DM them
- Quest log
- Battle system
- Burnout, Payroll
- Live feeds
- Office Replay

---

### 5. Clawfice
**URL:** openclawfice.com/
**Descripción:** Auto-discovers OpenClaw agents

#### Uso:
- Run it and your office appears
- No configuration needed

---

### 6. Claw3D
**Descripción:** "3D navigable office donde agents perform code reviews, standups, and task execution"

#### Tech:
- Next.js 15, React 19
- 3D environment

---

### 7. Liveavatar
**URL:** app.li...
**Descripción:** Avatar generation platform para AI agents

---

## OpenClaw Office — Detalles Completos

### Metaphor:
```
Agent = Digital Employee
Office = Agent Runtime
Desk = Session
Meeting Pod = Collaboration Context
```

### Páginas del Console:
| Página | Features |
|--------|----------|
| Dashboard | Overview stats, alert banners, Channel/Skill overview |
| Agents | Agent list/create/delete, detail tabs |
| Channels | Channel cards, config dialogs, stats, WhatsApp QR |
| Skills | Skill marketplace, install, detail dialogs |
| **Skill Workbench** ✨ | AI-assisted skills development con Mermaid flowcharts |
| Cron | Scheduled task management |
| Settings | Provider management, appearance, Gateway, developer |

### Chat Workspace:
- Session management
- Real-time streaming con abort/resend
- Persistent chat history (server-side, per-day sharded)
- Tool call visualization
- Slash commands: /help, /new, /reset, /model, /think, /export
- Attachments (images + files)
- Search, Markdown export, focus mode

---

## CLI Options (OpenClaw Office)

| Flag | Description | Default |
|------|-------------|---------|
| `-t, --token` | Gateway auth token | auto-detected |
| `-g, --gateway` | Gateway WebSocket URL | ws://localhost:18789 |
| `-p, --port` | Server port | 5180 |
| `--host` | Bind address | 0.0.0.0 |

---

## Comparativa

| Proyecto | Tipo | Dimensionalidad | Status |
|----------|------|----------------|--------|
| OpenClaw Office | Frontend completo | 2D SVG | ✅ Active |
| Pixel Office | Visualizer | 2D Pixel | ⚠️ Maybe deprecated |
| ClawOffice | SaaS | 3D | 💰 Paid |
| ClawHarbor | Virtual office | 2D | ✅ |
| Clawfice | Auto-discover | 2D | ✅ |
| Claw3D | 3D Office | 3D | ⚠️ Complex |

---

## Recomendación para Dani

**Empezar con OpenClaw Office:**
```bash
npx @ww-ai-lab/openclaw-office
```
- No necesita clonar
- Auto-detecta token
- Full console + virtual office
- Chat workspace integrado
- Skill Workbench incluido

**Alternativa simple: Clawfice**
```bash
# Si solo quieres ver agentes
openclawfice.com
```
- Auto-discovers agents
- Zero config

---

*Investigador — Query 2 completada.*