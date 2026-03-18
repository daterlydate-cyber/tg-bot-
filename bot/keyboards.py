from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config.config_manager import ConfigManager

print("[Bot] Загрузка keyboards")


def build_main_keyboard() -> ReplyKeyboardMarkup:
    config = ConfigManager()
    buttons = config.get_buttons()
    rows_dict: dict[int, list] = {}
    for btn in buttons:
        row = btn.get("row", 0)
        if row not in rows_dict:
            rows_dict[row] = []
        rows_dict[row].append(KeyboardButton(text=btn["text"]))
    keyboard_rows = [rows_dict[r] for r in sorted(rows_dict.keys())]
    if not keyboard_rows:
        keyboard_rows = [
            [KeyboardButton(text="💬 Текст AI"), KeyboardButton(text="🎨 Изображение AI")],
            [KeyboardButton(text="🎬 Видео AI"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="🔄 Сбросить"), KeyboardButton(text="⚙️ Текущая модель")]
        ]
    return ReplyKeyboardMarkup(keyboard=keyboard_rows, resize_keyboard=True)


def build_text_providers_inline(providers: list) -> InlineKeyboardMarkup:
    provider_names = {
        "openai": "🤖 OpenAI GPT",
        "gemini": "✨ Google Gemini",
        "claude": "🧠 Anthropic Claude"
    }
    buttons = []
    for p in providers:
        name = provider_names.get(p, p.capitalize())
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"select_text:{p}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_image_providers_inline(providers: list) -> InlineKeyboardMarkup:
    provider_names = {
        "dalle": "🎨 DALL-E 3",
        "stability": "🖼️ Stability AI",
        "kandinsky": "🎭 Kandinsky"
    }
    buttons = []
    for p in providers:
        name = provider_names.get(p, p.capitalize())
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"select_image:{p}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_video_providers_inline(providers: list) -> InlineKeyboardMarkup:
    provider_names = {
        "runway": "🎬 Runway ML",
        "replicate": "🔄 Replicate"
    }
    buttons = []
    for p in providers:
        name = provider_names.get(p, p.capitalize())
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"select_video:{p}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
