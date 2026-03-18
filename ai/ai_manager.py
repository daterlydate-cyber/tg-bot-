import asyncio
import threading
from typing import Optional

from config.config_manager import ConfigManager

print("[AI] Загрузка ai_manager")


class AIManager:
    def __init__(self):
        self._config = ConfigManager()
        self._text_clients = {}
        self._image_clients = {}
        self._video_clients = {}
        self._histories = {}
        self._lock = threading.Lock()
        self._reload_clients()
        print("[AI] AIManager инициализирован")

    def _reload_clients(self):
        with self._lock:
            self._text_clients = {}
            self._image_clients = {}
            self._video_clients = {}
            self._build_text_clients()
            self._build_image_clients()
            self._build_video_clients()

    def _build_text_clients(self):
        cfg = self._config

        openai_cfg = cfg.get("text_ai_providers.openai", {})
        if openai_cfg.get("enabled") and openai_cfg.get("api_key"):
            try:
                from ai.text.openai_client import OpenAIClient
                self._text_clients["openai"] = OpenAIClient(
                    api_key=openai_cfg["api_key"],
                    model=openai_cfg.get("model", "gpt-4o-mini"),
                    temperature=openai_cfg.get("temperature", 0.7),
                    max_tokens=openai_cfg.get("max_tokens", 2000),
                    system_prompt=openai_cfg.get("system_prompt", "You are a helpful assistant.")
                )
            except Exception as e:
                print(f"[AI] Не удалось создать OpenAI клиент: {e}")

        gemini_cfg = cfg.get("text_ai_providers.gemini", {})
        if gemini_cfg.get("enabled") and gemini_cfg.get("api_key"):
            try:
                from ai.text.gemini_client import GeminiClient
                self._text_clients["gemini"] = GeminiClient(
                    api_key=gemini_cfg["api_key"],
                    model=gemini_cfg.get("model", "gemini-1.5-flash"),
                    temperature=gemini_cfg.get("temperature", 0.7),
                    max_tokens=gemini_cfg.get("max_tokens", 2000),
                    system_prompt=gemini_cfg.get("system_prompt", "You are a helpful assistant.")
                )
            except Exception as e:
                print(f"[AI] Не удалось создать Gemini клиент: {e}")

        claude_cfg = cfg.get("text_ai_providers.claude", {})
        if claude_cfg.get("enabled") and claude_cfg.get("api_key"):
            try:
                from ai.text.claude_client import ClaudeClient
                self._text_clients["claude"] = ClaudeClient(
                    api_key=claude_cfg["api_key"],
                    model=claude_cfg.get("model", "claude-3-5-sonnet-20241022"),
                    temperature=claude_cfg.get("temperature", 0.7),
                    max_tokens=claude_cfg.get("max_tokens", 2000),
                    system_prompt=claude_cfg.get("system_prompt", "You are a helpful assistant.")
                )
            except Exception as e:
                print(f"[AI] Не удалось создать Claude клиент: {e}")

    def _build_image_clients(self):
        cfg = self._config

        dalle_cfg = cfg.get("image_ai_providers.dalle", {})
        if dalle_cfg.get("enabled") and dalle_cfg.get("api_key"):
            try:
                from ai.image.dalle_client import DalleClient
                self._image_clients["dalle"] = DalleClient(
                    api_key=dalle_cfg["api_key"],
                    model=dalle_cfg.get("model", "dall-e-3"),
                    size=dalle_cfg.get("size", "1024x1024"),
                    quality=dalle_cfg.get("quality", "standard"),
                    style=dalle_cfg.get("style", "vivid")
                )
            except Exception as e:
                print(f"[AI] Не удалось создать DALL-E клиент: {e}")

        stability_cfg = cfg.get("image_ai_providers.stability", {})
        if stability_cfg.get("enabled") and stability_cfg.get("api_key"):
            try:
                from ai.image.stability_client import StabilityClient
                self._image_clients["stability"] = StabilityClient(
                    api_key=stability_cfg["api_key"],
                    model=stability_cfg.get("model", "sd3"),
                    size=stability_cfg.get("size", "1024x1024")
                )
            except Exception as e:
                print(f"[AI] Не удалось создать Stability AI клиент: {e}")

        kandinsky_cfg = cfg.get("image_ai_providers.kandinsky", {})
        if kandinsky_cfg.get("enabled") and kandinsky_cfg.get("api_key"):
            try:
                from ai.image.kandinsky_client import KandinskyClient
                self._image_clients["kandinsky"] = KandinskyClient(
                    api_key=kandinsky_cfg["api_key"],
                    secret_key=kandinsky_cfg.get("secret_key", ""),
                    model=kandinsky_cfg.get("model", "4.0"),
                    size=kandinsky_cfg.get("size", "1024x1024")
                )
            except Exception as e:
                print(f"[AI] Не удалось создать Kandinsky клиент: {e}")

    def _build_video_clients(self):
        cfg = self._config

        runway_cfg = cfg.get("video_ai_providers.runway", {})
        if runway_cfg.get("enabled") and runway_cfg.get("api_key"):
            try:
                from ai.video.runway_client import RunwayClient
                self._video_clients["runway"] = RunwayClient(
                    api_key=runway_cfg["api_key"],
                    model=runway_cfg.get("model", "gen3a_turbo"),
                    duration=runway_cfg.get("duration", 5)
                )
            except Exception as e:
                print(f"[AI] Не удалось создать Runway клиент: {e}")

        replicate_cfg = cfg.get("video_ai_providers.replicate", {})
        if replicate_cfg.get("enabled") and replicate_cfg.get("api_key"):
            try:
                from ai.video.replicate_client import ReplicateClient
                self._video_clients["replicate"] = ReplicateClient(
                    api_key=replicate_cfg["api_key"],
                    model=replicate_cfg.get("model", "minimax/video-01-live"),
                    duration=replicate_cfg.get("duration", 5)
                )
            except Exception as e:
                print(f"[AI] Не удалось создать Replicate клиент: {e}")

    def reload_all(self):
        print("[AI] Перезагрузка всех AI-клиентов...")
        self._reload_clients()
        print("[AI] Все AI-клиенты перезагружены")

    def _get_user_history(self, user_id: int, provider: str) -> list:
        key = f"{user_id}_{provider}"
        if key not in self._histories:
            self._histories[key] = []
        return self._histories[key]

    def _update_history(self, user_id: int, provider: str, user_msg: str, assistant_msg: str):
        key = f"{user_id}_{provider}"
        if key not in self._histories:
            self._histories[key] = []
        self._histories[key].append({"role": "user", "content": user_msg})
        self._histories[key].append({"role": "assistant", "content": assistant_msg})
        if len(self._histories[key]) > 40:
            self._histories[key] = self._histories[key][-40:]

    def clear_history(self, user_id: int):
        keys_to_remove = [k for k in self._histories if k.startswith(f"{user_id}_")]
        for key in keys_to_remove:
            del self._histories[key]
        print(f"[AI] История пользователя {user_id} очищена")

    async def generate_text(self, provider: str, prompt: str, user_id: int) -> str:
        with self._lock:
            client = self._text_clients.get(provider)
        if not client:
            raise RuntimeError(f"Текстовый провайдер '{provider}' недоступен или не настроен")
        history = self._get_user_history(user_id, provider)
        result = await client.generate_text(prompt, history)
        self._update_history(user_id, provider, prompt, result)
        return result

    async def generate_image(self, provider: str, prompt: str) -> bytes:
        with self._lock:
            client = self._image_clients.get(provider)
        if not client:
            raise RuntimeError(f"Провайдер изображений '{provider}' недоступен или не настроен")
        return await client.generate(prompt)

    async def generate_video(self, provider: str, prompt: str) -> bytes:
        with self._lock:
            client = self._video_clients.get(provider)
        if not client:
            raise RuntimeError(f"Видео-провайдер '{provider}' недоступен или не настроен")
        return await client.generate(prompt)

    def get_available_text_providers(self) -> list:
        with self._lock:
            return list(self._text_clients.keys())

    def get_available_image_providers(self) -> list:
        with self._lock:
            return list(self._image_clients.keys())

    def get_available_video_providers(self) -> list:
        with self._lock:
            return list(self._video_clients.keys())
