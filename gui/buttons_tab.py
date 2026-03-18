import tkinter as tk
import customtkinter as ctk
from config.config_manager import ConfigManager

print("[GUI] Загрузка buttons_tab")

ACTION_OPTIONS = [
    "select_text_ai",
    "select_image_ai",
    "select_video_ai",
    "show_help",
    "reset",
    "show_model"
]


class ButtonsTab(ctk.CTkFrame):
    def __init__(self, parent, config: ConfigManager, **kwargs):
        super().__init__(parent, **kwargs)
        self._config = config
        self._build_ui()
        self._load_buttons()
        print("[GUI] ButtonsTab создан")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left_frame, text="📋 Текущие кнопки", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="w"
        )

        self._btn_list = ctk.CTkScrollableFrame(left_frame)
        self._btn_list.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        delete_btn = ctk.CTkButton(left_frame, text="🗑 Удалить выбранную", fg_color="#dc3545",
                                   hover_color="#c82333", command=self._delete_button)
        delete_btn.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(right_frame, text="➕ Добавить кнопку", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w"
        )

        ctk.CTkLabel(right_frame, text="Текст кнопки:").grid(row=1, column=0, padx=(10, 5), pady=6, sticky="w")
        self._btn_text_var = tk.StringVar()
        ctk.CTkEntry(right_frame, textvariable=self._btn_text_var, placeholder_text="💬 Моя кнопка").grid(
            row=1, column=1, padx=(0, 10), pady=6, sticky="ew"
        )

        ctk.CTkLabel(right_frame, text="Действие:").grid(row=2, column=0, padx=(10, 5), pady=6, sticky="w")
        self._action_var = tk.StringVar(value=ACTION_OPTIONS[0])
        ctk.CTkOptionMenu(right_frame, variable=self._action_var, values=ACTION_OPTIONS).grid(
            row=2, column=1, padx=(0, 10), pady=6, sticky="ew"
        )

        ctk.CTkLabel(right_frame, text="AI-провайдер:").grid(row=3, column=0, padx=(10, 5), pady=6, sticky="w")
        self._provider_var = tk.StringVar()
        ctk.CTkEntry(right_frame, textvariable=self._provider_var,
                     placeholder_text="openai / gemini / dalle / ...").grid(
            row=3, column=1, padx=(0, 10), pady=6, sticky="ew"
        )

        ctk.CTkLabel(right_frame, text="Строка (row):").grid(row=4, column=0, padx=(10, 5), pady=6, sticky="w")
        self._row_var = tk.StringVar(value="0")
        ctk.CTkEntry(right_frame, textvariable=self._row_var, placeholder_text="0").grid(
            row=4, column=1, padx=(0, 10), pady=6, sticky="ew"
        )

        ctk.CTkButton(right_frame, text="➕ Добавить кнопку", command=self._add_button,
                      font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )

        ctk.CTkLabel(right_frame, text="👁 Предпросмотр клавиатуры:",
                     font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=6, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w"
        )

        self._preview_frame = ctk.CTkScrollableFrame(right_frame, height=150)
        self._preview_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self._selected_id = None
        self._button_widgets = []

    def _load_buttons(self):
        for widget in self._btn_list.winfo_children():
            widget.destroy()
        self._button_widgets = []

        buttons = self._config.get_buttons()
        for btn in buttons:
            frame = ctk.CTkFrame(self._btn_list)
            frame.pack(fill="x", padx=5, pady=3)

            label = ctk.CTkLabel(
                frame,
                text=f"{btn['text']}  |  Действие: {btn['action']}  |  Строка: {btn['row']}",
                font=ctk.CTkFont(size=11), anchor="w"
            )
            label.pack(side="left", padx=10, pady=6, fill="x", expand=True)

            btn_id = btn["id"]
            select_btn = ctk.CTkButton(frame, text="◉", width=30, command=lambda bid=btn_id: self._select_button(bid))
            select_btn.pack(side="right", padx=(0, 5), pady=5)
            self._button_widgets.append((btn_id, frame))

        self._update_preview()

    def _select_button(self, btn_id: str):
        self._selected_id = btn_id
        for b_id, frame in self._button_widgets:
            color = "#2b5278" if b_id == btn_id else "transparent"
            frame.configure(fg_color=color)
        print(f"[GUI] Выбрана кнопка: {btn_id}")

    def _delete_button(self):
        if not self._selected_id:
            return
        if self._config.remove_button(self._selected_id):
            self._selected_id = None
            self._load_buttons()
            print("[GUI] Кнопка удалена")

    def _add_button(self):
        text = self._btn_text_var.get().strip()
        if not text:
            return
        action = self._action_var.get()
        provider = self._provider_var.get().strip()
        try:
            row = int(self._row_var.get())
        except ValueError:
            row = 0

        self._config.add_button(text=text, action=action, ai_provider=provider, row=row)
        self._btn_text_var.set("")
        self._provider_var.set("")
        self._row_var.set("0")
        self._load_buttons()
        print(f"[GUI] Добавлена кнопка: {text}")

    def _update_preview(self):
        for widget in self._preview_frame.winfo_children():
            widget.destroy()

        buttons = self._config.get_buttons()
        rows_dict: dict = {}
        for btn in buttons:
            row = btn.get("row", 0)
            if row not in rows_dict:
                rows_dict[row] = []
            rows_dict[row].append(btn["text"])

        for row_idx in sorted(rows_dict.keys()):
            row_frame = ctk.CTkFrame(self._preview_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            for btn_text in rows_dict[row_idx]:
                ctk.CTkButton(
                    row_frame, text=btn_text, height=32,
                    font=ctk.CTkFont(size=11), state="disabled",
                    fg_color="#2b5278"
                ).pack(side="left", padx=3)
