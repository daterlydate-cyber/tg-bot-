import aiohttp
import asyncio

print("[AI] Загрузка runway_client")

# TODO: Runway ML Gen-2/Gen-3 API не имеет публичного REST API для прямого доступа.
# Runway предоставляет доступ через веб-интерфейс и SDK (runwayml).
# Для использования необходимо: установить runwayml SDK и использовать официальный API.
# Документация: https://docs.runwayml.com/
# Данная реализация является заглушкой с поддержкой runwayml SDK когда он будет доступен.

RUNWAY_API_URL = "https://api.dev.runwayml.com/v1"


class RunwayClient:
    def __init__(self, api_key: str, model: str = "gen3a_turbo", duration: int = 5):
        self.api_key = api_key
        self.model = model
        self.duration = duration
        print(f"[AI] Runway ML клиент создан, модель: {model}")

    async def generate(self, prompt: str) -> bytes:
        try:
            print(f"[AI] Runway ML запрос: модель={self.model}, длительность={self.duration}с")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-11-06"
            }
            payload = {
                "promptText": prompt,
                "model": self.model,
                "duration": self.duration,
                "ratio": "1280:768"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{RUNWAY_API_URL}/image_to_video",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status not in (200, 201):
                        text = await resp.text()
                        raise RuntimeError(f"Runway ML API вернул {resp.status}: {text}")
                    task_data = await resp.json()
                    task_id = task_data.get("id")

                print(f"[AI] Runway ML задача создана: {task_id}")
                for attempt in range(60):
                    await asyncio.sleep(5)
                    async with session.get(
                        f"{RUNWAY_API_URL}/tasks/{task_id}",
                        headers=headers
                    ) as poll_resp:
                        poll_resp.raise_for_status()
                        status_data = await poll_resp.json()
                        status = status_data.get("status")
                        print(f"[AI] Runway ML статус: {status} (попытка {attempt + 1})")
                        if status == "SUCCEEDED":
                            video_url = status_data.get("output", [None])[0]
                            if not video_url:
                                raise RuntimeError("Runway ML: URL видео не получен")
                            async with session.get(video_url) as video_resp:
                                video_resp.raise_for_status()
                                video_bytes = await video_resp.read()
                            print(f"[AI] Runway ML видео скачано: {len(video_bytes)} байт")
                            return video_bytes
                        elif status in ("FAILED", "CANCELLED"):
                            raise RuntimeError(f"Runway ML: генерация провалилась: {status_data.get('failure', '')}")

            raise RuntimeError("Runway ML: превышено время ожидания генерации")
        except Exception as e:
            error_msg = f"Ошибка Runway ML: {e}"
            print(f"[AI] {error_msg}")
            raise RuntimeError(error_msg)
