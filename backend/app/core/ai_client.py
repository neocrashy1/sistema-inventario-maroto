"""
AI Client Configuration - Suporte para LLaMA e Hugging Face
"""
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class AIClient:
    """Cliente unificado para serviços de IA"""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.huggingface_client = None
        self.http_client = httpx.AsyncClient(
            timeout=settings.LLAMA_API_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )

    async def initialize_huggingface(self):
        """Inicializa cliente Hugging Face se necessário"""
        if not self.huggingface_client and self.provider == "huggingface":
            try:
                from transformers import pipeline
                self.huggingface_client = pipeline(
                    'text-generation',
                    model=settings.AI_MODEL,
                    device=-1
                )
                logger.info("Hugging Face client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Hugging Face client: {e}")
                raise

    async def generate_text_huggingface(self, prompt: str) -> str:
        """Gera texto usando Hugging Face"""
        try:
            await self.initialize_huggingface()
            result = self.huggingface_client(
                prompt,
                max_length=settings.AI_MAX_LENGTH,
                temperature=settings.AI_TEMPERATURE
            )
            return result[0]['generated_text'] if result else ""
        except Exception as e:
            logger.error(f"Error generating text with Hugging Face: {e}")
            return f"Erro na geração de texto: {str(e)}"

    async def generate_text_llama(self, prompt: str) -> str:
        """Gera texto usando LLaMA API"""
        try:
            payload = {
                "prompt": prompt,
                "temperature": settings.AI_TEMPERATURE,
                "max_tokens": settings.AI_MAX_LENGTH
            }
            
            async with self.http_client as client:
                response = await client.post(
                    f"{settings.LLAMA_API_URL}/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("text", "")
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error with LLaMA API: {e}")
            return f"Erro na comunicação com LLaMA: {str(e)}"
        except Exception as e:
            logger.error(f"Error generating text with LLaMA: {e}")
            return f"Erro na geração de texto: {str(e)}"

    async def generate_text(self, prompt: str) -> str:
        """Gera texto usando o provider configurado"""
        if not settings.AI_ENABLED:
            return "IA está desativada nas configurações"

        if self.provider == "llama":
            return await self.generate_text_llama(prompt)
        elif self.provider == "huggingface":
            return await self.generate_text_huggingface(prompt)
        else:
            return f"Provider de IA não suportado: {self.provider}"


# Instância global do cliente
ai_client = AIClient()