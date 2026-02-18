"""
Azure OpenAI Client
Access GPT-5.1-chat via Azure OpenAI Service
"""

import os
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class AzureOpenAIClient:
    """Client for Azure OpenAI GPT-5.1-chat"""

    def __init__(
        self,
        endpoint: str = None,
        api_key: str = None,
        deployment: str = None,
        api_version: str = None,
    ):
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai>=1.10.0")

        self.endpoint = endpoint or os.getenv(
            "AZURE_OPENAI_ENDPOINT",
            "https://capstonebatch4-resource.cognitiveservices.azure.com/",
        )
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY", "")
        self.deployment = deployment or os.getenv(
            "AZURE_OPENAI_DEPLOYMENT", "gpt-5.1-chat"
        )
        self.api_version = api_version or os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
        )
        # GPT-5.1-chat only supports temperature=1 (default)
        self.temperature = 1

        if not self.api_key:
            raise ValueError(
                "Azure OpenAI key not provided. Set AZURE_OPENAI_KEY in .env"
            )

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )
        self.model_name = self.deployment
        self.display_name = f"Azure OpenAI: {self.deployment}"

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5

        print(f"[OK] Azure OpenAI initialized: {self.deployment} @ {self.endpoint}")

    def _rate_limit(self):
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def generate_response(
        self, prompt: str, json_mode: bool = False, retry_count: int = 3
    ) -> str:
        """Generate a text response from Azure OpenAI"""
        self._rate_limit()

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert manufacturing AI assistant for a Pune EV SUV plant. "
                    "Provide precise, data-grounded, actionable analysis. "
                    "Reference actual numbers from the data provided."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        if json_mode:
            messages[0]["content"] += " Always respond with valid JSON only."

        for attempt in range(retry_count):
            try:
                kwargs = {
                    "model": self.deployment,
                    "messages": messages,
                    "max_completion_tokens": 16384,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e:
                print(f"  [Azure OpenAI] Attempt {attempt+1} failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                return f"Error: {str(e)}"

    def generate_json_response(
        self, prompt: str, retry_count: int = 3
    ) -> Dict[str, Any]:
        """Generate a JSON response from Azure OpenAI"""
        response_text = self.generate_response(
            prompt, json_mode=True, retry_count=retry_count
        )

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": "JSON parsing failed", "raw_response": response_text[:500]}

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model": self.display_name,
            "model_id": self.deployment,
            "provider": "Azure OpenAI",
            "endpoint": self.endpoint,
            "api_version": self.api_version,
            "has_key": bool(self.api_key),
        }


# ---------------------------------------------------------------------------
# Singleton & Active LLM Client Management
# ---------------------------------------------------------------------------
_azure_client: Optional[AzureOpenAIClient] = None
_active_client: Optional[AzureOpenAIClient] = None


def get_azure_openai_client(**kwargs) -> AzureOpenAIClient:
    """Get or create singleton Azure OpenAI client"""
    global _azure_client
    if _azure_client is None:
        _azure_client = AzureOpenAIClient(**kwargs)
    return _azure_client


def get_active_llm_client() -> AzureOpenAIClient:
    """Get the currently active LLM client (Azure OpenAI)."""
    global _active_client
    if _active_client is not None:
        return _active_client
    return get_azure_openai_client()


def set_active_llm_client(client):
    """Set the active LLM client."""
    global _active_client
    _active_client = client


def reset_active_llm_client():
    """Reset to default Azure OpenAI client."""
    global _active_client
    _active_client = None
