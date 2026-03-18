import json
import os
import threading
import uuid
from typing import Any

print("[Config] Инициализация модуля config_manager")

DEFAULT_CONFIG = {
    "bot": {
        "token": "",
        "welcome_message": "Привет! Я AI-бот. Выберите режим работы с помощью кнопок ниже."
    },
    "text_ai_providers": {
        "openai": {
            "enabled": False,
            "api_key": "",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 2000,
            "system_prompt": "You are a helpful assistant."
        },
        "gemini": {
            "enabled": False,
            "api_key": "",
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 2000,
            "system_prompt": "You are a helpful assistant."
        },
        "claude": {
            "enabled": False,
            "api_key": "",
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
            "max_tokens": 2000,
            "system_prompt": "You are a helpful assistant."
        }
    },
    "image_ai_providers": {
        "dalle": {
            "enabled": False,
            "api_key": "",
            "model": "dall-e-3",
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid"
        },
        "stability": {
            "enabled": False,
            "api_key": "",
            "model": "sd3",
            "size": "1024x1024"
        },
        "kandinsky": {
            "enabled": False,
            "api_key": "",
            "secret_key": "",
            "model": "4.0",
            "size": "1024x1024"
        }
    },
    "video_ai_providers": {
        "runway": {
            "enabled": False,
            "api_key": "",
            "model": "gen3a_turbo",
            "duration": 5
        },
        "replicate": {
            "enabled": False,
            "api_key": "",
            "model": "minimax/video-01-live",
            "duration": 5
        }
    },
    "buttons": [
        {"id": "btn_text", "text": "💬 Текст AI", "action": "select_text_ai", "ai_provider": "", "row": 0},
        {"id": "btn_image", "text": "🎨 Изображение AI", "action": "select_image_ai", "ai_provider": "", "row": 0},
        {"id": "btn_video", "text": "🎬 Видео AI", "action": "select_video_ai", "ai_provider": "", "row": 1},
        {"id": "btn_help", "text": "ℹ️ Помощь", "action": "show_help", "ai_provider": "", "row": 1},
        {"id": "btn_reset", "text": "🔄 Сбросить", "action": "reset", "ai_provider": "", "row": 2},
        {"id": "btn_model", "text": "⚙️ Текущая модель", "action": "show_model", "ai_provider": "", "row": 2}
    ]
}


class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self._data = {}
        self._rw_lock = threading.RLock()
        self._load()
        print(f"[Config] Конфиг загружен из {self._config_path}")

    def _load(self):
        with self._rw_lock:
            if os.path.exists(self._config_path):
                try:
                    with open(self._config_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                    self._data = self._deep_merge(DEFAULT_CONFIG, loaded)
                    print("[Config] Конфиг успешно прочитан")
                except Exception as e:
                    print(f"[Config] Ошибка чтения конфига: {e} — используется конфиг по умолчанию")
                    self._data = json.loads(json.dumps(DEFAULT_CONFIG))
            else:
                self._data = json.loads(json.dumps(DEFAULT_CONFIG))
                self._save()
                print("[Config] Создан новый конфиг по умолчанию")

    def _save(self):
        with self._rw_lock:
            try:
                with open(self._config_path, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Config] Ошибка сохранения конфига: {e}")

    def _deep_merge(self, base: dict, override: dict) -> dict:
        result = json.loads(json.dumps(base))
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, path: str, default: Any = None) -> Any:
        with self._rw_lock:
            keys = path.split(".")
            current = self._data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current

    def set(self, path: str, value: Any):
        with self._rw_lock:
            keys = path.split(".")
            current = self._data
            for key in keys[:-1]:
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
            self._save()
            print(f"[Config] Установлено {path} = {value if 'key' not in path.lower() else '***'}")

    def add_button(self, text: str, action: str, ai_provider: str = "", row: int = 0) -> dict:
        with self._rw_lock:
            button = {
                "id": f"btn_{uuid.uuid4().hex[:8]}",
                "text": text,
                "action": action,
                "ai_provider": ai_provider,
                "row": row
            }
            if "buttons" not in self._data:
                self._data["buttons"] = []
            self._data["buttons"].append(button)
            self._save()
            print(f"[Config] Добавлена кнопка: {text}")
            return button

    def remove_button(self, button_id: str) -> bool:
        with self._rw_lock:
            buttons = self._data.get("buttons", [])
            new_buttons = [b for b in buttons if b.get("id") != button_id]
            if len(new_buttons) < len(buttons):
                self._data["buttons"] = new_buttons
                self._save()
                print(f"[Config] Удалена кнопка: {button_id}")
                return True
            return False

    def get_buttons(self) -> list:
        with self._rw_lock:
            return list(self._data.get("buttons", []))

    def get_enabled_text_providers(self) -> list:
        with self._rw_lock:
            providers = self._data.get("text_ai_providers", {})
            return [name for name, cfg in providers.items() if cfg.get("enabled") and cfg.get("api_key")]

    def get_enabled_image_providers(self) -> list:
        with self._rw_lock:
            providers = self._data.get("image_ai_providers", {})
            return [name for name, cfg in providers.items() if cfg.get("enabled") and cfg.get("api_key")]

    def get_enabled_video_providers(self) -> list:
        with self._rw_lock:
            providers = self._data.get("video_ai_providers", {})
            return [name for name, cfg in providers.items() if cfg.get("enabled") and cfg.get("api_key")]

    def reload(self):
        self._load()
        print("[Config] Конфиг перезагружен")
