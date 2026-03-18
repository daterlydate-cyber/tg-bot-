from typing import Optional

print("[AI] Загрузка claude_client")


class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022",
                 temperature: float = 0.7, max_tokens: int = 2000,
                 system_prompt: str = "You are a helpful assistant."):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self._client = None
        print(f"[AI] Claude клиент создан, модель: {model}")

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Установите anthropic: pip install anthropic")
        return self._client

    async def generate_text(self, prompt: str, history: Optional[list] = None) -> str:
        try:
            client = self._get_client()
            messages = []
            if history:
                for msg in history[-20:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": prompt})

            print(f"[AI] Claude запрос: модель={self.model}, сообщений={len(messages)}")
            response = await client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                messages=messages,
                temperature=self.temperature
            )
            result = response.content[0].text
            print(f"[AI] Claude ответ получен: {len(result)} символов")
            return result
        except Exception as e:
            error_msg = f"Ошибка Claude: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
