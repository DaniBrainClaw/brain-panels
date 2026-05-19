#!/usr/bin/env python3
"""Convert AUDITORIA markdown files to HTML."""
from pathlib import Path

def md_to_html(content, title):
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: system-ui; background: #0a0a0f; color: #e0e0e0; padding: 20px; max-width: 900px; margin: 0 auto; line-height: 1.6; }}
        h1 {{ color: #00d4aa; font-size: 28px; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        h2 {{ color: #ffd93d; margin-top: 30px; font-size: 20px; }}
        h3 {{ color: #ff6b6b; margin-top: 20px; font-size: 16px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background: #00d4aa; color: #000; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border: 1px solid #333; }}
        td {{ background: #111; }}
        tr:hover td {{ background: #1a1a24; }}
        code {{ background: #1a1a24; padding: 2px 6px; border-radius: 4px; color: #ffd93d; }}
        a {{ color: #00d4aa; }}
        .back {{ display: inline-block; background: #1a1a24; color: #00d4aa; padding: 12px 20px; border-radius: 8px; text-decoration: none; margin-bottom: 20px; }}
        .back:hover {{ background: #00d4aa; color: #000; }}
        li {{ margin: 5px 0; }}
        hr {{ border: none; border-top: 1px solid #333; margin: 20px 0; }}
        strong {{ color: #ffd93d; }}
        .score {{ font-size: 24px; font-weight: bold; color: #00d4aa; }}
    </style>
</head>
<body>
    <a href="INDEX.html" class="back">← Volver al índice</a>
    {content}
</body>
</html>'''

def convert_file(src_path):
    content = src_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    html_parts = []
    table_rows = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('## ') and not line.startswith('### '):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and all(c.replace('-','').replace(':','').replace('','').isalnum() or c == '' for c in cells):
                continue  # skip separator row
            row = '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
            table_rows.append(row)
            in_table = True
        elif line.startswith('- '):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<li>{line[2:]}</li>')
        elif line.startswith('**') and line.endswith('**'):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<p><strong>{line[2:-2]}</strong></p>')
        elif line.startswith('`') and line.endswith('`'):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<code>{line[1:-1]}</code>')
        elif line.startswith('---'):
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append('<hr>')
        elif line == '':
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
        else:
            if in_table:
                html_parts.append('<table>' + ''.join(table_rows) + '</table>')
                table_rows = []
                in_table = False
            html_parts.append(f'<p>{line}</p>')
    
    if table_rows:
        html_parts.append('<table>' + ''.join(table_rows) + '</table>')
    
    title = src_path.stem.replace('_', ' ').replace('AUDITORIA ', '').title()
    html = md_to_html('\n'.join(html_parts), title)
    dst_path = src_path.with_suffix('.html')
    dst_path.write_text(html, encoding='utf-8')
    return dst_path.name

src_dir = Path('/data/.openclaw/workspace/brain-panels-local/research/Web_Audit/full')
for f in sorted(src_dir.glob('AUDITORIA_*.md')):
    result = convert_file(f)
    print(f'Converted {f.name} -> {result}')