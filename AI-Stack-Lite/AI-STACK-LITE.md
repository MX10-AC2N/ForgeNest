# 🏠 Stack IA LITE — Homeserver Edition

Stack IA légère optimisée pour les **homeservers domestiques** : ZimaBoard, NAS, Raspberry Pi 5, mini-PC N100/N305, ou toute machine avec 4-8 GB de RAM.

---

## 🆚 Full vs Lite — Comparaison

| Fonctionnalité         | Stack Full        | Stack Lite       |
|------------------------|-------------------|------------------|
| **RAM nécessaire**     | ~16-20 GB         | **3-5 GB** ✅     |
| **CPU recommandé**     | 8+ cœurs          | **2+ cœurs** ✅   |
| **Moteur LLM**         | Ollama            | **llama.cpp** ✅  |
| **Interface chat**     | Open WebUI        | Open WebUI       |
| **Gateway API**        | LiteLLM (full)    | LiteLLM (lite)   |
| **Cache**              | Redis             | Redis (léger)    |
| **Analytics/traces**   | Langfuse ❌        | —                |
| **Base de données**    | PostgreSQL ❌       | —                |
| **OLAP / ClickHouse**  | ClickHouse ❌      | —                |
| **Stockage S3**        | MinIO ❌           | —                |
| **Autocomplétion IDE** | Tabby ❌           | via llama.cpp    |
| **Agent autonome**     | Goose ❌           | —                |
| **Recherche web IA**   | Perplexica ❌      | — (optionnel)    |
| **APIs cloud gratuites** | ✅               | ✅ (fallback)     |
| **AI Gateway**         | ✅ (full stack)   | **✅ intégré**    |
| **Offline complet**    | ❌                 | **✅ possible**   |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  INTERFACES UTILISATEUR                  │
│            ┌──────────────────────┐                      │
│            │      Open WebUI      │  :3000               │
│            └──────────┬───────────┘                      │
│                       │                                  │
│            ┌──────────▼───────────┐                      │
│            │   LiteLLM Proxy      │  :4000               │
│            │  • Cache Redis       │                      │
│            │  • Retry / Fallback  │                      │
│            └──┬──────────────┬────┘                      │
│               │              │                           │
│   ┌───────────▼──┐  ┌────────▼──────────────────────┐   │
│   │ llama-cpp    │  │     AI Gateway                │   │
│   │ :8081 direct │  │     :8000                     │   │
│   └──────────────┘  │  • Routing llama.cpp + cloud  │   │
│                     │  • /v1/models dynamique        │   │
│                     │  • /v1/providers status        │   │
│                     └───────┬──────────────┬─────────┘   │
│                             │              │             │
│                   ┌─────────▼──┐    ┌──────▼──────────┐  │
│                   │ llama-cpp  │    │  APIs Gratuites  │  │
│                   │ (local)    │    │  • Groq          │  │
│                   └────────────┘    │  • OpenRouter    │  │
│                                     │  • HuggingFace   │  │
│                                     │  • Together AI   │  │
│                                     └──────────────────┘  │
│            ┌──────────────────────┐                      │
│            │       Redis          │  Cache (128 MB)      │
│            └──────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

**Deux chemins d'accès complémentaires :**
- **LiteLLM** `:4000` → utilisé par Open WebUI. Cache Redis, retry et fallbacks automatiques. Connexion directe à llama.cpp pour le chemin le plus rapide.
- **AI Gateway** `:8000` → endpoint unifié pour les outils externes (scripts, IDE plugins, agents, CI…). Découvre dynamiquement le modèle chargé dans llama.cpp via `/v1/models` et bascule automatiquement sur les APIs cloud si llama.cpp est indisponible.

## 🚀 Démarrage rapide

### Option 1 — Script interactif (recommandé)

```bash
cd AI-Stack
bash scripts/deploy.sh
```

Le script :
- Détecte votre RAM et CPU
- Vous guide dans le choix du modèle
- Configure automatiquement les threads et le contexte
- Télécharge le modèle GGUF depuis Hugging Face

### Option 2 — Démarrage manuel

```bash
cd AI-Stack

# 1. Copier et éditer la configuration
cp .env.lite.example .env.lite
nano .env.lite

# 2. Créer le dossier modèles
mkdir -p volumes/lite/models

# 3. Démarrer
docker compose -f docker-compose.lite.yaml --env-file .env.lite up -d

# 4. Suivre le téléchargement du modèle
docker logs -f ai-lite-model-downloader
```

---

## 🤖 Choix du modèle GGUF

