#!/bin/bash
# JOB-033: Convertir markdown a HTML para GitHub Pages Panel
# Ubicación: /data/.openclaw/workspace/brain-panels-local/

PANEL_DIR="/data/.openclaw/workspace/brain-panels-local"
RESEARCH_SOURCE="/data/.openclaw/agents/investigador/workspace/Research"
RESEARCH_OVERNIGHT="/data/.openclaw/workspace/research/overnight"
OUTPUT_RESEARCH="$PANEL_DIR/research"

echo "=== JOB-033: Markdown to HTML Converter ==="
echo "Panel dir: $PANEL_DIR"
echo "Source research: $RESEARCH_SOURCE"
echo ""

# Función para convertir markdown a HTML
convert_md_to_html() {
    local md_file="$1"
    local html_file="${md_file%.md}.html"
    
    if [ ! -f "$md_file" ]; then
        echo "  ⚠️ No existe: $md_file"
        return 1
    fi
    
    # Verificar si ya es más reciente que el html
    if [ -f "$html_file" ] && [ "$md_file" -ot "$html_file" ]; then
        echo "  ✓ Saltado (ya actualizado): $(basename $md_file)"
        return 0
    fi
    
    # Crear HTML con estilo
    local title=$(head -1 "$md_file" | sed 's/^#* //' | sed 's/<\/[^>]*>//g')
    local filename=$(basename "$md_file")
    
    cat > "$html_file" << HTML_EOF
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        h1 { color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 10px; }
        h2 { color: #16213e; margin-top: 30px; }
        h3 { color: #0f3460; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #1a1a2e; color: #eee; padding: 15px; border-radius: 5px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #e94560; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        .back-link { background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 20px; }
        .back-link:hover { background: #16213e; }
        .filename { color: #888; font-size: 0.9em; margin-bottom: 20px; }
        blockquote { border-left: 4px solid #e94560; margin: 0; padding-left: 20px; color: #555; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <a href="index.html" class="back-link">← Panel Principal</a>
    <p class="filename">📄 $filename</p>
HTML_EOF

    # Convertir markdown a HTML (manejar tablas y código)
    python3 << PYEOF >> "$html_file"
import re

with open("$md_file", "r", encoding="utf-8") as f:
    content = f.read()

# Saltar el título H1 (ya está en el <title>)
content = re.sub(r'^# .+\n', '', content, count=1)

# Encabezados
content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)

# Code blocks
content = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', content, flags=re.DOTALL)

# Inline code
content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)

# Negrita e italica
content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)

# Tablas
table_match = re.search(r'(\|.+\|\n)+', content)
if table_match:
    table_text = table_match.group(0)
    lines = table_text.strip().split('\n')
    html_table = '<table>\n'
    for i, line in enumerate(lines):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if i == 1:  # separator
            continue
        tag = 'th' if i == 0 else 'td'
        html_table += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cols) + '</tr>\n'
    html_table += '</table>\n'
    content = content[:table_match.start()] + html_table + content[table_match.end():]

# Listas
content = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
content = re.sub(r'^[-*] (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)

# Wrap consecutive <li> in <ul>
content = re.sub(r'(<li>.*?</li>\n)+', lambda m: '<ul>' + m.group(0) + '</ul>', content)

# Blockquotes
content = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)

# Horizontal rules
content = re.sub(r'^---+$', '<hr>', content)

# Links
content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)

# Paragraphs (líneas vacías como separadores)
content = re.sub(r'\n\n+', '\n\n', content)
paragraphs = content.split('\n\n')
for p in paragraphs:
    p = p.strip()
    if p and not p.startswith('<') and not p.startswith('|'):
        print(f'<p>{p}</p>')
    elif p:
        print(p)

print('\n</body>\n</html>')
PYEOF
    
    echo "  ✅ Convertido: $(basename $md_file)"
}

