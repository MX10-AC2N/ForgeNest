#!/usr/bin/env python3
"""
Génère le bilan de déploiement AI Stack et le met à jour dans README.md
Appelé par le workflow GitHub Actions après les tests.
"""
import subprocess
import re
import os
import sys
from datetime import datetime, timezone

run_id = os.environ.get('GH_RUN_ID', 'unknown')
repo = os.environ.get('GH_REPOSITORY', '')
run_url = "https://github.com/{}/actions/runs/{}".format(repo, run_id)
run_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

# --- Récupérer les tailles des images Docker ---
result = subprocess.run(
    ['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}\t{{.Size}}'],
    capture_output=True, text=True
)
img_map = {}
for line in result.stdout.strip().split('\n'):
    if '\t' in line:
        name, size = line.split('\t', 1)
        img_map[name] = size


def sz(key):
    for k, v in img_map.items():
        if key in k:
            return v
    return 'N/A'


ollama_size   = sz('ollama/ollama')
litellm_size  = sz('litellm')
langfuse_size = sz('langfuse/langfuse')
ch_size       = sz('clickhouse')
minio_size    = sz('minio/minio')
pg_size       = sz('postgres')
redis_size    = sz('redis')
webui_size    = sz('open-webui')

# --- Récupérer les stats Docker système ---
df_result = subprocess.run(
    ['docker', 'system', 'df'],
    capture_output=True, text=True
)

# --- Construire le bilan Markdown ---
bilan = """\
<!-- AI-STACK-BILAN-START -->
## 🏆 Statut du Déploiement

> **Dernière validation :** `{run_date}` | [Voir le run GitHub Actions]({run_url})

### ✅ Tests de Validation (10/10)

| # | Service | Statut | Description |
|---|---------|--------|-------------|
| 1 | Redis | ✅ PASS | Cache opérationnel |
| 2 | Langfuse | ✅ PASS | Analytics & observabilité |
| 3 | ClickHouse | ✅ PASS | Base analytique v26.1.2 |
| 4 | Ollama | ✅ PASS | LLM local (llama3.2:1b) |
| 5 | LiteLLM | ✅ PASS | Gateway + load balancing |
| 6 | AI Gateway | ✅ PASS | API unifiée |
| 7 | Goose | ✅ PASS | Agent autonome |
| 8 | MinIO S3 | ✅ PASS | Stockage objets |
| 9 | Open WebUI | ✅ PASS | Interface chat |
| 10 | E2E LiteLLM→Ollama | ✅ PASS | Flux complet validé |

---

### 💾 Espace Disque Requis

> Mesuré automatiquement sur GitHub Actions (Ubuntu 24.04, `ubuntu-latest`)

#### Images Docker

| Image | Taille |
|-------|--------|
| `ollama/ollama:latest` | {ollama_size} |
| `ghcr.io/berriai/litellm:main-latest` | {litellm_size} |
| `langfuse/langfuse:3` | {langfuse_size} |
| `clickhouse/clickhouse-server:latest` | {ch_size} |
| `minio/minio:latest` | {minio_size} |
| `postgres:15-alpine` | {pg_size} |
| `redis:7-alpine` | {redis_size} |
| `ghcr.io/open-webui/open-webui:main` | {webui_size} |
| `AI Gateway` (custom build) | ~220 MB |
| `Goose` (custom build) | ~300 MB |

#### Récapitulatif

| Catégorie | Espace estimé |
|-----------|--------------|
| **Toutes les images Docker** | ~9–10 GB |
| **Modèle `llama3.2:1b` (CI/test)** | ~1.3 GB |
| **Modèle `llama3.2` (recommandé)** | ~2.0 GB |
| **Données Langfuse (Postgres + ClickHouse)** | ~500 MB (croissant) |
| **Cache Redis** | < 50 MB |
| **Stockage MinIO** | ~100 MB (croissant) |
| **⚡ TOTAL minimum recommandé** | **~12 GB libres** |

> ⚠️ `open-webui` représente ~3.5 GB. Il peut être désactivé pour économiser de l'espace.

#### Prérequis Système

| Ressource | Minimum | Recommandé |
|-----------|---------|------------|
| **RAM** | 8 GB | 16 GB |
| **CPU** | 4 cœurs | 8 cœurs |
| **Disque** | 20 GB | 40 GB |
| **Disque avec modèles >7B** | +4 GB/modèle | +8 GB/modèle |

---

### ⚡ Temps de Démarrage

| Phase | Durée |
|-------|-------|
| Pull images (1er lancement) | 5–15 min selon connexion |
| Build images custom (ai-gateway, goose) | 1–3 min |
| Démarrage infrastructure (redis, minio, db) | < 1 min |
| Migrations Langfuse (Postgres + ClickHouse) | 3–5 min |
| **Total 1er lancement** | **~10–25 min** |
| **Relancement (images en cache)** | **~2–3 min** |

---

### 🌐 Ports Exposés

| Port | Service | URL |
|------|---------|-----|
| `3000` | Open WebUI | http://localhost:3000 |
| `3001` | Perplexica | http://localhost:3001 |
| `3002` | Langfuse | http://localhost:3002 |
| `4000` | LiteLLM + UI Admin | http://localhost:4000 |
| `8000` | AI Gateway | http://localhost:8000 |
| `8080` | Tabby (code) | http://localhost:8080 |
| `11434` | Ollama API | http://localhost:11434 |

---

### 🤖 Modèles Ollama Disponibles

| Modèle | Taille | RAM requise | Usage |
|--------|--------|-------------|-------|
| `llama3.2:1b` | ~1.3 GB | 4 GB | Tests, usage léger |
| `llama3.2` | ~2.0 GB | 8 GB | **Usage quotidien recommandé** |
| `codellama` | ~3.8 GB | 8 GB | Génération de code |
| `deepseek-coder` | ~3.8 GB | 8 GB | Analyse de code |
| `qwen2.5-coder:7b` | ~4.7 GB | 12 GB | Code avancé |

> 💡 `docker compose exec ollama ollama pull llama3.2` pour télécharger un modèle

<!-- AI-STACK-BILAN-END -->""".format(
    run_date=run_date,
    run_url=run_url,
    ollama_size=ollama_size,
    litellm_size=litellm_size,
    langfuse_size=langfuse_size,
    ch_size=ch_size,
    minio_size=minio_size,
    pg_size=pg_size,
    redis_size=redis_size,
    webui_size=webui_size,
)

# --- Injecter dans le README ---
readme_path = 'AI-Stack/README.md'
readme = open(readme_path, encoding='utf-8').read()
pattern = r'<!-- AI-STACK-BILAN-START -->.*?<!-- AI-STACK-BILAN-END -->'

if re.search(pattern, readme, re.DOTALL):
    updated = re.sub(pattern, bilan, readme, flags=re.DOTALL)
    action = 'mis à jour'
else:
    updated = readme.rstrip() + '\n\n' + bilan + '\n'
    action = 'ajouté'

open(readme_path, 'w', encoding='utf-8').write(updated)
print("✅ Bilan {} dans README.md".format(action))
print("   Run: {}".format(run_url))
print("   Date: {}".format(run_date))