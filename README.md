# ForgeNest
**The Autonomous Dev Nest – Code, Cache, Conquer** 🚀

[![Test Déploiement Racine](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-deploy.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-deploy.yml)
[![Test AI Stack Lite](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack-lite.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack-lite.yml)
[![Test AI Stack Full](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/test-ai-stack.yml)
[![Forgejo + Woodpecker](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/check-stack-forgejo.yml/badge.svg)](https://github.com/MX10-AC2N/ForgeNest/actions/workflows/check-stack-forgejo.yml)
[![Docker Compose](https://img.shields.io/badge/docker--compose-v2.20+-blue)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Votre forge de développement privée, autonome et souveraine.  
Git auto-hébergé, CI/CD et IA locale — tout en un, déployé en 5 minutes.

> Évolution de [Forgejo-Woodpecker-Docker](https://github.com/MX10-AC2N/Forgejo-Woodpecker-Docker).

---

## 🗺️ Vue d'ensemble

ForgeNest propose **2 configurations**. Les deux incluent toujours **Forgejo + Woodpecker CI/CD** — seule la partie IA change :

```
┌──────────────────────────────────────────────────────────────────────────┐
│                             ForgeNest                                    │
│                                                                          │
│          Forgejo + Woodpecker CI/CD  (commun aux 2 modes)                │
│   ┌────────────────────────────────────────────────────────────────┐     │
│   │   🦊 Forgejo :5333      🪵 Woodpecker :5444      🤖 Agent     │     │
│   └──────────────────────────────┬─────────────────────────────────┘     │
│                                  │ forgenest-bridge                      │
│               ┌──────────────────┴──────────────────┐                   │
│               │                                     │                   │
│  ┌────────────▼──────────┐           ┌──────────────▼────────────────┐  │
│  │   ForgeNest Full      │           │   ForgeNest Lite  ⭐           │  │
│  │                       │           │                               │  │
│  │  🧠 Ollama            │           │  ⚙️  llama.cpp  :8081         │  │
│  │  ⚡ LiteLLM   :4000   │           │  ⚡ LiteLLM    :4000          │  │
│  │  🌐 AI Gateway :8000  │           │  🌐 AI Gateway :8000          │  │
│  │  🎨 Open WebUI :3001  │           │  🎨 Open WebUI :3000          │  │
│  │  📊 Langfuse   :3002  │           │                               │  │
│  │  🦆 Goose · Tabby     │           │  RAM : 4–6 GB                 │  │
│  │  🔍 Perplexica :3003  │           │  ZimaBoard · NAS · N100       │  │
│  │  RAM : ~20 GB         │           │                               │  │
│  └───────────────────────┘           └───────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

| Mode | Compose | RAM totale | Cible |
|------|---------|-----------|-------|
| **Full** | `docker-compose.yml` | ~20 GB | Serveur dédié, workstation |
| **Lite** ⭐ | `docker-compose.lite.yaml` | 4–6 GB | ZimaBoard, NAS, Mini-PC N100 |

### Ce que ça permet concrètement

- **Push → Woodpecker pipeline → review IA automatique** sur chaque commit
- **LiteLLM cache les réponses dans Redis** — requêtes répétées instantanées
- **Goose** (Full) peut ouvrir des PRs, créer des issues, écrire du code de façon autonome
- **Langfuse** (Full) trace toutes les interactions IA — coût, latence, qualité
- **100% auto-hébergé** — aucune donnée ne quitte votre infrastructure

---

## 🚀 Démarrage rapide

### Prérequis

```
Docker Engine  ≥ 24.0
Docker Compose ≥ 2.20 (plugin V2)
```

### Installation

```bash
git clone https://github.com/MX10-AC2N/ForgeNest.git
cd ForgeNest
bash deploy.sh
```

Le script détecte votre RAM et vous guide :

```
  [1] ForgeNest Full
      Forgejo · Woodpecker CI/CD
      Ollama · LiteLLM · Langfuse · Open WebUI · AI Gateway · Goose · Tabby …
      RAM : ~20 GB — Serveur dédié

  [2] ForgeNest Lite  ⭐ recommandé homeserver
      Forgejo · Woodpecker CI/CD
      llama.cpp · LiteLLM · Open WebUI · AI Gateway
      RAM : 4–6 GB — ZimaBoard, NAS, Mini-PC N100

  Votre machine : 8 GB RAM → option 2 (Lite) recommandée

  Votre choix [1/2/q] :
```

### Démarrage direct sans menu

```bash
./deploy.sh start full    # ForgeNest Full
./deploy.sh start lite    # ForgeNest Lite
./deploy.sh stop          # Arrêt propre des stacks actives
./deploy.sh status        # État de tous les services
./deploy.sh logs [svc]    # Logs temps réel
```

### Déploiement manuel via Docker Compose

```bash
# Mode Full
cp .env.example .env && nano .env
docker compose -f docker-compose.yml up -d

# Mode Lite
cp .env.example .env && nano .env
cp AI-Stack-Lite/.env.lite.example AI-Stack-Lite/.env.lite && nano AI-Stack-Lite/.env.lite
docker compose -f docker-compose.lite.yaml up -d
```

---

## 🌐 Accès aux services

### ForgeNest Lite

| Service | URL | Rôle |
|---------|-----|------|
| 🦊 Forgejo | http://localhost:5333 | Forge Git |
| 🪵 Woodpecker | http://localhost:5444 | CI/CD |
| 🎨 Open WebUI | http://localhost:3000 | Interface chat |
| ⚡ LiteLLM | http://localhost:4000 | Proxy IA + cache |
| 🌐 AI Gateway | http://localhost:8000 | API unifiée multi-providers |
| ⚙️ llama.cpp | http://localhost:8081 | Inférence directe (debug) |

### ForgeNest Full

| Service | URL | Rôle |
|---------|-----|------|
| 🦊 Forgejo | http://localhost:5333 | Forge Git |
| 🪵 Woodpecker | http://localhost:5444 | CI/CD |
| 🎨 Open WebUI | http://localhost:3001 | Interface chat |
| ⚡ LiteLLM | http://localhost:4000 | Proxy IA + cache Redis |
| 📊 Langfuse | http://localhost:3002 | Observabilité IA |
| 🌐 AI Gateway | http://localhost:8000 | API unifiée multi-providers |
| 🤖 Tabby | http://localhost:8080 | Autocomplétion code IDE |
| 🔍 Perplexica | http://localhost:3003 | Recherche web IA |

---

## ⚙️ Configuration

### Mode Lite — `AI-Stack-Lite/.env.lite`

```ini
# Modèle IA (défaut : Qwen2.5-1.5B, ~1 GB, fonctionne sur 2 GB RAM libres)
LLAMACPP_MODEL_REPO=Qwen/Qwen2.5-1.5B-Instruct-GGUF
LLAMACPP_MODEL_FILE=qwen2.5-1.5b-instruct-q4_k_m.gguf

# Secrets (à changer)
LITELLM_MASTER_KEY=sk-lite-changeme
WEBUI_SECRET_KEY=changeme-webui-secret-32chars-min

# APIs cloud gratuites optionnelles (fallback si llama.cpp indisponible)
GROQ_API_KEY=          # https://console.groq.com/  — ultra-rapide, gratuit
OPENROUTER_API_KEY=    # https://openrouter.ai/keys — accès multi-modèles
```

**Modèles recommandés selon la RAM disponible :**

| RAM libre | Modèle | Taille |
|-----------|--------|--------|
| 2 GB | `Qwen/Qwen2.5-1.5B-Instruct-GGUF` Q4_K_M | ~1.0 GB |
| 4 GB | `microsoft/Phi-3.5-mini-instruct-gguf` Q4 | ~2.2 GB |
| 6 GB | `Qwen/Qwen2.5-3B-Instruct-GGUF` Q4_K_M | ~1.9 GB |
| 8 GB | `Qwen/Qwen2.5-7B-Instruct-GGUF` Q4_K_M | ~4.7 GB |

### Mode Full — `.env` (secrets à générer)

```bash
openssl rand -base64 48   # → WOODPECKER_AGENT_SECRET
openssl rand -hex 32      # → LITELLM_MASTER_KEY
openssl rand -base64 32   # → LANGFUSE_NEXTAUTH_SECRET, LANGFUSE_SALT
openssl rand -hex 32      # → LANGFUSE_ENCRYPTION_KEY  (64 chars hex)
openssl rand -base64 32   # → CLICKHOUSE_PASSWORD, WEBUI_SECRET_KEY
```

```ini
FORGEJO_ADMIN_PASSWORD=
WOODPECKER_AGENT_SECRET=   # min 48 chars
LITELLM_MASTER_KEY=
LANGFUSE_DB_PASSWORD=
LANGFUSE_NEXTAUTH_SECRET=
LANGFUSE_ENCRYPTION_KEY=   # 64 chars hex
LANGFUSE_SALT=
CLICKHOUSE_PASSWORD=
WEBUI_SECRET_KEY=

# APIs IA externes (optionnelles — Ollama fonctionne sans)
GROQ_API_KEY=
OPENROUTER_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

---

## 🏗️ Architecture

### Stack commune — Forgejo + Woodpecker

| Service | Port | Rôle |
|---------|------|------|
| 🦊 **Forgejo** | 5333 / 5222 SSH | Forge Git auto-hébergée |
| 🪵 **Woodpecker Server** | 5444 | Orchestrateur CI/CD |
| 🤖 **Woodpecker Agent** | — | Exécuteur de pipelines |

> OAuth entre Forgejo et Woodpecker est **entièrement automatisé** via `first-run-init.sh`. Zéro configuration manuelle.

### AI-Stack Lite

| Service | Rôle |
|---------|------|
| ⚙️ **llama.cpp** | Inférence GGUF, API OpenAI-compatible, CPU-optimisé |
| ⚡ **LiteLLM** | Proxy unifié llama.cpp + APIs cloud en fallback |
| 🌐 **AI Gateway** | API multi-providers avec alias `llama_cpp/local` |
| 🎨 **Open WebUI** | Interface chat connectée à LiteLLM |
| 💾 **Redis** | Cache LiteLLM |

### AI-Stack Full (services supplémentaires)

| Service | Rôle |
|---------|------|
| 🧠 **Ollama** | Inférence GPU/CPU, gestion de modèles simplifiée |
| 📊 **Langfuse** | Observabilité IA — traces, coûts, analytics |
| 🦆 **Goose** | Agent IA autonome (PRs, commits, issues) |
| 🤖 **Tabby** | Autocomplétion de code dans l'IDE |
| 🔍 **Perplexica** | Recherche web avec IA |
| 🗄️ **PostgreSQL + ClickHouse** | Bases Langfuse |
| 🪣 **MinIO** | Stockage objets S3-compatible |

### Réseau inter-stacks (`forgenest-bridge`)

```
Woodpecker Agent  →  litellm:4000       (review IA dans les pipelines)
Woodpecker Agent  →  ai-gateway:8000    (appels directs multi-providers)
LiteLLM           →  llama-cpp:8080     (inférence Lite)
LiteLLM           →  ollama:11434       (inférence Full)
LiteLLM           →  redis:6379         (cache)
```

---

## 🔬 CI/CD — Workflows GitHub Actions

| Workflow | Déclenché sur | Ce qui est testé |
|----------|--------------|-----------------|
| [`test-deploy.yml`](.github/workflows/test-deploy.yml) | push, PR | Lint YAML + démarrage Lite depuis la racine (7 tests) |
| [`test-ai-stack-lite.yml`](.github/workflows/test-ai-stack-lite.yml) | push, PR | Stack Lite isolée — 8 tests bout-en-bout |
| [`test-ai-stack.yml`](.github/workflows/test-ai-stack.yml) | manuel | Stack Full — 11 tests |
| [`check-stack-forgejo.yml`](.github/workflows/check-stack-forgejo.yml) | manuel | Forgejo + Woodpecker + OAuth — 5 tests |
| [`test-interactivity.yml`](.github/workflows/test-interactivity.yml) | manuel | Interopérabilité inter-stacks |

<details>
<summary><b>test-deploy</b> — Déploiement depuis la racine (7 tests)</summary>

**Job 1 — Lint (rapide, ~30s) :**
- Validation YAML `docker-compose.yml` via `docker compose config`
- Validation YAML `docker-compose.lite.yaml` via `docker compose config`
- Syntaxe bash `deploy.sh`

**Job 2 — Démarrage complet ForgeNest Lite :**
1. Forgejo répond (HTTP 200/302)
2. Woodpecker répond (HTTP 200/302)
3. llama.cpp `/health` → `{"status":"ok"}`
4. AI Gateway `/health` → providers actifs
5. AI Gateway inférence via `llama_cpp/local`
6. LiteLLM → llama.cpp via `local/default`
7. Open WebUI démarre (HTTP 200/302)

</details>

<details>
<summary><b>test-ai-stack-lite</b> — Stack Lite isolée (8 tests)</summary>

1. Redis → PONG
2. llama.cpp `/health` → `{"status":"ok"}`
3. llama.cpp inférence directe `/v1/chat/completions`
4. AI Gateway `/health` → providers actifs
5. AI Gateway `/v1/models` → `llama_cpp` détecté
6. AI Gateway inférence via `llama_cpp/local`
7. LiteLLM → llama.cpp via `local/default`
8. Open WebUI HTTP 200/302

</details>

<details>
<summary><b>check-stack-forgejo</b> — Forgejo + Woodpecker (5 tests)</summary>

1. Forgejo health
2. Woodpecker health
3. Woodpecker UI
4. OAuth endpoint (`/authorize`)
5. Variables OAuth injectées dans Woodpecker

> OAuth Forgejo↔Woodpecker entièrement automatisé via `first-run-init.sh`.

</details>

---

## 📁 Structure du projet

```
ForgeNest/
├── deploy.sh                          # ⭐ Point d'entrée — menu Full / Lite
├── docker-compose.yml                 # ForgeNest Full  (CI + AI-Stack Full)
├── docker-compose.lite.yaml           # ForgeNest Lite  (CI + AI-Stack-Lite)
├── .env.example                       # Variables CI/CD → copier vers .env
│
├── Forgejo-Woodpecker_CI-Stack/       # Stack CI/CD commune aux 2 modes
│   ├── docker-compose.yml
│   ├── Dockerfile.forgejo
│   ├── Dockerfile.woodpecker-server
│   └── scripts/
│       ├── first-run-init.sh          # OAuth Forgejo↔Woodpecker automatisé
│       └── entrypoint-woodpecker-server.sh
│
├── AI-Stack/                          # Mode Full — Ollama, Langfuse, Tabby…
│   ├── docker-compose.yaml
│   ├── .env.example
│   ├── ai-gateway/
│   ├── goose/
│   ├── litellm/
│   └── perplexica/
│
├── AI-Stack-Lite/                     # Mode Lite — llama.cpp, 4–6 GB RAM
│   ├── docker-compose.lite.yaml
│   ├── .env.lite.example
│   ├── ai-gateway/                    # Gateway avec résolution alias llama_cpp/local
│   ├── litellm/
│   └── scripts/deploy.sh
│
└── .github/workflows/
    ├── test-deploy.yml                # ⭐ Lint + démarrage Lite depuis la racine
    ├── test-ai-stack-lite.yml         # Stack Lite isolée
    ├── test-ai-stack.yml              # Stack Full (manuel)
    ├── check-stack-forgejo.yml        # Forgejo + Woodpecker + OAuth (manuel)
    └── test-interactivity.yml         # Interopérabilité inter-stacks (manuel)
```

---

## 🔒 Sécurité

- **`.env` et `.env.lite`** : jamais commités (`.gitignore`)
- **OAuth Forgejo/Woodpecker** : credentials auto-générés, non exposés en clair
- **Services internes** : Redis, PostgreSQL, ClickHouse non bindés sur l'hôte
- **Production** : ajouter un reverse proxy HTTPS

```caddyfile
git.mondomaine.com { reverse_proxy localhost:5333 }
ci.mondomaine.com  { reverse_proxy localhost:5444 }
ai.mondomaine.com  { reverse_proxy localhost:3000 }
```

---

## 🛠️ Commandes utiles

```bash
# Suivre le téléchargement du modèle (Lite, premier démarrage)
docker logs -f ai-lite-model-downloader

# Tester l'API IA
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama_cpp/local","messages":[{"role":"user","content":"Bonjour !"}],"max_tokens":50}'

# Lister les modèles disponibles
curl http://localhost:4000/v1/models -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Mettre à jour (Lite)
docker compose -f docker-compose.lite.yaml pull
docker compose -f docker-compose.lite.yaml up -d

# Nettoyage complet (⚠️ supprime les données)
docker compose -f docker-compose.lite.yaml down -v
docker system prune -f
```

---

## 📊 Ressources requises

| Mode | RAM | CPU | Disque |
|------|-----|-----|--------|
| **Lite** | 4–6 GB | 2 cœurs | ~15 GB + modèle (1–5 GB) |
| **Full** | 16–32 GB | 8+ cœurs | 60–120 GB |

---

## 💾 Backup

```bash
cd Forgejo-Woodpecker_CI-Stack
./scripts/backup.sh

# Restauration
docker compose down
tar xzf backup/forgejo-YYYYMMDD.tar.gz -C volumes/
docker compose up -d
```

---

## 🤝 Contribution

Issues et PRs bienvenues.  
Testé sur Ubuntu 22.04/24.04 et macOS (Docker Desktop).

---

## 📄 Licence

MIT — voir [LICENSE](LICENSE)

---

*Évolution de [Forgejo-Woodpecker-Docker](https://github.com/MX10-AC2N/Forgejo-Woodpecker-Docker)*
