# 🚀 Démarrage Rapide - Stack IA Ultime

## En 10 Minutes Chrono ⏱️

### 1️⃣ Obtenir une Clé Groq (2 min)

**Pourquoi ?** Groq est gratuit, ultra-rapide (<1s), et excellent qualité.

```bash
# 1. Aller sur https://console.groq.com/
# 2. S'inscrire avec email (gratuit)
# 3. Créer une API Key
# 4. Copier la clé (commence par gsk_)
```

### 2️⃣ Configurer (2 min)

```bash
cd AI-Ultimate-Stack/

# Créer .env
cp .env.example .env

# Éditer
nano .env
```

**Minimum requis** :
```bash
# Clé Groq (OBLIGATOIRE)
GROQ_API_KEY=gsk_votre_cle_ici

# Secrets (générer avec : openssl rand -base64 32)
LITELLM_MASTER_KEY=votre-secret-unique-ici
LANGFUSE_NEXTAUTH_SECRET=secret-32-chars-minimum
LANGFUSE_SALT=autre-secret-32-chars
WEBUI_SECRET_KEY=encore-un-secret-32-chars
LANGFUSE_DB_PASSWORD=mot-de-passe-securise
```

### 3️⃣ Démarrer (2 min)

```bash
# Lancer tout
docker compose up -d

# Suivre les logs
docker compose logs -f
```

**Attendre** : 2-5 minutes que tout démarre et que les modèles Ollama se téléchargent.

### 4️⃣ Vérifier (1 min)

```bash
# Voir l'état
docker compose ps

# Tous les services doivent être "healthy" ou "running"
```

### 5️⃣ Tester (3 min)

#### Open WebUI (Interface Chat)

```bash
# Ouvrir dans le navigateur
open http://localhost:3000

# 1. Créer un compte (premier utilisateur = admin)
# 2. Aller dans Settings → Models
# 3. Sélectionner "groq/llama-3.3-70b-versatile"
# 4. Commencer à chatter !
```

#### Goose (Agent Autonome)

```bash
# Lancer une session
docker compose exec goose goose session

# Dans la session Goose, taper :
> Create a Python hello world function

# Goose va le créer automatiquement !
```

#### LiteLLM (API)

```bash
# Test API
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "groq/llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## ✅ C'est Prêt !

Vous avez maintenant accès à :

| Service | URL | Description |
|---------|-----|-------------|
| **Open WebUI** | http://localhost:3000 | Chat type ChatGPT |
| **Langfuse** | http://localhost:3002 | Analytics IA |
| **LiteLLM UI** | http://localhost:4000/ui | Admin gateway |
| **Tabby** | http://localhost:8080 | Autocomplétion |
| **Goose** | `docker compose exec goose goose session` | Agent CLI |

---

## 🎯 Prochaines Étapes

### Option 1 : Configurer VSCode

**Tabby (Autocomplétion)** :
1. Installer extension "Tabby"
2. Endpoint : `http://localhost:8080`
3. Token : (laisser vide)

**Continue.dev (Chat)** :
1. Installer extension "Continue"
2. Base URL : `http://localhost:4000/v1`
3. API Key : `sk-1234`
4. Model : `groq/llama-3.3-70b-versatile`

### Option 2 : Explorer Langfuse

```bash
# Ouvrir Langfuse
open http://localhost:3002

# 1. Créer un compte
# 2. Créer un projet
# 3. Copier les clés API
# 4. Les mettre dans .env :
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# 5. Redémarrer
docker compose restart litellm open-webui
```

### Option 3 : Activer Perplexica (Recherche Web)

```bash
# Démarrer avec Perplexica
docker compose --profile perplexica up -d

# Accéder
open http://localhost:3001
```

---

## 🐛 Problèmes Courants

### "No space left on device"

```bash
# Les modèles Ollama prennent de la place
# Réduire les modèles dans .env :
OLLAMA_MODELS=llama3.2

# Ou augmenter l'espace Docker
```

### "Out of memory"

```bash
# Utiliser des modèles plus petits
TABBY_MODEL=StarCoder-1B
OLLAMA_MODELS=llama3.2
OLLAMA_NUM_CTX=2048
```

### Groq API Key invalide

```bash
# Vérifier dans .env
echo $GROQ_API_KEY

# Re-créer une clé sur https://console.groq.com/
```

### Services pas healthy

```bash
# Voir les logs
docker compose logs <service>

# Redémarrer
docker compose restart <service>
```

---

## 💡 Conseils

### Cache Redis (Vitesse x10)

Le cache Redis est activé automatiquement. Les requêtes identiques sont **100x plus rapides** !

```
Requête 1 : "Explain async" → 2s (API)
Requête 2 : "Explain async" → 0.02s (cache) ⚡
```

### Load Balancing

Si Groq est rate-limited, LiteLLM bascule automatiquement sur un autre provider :

```
Groq → Together AI → Ollama
```

### Analytics

Langfuse track **toutes** les requêtes :
- Latence
- Coûts
- Erreurs
- Conversations complètes

Parfait pour débugger !

---

## 🎉 Félicitations !

Vous avez une stack IA **ultra-complète** et **optimisée** :

- ✅ Cache Redis (x10-100 vitesse)
- ✅ Load balancing automatique
- ✅ Fallback multi-providers
- ✅ Analytics temps réel
- ✅ Agent autonome (Goose)
- ✅ Interface moderne
- ✅ 100% gratuit et auto-hébergé

**Consultez le README.md complet pour aller plus loin ! 🚀**
