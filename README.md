# 🤖 Telegram AI Bot Manager

Полноценное Python-приложение — Telegram-бот с нейросетями и графическим интерфейсом (GUI) для управления.

## 📋 Описание проекта

Приложение позволяет:
- Запустить Telegram-бота через удобный GUI-интерфейс
- Подключить текстовые AI: OpenAI GPT, Google Gemini, Anthropic Claude
- Подключить AI для генерации изображений: DALL-E 3, Stability AI, Kandinsky
- Подключить AI для генерации видео: Runway ML, Replicate
- Настраивать кнопки бота прямо из интерфейса
- Управлять API-ключами безопасно (скрытый ввод)

## 🗂️ Структура проекта

```
tg-bot-/
├── main.py                    # Точка входа — запуск GUI
├── run_headless.py            # Запуск без GUI (для сервера)
├── requirements.txt           # Зависимости
├── .gitignore
├── README.md                  # Документация
├── config/
│   ├── __init__.py
│   └── config_manager.py      # Singleton менеджер конфигурации (config.json)
├── bot/
│   ├── __init__.py
│   ├── telegram_bot.py        # Класс TelegramBot (start/stop в отдельном потоке)
│   ├── handlers.py            # Обработчики команд и сообщений
│   └── keyboards.py           # Динамические клавиатуры из конфига
├── ai/
│   ├── __init__.py
│   ├── ai_manager.py          # Центральный менеджер всех AI-провайдеров
│   ├── text/
│   │   ├── __init__.py
│   │   ├── openai_client.py   # OpenAI GPT
│   │   ├── gemini_client.py   # Google Gemini
│   │   └── claude_client.py   # Anthropic Claude
│   ├── image/
│   │   ├── __init__.py
│   │   ├── dalle_client.py    # OpenAI DALL-E 3
│   │   ├── stability_client.py # Stability AI
│   │   └── kandinsky_client.py # Kandinsky (FusionBrain)
│   └── video/
│       ├── __init__.py
│       ├── runway_client.py   # Runway ML
│       └── replicate_client.py # Replicate API
└── gui/
    ├── __init__.py
    ├── app.py                 # Главное окно с вкладками
    ├── bot_tab.py             # Вкладка: управление ботом
    ├── buttons_tab.py         # Вкладка: управление кнопками
    ├── text_ai_tab.py         # Вкладка: текстовые нейросети
    ├── image_ai_tab.py        # Вкладка: нейросети для изображений
    └── video_ai_tab.py        # Вкладка: нейросети для видео
```

## 🚀 Установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/daterlydate-cyber/tg-bot-.git
cd tg-bot-
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

## 🔑 Получение API-ключей

### Telegram Bot Token
1. Откройте Telegram и найдите бота [@BotFather](https://t.me/BotFather)
2. Напишите `/newbot`
3. Следуйте инструкциям, введите имя и username бота
4. Скопируйте полученный токен (формат: `1234567890:ABCdefGHIjklMNOpqrSTUvwxyz`)

### OpenAI (GPT + DALL-E)
1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Перейдите в раздел API Keys: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Нажмите "Create new secret key"
4. Скопируйте ключ (начинается с `sk-`)

### Google Gemini
1. Перейдите на [aistudio.google.com](https://aistudio.google.com)
2. Нажмите "Get API key" → "Create API key"
3. Выберите проект или создайте новый
4. Скопируйте ключ

### Anthropic Claude
1. Зарегистрируйтесь на [console.anthropic.com](https://console.anthropic.com)
2. Перейдите в Settings → API Keys
3. Нажмите "Create Key"
4. Скопируйте ключ (начинается с `sk-ant-`)

### Stability AI
1. Зарегистрируйтесь на [platform.stability.ai](https://platform.stability.ai)
2. Перейдите в Account → API Keys
3. Нажмите "Create API Key"
4. Скопируйте ключ

### Kandinsky (FusionBrain)
1. Зарегистрируйтесь на [fusionbrain.ai](https://fusionbrain.ai)
2. Перейдите на [fusionbrain.ai/diffusion#apikey](https://fusionbrain.ai/diffusion#apikey)
3. Нажмите "Создать ключ"
4. Скопируйте **API Key** и **Secret Key** (нужны оба!)

### Runway ML
1. Зарегистрируйтесь на [runwayml.com](https://runwayml.com)
2. Перейдите в Settings → API
3. Создайте API Token
4. Документация: [docs.runwayml.com](https://docs.runwayml.com)

### Replicate
1. Зарегистрируйтесь на [replicate.com](https://replicate.com)
2. Перейдите в Account Settings → API Tokens
3. Нажмите "Create token"
4. Скопируйте токен (начинается с `r8_`)

## ▶️ Запуск

### Запуск с GUI (рекомендуется для настройки)

```bash
python main.py
```

Откроется графический интерфейс с 5 вкладками:
- **🤖 Бот** — токен, запуск/остановка, логи
- **📱 Кнопки** — управление кнопками бота
- **💬 Текст AI** — настройка текстовых нейросетей
- **🎨 Изображения AI** — настройка нейросетей для изображений
- **🎬 Видео AI** — настройка нейросетей для видео

### Запуск без GUI (headless, для сервера)

```bash
python run_headless.py
```

Требует наличия `config.json` с заполненными настройками.

## 🤖 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и главная клавиатура |
| `/help` | Справка |
| `/text` | Выбрать текстовую нейросеть |
| `/image` | Выбрать нейросеть для изображений |
| `/video` | Выбрать нейросеть для видео |
| `/reset` | Сбросить историю диалога |

## ⚙️ Конфигурация

При первом запуске автоматически создаётся `config.json`. Файл содержит:
- Токен бота и приветственное сообщение
- Настройки всех AI-провайдеров (ключи, модели, параметры)
- Список кнопок бота

**Важно:** `config.json` добавлен в `.gitignore` — ваши API-ключи не попадут в репозиторий.

## 🖥️ Деплой на сервер (systemd)

### 1. Создайте сервисный файл

```bash
sudo nano /etc/systemd/system/tg-bot.service
```

```ini
[Unit]
Description=Telegram AI Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/tg-bot-
ExecStart=/path/to/tg-bot-/venv/bin/python run_headless.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Включите и запустите сервис

```bash
sudo systemctl daemon-reload
sudo systemctl enable tg-bot
sudo systemctl start tg-bot
sudo systemctl status tg-bot
```

### 3. Просмотр логов

```bash
sudo journalctl -u tg-bot -f
```

## 📦 Зависимости

| Библиотека | Версия | Назначение |
|-----------|--------|-----------|
| aiogram | 3.15.0 | Telegram Bot API |
| openai | 1.58.0 | OpenAI GPT + DALL-E |
| google-generativeai | 0.8.0 | Google Gemini |
| anthropic | 0.40.0 | Anthropic Claude |
| customtkinter | 5.2.2 | Современный GUI |
| Pillow | 11.0.0 | Обработка изображений |
| aiohttp | 3.11.0 | Async HTTP запросы |

## 🐍 Требования

- Python 3.10 или выше
- Операционная система: Windows / Linux / macOS
- Для GUI: дисплей (на сервере без GUI используйте `run_headless.py`)