echo "=== Copiando investigación desde source ==="
# Copiar archivos sueltos (INDEX, SUMMARY, sources) de cada carpeta de investigación
for folder in OpenClaw ROI_Agent_Optimization MVP_Monetization Web_Audit MiniMax_M2.7_analysis Hermes_Agent_Analysis GitHub_BRAIN_Integration Tareas_Autonomas OpenClaw_Panels Monetization_BRAIN; do
    if [ -d "$RESEARCH_SOURCE/$folder" ]; then
        echo "📁 Procesando: $folder"
        
        # Crear carpeta destino si no existe
        mkdir -p "$OUTPUT_RESEARCH/$folder"
        
        # Copiar archivos .md sueltos
        for md in "$RESEARCH_SOURCE/$folder"/*.md; do
            if [ -f "$md" ]; then
                convert_md_to_html "$md"
            fi
        done
        
        # Procesar subcarpetas findings/
        if [ -d "$RESEARCH_SOURCE/$folder/findings" ]; then
            mkdir -p "$OUTPUT_RESEARCH/$folder/findings"
            for md in "$RESEARCH_SOURCE/$folder/findings"/*.md; do
                if [ -f "$md" ]; then
                    convert_md_to_html "$md"
                fi
            done
        fi
    else
        echo "  ⚠️ No encontrado: $RESEARCH_SOURCE/$folder"
    fi
done

echo ""
echo "=== Copiando research/overnight ==="
for md in "$RESEARCH_OVERNIGHT"/*.md; do
    if [ -f "$md" ]; then
        convert_md_to_html "$md"
    fi
done

echo ""
echo "=== Actualizando index.html principal ==="
# Actualizar index.html con todos los исследования
cat > "$PANEL_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRAIN Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; background: #0f0f23; color: #eee; }
        h1 { color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }
        h2 { color: #e94560; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .card { background: #1a1a2e; border-radius: 10px; padding: 20px; border: 1px solid #e94560; }
        .card h3 { color: #e94560; margin-top: 0; }
        .card p { color: #aaa; font-size: 0.9em; }
        .card a { background: #e94560; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px; }
        .card a:hover { background: #fff; color: #e94560; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }
        .badge-critical { background: #e94560; }
        .badge-high { background: #f39c12; }
        .badge-medium { background: #3498db; }
        .badge-low { background: #27ae60; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat { background: #1a1a2e; padding: 15px 25px; border-radius: 10px; text-align: center; }
        .stat-value { font-size: 2em; color: #e94560; font-weight: bold; }
        .stat-label { color: #aaa; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>🧠 BRAIN Dashboard</h1>
    <p>Sistema de investigación continua — Panel público</p>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">11</div>
            <div class="stat-label">Investigaciones</div>
        </div>
        <div class="stat">
            <div class="stat-value">143+</div>
            <div class="stat-label">Archivos</div>
        </div>
        <div class="stat">
            <div class="stat-value">85+</div>
            <div class="stat-label">Fuentes consultadas</div>
        </div>
    </div>

    <h2>📊 Investigaciones Activas</h2>
    <div class="grid">
        <div class="card">
            <h3>🔍 OpenClaw Deep Dive</h3>
            <p>Hooks, skills, agents, patterns avanzados.</p>
            <span class="badge badge-high">25 archivos</span>
            <a href="research/OpenClaw/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>📈 ROI Agent Optimization</h3>
            <p>1,250-12,500% ROI potencial. Cómo rentabilizar BRAIN.</p>
            <span class="badge badge-high">13 archivos</span>
            <a href="research/ROI_Agent_Optimization/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>💰 MVP Monetization</h3>
            <p>8 pasos para €1,000/mes con coaches.</p>
            <span class="badge badge-medium">11 archivos</span>
            <a href="research/MVP_Monetization/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>🌐 Web Audit</h3>
            <p>8 webs analizadas. Score: 5-7.5/10.</p>
            <span class="badge badge-medium">9 archivos</span>
            <a href="research/Web_Audit/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>🧠 MiniMax M2.7 Analysis</h3>
            <p>Coding 78%, Agentic ELO 1495.</p>
            <span class="badge badge-high">17 archivos</span>
            <a href="research/MiniMax_M2.7_analysis/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>🔗 GitHub BRAIN Integration</h3>
            <p>Backup automático, panels públicos.</p>
            <span class="badge badge-medium">8 archivos</span>
            <a href="research/GitHub_BRAIN_Integration/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>🤖 Hermes Agent Analysis</h3>
            <p>Agente de nudge periódico.</p>
            <span class="badge badge-low">5 archivos</span>
            <a href="research/Hermes_Agent_Analysis/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>⚡ Tareas Autónomas</h3>
            <p>Script para procesar 3905 filas sin preguntar.</p>
            <span class="badge badge-low">4 archivos</span>
            <a href="research/Tareas_Autonomas/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>🎨 OpenClaw Panels</h3>
            <p>Paneles interactivos y canvas.</p>
            <span class="badge badge-low">en desarrollo</span>
            <a href="research/OpenClaw_Panels/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>💵 Monetization BRAIN</h3>
            <p>Cómo monetizar el sistema BRAIN.</p>
            <span class="badge badge-medium">en desarrollo</span>
            <a href="research/Monetization_BRAIN/index.html">Ver →</a>
        </div>
        <div class="card">
            <h3>🏛️ Web Implementation Plan</h3>
            <p>Plan de 4 semanas para optimizar webs.</p>
            <span class="badge badge-high">actualizado</span>
            <a href="WEB_IMPLEMENTATION_PLAN.html">Ver →</a>
        </div>
    </div>

    <h2>⚠️ Prioridades Críticas</h2>
    <div class="grid">
        <div class="card">
            <h3>🔴 SSL estudiovirtual.es CRÍTICO</h3>
            <p>Sin SSL — Chrome marca como "no seguro". Contactar Diewaves.</p>
            <span class="badge badge-critical">30 min</span>
        </div>
        <div class="card">
            <h3>🔴 Decidir multi-dominio MF3</h3>
            <p>mf3.es vs mediterraneanfusion.es — confusión SEO.</p>
            <span class="badge badge-critical">decisión</span>
        </div>
    </div>

    <p style="text-align: center; color: #666; margin-top: 40px;">
        Generado automáticamente por BRAIN — Sistema de investigación continua
    </p>
</body>
</html>
EOF

echo "✅ index.html actualizado"

echo ""
echo "=== Actualizando investigaciones.html ==="
cat > "$PANEL_DIR/investigaciones.html" << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investigaciones - BRAIN</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #0f0f23; color: #eee; }
        h1 { color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }
        .inv { background: #1a1a2e; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 4px solid #e94560; }
        .inv h2 { color: #e94560; margin-top: 0; }
        .inv a { background: #e94560; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; }
        .files { color: #aaa; font-size: 0.9em; margin: 10px 0; }
        .back-link { background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <a href="index.html" class="back-link">← Panel Principal</a>
    <h1>📚 Investigaciones Completas</h1>
    
    <div class="inv">
        <h2>🔍 OpenClaw Deep Dive</h2>
        <p>Hooks, skills, agents, patterns avanzados. 25 archivos de investigación.</p>
        <div class="files">📂 research/OpenClaw/</div>
        <a href="research/OpenClaw/index.html">Ver investigación →</a>
    </div>
    
    <div class="inv">
        <h2>📈 ROI Agent Optimization</h2>
        <p>1,250-12,500% ROI potencial. Cómo rentabilizar BRAIN.</p>
        <div class="files">📂 research/ROI_Agent_Optimization/</div>
        <a href="research/ROI_Agent_Optimization/index.html">Ver investigación →</a>
    </div>
    
    <div class="inv">
        <h2>💰 MVP Monetization</h2>
        <p>8 pasos para €1,000/mes con coaches. Landing + outreach + pricing.</p>
        <div class="files">📂 research/MVP_Monetization/</div>
        <a href="research/MVP_Monetization/index.html">Ver investigación →</a>
    </div>
    
    <div class="inv">
        <h2>🌐 Web Audit</h2>
        <p>8 webs analizadas. Score: 5-7.5/10. 3 problemas críticos.</p>
        <div class="files">📂 research/Web_Audit/</div>
        <a href="research/Web_Audit/index.html">Ver investigación →</a>
    </div>
    
    <div class="inv">
        <h2>🧠 MiniMax M2.7 Analysis</h2>
        <p>Coding 78%, Agentic ELO 1495. Mejor modelo para código.</p>
        <div class="files">📂 research/MiniMax_M2.7_analysis/</div>
        <a href="research/MiniMax_M2.7_analysis/index.html">Ver investigación →</a>
    </div>
    
    <div class="inv">
        <h2>🤖 Hermes Agent Analysis</h2>
        <p>Agente de nudge periódico. 5 archivos.</p>
        <div class="files">📂 research/Hermes_Agent_Analysis/</div>
        <a href="research/Hermes_Agent_Analysis/index.html">Ver investigación →</a>
    </div>
    
    <div class="inv">
        <h2>⚡ Tareas Autónomas</h2>
        <p>Script para procesar 3905 filas sin preguntar.</p>
        <div class="files">📂 research/Tareas_Autonomas/</div>
        <a href="research/Tareas_Autonomas/index.html">Ver investigación →</a>
    </div>
    
    <p style="text-align: center; color: #666; margin-top: 40px;">
        Generado automáticamente por BRAIN — 2026-05-17
    </p>
</body>
</html>
EOF

echo "✅ investigaciones.html actualizado"

echo ""
echo "=== Resumen ==="
echo "Archivos convertidos:"
find "$OUTPUT_RESEARCH" -name "*.html" 2>/dev/null | wc -l
echo ""
echo "✅ JOB-033 conversión completada"