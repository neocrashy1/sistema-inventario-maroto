"""
AI Configuration and Integration
"""
from typing import Optional
import httpx
import asyncio
from pydantic import BaseModel
from app.core.config import settings

class AIConfig(BaseModel):
    """AI Configuration Settings"""
    enabled: bool = True
    provider: str = "llama"  # Usando LLaMA como provider padrão
    model: str = "llama"  
    api_url: str = "http://172.30.0.61:8000"  # URL do servidor LLaMA
    api_timeout: int = 30  # timeout em segundos
    max_length: int = 100
    temperature: float = 0.7
    
    class Config:
        arbitrary_types_allowed = True

# Configuração padrão
default_ai_config = AIConfig()

# Função para inicializar cliente AI
def get_ai_client():
    """Get AI client based on configuration"""
    try:
        from transformers import pipeline
        
        # Inicializa o pipeline de geração de texto
        generator = pipeline('text-generation', 
                           model=default_ai_config.model,
                           device=-1)  # -1 usa CPU, mais compatível inicialmente
        
        return generator
    except Exception as e:
        print(f"Erro ao inicializar AI client: {e}")
        return None

async def generate_text(prompt: str) -> str:
    """Generate text using the LLaMA API"""
    try:
        if not default_ai_config.enabled:
            return "IA está desabilitada"
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{default_ai_config.api_url}/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": default_ai_config.max_length,
                    "temperature": default_ai_config.temperature
                },
                timeout=default_ai_config.api_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                return f"Erro na API: {response.status_code}"
                
    except httpx.RequestError as e:
        print(f"Erro de conexão com LLaMA: {e}")
        return "Erro de conexão com o servidor LLaMA"
    except Exception as e:
        print(f"Erro na geração de texto: {e}")
        return "Erro na geração de texto"