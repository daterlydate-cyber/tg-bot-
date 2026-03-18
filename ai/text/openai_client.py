import asyncio
from typing import Optional

print("[AI] Загрузка openai_client")


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini",
                 temperature: float = 0.7, max_tokens: int = 2000,
                 system_prompt: str = "You are a helpful assistant."):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self._client = None
        print(f"[AI] OpenAI клиент создан, модель: {model}")

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Установите openai: pip install openai")
        return self._client

    async def generate_text(self, prompt: str, history: Optional[list] = None) -> str:
        try:
            client = self._get_client()
            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-20:])
            messages.append({"role": "user", "content": prompt})

            print(f"[AI] OpenAI запрос: модель={self.model}, сообщений={len(messages)}")
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            result = response.choices[0].message.content
            print(f"[AI] OpenAI ответ получен: {len(result)} символов")
            return result
        except Exception as e:
            error_msg = f"Ошибка OpenAI: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
