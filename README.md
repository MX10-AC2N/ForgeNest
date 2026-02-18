# ==> ForgeNest <==
**The Autonomous Dev Nest – Code, Cache, Conquer** 🚀

[![Déploiement & Tests Forgejo + Woodpecker](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/check-stack-forgejo.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/check-stack-forgejo.yml)
[![Test AI Stack](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack.yml)
[![Test AI Stack Lite](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack-lite.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack-lite.yml)
[![Test Interactivité 2 Stacks](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-interactivity.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-interactivity.yml)
[![Docker Compose](https://img.shields.io/badge/docker--compose-v2.20+-blue)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Votre forge de développement privée, autonome et souveraine.
Git auto-hébergé, CI/CD, IA locale, observabilité — tout en un, déployé en 5 minutes.

> Évolution de [Forgejo-Woodpecker-Docker](https://github.com/MX10-AC2N/Forgejo-Woodpecker-Docker).

---

## 🗺️ Vue d'ensemble

ForgeNest propose **3 modes de déploiement** selon votre matériel :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ForgeNest                                      │
│                                                                             │
│  ┌──────────────────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │  Forgejo-Woodpecker_CI   │   │  AI-Stack    │   │  AI-Stack-Lite ⭐  │  │
│  │  (toutes configs)        │   │  (Full)      │   │  (Homeserver)      │  │
│  │                          │   │              │   │                    │  │
│  │  🦊 Forgejo   :5333      │   │  🧠 Ollama   │   │  ⚙️  llama.cpp     │  │
│  │  🪵 Woodpecker :5444     │   │  📊 Langfuse │   │  ⚡ LiteLLM  :4000 │  │
│  │  🤖 WP Agent             │   │  🎨 WebUI    │   │  🌐 Gateway  :8000 │  │
│  │                          │   │  🌐 Gateway  │   │  🎨 WebUI    :3000 │  │
│  │  RAM : ~1 GB             │   │  🦆 Goose    │   │                    │  │
│  │                          │   │  ...         │   │  RAM : 2.5–5.6 GB  │  │
│  │                          │   │  RAM : ~20GB │   │  ZimaBoard / NAS   │  │
│  └──────────┬───────────────┘   └──────┬───────┘   └─────────┬──────────┘  │
│             │                          │                      │             │
│             └──────────────────────────┴──────────────────────┘             │
│                           forgenest-bridge                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Mode | Stacks incluses | RAM | Cible |
|------|----------------|-----|-------|
| **[1] Full** | CI/CD + AI-Stack complète | ~20 GB | Serveur dédié |
| **[2] Lite** ⭐ | AI-Stack-Lite seule | 2.5–5.6 GB | ZimaBoard, NAS, N100 |
| **[3] CI + Lite** | CI/CD + AI-Stack-Lite | ~6 GB | Homeserver polyvalent |

### Ce que ça permet concrètement

- **Push du code → Woodpecker déclenche un pipeline → L'IA review le code automatiquement**
- **Goose (agent autonome) peut ouvrir des PRs, créer des issues, commiter du code**
- **LiteLLM cache les réponses IA dans Redis** — les requêtes répétées sont instantanées
- **Langfuse trace toutes les interactions IA** — coût, latence, qualité au fil du temps
- **100% auto-hébergé** — aucune donnée ne quitte votre infrastructure

---

## 🏗️ Architecture détaillée

### Stack 1 — Forgejo + Woodpecker CI

| Service | Port | Rôle |
|---------|------|------|
| 🦊 **Forgejo** | 5333 (HTTP) / 5222 (SSH) | Forge Git auto-hébergée (type GitHub/GitLab) |
| 🪵 **Woodpecker Server** | 5444 | Orchestrateur CI/CD + interface web |
| 🤖 **Woodpecker Agent** | — | Exécuteur de pipelines (Docker-in-Docker) |

**Particularité :** OAuth entre Forgejo et Woodpecker est **entièrement automatisé** via `first-run-init.sh`. Zéro clic manuel, zéro configuration post-démarrage.

### Stack 2 — AI Stack

| Service | Port | Rôle |
|---------|------|------|
| 🧠 **Ollama** | 11434 | Inférence LLM 100% locale (llama3.2, codellama…) |
| ⚡ **LiteLLM Proxy** | 4000 | Gateway OpenAI-compatible + cache Redis + load balancing |
| 📊 **Langfuse** | 3002 | Observabilité IA (traces, coûts, analytics) |
| 🎨 **Open WebUI** | 3001 | Interface chat type ChatGPT |
| 🌐 **AI Gateway** | 8000 | API unifiée multi-providers |
| 🤖 **Tabby** | 8080 | Autocomplétion de code (plugin IDE) |
| 🦆 **Goose** | CLI | Agent IA autonome (crée des PRs, écrit du code…) |
| 💾 **Redis** | 6379 | Cache LiteLLM (requêtes répétées ×10 plus rapides) |
| 🔍 **Perplexica** | 3003 | Recherche web avec IA (type Perplexity) |
| 🗄️ **PostgreSQL** | — | Base de données Langfuse |
| 📦 **ClickHouse** | 8123 | Analytics Langfuse (traces volumineuses) |
| 🪣 **MinIO** | 9002 | Stockage objets S3-compatible |

### Réseau inter-stacks

Un réseau Docker bridge `forgenest-bridge` connecte les deux stacks :

```
Woodpecker Agent  →  litellm-proxy:4000   (review IA dans les pipelines)
Goose Agent       →  forgejo:3000         (API Git depuis l'IA)
LiteLLM           →  ollama:11434         (inférence locale)
LiteLLM           →  ai-redis:6379        (cache)
Langfuse          →  ai-clickhouse:8123   (traces)
```

---

## 🚀 Démarrage rapide

### Prérequis

```
Docker Engine  ≥ 24.0
Docker Compose ≥ 2.20
```

### Déploiement interactif (recommandé)

```bash
git clone https://github.com/MX10-AC2N/ForgeNest.git
cd ForgeNest
bash deploy.sh
```

Le script détecte votre RAM disponible, vous propose les 3 modes et guide la configuration :

```
Quelle stack souhaitez-vous déployer ?

  [1] Stack Complète  (Full)
      Forgejo · Woodpecker · Ollama · LiteLLM · Langfuse · ...
      RAM requise : ~20 GB — Serveur dédié / workstation

  [2] Stack Légère    (Lite) ⭐ recommandée homeserver
      llama.cpp · LiteLLM · AI Gateway · Open WebUI
      RAM requise : 2.5–5.6 GB — ZimaBoard, NAS, Mini-PC N100

  [3] Les deux        (Forgejo+Woodpecker + Stack Lite)
      CI/CD complet + IA légère sur la même machine
      RAM requise : ~6 GB

Votre machine : 8 GB RAM → Options 2 ou 3 recommandées

Votre choix [1/2/3/q] :
```

### Déploiement manuel par stack

```bash
# Stack Complète
cp .env.example .env && nano .env
docker compose up -d

# Stack Lite uniquement
bash AI-Stack-Lite/scripts/deploy.sh

# CI/CD uniquement
cd Forgejo-Woodpecker_CI-Stack
cp .env.example .env && docker compose up -d
```

### Accès aux interfaces

**Stack Lite :**

| Interface | URL |
|-----------|-----|
| 🎨 Open WebUI | http://localhost:3000 |
| ⚡ LiteLLM | http://localhost:4000 |
| 🌐 AI Gateway | http://localhost:8000 |
| ⚙️ llama.cpp | http://localhost:8081 (debug) |

**Stack Complète :**

| Interface | URL |
|-----------|-----|
| 🦊 Forgejo | http://localhost:5333 |
| 🪵 Woodpecker | http://localhost:5444 |
| 🎨 Open WebUI | http://localhost:3001 |
| ⚡ LiteLLM | http://localhost:4000 |
| 📊 Langfuse | http://localhost:3002 |
| 🌐 AI Gateway | http://localhost:8000 |
| 🤖 Tabby | http://localhost:8080 |
| 🔍 Perplexica | http://localhost:3003 |

---

## ⚙️ Configuration

### Secrets à changer obligatoirement

```bash
openssl rand -base64 48   # → WOODPECKER_AGENT_SECRET
openssl rand -hex 32      # → LITELLM_MASTER_KEY
openssl rand -base64 32   # → LANGFUSE_DB_PASSWORD, LANGFUSE_NEXTAUTH_SECRET, LANGFUSE_SALT
openssl rand -hex 32      # → LANGFUSE_ENCRYPTION_KEY (exactement 64 chars hex)
openssl rand -base64 32   # → CLICKHOUSE_PASSWORD, WEBUI_SECRET_KEY
```

Variables critiques dans `.env` :

```ini
ADMIN_PASSWORD=            # Forgejo admin
WOODPECKER_AGENT_SECRET=   # min 48 chars
LITELLM_MASTER_KEY=
LANGFUSE_DB_PASSWORD=
LANGFUSE_NEXTAUTH_SECRET=
LANGFUSE_ENCRYPTION_KEY=   # 64 chars hex
LANGFUSE_SALT=
CLICKHOUSE_PASSWORD=
WEBUI_SECRET_KEY=
```

### Profils de configuration Ollama

```ini
# Profil 8 GB RAM
OLLAMA_MODELS=llama3.2,nomic-embed-text
OLLAMA_NUM_CTX=2048

# Profil 16 GB RAM (défaut)
OLLAMA_MODELS=codellama,llama3.2,nomic-embed-text
OLLAMA_NUM_CTX=4096

# Profil 32 GB RAM + GPU
OLLAMA_MODELS=deepseek-coder,qwen2.5-coder,llama3.2,nomic-embed-text
OLLAMA_NUM_GPU=999
OLLAMA_NUM_CTX=8192
```

### Clés API IA externes (optionnelles)

Sans clés : tout fonctionne en local via Ollama.
Avec clés : LiteLLM route automatiquement vers les providers cloud.

```ini
GROQ_API_KEY=         # Ultra-rapide, gratuit — https://console.groq.com/
HUGGINGFACE_API_KEY=  # Gratuit — https://huggingface.co/settings/tokens
TOGETHER_API_KEY=     # $25 crédits offerts — https://api.together.xyz/
OPENROUTER_API_KEY=   # Multi-providers — https://openrouter.ai/keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

---

## 🔬 CI/CD — Workflows GitHub Actions

Les trois workflows valident chaque couche de la stack :

| Workflow | Durée | Tests |
|----------|-------|-------|
| [`check-stack-forgejo.yml`](.github/workflows/check-stack-forgejo.yml) | ~8 min | 5/5 — Forgejo + Woodpecker + OAuth |
| [`test-ai-stack.yml`](.github/workflows/test-ai-stack.yml) | ~15 min | 10/10 — tous les services IA |
| [`test-interactivity.yml`](.github/workflows/test-interactivity.yml) | ~25 min | 6/6 — communication inter-stacks |

<details>
<summary><b>check-stack-forgejo</b> — détail des 5 tests</summary>

1. Build des images custom (Forgejo + Woodpecker)
2. Démarrage et attente Forgejo healthy
3. Extraction automatique des credentials OAuth depuis les logs
4. Injection OAuth dans Woodpecker + redémarrage
5. Tests : health endpoint, UI, OAuth `/authorize`, variables injectées dans le conteneur

</details>

<details>
<summary><b>test-ai-stack</b> — détail des 10 tests</summary>

1. Redis `ping` → PONG
2. Langfuse `/api/public/health` → 200
3. ClickHouse `SELECT version()`
4. Ollama `/api/tags` contient le modèle chargé
5. LiteLLM chat completion avec authentification
6. AI Gateway `/health` → 200
7. Goose container Up
8. MinIO `/minio/health/live` → 200
9. Open WebUI HTTP → 200/302
10. E2E LiteLLM → Ollama (inférence complète bout-en-bout)

</details>

<details>
<summary><b>test-interactivity</b> — détail des 6 tests</summary>

1. Connectivité réseau cross-stack (Woodpecker ↔ tous les services IA)
2. Appels IA depuis contexte pipeline (Ollama direct + LiteLLM)
3. Code Review IA automatique via LiteLLM
4. Goose ↔ Forgejo API (agent peut lire la forge)
5. Cache Redis actif (LiteLLM → Redis, vérification `DBSIZE`)
6. Scénario E2E complet : push → pipeline → review IA → résultat

> Après chaque run réussi, [`BILAN_WORKFLOW.md`](BILAN_WORKFLOW.md) est automatiquement commité avec les métriques du run.

</details>

---

## 📁 Structure du projet

```
ForgeNest/
├── deploy.sh                           # ⭐ Point d'entrée — choix interactif de stack
├── docker-compose.yml                  # Orchestration Full (include CI + AI-Stack)
├── .env.example                        # Variables unifiées → copier vers .env
├── BILAN_WORKFLOW.md                   # Généré auto par CI après chaque run
│
├── Forgejo-Woodpecker_CI-Stack/
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── Dockerfile.forgejo              # Image custom + first-run-init.sh
│   ├── Dockerfile.woodpecker-server
│   └── scripts/
│       ├── first-run-init.sh           # OAuth automatique au 1er démarrage
│       ├── entrypoint-woodpecker-server.sh
│       └── validate-stack.sh
│
├── AI-Stack/                           # Stack complète (Ollama, Langfuse, Tabby…)
│   ├── docker-compose.yaml
│   ├── .env.example
│   ├── ai-gateway/
│   ├── goose/
│   ├── litellm/
│   ├── clickhouse/
│   └── perplexica/
│
├── AI-Stack-Lite/                      # Stack légère (llama.cpp, 2.5–5.6 GB RAM)
│   ├── docker-compose.lite.yaml
│   ├── .env.lite.example
│   ├── ai-gateway/                     # Gateway adapté llama.cpp
│   ├── litellm/
│   └── scripts/
│       └── deploy.sh                   # Déploiement Lite avec sélection modèle
│
└── .github/
    ├── workflows/
    │   ├── check-stack-forgejo.yml
    │   ├── test-ai-stack.yml
    │   ├── test-ai-stack-lite.yml      # 8 tests automatisés Stack Lite
    │   └── test-interactivity.yml
    └── scripts/
        ├── generate_bilan.py
        └── generate_bilan_workflow.py
```

---

## 🔒 Sécurité

- **`.env`** : jamais commité, présent dans `.gitignore`
- **OAuth** : credentials Woodpecker/Forgejo auto-générés, non exposés dans les logs en clair
- **Réseau** : Redis, ClickHouse, MinIO liés à `127.0.0.1` (inaccessibles depuis l'extérieur)
- **Production** : placer un reverse proxy HTTPS devant les services exposés

```caddyfile
# Exemple Caddy
git.mondomaine.com { reverse_proxy localhost:5333 }
ci.mondomaine.com  { reverse_proxy localhost:5444 }
ai.mondomaine.com  { reverse_proxy localhost:3001 }
```

---

## 💾 Backup & restauration

```bash
# Sauvegarder les volumes Forgejo
cd Forgejo-Woodpecker_CI-Stack
./scripts/backup.sh

# Restauration
docker compose down
tar xzf backup/forgejo-20240101.tar.gz -C volumes/
docker compose up -d
```

---

## 🛠️ Commandes utiles

```bash
# État global
docker compose ps

# Logs temps réel
docker compose logs -f forgejo
docker compose logs -f litellm
docker compose logs -f ollama

# Redémarrer un service
docker compose restart woodpecker-server

# Mettre à jour
docker compose pull && docker compose up -d

# Goose — session agent IA
docker exec -it goose goose session

# Ollama — télécharger un modèle
docker exec ollama ollama pull llama3.2

# LiteLLM — lister les modèles disponibles
curl http://localhost:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Nettoyage complet (⚠️ supprime les données)
docker compose down -v && docker system prune -f
```

---

## 📊 Ressources requises

| Profil | RAM | CPU | Disque |
|--------|-----|-----|--------|
| Minimal | 8 GB | 4 cœurs | 30 GB |
| Standard | 16 GB | 8 cœurs | 60 GB |
| Haute perf. + GPU | 32 GB | 16 cœurs | 120 GB |

> Images Docker seules : ~9-10 GB. Compter +1-4 GB par modèle Ollama.

---

## 🤝 Contribution

Issues et PRs bienvenues.
Testé sur Ubuntu 22.04/24.04 et macOS (Docker Desktop).

---

## 📄 Licence

MIT — voir [LICENSE](LICENSE)

---

*Évolution de [Forgejo-Woodpecker-Docker](https://github.com/MX10-AC2N/Forgejo-Woodpecker-Docker)*
