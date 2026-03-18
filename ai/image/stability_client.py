import aiohttp
import asyncio

print("[AI] Загрузка stability_client")

STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"


class StabilityClient:
    def __init__(self, api_key: str, model: str = "sd3", size: str = "1024x1024"):
        self.api_key = api_key
        self.model = model
        self.size = size
        print(f"[AI] Stability AI клиент создан, модель: {model}")

    def _parse_size(self) -> tuple:
        parts = self.size.split("x")
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        return 1024, 1024

    async def generate(self, prompt: str) -> bytes:
        try:
            width, height = self._parse_size()
            print(f"[AI] Stability AI запрос: модель={self.model}, размер={width}x{height}")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"
            }
            data = aiohttp.FormData()
            data.add_field("prompt", prompt)
            data.add_field("model", self.model)
            data.add_field("output_format", "png")

            async with aiohttp.ClientSession() as session:
                async with session.post(STABILITY_API_URL, headers=headers, data=data) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise RuntimeError(f"Stability AI API вернул {resp.status}: {text}")
                    image_bytes = await resp.read()

            print(f"[AI] Stability AI изображение получено: {len(image_bytes)} байт")
            return image_bytes
        except Exception as e:
            error_msg = f"Ошибка Stability AI: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
