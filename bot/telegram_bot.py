import asyncio
import threading
from typing import Optional, Callable

print("[Bot] Загрузка telegram_bot")


class TelegramBot:
    def __init__(self, log_callback: Optional[Callable] = None):
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._dp = None
        self._bot = None
        self._running = False
        self._log_callback = log_callback
        self._ai_manager = None
        self._config = None
        print("[Bot] TelegramBot создан")

    def _log(self, message: str):
        print(f"[Bot] {message}")
        if self._log_callback:
            self._log_callback(message)

    def is_running(self) -> bool:
        return self._running

    def start(self, token: str):
        if self._running:
            self._log("Бот уже запущен")
            return
        if not token or not token.strip():
            self._log("Ошибка: токен бота не указан")
            raise ValueError("Токен бота не указан")

        self._log("Запуск бота...")
        self._thread = threading.Thread(target=self._run_in_thread, args=(token,), daemon=True, name="TelegramBotThread")
        self._thread.start()

    def _run_in_thread(self, token: str):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._async_start(token))
        except Exception as e:
            self._log(f"Критическая ошибка бота: {e}")
            self._running = False
        finally:
            try:
                self._loop.close()
            except Exception:
                pass
            self._running = False
            self._log("Бот остановлен")

    async def _async_start(self, token: str):
        try:
            from aiogram import Bot, Dispatcher
            from aiogram.enums import ParseMode
            from aiogram.client.default import DefaultBotProperties
            from config.config_manager import ConfigManager
            from ai.ai_manager import AIManager
            from bot.handlers import router, setup_handlers

            self._log("Инициализация бота...")
            self._bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            self._dp = Dispatcher()
            self._dp.include_router(router)

            config = ConfigManager()
            self._ai_manager = AIManager()
            setup_handlers(self._ai_manager, config)

            self._running = True
            self._log("Бот успешно запущен и слушает сообщения")

            await self._dp.start_polling(self._bot, allowed_updates=["message", "callback_query"])
        except Exception as e:
            self._log(f"Ошибка запуска бота: {e}")
            raise

    def stop(self):
        if not self._running:
            self._log("Бот не запущен")
            return
        self._log("Остановка бота...")
        if self._loop and self._dp:
            asyncio.run_coroutine_threadsafe(self._dp.stop_polling(), self._loop)
        if self._bot and self._loop:
            asyncio.run_coroutine_threadsafe(self._bot.session.close(), self._loop)
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._log("Бот остановлен")