| RAM disponible | Modèle recommandé         | Taille | Qualité |
|----------------|---------------------------|--------|---------|
| 2-4 GB         | Qwen2.5-1.5B-Q4_K_M       | 1.0 GB | ⭐⭐     |
| 4-6 GB         | Phi-3.5-mini-Q4_K_M        | 2.2 GB | ⭐⭐⭐    |
| 6-8 GB         | Llama-3.2-3B-Q4_K_M        | 2.0 GB | ⭐⭐⭐    |
| 8-12 GB        | Qwen2.5-7B-Q4_K_M          | 4.4 GB | ⭐⭐⭐⭐   |
| Code spécifique | Qwen2.5-Coder-1.5B-Q4     | 1.0 GB | ⭐⭐⭐    |

> **Pourquoi llama.cpp plutôt qu'Ollama ?**  
> llama.cpp utilise directement les poids GGUF sans couche d'abstraction.  
> Sur CPU, il est **30-50% plus rapide** qu'Ollama à RAM équivalente,  
> et expose une **API OpenAI-compatible** nativement.

---

## ⚡ Fallback automatique vers les APIs gratuites

Si le modèle local est trop lent pour une requête, LiteLLM bascule automatiquement vers les APIs cloud gratuites configurées dans `.env.lite`.

**Priorité de routing :**
```
local/default  →  groq/llama-3.1-8b-instant  →  openrouter/llama-3.2-3b
local/chat     →  groq/llama-3.3-70b          →  openrouter/gemma-2-9b
local/code     →  groq/deepseek-r1-70b        →  hf/qwen-2.5-coder
```

**Obtenir les clés gratuitement :**
- **Groq** (⭐ prioritaire) : https://console.groq.com — 14 400 req/jour
- **OpenRouter** : https://openrouter.ai/keys — modèles gratuits
- **HuggingFace** : https://huggingface.co/settings/tokens
- **Together AI** : https://api.together.xyz — $25 crédits

---

## 🔧 Ajustement des performances

Modifiez `.env.lite` selon votre matériel :

```bash
# Threads : nombre de cœurs physiques - 1
LLAMACPP_THREADS=3          # Pour N100 (4 cœurs)
LLAMACPP_THREADS=2          # Pour ZimaBoard 216 (2 cœurs)

# Contexte : impact fort sur la RAM
LLAMACPP_CTX=1024           # ZimaBoard 216 (4 GB)
LLAMACPP_CTX=2048           # ZimaBoard 832 (8 GB)  ← défaut
LLAMACPP_CTX=4096           # N100 Mini-PC (16 GB)

# Requêtes parallèles (augmente RAM mais améliore le débit multi-user)
LLAMACPP_PARALLEL=1         # Usage solo
LLAMACPP_PARALLEL=2         # Quelques utilisateurs

# Mémoire allouée à llama.cpp
LLAMACPP_MEMORY_LIMIT=3G    # ZimaBoard 216 (modèle 1.5B)
LLAMACPP_MEMORY_LIMIT=4G    # ZimaBoard 832 (modèle 3B)  ← défaut
```

---

## 📊 Commandes utiles

```bash
# Statut des services
docker compose -f docker-compose.lite.yaml --env-file .env.lite ps

# Logs en temps réel
docker compose -f docker-compose.lite.yaml --env-file .env.lite logs -f

# Logs llama.cpp uniquement
docker logs -f ai-lite-llama-cpp

# Arrêt propre
docker compose -f docker-compose.lite.yaml --env-file .env.lite down

# Arrêt + suppression volumes
docker compose -f docker-compose.lite.yaml --env-file .env.lite down -v
```

---

## 🔄 Changer de modèle

1. Modifiez `.env.lite` :
   ```bash
   LLAMACPP_MODEL_REPO=bartowski/Llama-3.2-3B-Instruct-GGUF
   LLAMACPP_MODEL_FILE=Llama-3.2-3B-Instruct-Q4_K_M.gguf
   ```
2. Redémarrez :
   ```bash
   docker compose -f docker-compose.lite.yaml --env-file .env.lite up -d model-downloader
   docker compose -f docker-compose.lite.yaml --env-file .env.lite restart llama-cpp
   ```

> Les anciens modèles restent dans `volumes/lite/models/` — supprimez-les manuellement si besoin d'espace.

---

## 🔒 Sécurité en production

Même en homeserver, changez les secrets par défaut dans `.env.lite` :

```bash
# Générer des secrets forts
openssl rand -base64 32
```

Variables à changer impérativement :
- `LITELLM_MASTER_KEY`
- `WEBUI_SECRET_KEY`
