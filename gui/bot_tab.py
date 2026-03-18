import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from config.config_manager import ConfigManager
from bot.telegram_bot import TelegramBot

print("[GUI] Загрузка bot_tab")


class BotTab(ctk.CTkFrame):
    def __init__(self, parent, bot: TelegramBot, config: ConfigManager, **kwargs):
        super().__init__(parent, **kwargs)
        self._bot = bot
        self._config = config
        self._token_visible = False
        self._build_ui()
        self._load_config()
        print("[GUI] BotTab создан")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(settings_frame, text="🔑 Токен бота:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=(10, 5), pady=8, sticky="w"
        )
        token_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        token_frame.grid(row=0, column=1, padx=(0, 10), pady=8, sticky="ew")
        token_frame.grid_columnconfigure(0, weight=1)

        self._token_var = tk.StringVar()
        self._token_entry = ctk.CTkEntry(
            token_frame, textvariable=self._token_var, show="*",
            placeholder_text="Введите токен бота от @BotFather", font=ctk.CTkFont(size=12)
        )
        self._token_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self._toggle_token_btn = ctk.CTkButton(
            token_frame, text="👁", width=36, command=self._toggle_token_visibility
        )
        self._toggle_token_btn.grid(row=0, column=1)

        ctk.CTkLabel(settings_frame, text="👋 Приветствие:", font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=(10, 5), pady=8, sticky="w"
        )
        self._welcome_var = tk.StringVar()
        ctk.CTkEntry(
            settings_frame, textvariable=self._welcome_var,
            placeholder_text="Приветственное сообщение", font=ctk.CTkFont(size=12)
        ).grid(row=1, column=1, padx=(0, 10), pady=8, sticky="ew")

        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self._start_btn = ctk.CTkButton(
            controls_frame, text="▶ Запустить", fg_color="#28a745", hover_color="#218838",
            font=ctk.CTkFont(size=14, weight="bold"), command=self._start_bot, height=40
        )
        self._start_btn.pack(side="left", padx=(10, 5), pady=10)

        self._stop_btn = ctk.CTkButton(
            controls_frame, text="⏹ Остановить", fg_color="#dc3545", hover_color="#c82333",
            font=ctk.CTkFont(size=14, weight="bold"), command=self._stop_bot, height=40, state="disabled"
        )
        self._stop_btn.pack(side="left", padx=5, pady=10)

        self._save_btn = ctk.CTkButton(
            controls_frame, text="💾 Сохранить", font=ctk.CTkFont(size=13),
            command=self._save_config, height=40
        )
        self._save_btn.pack(side="left", padx=5, pady=10)

        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(status_frame, text="Статус:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(10, 5), pady=8)
        self._status_indicator = ctk.CTkLabel(
            status_frame, text="● Остановлен", text_color="#dc3545",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self._status_indicator.pack(side="left", pady=8)

        ctk.CTkLabel(self, text="📋 Лог:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=3, column=0, padx=10, pady=(5, 0), sticky="w"
        )

        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        self._log_text = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Courier", size=11), state="disabled")
        self._log_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        clear_btn = ctk.CTkButton(log_frame, text="🗑 Очистить лог", width=130, command=self._clear_log)
        clear_btn.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="e")

    def _toggle_token_visibility(self):
        self._token_visible = not self._token_visible
        self._token_entry.configure(show="" if self._token_visible else "*")
        self._toggle_token_btn.configure(text="🙈" if self._token_visible else "👁")

    def _load_config(self):
        self._token_var.set(self._config.get("bot.token", ""))
        self._welcome_var.set(self._config.get("bot.welcome_message", ""))

    def _save_config(self):
        self._config.set("bot.token", self._token_var.get().strip())
        self._config.set("bot.welcome_message", self._welcome_var.get().strip())
        self.log("Настройки бота сохранены")

    def _start_bot(self):
        token = self._token_var.get().strip()
        if not token:
            self.log("❌ Укажите токен бота")
            return
        self._save_config()
        try:
            self._bot.start(token)
            self._start_btn.configure(state="disabled")
            self._stop_btn.configure(state="normal")
            self._status_indicator.configure(text="● Запущен", text_color="#28a745")
            self.log("✅ Бот запущен")
        except Exception as e:
            self.log(f"❌ Ошибка запуска: {e}")

    def _stop_bot(self):
        self._bot.stop()
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._status_indicator.configure(text="● Остановлен", text_color="#dc3545")
        self.log("⏹ Бот остановлен")

    def _clear_log(self):
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log_text.configure(state="normal")
        self._log_text.insert("end", f"[{timestamp}] {message}\n")
        self._log_text.see("end")
        self._log_text.configure(state="disabled")
