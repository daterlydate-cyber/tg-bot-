from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile

from config.config_manager import ConfigManager
from ai.ai_manager import AIManager
from bot.keyboards import (
    build_main_keyboard,
    build_text_providers_inline,
    build_image_providers_inline,
    build_video_providers_inline
)

print("[Bot] Загрузка handlers")

router = Router()
_ai_manager: AIManager = None
_config: ConfigManager = None

user_state: dict = {}
CHUNK_SIZE = 4096


def setup_handlers(ai_manager: AIManager, config: ConfigManager):
    global _ai_manager, _config
    _ai_manager = ai_manager
    _config = config
    print("[Bot] Обработчики настроены")


def _get_user_state(user_id: int) -> dict:
    if user_id not in user_state:
        user_state[user_id] = {"mode": "text", "provider": None}
    return user_state[user_id]


def _get_provider_display_name(mode: str, provider: str) -> str:
    names = {
        "openai": "OpenAI GPT", "gemini": "Google Gemini", "claude": "Anthropic Claude",
        "dalle": "DALL-E 3", "stability": "Stability AI", "kandinsky": "Kandinsky",
        "runway": "Runway ML", "replicate": "Replicate"
    }
    mode_names = {"text": "Текст", "image": "Изображение", "video": "Видео"}
    provider_name = names.get(provider, provider or "не выбран")
    mode_name = mode_names.get(mode, mode)
    return f"{mode_name} / {provider_name}"


async def _split_and_send(message: Message, text: str):
    for i in range(0, len(text), CHUNK_SIZE):
        await message.answer(text[i:i + CHUNK_SIZE])


@router.message(Command("start"))
async def cmd_start(message: Message):
    print(f"[Bot] /start от пользователя {message.from_user.id}")
    welcome = _config.get("bot.welcome_message", "Привет! Я AI-бот.")
    keyboard = build_main_keyboard()
    await message.answer(welcome, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    print(f"[Bot] /help от пользователя {message.from_user.id}")
    text_providers = _ai_manager.get_available_text_providers()
    image_providers = _ai_manager.get_available_image_providers()
    video_providers = _ai_manager.get_available_video_providers()

    help_text = (
        "📖 *Справка по боту*\n\n"
        "Команды:\n"
        "/start — приветствие и главное меню\n"
        "/help — эта справка\n"
        "/text — выбрать текстовую нейросеть\n"
        "/image — выбрать нейросеть для изображений\n"
        "/video — выбрать нейросеть для видео\n"
        "/reset — сбросить историю диалога\n\n"
        f"Доступные текстовые AI: {', '.join(text_providers) or 'не настроены'}\n"
        f"Доступные AI для изображений: {', '.join(image_providers) or 'не настроены'}\n"
        f"Доступные AI для видео: {', '.join(video_providers) or 'не настроены'}"
    )
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("text"))
async def cmd_text(message: Message):
    print(f"[Bot] /text от пользователя {message.from_user.id}")
    providers = _ai_manager.get_available_text_providers()
    if not providers:
        await message.answer("❌ Нет доступных текстовых AI. Настройте API-ключи в панели управления.")
        return
    keyboard = build_text_providers_inline(providers)
    await message.answer("💬 Выберите текстовую нейросеть:", reply_markup=keyboard)


@router.message(Command("image"))
async def cmd_image(message: Message):
    print(f"[Bot] /image от пользователя {message.from_user.id}")
    providers = _ai_manager.get_available_image_providers()
    if not providers:
        await message.answer("❌ Нет доступных AI для изображений. Настройте API-ключи в панели управления.")
        return
    keyboard = build_image_providers_inline(providers)
    await message.answer("🎨 Выберите нейросеть для генерации изображений:", reply_markup=keyboard)


@router.message(Command("video"))
async def cmd_video(message: Message):
    print(f"[Bot] /video от пользователя {message.from_user.id}")
    providers = _ai_manager.get_available_video_providers()
    if not providers:
        await message.answer("❌ Нет доступных AI для видео. Настройте API-ключи в панели управления.")
        return
    keyboard = build_video_providers_inline(providers)
    await message.answer("🎬 Выберите нейросеть для генерации видео:", reply_markup=keyboard)


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    user_id = message.from_user.id
    print(f"[Bot] /reset от пользователя {user_id}")
    _ai_manager.clear_history(user_id)
    if user_id in user_state:
        user_state[user_id]["provider"] = None
    await message.answer("🔄 История диалога сброшена. Выберите режим работы.", reply_markup=build_main_keyboard())


@router.callback_query(F.data.startswith("select_text:"))
async def cb_select_text(callback: CallbackQuery):
    provider = callback.data.split(":")[1]
    user_id = callback.from_user.id
    state = _get_user_state(user_id)
    state["mode"] = "text"
    state["provider"] = provider
    provider_names = {"openai": "OpenAI GPT", "gemini": "Google Gemini", "claude": "Anthropic Claude"}
    name = provider_names.get(provider, provider)
    print(f"[Bot] Пользователь {user_id} выбрал текстовый провайдер: {provider}")
    await callback.message.edit_text(f"✅ Выбрана нейросеть: *{name}*\n\nТеперь отправьте ваше сообщение.", parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("select_image:"))
