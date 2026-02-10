# AI Gateway

API unifiée pour accéder à plusieurs providers IA via une interface compatible OpenAI.

## Fichiers

- `Dockerfile` - Image Docker
- `ai-gateway.py` - Application FastAPI
- `requirements.txt` - Dépendances Python
- `config.yaml` - Configuration des providers

## Providers Supportés

- **Groq** - Ultra-rapide, gratuit (14,400 req/jour)
- **Ollama** - Local, privé, illimité
- **Hugging Face** - Gratuit
- **Together AI** - $25 crédits gratuits
- **OpenRouter** - Modèles gratuits sélectionnés

## Utilisation

### API

```bash
# Lister les modèles
curl http://localhost:8000/v1/models

# Chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/llama3.2",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Variables d'environnement

- `OLLAMA_URL` - URL d'Ollama (défaut: http://ollama:11434)
- `GROQ_API_KEY` - Clé API Groq (optionnel)
- `HUGGINGFACE_API_KEY` - Clé API HuggingFace (optionnel)
- `TOGETHER_API_KEY` - Clé API Together (optionnel)
- `OPENROUTER_API_KEY` - Clé API OpenRouter (optionnel)

## Build

```bash
docker build -t ai-gateway .
docker run -p 8000:8000 -e OLLAMA_URL=http://ollama:11434 ai-gateway
```