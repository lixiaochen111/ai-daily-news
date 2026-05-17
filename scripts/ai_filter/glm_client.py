"""
GLM API Client

Wrapper for Zhipu AI's GLM-4.7-Flash model (free tier).
Uses OpenAI-compatible API format with custom endpoint.
"""

import os
from openai import OpenAI


class GLMClient:
    """
    Client for accessing Zhipu AI's GLM models via OpenAI-compatible API.

    Official documentation: https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash
    """

    def __init__(self, api_key=None):
        """
        Initialize GLM client.

        Args:
            api_key: Zhipu AI API key. If None, reads from GLM_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("GLM_API_KEY is required. Get one from https://open.bigmodel.cn/")

        # Initialize OpenAI client with Zhipu AI endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )

    def call_model(
        self,
        model="glm-4.7-flash",
        system_prompt="",
        user_prompt="",
        temperature=0.7,
        max_tokens=2000
    ):
        """
        Call GLM model with given prompts.

        Args:
            model: Model identifier (default: glm-4.7-flash)
            system_prompt: System prompt to set model behavior
            user_prompt: User prompt/query
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            dict: Response with 'content' and 'usage' keys
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            raise RuntimeError(f"GLM API call failed: {str(e)}")
