import aiohttp
import asyncio
import base64
import json

print("[AI] Загрузка kandinsky_client")

FUSIONBRAIN_BASE_URL = "https://api-key.fusionbrain.ai"


class KandinskyClient:
    def __init__(self, api_key: str, secret_key: str, model: str = "4.0", size: str = "1024x1024"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.model = model
        self.size = size
        print(f"[AI] Kandinsky клиент создан, модель: {model}")

    def _parse_size(self) -> tuple:
        parts = self.size.split("x")
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        return 1024, 1024

    def _get_headers(self) -> dict:
        return {
            "X-Key": f"Key {self.api_key}",
            "X-Secret": f"Secret {self.secret_key}"
        }

    async def _get_model_id(self, session: aiohttp.ClientSession) -> str:
        url = f"{FUSIONBRAIN_BASE_URL}/key/api/v1/models"
        async with session.get(url, headers=self._get_headers()) as resp:
            resp.raise_for_status()
            models = await resp.json()
            if models:
                return str(models[0]["id"])
        return "4"

    async def _run_generation(self, session: aiohttp.ClientSession, model_id: str,
                               prompt: str, width: int, height: int) -> str:
        url = f"{FUSIONBRAIN_BASE_URL}/key/api/v1/text2image/run"
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": width,
            "height": height,
            "generateParams": {"query": prompt}
        }
        data = aiohttp.FormData()
        data.add_field("model_id", model_id)
        data.add_field("params", json.dumps(params), content_type="application/json")

        async with session.post(url, headers=self._get_headers(), data=data) as resp:
            resp.raise_for_status()
            result = await resp.json()
            return result["uuid"]

    async def _check_status(self, session: aiohttp.ClientSession, task_uuid: str) -> dict:
        url = f"{FUSIONBRAIN_BASE_URL}/key/api/v1/text2image/status/{task_uuid}"
        async with session.get(url, headers=self._get_headers()) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def generate(self, prompt: str) -> bytes:
        try:
            width, height = self._parse_size()
            print(f"[AI] Kandinsky запрос: размер={width}x{height}")
            async with aiohttp.ClientSession() as session:
                model_id = await self._get_model_id(session)
                task_uuid = await self._run_generation(session, model_id, prompt, width, height)
                print(f"[AI] Kandinsky задача создана: {task_uuid}")

                for attempt in range(30):
                    await asyncio.sleep(3)
                    status = await self._check_status(session, task_uuid)
                    print(f"[AI] Kandinsky статус: {status.get('status')} (попытка {attempt + 1})")
                    if status.get("status") == "DONE":
                        images = status.get("images", [])
                        if images:
                            image_bytes = base64.b64decode(images[0])
                            print(f"[AI] Kandinsky изображение получено: {len(image_bytes)} байт")
                            return image_bytes
                        raise RuntimeError("Kandinsky: изображение не получено")
                    elif status.get("status") == "FAIL":
                        raise RuntimeError(f"Kandinsky: генерация провалилась: {status.get('errorDescription', '')}")

                raise RuntimeError("Kandinsky: превышено время ожидания генерации")
        except Exception as e:
            error_msg = f"Ошибка Kandinsky: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
