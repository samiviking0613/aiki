#!/usr/bin/env python3
"""
AIKI API Client - Unified LLM access with key rotation

Supports:
- OpenRouter (multiple cheap models)
- Anthropic (Claude)
- OpenAI (GPT)

Features:
- Automatic key rotation on rate limits
- Cost tracking per request
- Retry with exponential backoff
- Model-specific routing
"""

import os
import asyncio
import httpx
import json
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: str  # 'openrouter', 'anthropic', 'openai'
    model_id: str  # API model identifier
    cost_per_1k_input: float  # NOK
    cost_per_1k_output: float  # NOK
    max_tokens: int = 4096


# OpenRouter API keys (roterer automatisk)
OPENROUTER_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
]

# Anthropic API keys
ANTHROPIC_KEYS = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
]

# OpenAI API keys
OPENAI_KEYS = [
    "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",
    "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",
    "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",
]

# Available models
MODELS = {
    # Cheap swarm models (via OpenRouter)
    'haiku-3.5': ModelConfig('haiku-3.5', 'openrouter', 'anthropic/claude-3.5-haiku', 0.008, 0.024),
    'gemini-flash': ModelConfig('gemini-flash', 'openrouter', 'google/gemini-flash-1.5', 0.003, 0.006),
    'llama-3.3-70b': ModelConfig('llama-3.3-70b', 'openrouter', 'meta-llama/llama-3.3-70b-instruct', 0.004, 0.004),
    'deepseek-v3': ModelConfig('deepseek-v3', 'openrouter', 'deepseek/deepseek-chat', 0.001, 0.002),
    'qwen-2.5': ModelConfig('qwen-2.5', 'openrouter', 'qwen/qwen-2.5-72b-instruct', 0.003, 0.003),
    'phi-3-mini': ModelConfig('phi-3-mini', 'openrouter', 'microsoft/phi-3-mini-128k-instruct', 0.001, 0.001),
    'mistral-nemo': ModelConfig('mistral-nemo', 'openrouter', 'mistralai/mistral-nemo', 0.002, 0.002),

    # Premium models
    'sonnet-4.5': ModelConfig('sonnet-4.5', 'openrouter', 'anthropic/claude-sonnet-4', 0.030, 0.150),
    'opus-4': ModelConfig('opus-4', 'openrouter', 'anthropic/claude-opus-4', 0.150, 0.750),
    'gpt-4o': ModelConfig('gpt-4o', 'openrouter', 'openai/gpt-4o', 0.025, 0.100),
    'gemini-pro': ModelConfig('gemini-pro', 'openrouter', 'google/gemini-pro-1.5', 0.013, 0.050),
}


class APIClient:
    """Unified API client with key rotation"""

    def __init__(self):
        self.openrouter_key_index = 0
        self.anthropic_key_index = 0
        self.openai_key_index = 0

        self.total_cost = 0.0
        self.request_count = 0
        self.errors = []

        self.client = httpx.AsyncClient(timeout=60.0)

    def _get_key(self, provider: str) -> str:
        """Get next API key with rotation"""
        if provider == 'openrouter':
            key = OPENROUTER_KEYS[self.openrouter_key_index % len(OPENROUTER_KEYS)]
            return key
        elif provider == 'anthropic':
            key = ANTHROPIC_KEYS[self.anthropic_key_index % len(ANTHROPIC_KEYS)]
            return key
        elif provider == 'openai':
            key = OPENAI_KEYS[self.openai_key_index % len(OPENAI_KEYS)]
            return key
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _rotate_key(self, provider: str):
        """Rotate to next key on rate limit"""
        if provider == 'openrouter':
            self.openrouter_key_index += 1
            logger.warning(f"Rotated OpenRouter key to index {self.openrouter_key_index % len(OPENROUTER_KEYS)}")
        elif provider == 'anthropic':
            self.anthropic_key_index += 1
            logger.warning(f"Rotated Anthropic key to index {self.anthropic_key_index % len(ANTHROPIC_KEYS)}")
        elif provider == 'openai':
            self.openai_key_index += 1
            logger.warning(f"Rotated OpenAI key to index {self.openai_key_index % len(OPENAI_KEYS)}")

    async def complete(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Get completion from specified model

        Returns: {
            'content': str,
            'model': str,
            'input_tokens': int,
            'output_tokens': int,
            'cost': float,
            'latency': float
        }
        """
        if model_name not in MODELS:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(MODELS.keys())}")

        model = MODELS[model_name]
        start_time = datetime.now(timezone.utc)

        # All models go through OpenRouter for simplicity
        result = await self._openrouter_complete(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        latency = (datetime.now(timezone.utc) - start_time).total_seconds()
        result['latency'] = latency

        # Track costs
        self.total_cost += result.get('cost', 0)
        self.request_count += 1

        return result

    async def _openrouter_complete(
        self,
        model: ModelConfig,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Make request to OpenRouter API"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self._get_key('openrouter')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aiki.local",
            "X-Title": "AIKI Ultimate"
        }

        payload = {
            "model": model.model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        for attempt in range(3):
            try:
                response = await self.client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 429:
                    # Rate limited, rotate key and retry
                    self._rotate_key('openrouter')
                    headers["Authorization"] = f"Bearer {self._get_key('openrouter')}"
                    await asyncio.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                data = response.json()

                # Extract response
                content = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)

                # Calculate cost in NOK
                cost = (
                    (input_tokens / 1000) * model.cost_per_1k_input +
                    (output_tokens / 1000) * model.cost_per_1k_output
                )

                return {
                    'content': content,
                    'model': model.name,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'cost': cost
                }

            except httpx.HTTPStatusError as e:
                self.errors.append({
                    'time': datetime.now(timezone.utc).isoformat(),
                    'model': model.name,
                    'error': str(e)
                })
                if attempt < 2:
                    self._rotate_key('openrouter')
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except Exception as e:
                logger.error(f"API error: {e}")
                raise

        raise RuntimeError("Max retries exceeded")

    async def complete_parallel(
        self,
        model_names: List[str],
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Run multiple models in parallel

        Returns list of results (one per model)
        """
        tasks = [
            self.complete(
                model_name=name,
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            for name in model_names
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error dicts
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    'content': None,
                    'model': model_names[i],
                    'error': str(result),
                    'cost': 0
                })
            else:
                processed.append(result)

        return processed

    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            'total_cost': self.total_cost,
            'request_count': self.request_count,
            'average_cost': self.total_cost / max(self.request_count, 1),
            'errors': len(self.errors)
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global singleton
_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """Get or create global API client"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client


async def test_api():
    """Test API connectivity"""
    client = get_api_client()

    print("Testing API connectivity...")

    # Test single model
    print("\n1. Testing single model (haiku-3.5)...")
    result = await client.complete(
        model_name='haiku-3.5',
        prompt='Say "Hello from AIKI!" and nothing else.',
        max_tokens=50
    )
    print(f"   Response: {result['content']}")
    print(f"   Cost: {result['cost']:.4f} NOK")
    print(f"   Latency: {result['latency']:.2f}s")

    # Test parallel
    print("\n2. Testing parallel models...")
    results = await client.complete_parallel(
        model_names=['haiku-3.5', 'gemini-flash', 'phi-3-mini'],
        prompt='What is 2+2? Answer with just the number.',
        max_tokens=10
    )
    for r in results:
        if r.get('error'):
            print(f"   {r['model']}: ERROR - {r['error']}")
        else:
            print(f"   {r['model']}: {r['content'].strip()} (cost: {r['cost']:.4f} NOK)")

    # Stats
    print(f"\nTotal stats: {client.get_stats()}")

    await client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_api())
