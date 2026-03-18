import tkinter as tk
import customtkinter as ctk
from config.config_manager import ConfigManager

print("[GUI] Загрузка text_ai_tab")

TEXT_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    "gemini": ["gemini-1.5-flash", "gemini-1.5-pro"],
    "claude": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]
}

PROVIDER_LABELS = {
    "openai": "🤖 OpenAI GPT",
    "gemini": "✨ Google Gemini",
    "claude": "🧠 Anthropic Claude"
}


class TextAITab(ctk.CTkFrame):
    def __init__(self, parent, config: ConfigManager, **kwargs):
        super().__init__(parent, **kwargs)
        self._config = config
        self._widgets = {}
        self._build_ui()
        self._load_config()
        print("[GUI] TextAITab создан")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Настройки текстовых нейросетей",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        for idx, provider in enumerate(["openai", "gemini", "claude"]):
            self._build_provider_card(scroll, provider, idx)

        ctk.CTkButton(self, text="💾 Сохранить все", font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._save_all, height=40).grid(
            row=2, column=0, padx=10, pady=10, sticky="ew"
        )

    def _build_provider_card(self, parent, provider: str, idx: int):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=idx, column=0, padx=5, pady=8, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        self._widgets[provider] = {}

        ctk.CTkLabel(card, text=PROVIDER_LABELS[provider],
                     font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=15, pady=(12, 6), sticky="w"
        )

        enabled_var = tk.BooleanVar()
        self._widgets[provider]["enabled"] = enabled_var
        ctk.CTkSwitch(card, text="Включить", variable=enabled_var).grid(
            row=0, column=1, padx=10, pady=(12, 6), sticky="e"
        )

        ctk.CTkLabel(card, text="API-ключ:").grid(row=1, column=0, padx=(15, 5), pady=5, sticky="w")
        key_frame = ctk.CTkFrame(card, fg_color="transparent")
        key_frame.grid(row=1, column=1, padx=(0, 15), pady=5, sticky="ew")
        key_frame.grid_columnconfigure(0, weight=1)

        key_var = tk.StringVar()
        self._widgets[provider]["api_key"] = key_var
        key_entry = ctk.CTkEntry(key_frame, textvariable=key_var, show="*",
                                 placeholder_text="sk-...")
        key_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        visible_var = {"v": False}

        def toggle_key(e=key_entry, vv=visible_var):
            vv["v"] = not vv["v"]
            e.configure(show="" if vv["v"] else "*")

        ctk.CTkButton(key_frame, text="👁", width=36, command=toggle_key).grid(row=0, column=1)

        ctk.CTkLabel(card, text="Модель:").grid(row=2, column=0, padx=(15, 5), pady=5, sticky="w")
        model_var = tk.StringVar(value=TEXT_MODELS[provider][0])
        self._widgets[provider]["model"] = model_var
        ctk.CTkOptionMenu(card, variable=model_var, values=TEXT_MODELS[provider]).grid(
            row=2, column=1, padx=(0, 15), pady=5, sticky="ew"
        )

        ctk.CTkLabel(card, text="Temperature:").grid(row=3, column=0, padx=(15, 5), pady=5, sticky="w")
        temp_var = tk.DoubleVar(value=0.7)
        self._widgets[provider]["temperature"] = temp_var
        temp_frame = ctk.CTkFrame(card, fg_color="transparent")
        temp_frame.grid(row=3, column=1, padx=(0, 15), pady=5, sticky="ew")
        temp_frame.grid_columnconfigure(0, weight=1)
        temp_label = ctk.CTkLabel(temp_frame, text="0.70", width=45)
        temp_label.grid(row=0, column=1, padx=(5, 0))

        def update_temp_label(val, lbl=temp_label, var=temp_var):
            lbl.configure(text=f"{float(val):.2f}")

        ctk.CTkSlider(temp_frame, variable=temp_var, from_=0.0, to=2.0,
                      command=update_temp_label).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(card, text="Max tokens:").grid(row=4, column=0, padx=(15, 5), pady=5, sticky="w")
        tokens_var = tk.StringVar(value="2000")
        self._widgets[provider]["max_tokens"] = tokens_var
        ctk.CTkEntry(card, textvariable=tokens_var, placeholder_text="2000").grid(
            row=4, column=1, padx=(0, 15), pady=5, sticky="ew"
        )

        ctk.CTkLabel(card, text="System prompt:").grid(row=5, column=0, padx=(15, 5), pady=(5, 12), sticky="nw")
        prompt_var = tk.StringVar(value="You are a helpful assistant.")
        self._widgets[provider]["system_prompt"] = prompt_var
        ctk.CTkEntry(card, textvariable=prompt_var,
                     placeholder_text="You are a helpful assistant.").grid(
            row=5, column=1, padx=(0, 15), pady=(5, 12), sticky="ew"
        )

    def _load_config(self):
        for provider in ["openai", "gemini", "claude"]:
            cfg = self._config.get(f"text_ai_providers.{provider}", {})
            w = self._widgets[provider]
            w["enabled"].set(cfg.get("enabled", False))
            w["api_key"].set(cfg.get("api_key", ""))
            w["model"].set(cfg.get("model", TEXT_MODELS[provider][0]))
            w["temperature"].set(cfg.get("temperature", 0.7))
            w["max_tokens"].set(str(cfg.get("max_tokens", 2000)))
            w["system_prompt"].set(cfg.get("system_prompt", "You are a helpful assistant."))

    def _save_all(self):
        for provider in ["openai", "gemini", "claude"]:
            w = self._widgets[provider]
            try:
                max_tokens = int(w["max_tokens"].get())
            except ValueError:
                max_tokens = 2000
            self._config.set(f"text_ai_providers.{provider}.enabled", w["enabled"].get())
            self._config.set(f"text_ai_providers.{provider}.api_key", w["api_key"].get().strip())
            self._config.set(f"text_ai_providers.{provider}.model", w["model"].get())
            self._config.set(f"text_ai_providers.{provider}.temperature", round(w["temperature"].get(), 2))
            self._config.set(f"text_ai_providers.{provider}.max_tokens", max_tokens)
            self._config.set(f"text_ai_providers.{provider}.system_prompt", w["system_prompt"].get().strip())
        print("[GUI] Настройки текстовых AI сохранены")
