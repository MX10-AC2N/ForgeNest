# 📦 Fichiers Manquants pour ForgeNest - Guide Complet

## 🎯 Fichiers AI Gateway (OBLIGATOIRES)

Ces fichiers doivent être dans `AI-Stack/ai-gateway/` :

### 1. `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai-gateway.py .
COPY config.yaml .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-u", "ai-gateway.py"]
```

### 2. `requirements.txt`
```
fastapi==0.109.0
uvicorn==0.27.0
httpx==0.26.0
pyyaml==6.0.1
pydantic==2.5.3
requests==2.31.0
python-multipart==0.0.6
aiohttp==3.9.1
```

### 3. `ai-gateway.py`
(Fichier Python complet fourni séparément - 300+ lignes)

### 4. `config.yaml`
(Fichier de configuration fourni séparément)

### 5. `README.md` (optionnel mais recommandé)
Documentation du module ai-gateway

---

## 📁 Structure Complète Attendue

```
ForgeNest/
├── .github/
│   └── workflows/
│       ├── test-ai-stack.yml
│       └── test-interactivity.yml
│
├── AI-Stack/
│   ├── ai-gateway/                    ⚠️ MANQUANT
│   │   ├── Dockerfile                 ⚠️ OBLIGATOIRE
│   │   ├── ai-gateway.py              ⚠️ OBLIGATOIRE
│   │   ├── requirements.txt           ⚠️ OBLIGATOIRE
│   │   ├── config.yaml                ⚠️ OBLIGATOIRE
│   │   └── README.md                  ✅ Optionnel
│   │
│   ├── goose/
│   │   ├── Dockerfile                 ❓ Vérifier
│   │   ├── entrypoint.sh              ❓ Vérifier
│   │   └── goose-config.yaml          ❓ Vérifier
│   │
│   ├── litellm/
│   │   └── config.yaml                ❓ Vérifier
│   │
│   ├── perplexica/
│   │   └── config.toml                ❓ Vérifier
│   │
│   ├── docker-compose.yml             ✅ Doit exister
│   ├── .env.example                   ✅ Doit exister
│   └── README.md                      ✅ Doit exister
│
├── Forgejo-Woodpecker_CI-Stack/
│   ├── scripts/
│   ├── docker-compose.yml
│   ├── .env.example
│   └── README.md
│
├── LICENSE
└── README.md
```

---

## 🚨 Fichiers Critiques à Vérifier

### Dans `AI-Stack/`

1. **ai-gateway/** (MANQUE COMPLÈTEMENT)
   - Doit contenir les 4 fichiers listés ci-dessus

2. **goose/Dockerfile** 
   - Vérifier qu'il existe et qu'il a ce contenu :
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   RUN apt-get update && apt-get install -y git curl jq vim nano && rm -rf /var/lib/apt/lists/*
   RUN pip install --no-cache-dir goose-ai httpx pyyaml rich click
   RUN mkdir -p /workspace /root/.config/goose
   COPY goose-config.yaml /root/.config/goose/config.yaml
   COPY entrypoint.sh /entrypoint.sh
   RUN chmod +x /entrypoint.sh
   VOLUME ["/workspace"]
   WORKDIR /workspace
   ENTRYPOINT ["/entrypoint.sh"]
   CMD ["bash"]
   ```

3. **goose/entrypoint.sh**
   ```bash
   #!/bin/bash
   set -e
   echo "🦆 Goose Agent IA - Prêt"
   echo "Workspace: ${WORKSPACE_DIR:-/workspace}"
   if [ "$#" -eq 0 ]; then
       exec bash
   else
       exec "$@"
   fi
   ```

4. **goose/goose-config.yaml**
   ```yaml
   provider: openai
   model: groq/llama-3.3-70b-versatile
   openai:
     base_url: http://litellm:4000/v1
     api_key: ${LITELLM_MASTER_KEY}
   temperature: 0.7
   max_tokens: 4000
   ```

5. **litellm/config.yaml**
   - Fichier de configuration LiteLLM (fourni séparément)

6. **perplexica/config.toml**
   ```toml
   [GENERAL]
   PORT = 3001
   
   [API_ENDPOINTS]
   OPENAI = "http://litellm:4000/v1"
   OLLAMA = "http://ollama:11434"
   
   [CHAT_MODEL]
   PROVIDER = "openai"
   MODEL = "groq/llama-3.3-70b-versatile"
   ```

---

## ✅ Installation des Fichiers Manquants

