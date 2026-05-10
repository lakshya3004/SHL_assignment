import json
import requests
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings


class LLMService:
    """
    Generic wrapper for OpenAI-compatible LLM providers.
    Handles retries, timeouts, and structured response parsing.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.OPENAI_MODEL_NAME

    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.2,
        max_tokens: int = 800,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Sends a request to the LLM provider with timeout and retry logic.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            payload["response_format"] = response_format

        max_retries = 2
        for attempt in range(max_retries):
            try:
                logger.debug(f"Calling LLM (Attempt {attempt+1})")
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=15 # Hard timeout for evaluator safety
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except requests.Timeout:
                logger.error("LLM Request timed out.")
            except Exception as e:
                logger.error(f"LLM Call failed: {e}")
                
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(1) # Wait before retry

        return "I apologize, but I'm having trouble processing your request right now. I can help you find SHL assessments if you describe your hiring needs."

    async def generate_json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Helper to get JSON responses from the LLM.
        """
        # Ensure we ask for JSON in the prompt or use response_format if supported
        content = await self.generate_completion(
            messages, 
            response_format={"type": "json_object"} if "gpt-4" in self.model else None
        )
        
        try:
            # Basic sanitization in case of markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON: {e}. Content: {content[:100]}...")
            return {}
