"""
Запуск бота без GUI — для деплоя на сервер (headless режим).
Использование:
    python run_headless.py

Требует наличия config.json с заполненным токеном и API-ключами.
"""
import sys
import os
import asyncio
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[Bot] Запуск headless режима...")

from config.config_manager import ConfigManager
from ai.ai_manager import AIManager
from bot.handlers import setup_handlers


async def main():
    config = ConfigManager()
    token = config.get("bot.token", "").strip()

    if not token:
        print("[Bot] ОШИБКА: Токен бота не указан в config.json")
        print("[Bot] Укажите токен в секции 'bot.token' файла config.json")
        sys.exit(1)

    print(f"[Bot] Токен: {'*' * (len(token) - 5)}{token[-5:]}")

    ai_manager = AIManager()
    setup_handlers(ai_manager, config)

    text_providers = ai_manager.get_available_text_providers()
    image_providers = ai_manager.get_available_image_providers()
    video_providers = ai_manager.get_available_video_providers()

    print(f"[Bot] Доступные текстовые AI: {text_providers or 'нет'}")
    print(f"[Bot] Доступные AI для изображений: {image_providers or 'нет'}")
    print(f"[Bot] Доступные AI для видео: {video_providers or 'нет'}")

    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties
        from bot.handlers import router
    except ImportError as e:
        print(f"[Bot] ОШИБКА: Не удалось импортировать aiogram: {e}")
        print("[Bot] Установите зависимости: pip install -r requirements.txt")
        sys.exit(1)

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    print("[Bot] Бот запущен в headless режиме. Нажмите Ctrl+C для остановки.")

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except asyncio.CancelledError:
        print("[Bot] Получен сигнал остановки")
    finally:
        await bot.session.close()
        print("[Bot] Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Bot] Остановлено пользователем")
