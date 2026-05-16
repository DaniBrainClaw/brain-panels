#!/usr/bin/env python3
"""Convert markdown files to HTML - Fixed version."""

import re
import os
from pathlib import Path

PANEL_DIR = Path("/data/.openclaw/workspace/brain-panels-local")
RESEARCH_SOURCE = Path("/data/.openclaw/agents/investigador/workspace/Research")
RESEARCH_OVERNIGHT = Path("/data/.openclaw/workspace/research/overnight")
OUTPUT_RESEARCH = PANEL_DIR / "research"

def convert_file(md_path):
    """Convert single markdown file to HTML."""
    html_path = Path(str(md_path).replace('.md', '.html'))
    
    # Read markdown
    content = md_path.read_text(encoding='utf-8')
    
    # Get title from first heading or filename
    title_match = re.match(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else md_path.stem
    
    # Remove the title line
    content = re.sub(r'^# .+\n', '', content, count=1)
    
    # Convert markdown to HTML
    # Headers
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Code blocks - handle properly
    content = re.sub(r'```\w*\n(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
    
    # Inline code
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    
    # Bold and italic
    content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)
    
    # Tables
    table_pattern = re.compile(r'^(\|.+\|\n)+', re.MULTILINE)
    tables_found = table_pattern.findall(content)
    for table_text in tables_found:
        lines = [l for l in table_text.split('\n') if l.strip()]
        if len(lines) < 2:
            continue
        html_table = '<table>\n'
        for i, line in enumerate(lines):
            if i == 1 and re.match(r'^\|[\s|-]+\|$', line):
                continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            tag = 'th' if i == 0 else 'td'
            html_table += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cols) + '</tr>\n'
        html_table += '</table>\n'
        content = content.replace(table_text, html_table)
    
    # Lists
    content = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', content, flags=re.MULTILINE)
    content = re.sub(r'^[-*] (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', content)
    
    # Blockquotes
    content = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
    
    # Horizontal rules
    content = re.sub(r'^---+$', '<hr>', content, flags=re.MULTILINE)
    
    # Links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
    
    # Paragraphs
    paragraphs = []
    for block in content.split('\n\n'):
        block = block.strip()
        if not block:
            continue
        if block.startswith('<') or block.startswith('|'):
            paragraphs.append(block)
        else:
            paragraphs.append(f'<p>{block}</p>')
    
    body = '\n'.join(paragraphs)
    
    # Build full HTML
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; line-height: 1.6; background: #0f0f23; color: #eee; }}
        h1 {{ color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }}
        h2 {{ color: #e94560; margin-top: 30px; }}
        h3 {{ color: #0f3460; }}
        code {{ background: #1a1a2e; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #1a1a2e; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
        th {{ background: #e94560; color: white; }}
        tr:nth-child(even) {{ background: #1a1a2e; }}
        .back-link {{ background: #e94560; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 20px; }}
        .back-link:hover {{ background: #fff; color: #e94560; }}
        .filename {{ color: #888; font-size: 0.9em; margin-bottom: 20px; }}
        blockquote {{ border-left: 4px solid #e94560; margin: 0; padding-left: 20px; color: #aaa; }}
        img {{ max-width: 100%; height: auto; }}
        a {{ color: #e94560; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← Panel Principal</a>
    <p class="filename">📄 {md_path.name}</p>
    {body}
</body>
</html>'''
    
    # Write
    html_path.write_text(html, encoding='utf-8')
    return True

def process_folder(src, dst):
    """Process all markdown files in a folder."""
    dst.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for md in src.glob('*.md'):
        try:
            convert_file(md)
            count += 1
            print(f'  ✅ {md.name}')
        except Exception as e:
            print(f'  ❌ {md.name}: {e}')
    
    # Subfolder findings/
    if src.exists():
        for md in src.rglob('*.md'):
            if 'findings' in str(md):
                rel_path = md.relative_to(src)
                dst_path = dst / rel_path
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    convert_file(md)
                    count += 1
                    print(f'  ✅ {md.name}')
                except Exception as e:
                    print(f'  ❌ {md.name}: {e}')
    
    return count

def main():
    print('=== JOB-033: Markdown to HTML ===\n')
    total = 0
    
    folders = [
        ('OpenClaw', RESEARCH_SOURCE / 'OpenClaw'),
        ('ROI_Agent_Optimization', RESEARCH_SOURCE / 'ROI_Agent_Optimization'),
        ('MVP_Monetization', RESEARCH_SOURCE / 'MVP_Monetization'),
        ('Web_Audit', RESEARCH_SOURCE / 'Web_Audit'),
        ('MiniMax_M2.7_analysis', RESEARCH_SOURCE / 'MiniMax_M2.7_analysis'),
        ('Hermes_Agent_Analysis', RESEARCH_SOURCE / 'Hermes_Agent_Analysis'),
        ('GitHub_BRAIN_Integration', RESEARCH_SOURCE / 'GitHub_BRAIN_Integration'),
        ('Tareas_Autonomas', RESEARCH_SOURCE / 'Tareas_Autonomas'),
    ]
    
    for name, path in folders:
        print(f'📁 {name}')
        dst = OUTPUT_RESEARCH / name
        if path.exists():
            total += process_folder(path, dst)
        else:
            print(f'  ⚠️ No existe: {path}')
        print()
    
    # Overnight
    print('📁 overnight')
    for md in RESEARCH_OVERNIGHT.glob('*.md'):
        try:
            convert_file(md)
            total += 1
            print(f'  ✅ {md.name}')
        except Exception as e:
            print(f'  ❌ {md.name}: {e}')
    
    print(f'\n=== Total: {total} archivos convertidos ===')

if __name__ == '__main__':
    main()