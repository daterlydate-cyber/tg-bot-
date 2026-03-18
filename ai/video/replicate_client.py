import aiohttp
import asyncio

print("[AI] Загрузка replicate_client")

REPLICATE_API_URL = "https://api.replicate.com/v1"


class ReplicateClient:
    def __init__(self, api_key: str, model: str = "minimax/video-01-live", duration: int = 5):
        self.api_key = api_key
        self.model = model
        self.duration = duration
        print(f"[AI] Replicate клиент создан, модель: {model}")

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "wait"
        }

    async def generate(self, prompt: str) -> bytes:
        try:
            print(f"[AI] Replicate запрос: модель={self.model}")
            payload = {
                "version": self.model if "/" not in self.model else None,
                "input": {
                    "prompt": prompt,
                    "duration": self.duration
                }
            }
            if "/" in self.model:
                payload.pop("version", None)
                url = f"{REPLICATE_API_URL}/models/{self.model}/predictions"
            else:
                url = f"{REPLICATE_API_URL}/predictions"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self._get_headers(), json=payload) as resp:
                    if resp.status not in (200, 201):
                        text = await resp.text()
                        raise RuntimeError(f"Replicate API вернул {resp.status}: {text}")
                    prediction = await resp.json()
                    prediction_id = prediction.get("id")

                print(f"[AI] Replicate предсказание создано: {prediction_id}")
                for attempt in range(60):
                    await asyncio.sleep(5)
                    async with session.get(
                        f"{REPLICATE_API_URL}/predictions/{prediction_id}",
                        headers=self._get_headers()
                    ) as poll_resp:
                        poll_resp.raise_for_status()
                        status_data = await poll_resp.json()
                        status = status_data.get("status")
                        print(f"[AI] Replicate статус: {status} (попытка {attempt + 1})")
                        if status == "succeeded":
                            output = status_data.get("output")
                            video_url = output if isinstance(output, str) else (output[0] if output else None)
                            if not video_url:
                                raise RuntimeError("Replicate: URL видео не получен")
                            async with session.get(video_url) as video_resp:
                                video_resp.raise_for_status()
                                video_bytes = await video_resp.read()
                            print(f"[AI] Replicate видео скачано: {len(video_bytes)} байт")
                            return video_bytes
                        elif status == "failed":
                            raise RuntimeError(f"Replicate: генерация провалилась: {status_data.get('error', '')}")

            raise RuntimeError("Replicate: превышено время ожидания генерации")
        except Exception as e:
            error_msg = f"Ошибка Replicate: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
