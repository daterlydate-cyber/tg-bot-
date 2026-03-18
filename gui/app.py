import customtkinter as ctk
from config.config_manager import ConfigManager
from bot.telegram_bot import TelegramBot
from gui.bot_tab import BotTab
from gui.buttons_tab import ButtonsTab
from gui.text_ai_tab import TextAITab
from gui.image_ai_tab import ImageAITab
from gui.video_ai_tab import VideoAITab

print("[GUI] Загрузка app")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🤖 Telegram AI Bot Manager")
        self.geometry("900x680")
        self.minsize(750, 550)

        self._config = ConfigManager()
        self._bot = TelegramBot(log_callback=self._on_bot_log)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        print("[GUI] Главное окно создано")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, height=50, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(header, text="🤖 Telegram AI Bot Manager",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20, pady=10)

        self._tab_view = ctk.CTkTabview(self)
        self._tab_view.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        tabs = [
            ("🤖 Бот", None),
            ("📱 Кнопки", None),
            ("💬 Текст AI", None),
            ("🎨 Изображения AI", None),
            ("🎬 Видео AI", None)
        ]
        for name, _ in tabs:
            self._tab_view.add(name)

        bot_tab_frame = self._tab_view.tab("🤖 Бот")
        bot_tab_frame.grid_columnconfigure(0, weight=1)
        bot_tab_frame.grid_rowconfigure(0, weight=1)
        self._bot_tab = BotTab(bot_tab_frame, self._bot, self._config)
        self._bot_tab.grid(row=0, column=0, sticky="nsew")

        buttons_tab_frame = self._tab_view.tab("📱 Кнопки")
        buttons_tab_frame.grid_columnconfigure(0, weight=1)
        buttons_tab_frame.grid_rowconfigure(0, weight=1)
        self._buttons_tab = ButtonsTab(buttons_tab_frame, self._config)
        self._buttons_tab.grid(row=0, column=0, sticky="nsew")

        text_ai_frame = self._tab_view.tab("💬 Текст AI")
        text_ai_frame.grid_columnconfigure(0, weight=1)
        text_ai_frame.grid_rowconfigure(0, weight=1)
        self._text_ai_tab = TextAITab(text_ai_frame, self._config)
        self._text_ai_tab.grid(row=0, column=0, sticky="nsew")

        image_ai_frame = self._tab_view.tab("🎨 Изображения AI")
        image_ai_frame.grid_columnconfigure(0, weight=1)
        image_ai_frame.grid_rowconfigure(0, weight=1)
        self._image_ai_tab = ImageAITab(image_ai_frame, self._config)
        self._image_ai_tab.grid(row=0, column=0, sticky="nsew")

        video_ai_frame = self._tab_view.tab("🎬 Видео AI")
        video_ai_frame.grid_columnconfigure(0, weight=1)
        video_ai_frame.grid_rowconfigure(0, weight=1)
        self._video_ai_tab = VideoAITab(video_ai_frame, self._config)
        self._video_ai_tab.grid(row=0, column=0, sticky="nsew")

    def _on_bot_log(self, message: str):
        try:
            self._bot_tab.log(message)
        except Exception:
            pass

    def _on_close(self):
        print("[GUI] Закрытие приложения...")
        if self._bot.is_running():
            self._bot.stop()
        self.destroy()

    def run(self):
        print("[GUI] Запуск GUI mainloop")
        self.mainloop()
