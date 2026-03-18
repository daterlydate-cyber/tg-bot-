import aiohttp
import asyncio

print("[AI] Загрузка dalle_client")


class DalleClient:
    def __init__(self, api_key: str, model: str = "dall-e-3",
                 size: str = "1024x1024", quality: str = "standard", style: str = "vivid"):
        self.api_key = api_key
        self.model = model
        self.size = size
        self.quality = quality
        self.style = style
        self._client = None
        print(f"[AI] DALL-E клиент создан, модель: {model}")

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Установите openai: pip install openai")
        return self._client

    async def generate(self, prompt: str) -> bytes:
        try:
            client = self._get_client()
            print(f"[AI] DALL-E запрос: модель={self.model}, размер={self.size}, качество={self.quality}")
            response = await client.images.generate(
                model=self.model,
                prompt=prompt,
                size=self.size,
                quality=self.quality,
                style=self.style,
                n=1
            )
            image_url = response.data[0].url
            print(f"[AI] DALL-E изображение сгенерировано, скачивание: {image_url[:60]}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    resp.raise_for_status()
                    image_bytes = await resp.read()
            print(f"[AI] DALL-E изображение скачано: {len(image_bytes)} байт")
            return image_bytes
        except Exception as e:
            error_msg = f"Ошибка DALL-E: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
