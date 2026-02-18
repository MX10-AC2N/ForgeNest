#!/usr/bin/env python3
"""
AI Gateway — Stack LITE
Endpoint unifié pour outils externes (scripts, IDE, agents, CI).

Providers supportés :
  - llama_cpp   : serveur local OpenAI-compatible (priorité 1)
  - groq        : cloud gratuit ultra-rapide  (fallback, si GROQ_API_KEY)
  - openrouter  : cloud, modèles gratuits     (fallback, si OPENROUTER_API_KEY)
  - huggingface : cloud gratuit               (fallback, si HUGGINGFACE_API_KEY)
  - together    : cloud, $25 crédits          (fallback, si TOGETHER_API_KEY)
  - ollama      : activé UNIQUEMENT si OLLAMA_URL est défini et non vide
"""

import os
import yaml
import httpx
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Modèles Pydantic
# =============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False

class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512
    stream: Optional[bool] = False

# =============================================================================
# Gateway
# =============================================================================

class AIGateway:
    def __init__(self):
        self.config = self._load_config()
        self.providers: Dict[str, Dict] = {}
        self._init_providers()

    def _load_config(self) -> Dict:
        config_file = os.getenv("CONFIG_FILE", "config.yaml")
        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"{config_file} introuvable — config vide")
            config = {}

        providers = config.get("providers", {})

        # llama.cpp — activé si LLAMACPP_URL est défini et non vide
        llamacpp_url = os.getenv("LLAMACPP_URL", "").strip()
        if llamacpp_url:
            providers.setdefault("llama_cpp", {})
            providers["llama_cpp"]["enabled"] = True
            providers["llama_cpp"]["base_url"] = llamacpp_url
            providers["llama_cpp"].setdefault("models", ["local-model"])
            logger.info(f"llama_cpp activé → {llamacpp_url}")

        # Ollama — activé UNIQUEMENT si OLLAMA_URL est défini et non vide
        ollama_url = os.getenv("OLLAMA_URL", "").strip()
        if ollama_url:
            providers.setdefault("ollama", {})
            providers["ollama"]["enabled"] = True
            providers["ollama"]["base_url"] = ollama_url
            providers["ollama"].setdefault("models", [])
            logger.info(f"ollama activé → {ollama_url}")
        else:
            # Forcer la désactivation même si présent dans config.yaml
            providers.setdefault("ollama", {})
            providers["ollama"]["enabled"] = False

        # Groq
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        if groq_key:
            providers.setdefault("groq", {})
            providers["groq"].update({"enabled": True, "api_key": groq_key,
                "base_url": "https://api.groq.com/openai/v1"})
            providers["groq"].setdefault("models", [
                "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
                "deepseek-r1-distill-llama-70b", "mixtral-8x7b-32768"])

        # OpenRouter
        or_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if or_key:
            providers.setdefault("openrouter", {})
            providers["openrouter"].update({"enabled": True, "api_key": or_key,
                "base_url": "https://openrouter.ai/api/v1"})
            providers["openrouter"].setdefault("models", [
                "meta-llama/llama-3.2-3b-instruct:free",
                "google/gemma-2-9b-it:free",
                "qwen/qwen-2.5-7b-instruct:free",
                "mistralai/mistral-7b-instruct:free"])

        # Hugging Face
        hf_key = os.getenv("HUGGINGFACE_API_KEY", "").strip()
        if hf_key:
            providers.setdefault("huggingface", {})
            providers["huggingface"].update({"enabled": True, "api_key": hf_key,
                "base_url": "https://api-inference.huggingface.co/models"})
            providers["huggingface"].setdefault("models", [
                "meta-llama/Llama-3.2-3B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct"])

        # Together AI
        together_key = os.getenv("TOGETHER_API_KEY", "").strip()
        if together_key:
            providers.setdefault("together", {})
            providers["together"].update({"enabled": True, "api_key": together_key,
                "base_url": "https://api.together.xyz/v1"})
            providers["together"].setdefault("models", [
                "meta-llama/Llama-3-70b-chat-hf",
                "mistralai/Mixtral-8x7B-Instruct-v0.1"])

        config["providers"] = providers
        return config

    def _init_providers(self):
        for name, cfg in self.config.get("providers", {}).items():
            if cfg.get("enabled", False):
                self.providers[name] = cfg
                logger.info(f"Provider '{name}' prêt — modèles: {cfg.get('models', [])}")

    async def _discover_llamacpp_models(self, provider: Dict) -> List[str]:
        """Interroge /v1/models sur llama.cpp pour obtenir le modèle réellement chargé."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{provider['base_url']}/v1/models")
                r.raise_for_status()
                data = r.json()
                ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
                if ids:
                    return ids
        except Exception as e:
            logger.debug(f"Découverte llama.cpp échouée ({e}), fallback liste statique")
        return provider.get("models", ["local-model"])

    def _parse_model(self, model: str):
        """
        Retourne (provider_name, model_name).
        Formats : "llama_cpp/local", "groq/llama-3.1-8b-instant", "local-model"
        """
        if "/" in model:
            provider, m = model.split("/", 1)
            return provider, m
        for pname, pcfg in self.providers.items():
            if model in pcfg.get("models", []):
                return pname, model
        if "llama_cpp" in self.providers:
            return "llama_cpp", model
        if self.providers:
            return next(iter(self.providers)), model
        raise HTTPException(status_code=503, detail="Aucun provider disponible")

    async def chat_completion(self, request: ChatRequest) -> Dict[str, Any]:
        provider_name, model_name = self._parse_model(request.model)

        if provider_name not in self.providers:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_name}' non configuré. "
                       f"Providers actifs : {list(self.providers.keys())}")

        provider = self.providers[provider_name]

        # Alias "local" → résolution dynamique du modèle chargé
        if provider_name == "llama_cpp" and model_name in ("local", ""):
            models = await self._discover_llamacpp_models(provider)
            model_name = models[0] if models else "local-model"
            logger.info(f"Alias llama_cpp/local résolu → {model_name}")

        if provider_name == "llama_cpp":
            return await self._llamacpp_chat(provider, model_name, request)
        elif provider_name in ("groq", "together"):
            return await self._openai_compat_chat(provider, model_name, request)
        elif provider_name == "openrouter":
            return await self._openrouter_chat(provider, model_name, request)
        elif provider_name == "huggingface":
            return await self._huggingface_chat(provider, model_name, request)
        elif provider_name == "ollama":
            return await self._ollama_chat(provider, model_name, request)
        else:
            raise HTTPException(status_code=400, detail=f"Provider inconnu: {provider_name}")

    async def _llamacpp_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Appel direct à llama.cpp — API OpenAI-compatible, sans auth."""
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{provider['base_url']}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": False,
                })
            resp.raise_for_status()
            data = resp.json()
            # Normaliser le champ model (llama.cpp renvoie parfois le nom du fichier GGUF)
            data["model"] = model
            return data

    async def _openai_compat_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        """Handler générique pour providers OpenAI-compatibles (Groq, Together)."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": False,
                })
            resp.raise_for_status()
            return resp.json()

    async def _openrouter_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['api_key']}",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "ForgeNest AI Gateway",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                })
            resp.raise_for_status()
            return resp.json()

    async def _huggingface_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        prompt = self._messages_to_prompt(request.messages)
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{provider['base_url']}/{model}",
                headers={"Authorization": f"Bearer {provider['api_key']}", "Content-Type": "application/json"},
                json={"inputs": prompt, "parameters": {
                    "temperature": request.temperature,
                    "max_new_tokens": request.max_tokens,
                    "return_full_text": False}})
            resp.raise_for_status()
            data = resp.json()
            generated = data[0].get("generated_text", "") if isinstance(data, list) else ""
            return {
                "id": f"hf-{hash(prompt)}", "object": "chat.completion",
                "created": int(datetime.now().timestamp()), "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": generated}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}

    async def _ollama_chat(self, provider: Dict, model: str, request: ChatRequest) -> Dict:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{provider['base_url']}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": m.role, "content": m.content} for m in request.messages],
                    "stream": False,
                    "options": {"temperature": request.temperature, "num_predict": request.max_tokens}})
            resp.raise_for_status()
            data = resp.json()
            return {
                "id": f"ollama-{hash(str(request.messages))}", "object": "chat.completion",
                "created": int(datetime.now().timestamp()), "model": model,
                "choices": [{"index": 0, "message": data.get("message", {"role": "assistant", "content": ""}), "finish_reason": "stop"}],
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)}}

    def _messages_to_prompt(self, messages: List[ChatMessage]) -> str:
        parts = []
        for m in messages:
            if m.role == "system":   parts.append(f"System: {m.content}")
            elif m.role == "user":   parts.append(f"User: {m.content}")
            elif m.role == "assistant": parts.append(f"Assistant: {m.content}")
        parts.append("Assistant:")
        return "\n\n".join(parts)

    async def list_models(self) -> List[Dict[str, Any]]:
        """Liste tous les modèles disponibles, avec découverte live pour llama.cpp."""
        models = []
        ts = int(datetime.now().timestamp())

        for provider_name, provider_cfg in self.providers.items():
            if provider_name == "llama_cpp":
                live_models = await self._discover_llamacpp_models(provider_cfg)
                for m in live_models:
                    models.append({"id": f"llama_cpp/{m}", "object": "model", "created": ts,
                        "owned_by": "llama_cpp", "provider": "llama_cpp", "model": m, "local": True})
                # Toujours exposer l'alias llama_cpp/local
                if not any(m["id"] == "llama_cpp/local" for m in models):
                    models.append({"id": "llama_cpp/local", "object": "model", "created": ts,
                        "owned_by": "llama_cpp", "provider": "llama_cpp", "model": "local", "local": True})
            else:
                for model_name in provider_cfg.get("models", []):
                    models.append({"id": f"{provider_name}/{model_name}", "object": "model",
                        "created": ts, "owned_by": provider_name,
                        "provider": provider_name, "model": model_name, "local": False})
        return models


# =============================================================================
# FastAPI
# =============================================================================

app = FastAPI(title="AI Gateway — Lite", version="2.0.0")
gateway = AIGateway()

@app.get("/")
async def root():
    return {"name": "AI Gateway — Lite", "version": "2.0.0",
            "providers": list(gateway.providers.keys())}

@app.get("/health")
async def health():
    status = "healthy"
    llama_status = "n/a"
    if "llama_cpp" in gateway.providers:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{gateway.providers['llama_cpp']['base_url']}/health")
                llama_status = "ok" if r.status_code == 200 else "degraded"
        except Exception:
            llama_status = "unreachable"
            status = "degraded"
    return {"status": status, "providers": len(gateway.providers), "llama_status": llama_status}

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": await gateway.list_models()}

@app.get("/v1/providers")
async def list_providers():
    result = {}
    for name, cfg in gateway.providers.items():
        result[name] = {"enabled": True, "base_url": cfg.get("base_url", ""),
            "models": cfg.get("models", []), "local": name in ("llama_cpp", "ollama")}
    return {"providers": result, "count": len(result)}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        return await gateway.chat_completion(request)
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code} depuis {e.request.url}: {e.response.text[:200]}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        logger.error(f"Erreur réseau : {e}")
        raise HTTPException(status_code=503, detail=f"Provider inaccessible : {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def completions(request: CompletionRequest):
    return await chat_completions(ChatRequest(
        model=request.model,
        messages=[ChatMessage(role="user", content=request.prompt)],
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        stream=request.stream))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
