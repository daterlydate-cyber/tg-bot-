import tkinter as tk
import customtkinter as ctk
from config.config_manager import ConfigManager

print("[GUI] Загрузка image_ai_tab")

IMAGE_MODELS = {
    "dalle": ["dall-e-3", "dall-e-2"],
    "stability": ["sd3", "sd3-turbo", "stable-diffusion-xl-1024-v1-0"],
    "kandinsky": ["4.0", "3.1", "3.0"]
}

IMAGE_SIZES = {
    "dalle": ["1024x1024", "1024x1792", "1792x1024"],
    "stability": ["1024x1024", "1152x896", "896x1152", "1216x832"],
    "kandinsky": ["1024x1024", "1024x576", "576x1024", "640x960"]
}

QUALITY_OPTIONS = ["standard", "hd"]
STYLE_OPTIONS = ["vivid", "natural"]

PROVIDER_LABELS = {
    "dalle": "🎨 DALL-E 3 (OpenAI)",
    "stability": "🖼️ Stability AI",
    "kandinsky": "🎭 Kandinsky (FusionBrain)"
}


class ImageAITab(ctk.CTkFrame):
    def __init__(self, parent, config: ConfigManager, **kwargs):
        super().__init__(parent, **kwargs)
        self._config = config
        self._widgets = {}
        self._build_ui()
        self._load_config()
        print("[GUI] ImageAITab создан")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Настройки нейросетей для изображений",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        for idx, provider in enumerate(["dalle", "stability", "kandinsky"]):
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
                                 placeholder_text="API ключ")
        key_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        visible_var = {"v": False}

        def toggle_key(e=key_entry, vv=visible_var):
            vv["v"] = not vv["v"]
            e.configure(show="" if vv["v"] else "*")

        ctk.CTkButton(key_frame, text="👁", width=36, command=toggle_key).grid(row=0, column=1)

        if provider == "kandinsky":
            ctk.CTkLabel(card, text="Secret-ключ:").grid(row=2, column=0, padx=(15, 5), pady=5, sticky="w")
            secret_key_var = tk.StringVar()
            self._widgets[provider]["secret_key"] = secret_key_var
            sk_frame = ctk.CTkFrame(card, fg_color="transparent")
            sk_frame.grid(row=2, column=1, padx=(0, 15), pady=5, sticky="ew")
            sk_frame.grid_columnconfigure(0, weight=1)
            sk_entry = ctk.CTkEntry(sk_frame, textvariable=secret_key_var, show="*",
                                    placeholder_text="Secret ключ")
            sk_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            sk_vis = {"v": False}

            def toggle_sk(e=sk_entry, vv=sk_vis):
                vv["v"] = not vv["v"]
                e.configure(show="" if vv["v"] else "*")

            ctk.CTkButton(sk_frame, text="👁", width=36, command=toggle_sk).grid(row=0, column=1)
            next_row = 3
        else:
            next_row = 2

        ctk.CTkLabel(card, text="Модель:").grid(row=next_row, column=0, padx=(15, 5), pady=5, sticky="w")
        model_var = tk.StringVar(value=IMAGE_MODELS[provider][0])
        self._widgets[provider]["model"] = model_var
        ctk.CTkOptionMenu(card, variable=model_var, values=IMAGE_MODELS[provider]).grid(
            row=next_row, column=1, padx=(0, 15), pady=5, sticky="ew"
        )

        ctk.CTkLabel(card, text="Размер:").grid(row=next_row + 1, column=0, padx=(15, 5), pady=5, sticky="w")
        size_var = tk.StringVar(value=IMAGE_SIZES[provider][0])
        self._widgets[provider]["size"] = size_var
        ctk.CTkOptionMenu(card, variable=size_var, values=IMAGE_SIZES[provider]).grid(
            row=next_row + 1, column=1, padx=(0, 15), pady=5, sticky="ew"
        )

        if provider == "dalle":
            ctk.CTkLabel(card, text="Качество:").grid(row=next_row + 2, column=0, padx=(15, 5), pady=5, sticky="w")
            quality_var = tk.StringVar(value="standard")
            self._widgets[provider]["quality"] = quality_var
            ctk.CTkOptionMenu(card, variable=quality_var, values=QUALITY_OPTIONS).grid(
                row=next_row + 2, column=1, padx=(0, 15), pady=5, sticky="ew"
            )

            ctk.CTkLabel(card, text="Стиль:").grid(row=next_row + 3, column=0, padx=(15, 5), pady=(5, 12), sticky="w")
            style_var = tk.StringVar(value="vivid")
            self._widgets[provider]["style"] = style_var
            ctk.CTkOptionMenu(card, variable=style_var, values=STYLE_OPTIONS).grid(
                row=next_row + 3, column=1, padx=(0, 15), pady=(5, 12), sticky="ew"
            )
        else:
            ctk.CTkFrame(card, height=5, fg_color="transparent").grid(row=next_row + 2, column=0, columnspan=2)

    def _load_config(self):
        for provider in ["dalle", "stability", "kandinsky"]:
            cfg = self._config.get(f"image_ai_providers.{provider}", {})
            w = self._widgets[provider]
            w["enabled"].set(cfg.get("enabled", False))
            w["api_key"].set(cfg.get("api_key", ""))
            w["model"].set(cfg.get("model", IMAGE_MODELS[provider][0]))
            w["size"].set(cfg.get("size", IMAGE_SIZES[provider][0]))
            if provider == "kandinsky":
                w["secret_key"].set(cfg.get("secret_key", ""))
            if provider == "dalle":
                w["quality"].set(cfg.get("quality", "standard"))
                w["style"].set(cfg.get("style", "vivid"))

    def _save_all(self):
        for provider in ["dalle", "stability", "kandinsky"]:
            w = self._widgets[provider]
            self._config.set(f"image_ai_providers.{provider}.enabled", w["enabled"].get())
            self._config.set(f"image_ai_providers.{provider}.api_key", w["api_key"].get().strip())
            self._config.set(f"image_ai_providers.{provider}.model", w["model"].get())
            self._config.set(f"image_ai_providers.{provider}.size", w["size"].get())
            if provider == "kandinsky":
                self._config.set(f"image_ai_providers.{provider}.secret_key", w["secret_key"].get().strip())
            if provider == "dalle":
                self._config.set(f"image_ai_providers.{provider}.quality", w["quality"].get())
                self._config.set(f"image_ai_providers.{provider}.style", w["style"].get())
        print("[GUI] Настройки image AI сохранены")