### Étape 1 : Créer le dossier ai-gateway

```bash
cd ForgeNest/AI-Stack/
mkdir -p ai-gateway
cd ai-gateway
```

### Étape 2 : Copier les fichiers fournis

Copiez les 5 fichiers fournis dans ce dossier :
- `Dockerfile`
- `ai-gateway.py`
- `requirements.txt`
- `config.yaml`
- `README.md`

### Étape 3 : Vérifier la structure

```bash
cd ForgeNest/AI-Stack/
ls -la ai-gateway/

# Devrait afficher :
# -rw-r--r-- 1 user user  xxx Dockerfile
# -rw-r--r-- 1 user user  xxx ai-gateway.py
# -rw-r--r-- 1 user user  xxx requirements.txt
# -rw-r--r-- 1 user user  xxx config.yaml
# -rw-r--r-- 1 user user  xxx README.md
```

### Étape 4 : Test local (optionnel)

```bash
cd ai-gateway/
docker build -t test-ai-gateway .

# Si ça build sans erreur, c'est bon !
```

### Étape 5 : Commit et push

```bash
git add ai-gateway/
git commit -m "feat: Add missing ai-gateway module

- Dockerfile for ai-gateway service
- FastAPI application with multi-provider support
- Configuration for Groq, Ollama, HF, Together, OpenRouter
- Requirements and documentation"

git push origin main
```

---

## 🔍 Vérification Complète

### Checklist Avant Re-test Workflow

- [ ] `AI-Stack/ai-gateway/Dockerfile` existe
- [ ] `AI-Stack/ai-gateway/ai-gateway.py` existe
- [ ] `AI-Stack/ai-gateway/requirements.txt` existe
- [ ] `AI-Stack/ai-gateway/config.yaml` existe
- [ ] `AI-Stack/goose/Dockerfile` existe (si utilisé)
- [ ] `AI-Stack/goose/entrypoint.sh` existe et est exécutable
- [ ] `AI-Stack/litellm/config.yaml` existe
- [ ] `AI-Stack/docker-compose.yml` référence bien ai-gateway
- [ ] Pas de variable `MODEL` non définie dans docker-compose.yml

### Commande de Vérification Rapide

```bash
cd ForgeNest/

# Vérifier ai-gateway
test -f AI-Stack/ai-gateway/Dockerfile && echo "✅ Dockerfile" || echo "❌ Dockerfile manquant"
test -f AI-Stack/ai-gateway/ai-gateway.py && echo "✅ ai-gateway.py" || echo "❌ ai-gateway.py manquant"
test -f AI-Stack/ai-gateway/requirements.txt && echo "✅ requirements.txt" || echo "❌ requirements.txt manquant"
test -f AI-Stack/ai-gateway/config.yaml && echo "✅ config.yaml" || echo "❌ config.yaml manquant"

# Vérifier goose
test -f AI-Stack/goose/Dockerfile && echo "✅ Goose Dockerfile" || echo "❌ Goose Dockerfile manquant"
test -x AI-Stack/goose/entrypoint.sh && echo "✅ Goose entrypoint.sh" || echo "❌ Goose entrypoint.sh manquant ou non exécutable"

# Vérifier litellm
test -f AI-Stack/litellm/config.yaml && echo "✅ LiteLLM config" || echo "❌ LiteLLM config manquant"
```

---

## 🐛 Erreur "MODEL variable not set"

Cette erreur indique que dans votre `docker-compose.yml`, il y a une référence à `${MODEL}` qui n'est pas définie.

### Solution

Ouvrir `AI-Stack/docker-compose.yml` et chercher `${MODEL}` :

```bash
grep -n "MODEL" AI-Stack/docker-compose.yml
```

Puis remplacer `${MODEL}` par la valeur appropriée ou définir `MODEL` dans `.env` :

```bash
# Dans .env
MODEL=llama3.2
```

Ou mieux, utiliser des noms de variables plus spécifiques :
- `TABBY_MODEL` pour Tabby
- `GOOSE_MODEL` pour Goose
- `OLLAMA_MODELS` pour Ollama

---

## 📞 Support

Si après avoir ajouté tous les fichiers l'erreur persiste :

1. Vérifier les logs exacts de l'erreur
2. Partager le contenu de `docker-compose.yml` (section ai-gateway)
3. Vérifier que tous les fichiers sont bien commités

---

**Tous les fichiers sont fournis dans le dossier de sortie. Copiez-les dans votre repo ForgeNest et le workflow devrait passer ! ✅**