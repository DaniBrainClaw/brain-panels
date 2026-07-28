#!/usr/bin/env python3
"""
build_panel.py — Genera el panel HTML de actividad de BRAIN.

Fuentes:
  - /data/sync/TUNEL/OPENCLAW/workspace/Research/L7/  (dossier + notas + data)
  - /data/sync/TUNEL/OPENCLAW/workspace/state/heartbeat-state.json
  - /data/sync/TUNEL/OPENCLAW/workspace/memory/YYYY-MM-DD.md (hoy + ayer)
  - /data/sync/TUNEL/OPENCLAW/workspace/Research/LINEAS.md

Salidas:
  - research/L7_MediterraneanFusion/index.html  (overview)
  - research/L7_MediterraneanFusion/dossier.html
  - research/L7_MediterraneanFusion/notas.html
  - live.html  (actividad reciente cross-línea)
  - index.html  (dashboard principal — actualiza stats + añade card L7)

Ejecución:
  python3 scripts/build_panel.py            # build completo
  python3 scripts/build_panel.py --live-only # solo live.html (uso en heartbeat)
"""
import json, os, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/data/sync/TUNEL/OPENCLAW/workspace")
PANEL = WORKSPACE / "brain-panels-local"
RESEARCH_L7 = WORKSPACE / "Research" / "L7"
RESEARCH_PANEL_L7 = PANEL / "research" / "L7_MediterraneanFusion"

NOW = datetime.now(timezone(timedelta(hours=2)))
DATE_STR = NOW.strftime("%Y-%m-%d")
TIME_STR = NOW.strftime("%H:%M")
ISO_NOW = NOW.isoformat()

def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_table(rows):
    if len(rows) < 2:
        return "\n".join(rows)
    head = rows[0]
    body = rows[2:]
    cells_h = [c.strip() for c in head.strip("|").split("|")]
    out = ["<table>", "<thead><tr>"]
    for c in cells_h:
        out.append(f"<th>{c}</th>")
    out.append("</tr></thead><tbody>")
    for r in body:
        cells = [c.strip() for c in r.strip("|").split("|")]
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)

