import tkinter as tk
import customtkinter as ctk
from config.config_manager import ConfigManager

print("[GUI] Загрузка video_ai_tab")

VIDEO_MODELS = {
    "runway": ["gen3a_turbo", "gen3a", "gen2"],
    "replicate": ["minimax/video-01-live", "minimax/video-01", "stability-ai/stable-video-diffusion"]
}

PROVIDER_LABELS = {
    "runway": "🎬 Runway ML",
    "replicate": "🔄 Replicate"
}


class VideoAITab(ctk.CTkFrame):
    def __init__(self, parent, config: ConfigManager, **kwargs):
        super().__init__(parent, **kwargs)
        self._config = config
        self._widgets = {}
        self._build_ui()
        self._load_config()
        print("[GUI] VideoAITab создан")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Настройки нейросетей для видео",
                     font=ctk.CTkFont(size=15, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        for idx, provider in enumerate(["runway", "replicate"]):
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

        ctk.CTkLabel(card, text="Модель:").grid(row=2, column=0, padx=(15, 5), pady=5, sticky="w")
        model_var = tk.StringVar(value=VIDEO_MODELS[provider][0])
        self._widgets[provider]["model"] = model_var
        ctk.CTkOptionMenu(card, variable=model_var, values=VIDEO_MODELS[provider]).grid(
            row=2, column=1, padx=(0, 15), pady=5, sticky="ew"
        )

        ctk.CTkLabel(card, text="Длительность (сек):").grid(row=3, column=0, padx=(15, 5), pady=(5, 12), sticky="w")
        duration_var = tk.StringVar(value="5")
        self._widgets[provider]["duration"] = duration_var
        dur_frame = ctk.CTkFrame(card, fg_color="transparent")
        dur_frame.grid(row=3, column=1, padx=(0, 15), pady=(5, 12), sticky="ew")
        dur_frame.grid_columnconfigure(0, weight=1)
        dur_label = ctk.CTkLabel(dur_frame, text="5 сек", width=60)
        dur_label.grid(row=0, column=1, padx=(5, 0))
        dur_slider = ctk.CTkSlider(
            dur_frame, from_=4, to=10, number_of_steps=6,
            command=lambda v, lbl=dur_label, var=duration_var: (
                lbl.configure(text=f"{int(v)} сек"),
                var.set(str(int(v)))
            )
        )
        dur_slider.set(5)
        dur_slider.grid(row=0, column=0, sticky="ew")

    def _load_config(self):
        for provider in ["runway", "replicate"]:
            cfg = self._config.get(f"video_ai_providers.{provider}", {})
            w = self._widgets[provider]
            w["enabled"].set(cfg.get("enabled", False))
            w["api_key"].set(cfg.get("api_key", ""))
            w["model"].set(cfg.get("model", VIDEO_MODELS[provider][0]))
            w["duration"].set(str(cfg.get("duration", 5)))

    def _save_all(self):
        for provider in ["runway", "replicate"]:
            w = self._widgets[provider]
            try:
                duration = int(w["duration"].get())
            except ValueError:
                duration = 5
            self._config.set(f"video_ai_providers.{provider}.enabled", w["enabled"].get())
            self._config.set(f"video_ai_providers.{provider}.api_key", w["api_key"].get().strip())
            self._config.set(f"video_ai_providers.{provider}.model", w["model"].get())
            self._config.set(f"video_ai_providers.{provider}.duration", duration)
        print("[GUI] Настройки video AI сохранены")
