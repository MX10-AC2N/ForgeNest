#!/usr/bin/env python3
"""
AI Gateway - Agrégateur d'APIs IA gratuites
Supporte : Groq, Hugging Face, Together AI, Ollama local, OpenRouter
"""

import os
import yaml
import httpx
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Models Pydantic
# =============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False

# =============================================================================
# AI Gateway Class
# =============================================================================

class AIGateway:
    def __init__(self):
        self.config = self.load_config()
        self.providers = {}
        self.init_providers()
    
    def load_config(self) -> Dict:
        """Charge la configuration depuis config.yaml et variables d'environnement"""
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("config.yaml non trouvé, utilisation config par défaut")
            config = {'providers': {}}
        
        providers = config.get('providers', {})
        
        # Groq (gratuit, très rapide)
        if os.getenv('GROQ_API_KEY'):
            providers['groq'] = {
                'enabled': True,
                'api_key': os.getenv('GROQ_API_KEY'),
                'base_url': 'https://api.groq.com/openai/v1',
                'models': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768']
            }
        
        # Ollama local (toujours disponible)
        ollama_url = os.getenv('OLLAMA_URL', 'http://ollama:11434')
        providers['ollama'] = {
            'enabled': True,
            'base_url': ollama_url,
            'models': ['codellama', 'deepseek-coder', 'llama3.2', 'qwen2.5-coder']
        }
        
        # Hugging Face (gratuit)
        if os.getenv('HUGGINGFACE_API_KEY'):
            providers['huggingface'] = {
                'enabled': True,
                'api_key': os.getenv('HUGGINGFACE_API_KEY'),
                'base_url': 'https://api-inference.huggingface.co/models',
                'models': ['meta-llama/Llama-3.2-3B-Instruct', 'Qwen/Qwen2.5-Coder-32B-Instruct']
            }
        
        # Together AI (gratuit avec crédits)
        if os.getenv('TOGETHER_API_KEY'):
            providers['together'] = {
                'enabled': True,
                'api_key': os.getenv('TOGETHER_API_KEY'),
                'base_url': 'https://api.together.xyz/v1',
                'models': ['meta-llama/Llama-3-70b-chat-hf', 'mistralai/Mixtral-8x7B-Instruct-v0.1']
            }
        
        # OpenRouter (gratuit avec certains modèles)
        if os.getenv('OPENROUTER_API_KEY'):
            providers['openrouter'] = {
                'enabled': True,
                'api_key': os.getenv('OPENROUTER_API_KEY'),
                'base_url': 'https://openrouter.ai/api/v1',
                'models': ['meta-llama/llama-3.1-8b-instruct:free', 'google/gemma-2-9b-it:free']
            }
        
        config['providers'] = providers
        return config
    
    def init_providers(self):
        """Initialise les providers configurés"""
        for name, config in self.config['providers'].items():
            if config.get('enabled', False):
                self.providers[name] = config
                logger.info(f"Provider {name} initialisé avec modèles: {config.get('models', [])}")
    
    async def chat_completion(self, request: ChatRequest) -> Dict[str, Any]:
        """Route vers le bon provider selon le modèle demandé"""
        provider_name, model_name = self.parse_model(request.model)
        
        if provider_name not in self.providers:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} non configuré")
        
        provider = self.providers[provider_name]
        
        # Router vers la méthode appropriée
        if provider_name == 'groq':
            return await self.groq_chat(provider, model_name, request)
        elif provider_name == 'huggingface':
            return await self.huggingface_chat(provider, model_name, request)
        elif provider_name == 'together':
            return await self.together_chat(provider, model_name, request)
        elif provider_name == 'ollama':
            return await self.ollama_chat(provider, model_name, request)
        elif provider_name == 'openrouter':
            return await self.openrouter_chat(provider, model_name, request)
        else:
            raise HTTPException(status_code=400, detail=f"Provider inconnu: {provider_name}")
    
    def parse_model(self, model: str) -> tuple:
        """Parse le format provider/model ou retourne ollama par défaut"""
        if '/' in model:
            parts = model.split('/', 1)
            return parts[0], parts[1]
        else:
            # Si pas de provider spécifié, chercher dans tous les providers
            for provider_name, provider_config in self.providers.items():
                if model in provider_config.get('models', []):
                    return provider_name, model
            # Par défaut, utiliser ollama
            return 'ollama', model
    
    async def groq_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Appel à Groq API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": request.stream
                },
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
    
    async def huggingface_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Appel à Hugging Face Inference API"""
        prompt = self.messages_to_prompt(request.messages)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider['base_url']}/{model}",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "temperature": request.temperature,
                        "max_new_tokens": request.max_tokens,
                        "return_full_text": False
                    }
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Convertir au format OpenAI
            return {
                "id": "hf-" + str(hash(prompt)),
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": data[0].get('generated_text', '')
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(data[0].get('generated_text', '').split()),
                    "total_tokens": len(prompt.split()) + len(data[0].get('generated_text', '').split())
                }
            }
    
    async def together_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Appel à Together AI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                },
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
    
    async def ollama_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Appel à Ollama local"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider['base_url']}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens
                    }
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Convertir au format OpenAI
            return {
                "id": "ollama-" + str(hash(str(request.messages))),
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": data.get('message', {}).get('content', '')
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": data.get('prompt_eval_count', 0),
                    "completion_tokens": data.get('eval_count', 0),
                    "total_tokens": data.get('prompt_eval_count', 0) + data.get('eval_count', 0)
                }
            }
    
    async def openrouter_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Appel à OpenRouter"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "AI Gateway",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                },
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
    
    def messages_to_prompt(self, messages: List[ChatMessage]) -> str:
        """Convertit une liste de messages en prompt unique"""
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Liste tous les modèles disponibles"""
        models = []
        for provider_name, provider_config in self.providers.items():
            for model_name in provider_config.get('models', []):
                models.append({
                    "id": f"{provider_name}/{model_name}",
                    "object": "model",
                    "created": int(datetime.now().timestamp()),
                    "owned_by": provider_name,
                    "provider": provider_name,
                    "model": model_name
                })
        return models

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(title="AI Gateway", version="1.0.0")
gateway = AIGateway()

@app.get("/")
async def root():
    return {
        "name": "AI Gateway",
        "version": "1.0.0",
        "description": "Unified API for multiple AI providers",
        "providers": list(gateway.providers.keys())
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "providers": len(gateway.providers)}

@app.get("/v1/models")
async def list_models():
    """Liste tous les modèles disponibles (compatible OpenAI)"""
    return {
        "object": "list",
        "data": gateway.list_models()
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Chat completion compatible OpenAI"""
    try:
        response = await gateway.chat_completion(request)
        return response
    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    """Text completion (convertit en chat completion)"""
    chat_request = ChatRequest(
        model=request.model,
        messages=[ChatMessage(role="user", content=request.prompt)],
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        stream=request.stream
    )
    return await chat_completions(chat_request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")