def md_to_html(md_text: str) -> str:
    html = md_text
    html = re.sub(r"```(\w*)\n(.*?)\n```", lambda m: f'<pre><code class="lang-{m.group(1)}">{escape(m.group(2))}</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r"^###### (.+)$", r"<h6>\1</h6>", html, flags=re.MULTILINE)
    html = re.sub(r"^##### (.+)$", r"<h5>\1</h5>", html, flags=re.MULTILINE)
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)
    html = re.sub(r"^---$", r"<hr>", html, flags=re.MULTILINE)
    lines = html.split("\n")
    out = []
    in_table = False
    table_rows = []
    for line in lines:
        if "|" in line and line.strip().startswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
        else:
            if in_table:
                out.append(render_table(table_rows))
                in_table = False
                table_rows = []
            out.append(line)
    if in_table:
        out.append(render_table(table_rows))
    html = "\n".join(out)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", html)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>[^<]+</li>\n?)+", lambda m: "<ul>" + m.group(0) + "</ul>", html)
    html = re.sub(r"^\d+\. (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    paragraphs = html.split("\n\n")
    final = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith(("<h", "<ul", "<ol", "<li", "<pre", "<blockquote", "<hr", "<table", "<strong", "<em")):
            final.append(p)
        else:
            final.append(f"<p>{p}</p>")
    return "\n".join(final)

SHARED_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #0a0a0f; color: #e0e0e0; padding: 20px; line-height: 1.6; max-width: 1100px; margin: 0 auto; }
h1 { color: #00d4aa; margin-bottom: 10px; font-size: 28px; }
h2 { color: #00d4aa; margin: 30px 0 15px 0; font-size: 22px; border-bottom: 1px solid #2a2a3a; padding-bottom: 8px; }
h3 { color: #fff; margin: 20px 0 10px 0; font-size: 17px; }
h4 { color: #ddd; margin: 15px 0 8px 0; font-size: 15px; }
p { color: #c0c0c0; margin-bottom: 12px; }
strong { color: #fff; }
em { color: #ffaa00; }
code { background: #1a1a24; color: #00d4aa; padding: 2px 6px; border-radius: 3px; font-family: 'SF Mono', Monaco, monospace; font-size: 0.9em; }
pre { background: #1a1a24; color: #eee; padding: 15px; border-radius: 8px; overflow-x: auto; margin: 15px 0; }
pre code { background: none; color: inherit; padding: 0; }
blockquote { border-left: 3px solid #00d4aa; padding: 10px 15px; margin: 15px 0; background: #1a1a24; color: #ddd; font-style: italic; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th { background: #1a1a24; color: #00d4aa; padding: 10px; text-align: left; border-bottom: 2px solid #00d4aa; }
td { padding: 8px 10px; border-bottom: 1px solid #2a2a3a; color: #c0c0c0; }
tr:hover td { background: #1a1a24; }
ul, ol { margin: 10px 0 15px 25px; color: #c0c0c0; }
li { margin-bottom: 5px; }
hr { border: none; border-top: 1px solid #2a2a3a; margin: 25px 0; }
a { color: #00d4aa; text-decoration: none; }
a:hover { text-decoration: underline; }
.nav { background: #1a1a24; padding: 12px 20px; border-radius: 8px; margin-bottom: 25px; }
.nav a { color: #00d4aa; margin-right: 15px; font-weight: 500; }
.nav a.active { color: #fff; }
.meta { color: #888; font-size: 13px; margin-bottom: 25px; }
.meta strong { color: #00d4aa; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-right: 5px; }
.badge-active { background: #27ae60; color: white; }
.badge-critical { background: #ff4444; color: white; }
.badge-pending { background: #ffaa00; color: black; }
.pulse { background: #1a1a24; border-radius: 12px; padding: 18px; margin-bottom: 12px; border-left: 4px solid #00d4aa; }
.pulse-time { color: #888; font-size: 13px; }
.pulse-body { color: #ddd; margin-top: 8px; }
footer { color: #555; font-size: 12px; text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #2a2a3a; }
"""

def page(title, body_html, active_nav=""):
    nav_items = [
        ("📊 Dashboard", "index.html", "index"),
        ("🔴 Live", "live.html", "live"),
        ("🔬 Investigaciones", "investigaciones.html", "investigaciones"),
        ("📋 Tareas", "tareas.html", "tareas"),
        ("📖 Visor MD", "viewer.html", "viewer"),
    ]
    nav_html = '<div class="nav">'
    for label, href, key in nav_items:
        cls = ' class="active"' if key == active_nav else ""
        nav_html += f'<a href="{href}"{cls}>{label}</a>'
    nav_html += "</div>"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{SHARED_CSS}</style>
</head>
<body>
{nav_html}
{body_html}
<footer>
Generado por BRAIN — {ISO_NOW} · Panel público <a href="https://danibrainclaw.github.io/brain-panels/">danibrainclaw.github.io/brain-panels</a>
</footer>
</body>
</html>"""

def build_l7():
    notes_md = (RESEARCH_PANEL_L7 / "notas.md").read_text()
    dossier_md = (RESEARCH_PANEL_L7 / "dossier.md").read_text()
    sources_md = (RESEARCH_PANEL_L7 / "sources.md").read_text() if (RESEARCH_PANEL_L7 / "sources.md").exists() else ""
    version_match = re.search(r"v(\d+).*?(\d{4}-\d{2}-\d{2})", dossier_md[:500])
    version = version_match.group(1) if version_match else "?"
    version_date = version_match.group(2) if version_match else "?"
    body = f"""
<h1>🔬 L7 — Mediterranean Fusion (consolidación de dominio)</h1>
<p class="meta">
<span class="badge badge-active">Línea activa</span>
Versión vigente: <strong>v{version}</strong> ({version_date}) ·
Estado: <strong>esperando decisión A/B''/C/D de Dani</strong>
</p>

<p>Investigación viva sobre la consolidación del dominio <code>mediterraneanfusion.es</code> hacia <code>mf3.es</code> y/o <code>dindonliving.com</code>. Auditoría independiente del catálogo, evidencia Wayback, validación contra Google Search Central, propuesta de redirect selectivo dividido por intención.</p>

<h2>📌 Recomendación vigente</h2>
<blockquote><strong>B'' — Migración selectiva dividida por intención.</strong> Catálogo transaccional con equivalente real → evaluar <code>dindonliving.com</code>; páginas editoriales/servicios → evaluar <code>mf3.es</code>. 301 solo tras crear y validar el destino. Wildcard descartado.</blockquote>

<h2>📂 Entregables</h2>
<ul>
<li><a href="dossier.html">Dossier ejecutivo completo</a> — análisis, evidencia, opciones, plan B'</li>
<li><a href="notas.html">Notas de pulso</a> — últimas iteraciones de la investigación</li>
<li><a href="sources.html">Fuentes consultadas</a> — URLs oficiales y JSONs de evidencia</li>
<li><a href="data/">Datos JSON</a> — evidencia reproducible de cada versión</li>
</ul>

<h2>🧭 Línea de tiempo de versiones</h2>
<table>
<tr><th>v</th><th>Fecha</th><th>Hallazgo</th></tr>
<tr><td>v51</td><td>2026-07-21</td><td>Propuso wildcard — RETRACTADA</td></tr>
<tr><td>v53</td><td>2026-07-22</td><td>23/36 páginas de marca con contenido real vivo</td></tr>
<tr><td>v54</td><td>2026-07-22</td><td>Wayback proxy: 20/23 con 200 histórico</td></tr>
<tr><td>v55</td><td>2026-07-22</td><td>Sitemap con UA: 2.058 entradas anunciadas</td></tr>
<tr><td>v56</td><td>2026-07-22</td><td>Deduplicación: 1.877 productos únicos, 80,3% retail</td></tr>
<tr><td>v59</td><td>2026-07-23</td><td>FácilReformas aún enlaza a mediterraneanfusion.es</td></tr>
<tr><td>v60</td><td>2026-07-24</td><td>/mobalco1/ y /firmas/ con contenido paralelo</td></tr>
<tr><td>v66</td><td>2026-07-28</td><td>Validación oficial Google Search Central</td></tr>
<tr><td>v67</td><td>2026-07-29</td><td>Redirect strategy oficial + nota actual</td></tr>
</table>

<h2>⚠️ Decisión pendiente de Dani</h2>
<ol>
<li>¿Qué marcas del catálogo siguen siendo comerciales para MF3?</li>
<li>¿Consolidar en <code>mf3.es</code> o mantener vertical separado?</li>
<li>¿Puede facilitar acceso de solo lectura a GSC o export de backlinks?</li>
</ol>
"""
    (RESEARCH_PANEL_L7 / "index.html").write_text(page(f"L7 — Mediterranean Fusion · v{version}", body, active_nav="investigaciones"))
    body_dossier = f"""
<h1>Dossier ejecutivo — mediterraneanfusion.es</h1>
<p class="meta">Versión vigente <strong>v{version}</strong> · {version_date}</p>
{md_to_html(dossier_md)}
"""
    (RESEARCH_PANEL_L7 / "dossier.html").write_text(page(f"Dossier L7 · v{version}", body_dossier, active_nav="investigaciones"))
    body_notes = f"""
<h1>Notas de pulso — L7 Mediterranean Fusion</h1>
<p class="meta">Última versión: <strong>2026-07-29 00:04 (v67)</strong></p>
{md_to_html(notes_md)}
"""
    (RESEARCH_PANEL_L7 / "notas.html").write_text(page("Notas L7", body_notes, active_nav="investigaciones"))
    if sources_md:
        body_sources = f"""
<h1>Fuentes consultadas — L7</h1>
<p class="meta">Documentos canónicos y JSONs de evidencia</p>
{md_to_html(sources_md)}
<h2>📦 Datos JSON de evidencia</h2>
<ul>
<li><a href="data/l7_v66_google_redirect_official_guidance_2026-07-28.json">l7_v66_google_redirect_official_guidance_2026-07-28.json</a> — validación Google Search Central</li>
<li><a href="data/l7_v56_sitemap_structure_2026-07-22.json">l7_v56_sitemap_structure_2026-07-22.json</a> — estructura deduplicada</li>
</ul>
"""
        (RESEARCH_PANEL_L7 / "sources.html").write_text(page("Fuentes L7", body_sources, active_nav="investigaciones"))

def build_live():
    hb_state_path = WORKSPACE / "state" / "heartbeat-state.json"
    hb_state = {}
    if hb_state_path.exists():
        try:
            hb_state = json.loads(hb_state_path.read_text())
        except Exception:
            pass
    today_md = (WORKSPACE / "memory" / f"{DATE_STR}.md").read_text() if (WORKSPACE / "memory" / f"{DATE_STR}.md").exists() else ""
    yesterday = (NOW - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_md = (WORKSPACE / "memory" / f"{yesterday}.md").read_text() if (WORKSPACE / "memory" / f"{yesterday}.md").exists() else ""
    def extract_heartbeats(md_text):
        return [{"time": m.group(1), "body": m.group(2).strip()} for m in re.finditer(r"HB (\d{2}:\d{2})\s*[—\-]\s*(.+?)(?:\n|$)", md_text)]
    pulses_today = extract_heartbeats(today_md)
    pulses_yesterday = extract_heartbeats(yesterday_md)
    last_line = hb_state.get("lastResearchLine", "L7")
    last_version = hb_state.get("lastVersion", "?")
    next_line = hb_state.get("nextLine", last_line)
    body = f"""
<h1>🔴 Live — Lo que BRAIN está haciendo ahora</h1>
<p class="meta">
Actualizado <strong>{ISO_NOW}</strong> ·
Última línea investigada: <strong>{last_line}</strong> (v{last_version}) ·
Próxima: <strong>{next_line}</strong>
</p>

<h2>🟢 Pulso en curso</h2>
<div class="pulse">
<div class="pulse-time">{DATE_STR} {TIME_STR} (Europe/Berlin)</div>
<div class="pulse-body">
Investigación activa: <strong>{last_line}</strong> · versión <strong>v{last_version}</strong>.
Hallazgos en <a href="research/L7_MediterraneanFusion/notas.html">L7 / Notas</a>.
Próximo paso natural: {next_line}.
</div>
</div>

<h2>📡 Últimos pulsos de hoy ({DATE_STR})</h2>
"""
    if pulses_today:
        for p in reversed(pulses_today[-8:]):
            body += f"""
<div class="pulse">
<div class="pulse-time">{DATE_STR} {p['time']}</div>
<div class="pulse-body">{escape(p['body'])}</div>
</div>
"""
    else:
        body += "<p>Sin pulsos registrados hoy todavía.</p>"
    body += f"<h2>📅 Pulsos de ayer ({yesterday})</h2>"
    if pulses_yesterday:
        for p in reversed(pulses_yesterday[-8:]):
            body += f"""
<div class="pulse">
<div class="pulse-time">{yesterday} {p['time']}</div>
<div class="pulse-body">{escape(p['body'])}</div>
</div>
"""
    else:
        body += "<p>Sin pulsos registrados ayer.</p>"
    body += "<h2>🔬 L7 — última nota</h2>"
    body += md_to_html((RESEARCH_PANEL_L7 / "notas.md").read_text())
    body += "<h2>📊 Estado del sistema</h2>"
    if hb_state:
        body += "<ul>"
        for k, v in hb_state.items():
            if isinstance(v, (str, int, float)):
                body += f"<li><code>{k}</code> = <strong>{escape(str(v))}</strong></li>"
        body += "</ul>"
    (PANEL / "live.html").write_text(page("Live · BRAIN", body, active_nav="live"))

def update_index():
    idx = PANEL / "index.html"
    if not idx.exists():
        return
    html = idx.read_text()
    l7_card = """
<div class="card" style="border-color: #ff4444;">
<h2>🔴 L7 MediterraneanFusion (EN VIVO)</h2>
<p>Consolidación dominio mediterraneanfusion.es. v66 con validación oficial Google Search Central. Recomendación B'': 301 selectivo dividido por intención.</p>
<div class="card-meta"><span>📂 research/L7_MediterraneanFusion/</span><span style="color: #ff4444;">● ACTIVA</span></div>
<a href="research/L7_MediterraneanFusion/" class="btn">Ver →</a>
</div>
"""
    if 'L7_MediterraneanFusion' not in html:
        marker = '<div class="section-title">📊 Investigaciones Activas</div>'
        idx_marker = html.find(marker)
        if idx_marker >= 0:
            grid_start = html.find('<div class="grid">', idx_marker)
            first_card_close = html.find('</div>', grid_start)
            if first_card_close >= 0:
                first_card_close = html.find('</div>', first_card_close + 6)
                html = html[:first_card_close + 6] + l7_card + html[first_card_close + 6:]
    new_priorities = """
<div class="priorities">
<h3>⚠️ Prioridades Críticas (actualizado 2026-07-29)</h3>
<div class="priority-item">
<span>🔴 L7 — Decidir consolidación mediterraneanfusion.es</span>
<span style="color: #888;">Opción B'' (migración selectiva) recomendada; wildcard descartado.</span>
<span class="badge badge-critical">decisión</span>
</div>
<div class="priority-item">
<span>🟠 Director — 🔴 URGENTE: pasar transferencia ICO</span>
<span style="color: #888;">Tarea manual_priority 1 en cola del director, vence HOY.</span>
<span class="badge badge-high">hoy</span>
</div>
<div class="priority-item">
<span>🟠 Meta descriptions todas las webs</span>
<span style="color: #888;">8 webs sin meta descriptions. Listas para copiar/pegar.</span>
<span class="badge badge-high">2 horas</span>
</div>
</div>
"""
    if "L7 — Decidir consolidación" not in html:
        old_priorities_start = html.find('<div class="priorities">')
        old_priorities_end = html.find('</div>\n</body>', old_priorities_start)
        if old_priorities_start >= 0 and old_priorities_end >= 0:
            html = html[:old_priorities_start] + new_priorities + html[old_priorities_end:]
    html = re.sub(r'<div class="stat-value">11</div>\s*<div class="stat-label">Investigaciones</div>',
                  '<div class="stat-value">12</div>\n<div class="stat-label">Investigaciones</div>', html)
    if 'href="live.html"' not in html:
        html = html.replace('<a href="index.html" class="active">📊 Dashboard</a>',
                            '<a href="index.html" class="active">📊 Dashboard</a> <a href="live.html">🔴 Live</a>')
    idx.write_text(html)

def main():
    print(f"[build_panel] {ISO_NOW}")
    if "--live-only" in sys.argv[1:]:
        build_live()
        print("[build_panel] live.html actualizado")
        return
    build_l7()
    build_live()
    update_index()
    print("[build_panel] OK — L7 + live + index actualizados")

if __name__ == "__main__":
    main()
