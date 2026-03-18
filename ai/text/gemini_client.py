from typing import Optional

print("[AI] Загрузка gemini_client")


class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash",
                 temperature: float = 0.7, max_tokens: int = 2000,
                 system_prompt: str = "You are a helpful assistant."):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self._genai = None
        print(f"[AI] Gemini клиент создан, модель: {model}")

    def _get_genai(self):
        if self._genai is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._genai = genai
            except ImportError:
                raise ImportError("Установите google-generativeai: pip install google-generativeai")
        return self._genai

    def _convert_history(self, history: list) -> list:
        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        return gemini_history

    async def generate_text(self, prompt: str, history: Optional[list] = None) -> str:
        try:
            import asyncio
            genai = self._get_genai()

            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }

            model_instance = genai.GenerativeModel(
                model_name=self.model,
                generation_config=generation_config,
                system_instruction=self.system_prompt
            )

            gemini_history = self._convert_history(history[-20:]) if history else []
            chat = model_instance.start_chat(history=gemini_history)

            print(f"[AI] Gemini запрос: модель={self.model}, история={len(gemini_history)} сообщений")
            response = await asyncio.to_thread(chat.send_message, prompt)
            result = response.text
            print(f"[AI] Gemini ответ получен: {len(result)} символов")
            return result
        except Exception as e:
            error_msg = f"Ошибка Gemini: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
