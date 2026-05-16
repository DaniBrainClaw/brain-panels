# GitHub + BRAIN Integration — Query 1: GitHub API Automation Scripts Backup System

**Fecha:** 2026-05-16
**Query:** "GitHub API automation scripts backup system"
**Resultados:** 20 found

---

## Fuentes

1. **How to Automate OpenClaw Backup and Optimization with GitHub** — dev.to (Tutorial específico para OpenClaw + GitHub)
2. **The Ultimate Developer's Guide to GitHub Backups** — simplebackups.com
3. **GitHub Backup Scripts (Topics)** — github.com/topics/backup-scripts
4. **GitHub Automated Backup** — github.com/topics/automated-backup

---

## OpenClaw + GitHub Backup (Tutorial Completo)

**Fuente:** dev.to — "How to Automate OpenClaw Backup and Optimization with GitHub"

### Por qué GitHub para backup:

| Opción | Problema |
|--------|----------|
| Dropbox/Google Drive | No versiona automáticamente, sin diff visual |
| Manual tar | Requiere intervención humana, no escala |
| **GitHub (private)** | ✅ Versioning automático, diff visual, rollback fácil, gratis, accesible |

### Qué hacer backup:

**1. Core Files (críticos):**
- `AGENTS.md` — Operational instructions
- `SOUL.md` — Personality
- `USER.md` — Info about Dani
- `TOOLS.md` — Local notes
- `MEMORY.md` — Long-term memory

**2. Custom Skills:**
- `skills/` directory

**3. Automation Scripts:**
- `scripts/` directory

---

## Script de Sync para BRAIN

```bash
#!/bin/bash
# sync-core-to-github.sh
# Syncs core files and skills to GitHub repo

set -e  # Exit on error

echo "🔄 Starting sync..."

# Detect repo name automatically
REPO_DIR=$(find ~/clawd/repos -maxdepth 1 -type d -name "core-*" | head -n 1)

if [ -z "$REPO_DIR" ]; then
    echo "❌ Error: No core-* repo found"
    exit 1
fi

cd "$REPO_DIR"

# Pull first
echo "📥 Pulling remote changes..."
git pull origin main

# Copy CORE files
echo "📋 Copying core files..."
cp ~/clawd/*.md .

# Copy SKILLS
echo "🛠️ Copying skills..."
cp -r ~/clawd/skills .

# Copy SCRIPTS
echo "📜 Copying scripts..."
cp -r ~/clawd/scripts .

# Git add
echo "📦 Staging changes..."
git add .

# Check if there are changes
if git diff --staged --quiet; then
    echo "✅ No new changes"
    exit 0
fi

# Commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "Auto-sync: $TIMESTAMP"

# Push
echo "⬆️ Pushing to GitHub..."
git push origin main

echo "✅ Sync complete"
```

---

## .gitignore Estratégico

```gitignore
# Secrets
**/.config/credentials.json
**/.env
**/api_key
secrets/

# Temporary
*.log
*.tmp
temp-*
**/node_modules/
**/__pycache__/

# OS
.DS_Store
```

---

## Automatización con Cron

```bash
# crontab -e
# Cada día a las 3 AM: optimizar y sync
0 3 * * * /home/user/clawd/scripts/optimize-core.sh >> /home/user/clawd/logs/optimize.log 2>&1
5 3 * * * /home/user/clawd/scripts/sync-core.sh >> /home/user/clawd/logs/sync-core.log 2>&1
```

---

## Python Script — Backup vía GitHub API

```python
import os
import requests

GITHUB_TOKEN = 'your_github_token'
REPO_OWNER = 'username'
REPO_NAME = 'repository'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def backup_repo():
    repo_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}'
    response = requests.get(repo_url, headers=headers)
    with open(f'{REPO_NAME}_repo.json', 'w') as f:
        f.write(response.text)
    print(f'Repository metadata backed up')

def backup_issues():
    issues_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    response = requests.get(issues_url, headers=headers)
    with open(f'{REPO_NAME}_issues.json', 'w') as f:
        f.write(response.text)
    print(f'Issues backed up')

def backup_pull_requests():
    pulls_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls'
    response = requests.get(pulls_url, headers=headers)
    with open(f'{REPO_NAME}_pulls.json', 'w') as f:
        f.write(response.text)
    print(f'Pull requests backed up')

backup_repo()
backup_issues()
backup_pull_requests()
```

---

## Git Clone para Backup Completo

```bash
# Clone con mirror (todas las ramas, todos los tags)
git clone --mirror https://github.com/username/repository.git

# Luego agregar remote de backup y push
git remote add backup https://backupserver.com/username/repository.git
git push --mirror backup
```

### Múltiples remotes para push automático:

```bash
# Configurar origin para push a dos URLs
git remote set-url --add --push origin https://primary-repo.com/user/repo.git
git remote set-url --add --push origin https://backup-repo.com/user/repo.git

# Ver configuración
git remote -v
# origin  https://primary-repo.com/user/repo.git (fetch)
# origin  https://primary-repo.com/user/repo.git (push)
# origin  https://backup-repo.com/user/repo.git (push)
```

---

## Backup de Wiki y Project Boards

```bash
# Wiki
git clone https://github.com/username/repository.wiki.git

# Project boards via API (Python script del artículo)
```

---

## Quick Start — BRAIN puede hacerlo solo

**Dani solo necesita decirle a BRAIN:**
> "Hey, automatically backup my core files to GitHub. My token is `ghp_XXXXX` and my username is `DaniBrainClaw`. Create a private repo and sync everything."

**BRAIN entiende, configura, y confirma cuando está listo.**

---

*Investigador — Query 1 completada.*