async def cb_select_image(callback: CallbackQuery):
    provider = callback.data.split(":")[1]
    user_id = callback.from_user.id
    state = _get_user_state(user_id)
    state["mode"] = "image"
    state["provider"] = provider
    provider_names = {"dalle": "DALL-E 3", "stability": "Stability AI", "kandinsky": "Kandinsky"}
    name = provider_names.get(provider, provider)
    print(f"[Bot] Пользователь {user_id} выбрал провайдер изображений: {provider}")
    await callback.message.edit_text(f"✅ Выбрана нейросеть: *{name}*\n\nОпишите изображение, которое хотите сгенерировать.", parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("select_video:"))
async def cb_select_video(callback: CallbackQuery):
    provider = callback.data.split(":")[1]
    user_id = callback.from_user.id
    state = _get_user_state(user_id)
    state["mode"] = "video"
    state["provider"] = provider
    provider_names = {"runway": "Runway ML", "replicate": "Replicate"}
    name = provider_names.get(provider, provider)
    print(f"[Bot] Пользователь {user_id} выбрал видео-провайдер: {provider}")
    await callback.message.edit_text(f"✅ Выбрана нейросеть: *{name}*\n\nОпишите видео, которое хотите сгенерировать.", parse_mode="Markdown")
    await callback.answer()


@router.message(F.text)
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text
    state = _get_user_state(user_id)

    print(f"[Bot] Сообщение от {user_id}: '{text[:50]}...' (режим: {state['mode']}, провайдер: {state['provider']})")

    if text == "💬 Текст AI":
        providers = _ai_manager.get_available_text_providers()
        if not providers:
            await message.answer("❌ Нет доступных текстовых AI. Настройте API-ключи в панели управления.")
            return
        await message.answer("💬 Выберите текстовую нейросеть:", reply_markup=build_text_providers_inline(providers))
        return

    if text == "🎨 Изображение AI":
        providers = _ai_manager.get_available_image_providers()
        if not providers:
            await message.answer("❌ Нет доступных AI для изображений. Настройте API-ключи в панели управления.")
            return
        await message.answer("🎨 Выберите нейросеть для генерации изображений:", reply_markup=build_image_providers_inline(providers))
        return

    if text == "🎬 Видео AI":
        providers = _ai_manager.get_available_video_providers()
        if not providers:
            await message.answer("❌ Нет доступных AI для видео. Настройте API-ключи в панели управления.")
            return
        await message.answer("🎬 Выберите нейросеть для генерации видео:", reply_markup=build_video_providers_inline(providers))
        return

    if text == "ℹ️ Помощь":
        await cmd_help(message)
        return

    if text == "🔄 Сбросить":
        await cmd_reset(message)
        return

    if text == "⚙️ Текущая модель":
        info = _get_provider_display_name(state["mode"], state["provider"])
        await message.answer(f"⚙️ Текущая модель: *{info}*", parse_mode="Markdown")
        return

    if not state.get("provider"):
        if state["mode"] == "text":
            providers = _ai_manager.get_available_text_providers()
            if providers:
                await message.answer("💬 Выберите текстовую нейросеть:", reply_markup=build_text_providers_inline(providers))
            else:
                await message.answer("❌ Нет доступных AI. Настройте API-ключи в панели управления.")
        elif state["mode"] == "image":
            providers = _ai_manager.get_available_image_providers()
            if providers:
                await message.answer("🎨 Выберите нейросеть:", reply_markup=build_image_providers_inline(providers))
            else:
                await message.answer("❌ Нет доступных AI для изображений.")
        elif state["mode"] == "video":
            providers = _ai_manager.get_available_video_providers()
            if providers:
                await message.answer("🎬 Выберите нейросеть:", reply_markup=build_video_providers_inline(providers))
            else:
                await message.answer("❌ Нет доступных AI для видео.")
        return

    mode = state["mode"]
    provider = state["provider"]

    if mode == "text":
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        try:
            response = await _ai_manager.generate_text(provider, text, user_id)
            await _split_and_send(message, response)
        except Exception as e:
            print(f"[Bot] Ошибка генерации текста: {e}")
            await message.answer(f"❌ Ошибка: {e}")

    elif mode == "image":
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_PHOTO)
        try:
            wait_msg = await message.answer("🎨 Генерирую изображение, подождите...")
            image_bytes = await _ai_manager.generate_image(provider, text)
            await wait_msg.delete()
            photo = BufferedInputFile(image_bytes, filename="image.png")
            await message.answer_photo(photo, caption=f"🎨 Сгенерировано с помощью {provider}")
        except Exception as e:
            print(f"[Bot] Ошибка генерации изображения: {e}")
            await message.answer(f"❌ Ошибка генерации изображения: {e}")

    elif mode == "video":
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)
        try:
            wait_msg = await message.answer("🎬 Генерирую видео, это может занять несколько минут...")
            video_bytes = await _ai_manager.generate_video(provider, text)
            await wait_msg.delete()
            video_file = BufferedInputFile(video_bytes, filename="video.mp4")
            try:
                await message.answer_video(video_file, caption=f"🎬 Сгенерировано с помощью {provider}")
            except Exception:
                await message.answer_animation(video_file, caption=f"🎬 Сгенерировано с помощью {provider}")
        except Exception as e:
            print(f"[Bot] Ошибка генерации видео: {e}")
            await message.answer(f"❌ Ошибка генерации видео: {e}")
