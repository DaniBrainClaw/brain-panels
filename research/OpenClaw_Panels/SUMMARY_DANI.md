# OpenClaw Panels & Avatares — Resumen para Dani

**Última actualización:** 2026-05-16

---

## tl;dr

Dani, OpenClaw tiene VARIAS formas de crear paneles:

| Qué quieres | Herramienta | Tiempo |
|-------------|-------------|--------|
| BRAIN muestre un dashboard HTML | Canvas tool | 10 min |
| Ver avatares de agentes trabajando | OpenClaw Office | 5 min |
| Dashboard de métricas del sistema | openclaw-dashboard | 5 min |
| Reemplazar WebChat con UI mejor | PinchChat | 5 min |
| Acceso remoto desde cualquier lugar | Tailscale | 15 min |

---

## 1. Canvas — Cómo BRAIN presenta paneles

Canvas es el sistema para que BRAIN muestre paneles en tu Mac/iPhone/Android.

### Arquitectura:
```
BRAIN → Gateway → Canvas Host (:18793) → Node Bridge → Tu Mac/iPhone (WebView)
```

### Cómo funciona:
1. **Crear HTML** — cualquier archivo HTML/CSS/JS
2. **BRAIN lo presenta** — usa `canvas action:present node:<id> target:<url>`
3. **Tu dispositivo lo muestra** — en el canvas panel

### Ejemplo rápido:
```bash
# 1. Crear archivo
mkdir -p ~/.openclaw/canvas/mi-panel
cat > ~/.openclaw/canvas/mi-panel/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
  <h1>Ventas del día</h1>
  <p id="ventas">Cargando...</p>
  <script>
    document.getElementById('ventas').innerText = '€1,234';
  </script>
</body>
</html>
EOF

# 2. BRAIN lo presenta ( automática)
canvas action:present node:<tu-node-id> target:http://tu-host:18793/__openclaw__/canvas/mi-panel/index.html
```

---

## 2. OpenClaw Office — Avatares animados ⭐

**Esto es lo que has visto con avatares moviéndose por oficina simulada.**

### Instalar:
```bash
npx @ww-ai-lab/openclaw-office
# Abre http://localhost:5180
```

### Qué incluye:
- **Virtual Office 2D** — avatares SVG animados (idle, working, speaking, error)
- **Agent collaboration lines** — líneas visuales mostrando flujo de mensajes
- **Chat workspace** — streaming en tiempo real
- **Console completo** — Dashboard, Agents, Channels, Skills, Cron, Settings
- **Skill Workbench** — crear skills con AI assistance

### Avatares:
- Cada agente tiene avatar único (generado desde su ID)
- Se mueven por la oficina, se sienta en desks
- Muestran status en tiempo real

---

## 3. openclaw-dashboard — Métricas del sistema

### Instalar:
```bash
brew install mudrii/tap/openclaw-dashboard
openclaw-dashboard --refresh
openclaw-dashboard
# Abre http://localhost:8080
```

### 12 paneles:
1. **Top Metrics Bar** — CPU, RAM, disco
2. **Alerts Banner** — costos altos, crons fallidos
3. **System Health** — gateway status, uptime
4. **Cost Cards** — hoy, total, proyectado
5. **Cron Jobs** — todos los jobs programados
6. **Active Sessions** — sesiones activas
7. **Token Usage** — desglose por modelo
8. **Sub-Agent Activity** — actividad de sub-agentes
9. **Charts & Trends** — gráficos de costo
10. **Models** — modelos disponibles
11. **Skills** — lista de skills
12. **Git log** — commits recientes

---

## 4. PinchChat — Mejor WebChat

**Reemplaza la UI de chat por algo mucho mejor.**

### Instalar:
```bash
docker run -p 3000:80 ghcr.io/marlburrow/pinchchat:latest
# Abre http://localhost:3000
```

### Características:
- **Tool call visualization** — ves exactamente qué herramientas usa BRAIN
- **Live streaming** — token por token
- **Token usage** — barras de progreso
- **Split view** — 2 sesiones lado a lado
- **Themes** — Dark, Light, OLED Black
- **Search** — Ctrl+F para buscar

---

## 5. Acceso remoto con Tailscale

### Setup:
```bash
# Instalar Tailscale en el servidor
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Configurar gateway
{
  "gateway": {
    "tailscale": { "mode": "serve" }
  }
}
```

### Luego accedes desde cualquier lugar:
- **Control UI:** https://tu-host.ts.net/
- **Dashboard:** https://tu-host.ts.net:8080/
- **PinchChat:** https://tu-host.ts.net:3000/

---

## Canvas Tool — Comandos

BRAIN puede usar estas acciones:

| Acción | Para qué |
|--------|----------|
| `canvas.present` | Mostrar un panel HTML |
| `canvas.hide` | Ocultar el panel |
| `canvas.navigate` | Ir a otra URL |
| `canvas.eval` | Ejecutar JavaScript |
| `canvas.snapshot` | Tomar screenshot → imagen |
| `canvas.a2ui_push` | Enviar mensaje A2UI |

---

## Live Reload — Desarrollo rápido

Si pones `liveReload: true` en config:
- Cada vez que guardas el HTML, el canvas se actualiza solo
- No necesitas reiniciar nada
- Perfecto para desarrollo iterativo

```json
{
  "canvasHost": {
    "enabled": true,
    "port": 18793,
    "root": "/Users/tú/.openclaw/canvas",
    "liveReload": true
  }
}
```

---

## Quick reference — URLs

| Servicio | URL local | Puerto |
|----------|----------|--------|
| Control UI | http://localhost:18789/ | 18789 |
| Canvas Host | http://localhost:18793/ | 18793 |
| openclaw-dashboard | http://localhost:8080/ | 8080 |
| OpenClaw Office | http://localhost:5180/ | 5180 |
| PinchChat | http://localhost:3000/ | 3000 |

---

## Para qué sirve cada cosa

| Uso | Herramienta recomendada |
|-----|----------------------|
| **Ver cómo BRAIN trabaja** | OpenClaw Office |
| **Saber costos y métricas** | openclaw-dashboard |
| **Chat con visualización de tools** | PinchChat |
| **BRAIN muestra resultados visuales** | Canvas tool |
| **Acceder desde fuera de casa** | Tailscale |

---

*Dani: ¿Cuál quieres probar primero?*