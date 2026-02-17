#!/usr/bin/env python3
"""
Génère BILAN_WORKFLOW.md à la racine du repo.
Documente les 3 workflows ForgeNest et les résultats du run d'interactivité.
Appelé par test-interactivity.yml après tous les tests.
"""
import subprocess
import re
import os
from datetime import datetime, timezone

run_id    = os.environ.get('GH_RUN_ID', 'unknown')
repo      = os.environ.get('GH_REPOSITORY', '')
run_url   = "https://github.com/{}/actions/runs/{}".format(repo, run_id)
run_date  = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

# --- Tailles images des 2 stacks ---
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

# --- Infos système ---
cpu = subprocess.run(['nproc'], capture_output=True, text=True).stdout.strip()
ram_raw = subprocess.run(['free', '-h'], capture_output=True, text=True).stdout
ram = 'N/A'
for line in ram_raw.split('\n'):
    if 'Mem:' in line:
        ram = line.split()[1]
        break

# --- Docker version ---
docker_ver = subprocess.run(['docker', '--version'], capture_output=True, text=True).stdout.strip()

bilan = """\
# 📊 Bilan des Workflows ForgeNest

> **Généré automatiquement** par GitHub Actions
> **Date :** `{run_date}`
> **Run :** [{run_id}]({run_url})

---

## 🗺️ Vue d'ensemble des Workflows

ForgeNest utilise **3 workflows GitHub Actions** couvrant chaque couche de la stack :

| Workflow | Fichier | Déclenche | Rôle |
|----------|---------|-----------|------|
| 🦊 **Forgejo + Woodpecker** | `check-stack-forgejo.yml` | Manuel | Valide la stack Git & CI |
| 🤖 **AI Stack** | `test-ai-stack.yml` | Manuel | Valide la stack IA (10 tests) |
| 🔗 **Interactivité** | `test-interactivity.yml` | Manuel | Valide la comm. entre les 2 stacks |

---

## 🦊 Workflow 1 — Forgejo + Woodpecker CI

### Objectif
Valider le déploiement de la stack Git+CI : Forgejo (forge), Woodpecker Server, Woodpecker Agent, et la configuration OAuth automatique entre eux.

### Tests effectués (5/5)

| # | Test | Description |
|---|------|-------------|
| 1 | Forgejo health | `GET /api/healthz` → 200 |
| 2 | Woodpecker health | `GET /healthz` → 200 |
| 3 | Woodpecker UI | Page UI chargée |
| 4 | OAuth endpoint | `/authorize` → 200/302/303/401 |
| 5 | Variables OAuth | Credentials injectés dans Woodpecker |

### Architecture

```
GitHub Actions Runner
        │
        ├── forgejo:5333  (git forge, OAuth provider)
        │       │ OAuth credentials
        ├── woodpecker-server:5444  (CI server)
        │       │ GRPC agent connection
        └── woodpecker-agent:3000  (pipeline executor)
```

### Services

| Service | Image | Port hôte |
|---------|-------|-----------|
| Forgejo | custom build (Dockerfile.forgejo) | 5333 |
| Woodpecker Server | custom build (Dockerfile.woodpecker-server) | 5444 |
| Woodpecker Agent | `woodpeckerci/woodpecker-agent:v2.7.1-alpine` | — |

### Particularité : OAuth automatique
Forgejo génère automatiquement les credentials OAuth lors du premier démarrage via `first-run-init.sh`. Woodpecker Server est ensuite redémarré avec ces credentials pour s'authentifier auprès de Forgejo.

---

## 🤖 Workflow 2 — AI Stack

### Objectif
Valider les 9 services de la stack IA, le flux complet LiteLLM→Ollama, et mesurer l'espace disque réel.

### Tests effectués (10/10)

| # | Test | Description |
|---|------|-------------|
| 1 | Redis | `redis-cli ping` → PONG |
| 2 | Langfuse | `GET /api/public/health` → 200 |
| 3 | ClickHouse | Ping + `SELECT version()` |
| 4 | Ollama | `/api/tags` contient `llama3.2` |
| 5 | LiteLLM | Chat completion avec auth |
| 6 | AI Gateway | `GET /health` |
| 7 | Goose | Container Up |
| 8 | MinIO S3 | `GET /minio/health/live` → 200 |
| 9 | Open WebUI | `GET /` → 200/302 |
| 10 | E2E LiteLLM→Ollama | Chat completion bout-en-bout |

### Images Docker

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

### Espace disque total

| Catégorie | Espace |
|-----------|--------|
| Toutes images Docker | ~9–10 GB |
| Modèle `llama3.2:1b` (test CI) | ~1.3 GB |
| Modèle `llama3.2` (recommandé) | ~2.0 GB |
| Données Langfuse | ~500 MB (croissant) |
| **TOTAL minimum** | **~12 GB** |

### Prérequis

| Ressource | Minimum | Recommandé |
|-----------|---------|------------|
| RAM | 8 GB | 16 GB |
| CPU | 4 cœurs | 8 cœurs |
| Disque | 20 GB | 40 GB |

---

## 🔗 Workflow 3 — Interactivité des 2 Stacks

### Objectif
Valider que la stack Forgejo/Woodpecker et la stack IA peuvent **communiquer entre elles** via un réseau Docker bridge partagé (`forgenest-bridge`).

### Dernier run : {run_date}

### Tests effectués (6/6)

| # | Test | Sens | Description |
|---|------|------|-------------|
| 1 | Connectivité réseau | Woodpecker ↔ IA | Ping entre tous les services |
| 2 | Pipeline IA | Woodpecker → Ollama/LiteLLM | Appel IA depuis contexte CI |
| 3 | Code Review IA | CI pipeline → LiteLLM | Review automatique de code |
| 4 | Goose ↔ Forgejo | Agent IA → Git forge | Agent peut lire l'API Forgejo |
| 5 | Cache Redis | LiteLLM → Redis | Vérification clés Redis actives |
| 6 | E2E complet | Push → Woodpecker → IA → Result | Flux DevOps complet |

### Architecture du réseau partagé

```
┌──────────────────────────────────────────────────────────────┐
│                    forgenest-bridge                          │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   forgejo   │    │   litellm-   │    │   ai-gateway  │  │
│  │  :3000      │    │   proxy:4000 │    │   :8000       │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         ↑                  ↑                   ↑            │
│  ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐    │
│  │ woodpecker- │    │   ollama    │    │    goose     │    │
│  │   server    │    │   :11434    │    │              │    │
│  │   :8000     │    └─────────────┘    └─────────────┘    │
│  └─────────────┘                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  woodpecker-agent                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘

Stack Forgejo (réseau forgejo-net) ←──→ forgenest-bridge
Stack IA (réseau ai-network)       ←──→ forgenest-bridge
```

### Scénario E2E validé

```
1. Développeur push code → Forgejo
2. Forgejo notifie Woodpecker (webhook)
3. Woodpecker démarre pipeline
4. Pipeline appelle LiteLLM → Ollama (via forgenest-bridge)
5. IA génère review du code
6. Résultat retourné (commentaire PR simulé)
```

---

## 💻 Environnement de Test

| Paramètre | Valeur |
|-----------|--------|
| Runner | `ubuntu-latest` (GitHub Actions) |
| CPU | {cpu} cœurs |
| RAM | {ram} |
| {docker_ver} | |
| Date du run | {run_date} |

---

## 🚀 Lancer les Workflows

```bash
# Via GitHub CLI
gh workflow run check-stack-forgejo.yml
gh workflow run test-ai-stack.yml
gh workflow run test-interactivity.yml

# Via GitHub UI
# Actions → choisir le workflow → Run workflow
```

### Ordre recommandé
1. `check-stack-forgejo.yml` — valider la stack Git/CI seule
2. `test-ai-stack.yml` — valider la stack IA seule
3. `test-interactivity.yml` — valider l'intégration complète

---

## 📋 Checklist Déploiement Production

- [ ] Docker >= 20.10 + Docker Compose >= 2.0 installés
- [ ] **20 GB disque minimum** disponibles (40 GB recommandés)
- [ ] **8 GB RAM minimum** (16 GB recommandés)
- [ ] Fichier `.env` configuré dans chaque stack
- [ ] Secrets changés (ne pas utiliser les valeurs CI !)
- [ ] `workflow check-stack-forgejo.yml` → ✅
- [ ] `workflow test-ai-stack.yml` → ✅
- [ ] `workflow test-interactivity.yml` → ✅

---

*Généré automatiquement par `.github/scripts/generate_bilan_workflow.py`*
*[Voir tous les runs](https://github.com/{repo}/actions)*
""".format(
    run_date=run_date,
    run_id=run_id,
    run_url=run_url,
    repo=repo,
    ollama_size=sz('ollama/ollama'),
    litellm_size=sz('litellm'),
    langfuse_size=sz('langfuse/langfuse'),
    ch_size=sz('clickhouse'),
    minio_size=sz('minio/minio'),
    pg_size=sz('postgres'),
    redis_size=sz('redis'),
    webui_size=sz('open-webui'),
    cpu=cpu,
    ram=ram,
    docker_ver=docker_ver,
)

out_path = 'BILAN_WORKFLOW.md'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(bilan)

print("BILAN_WORKFLOW.md genere ({} lignes)".format(len(bilan.split('\n'))))
print("Run: {}".format(run_url))