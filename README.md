# 🎧 YouTube Music to Spotify Migrator

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev/)
[![Status](https://img.shields.io/badge/Status-Production--Ready-success?style=flat)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Автоматизированный инструмент для бесшовного переноса аудиотеки из **YouTube Music** в **Spotify**. 

Проект разработан как надежная альтернатива официальному REST API Spotify в условиях жестких ограничений: блокировки сторонних приложений в режиме *Development Mode*, ошибок `429 Too Many Requests` и платного доступа к инструментам разработчика.

---

## 💡 Архитектура решения

Перенос разделен на два независимых и устойчивых к сбоям этапа:

```text
[ YouTube Music ] 
       │
       ▼ (ytmusicapi + сессионные куки)
[ export_smart.py ] ──► Очистка названий через Regex (удаление мусора клипов)
       │
       ▼
[ my_cleaned_tracks.txt ] (Нормализованный список треков)
       │
       ▼ (Инъекция sp_dc сессии + CDP эмуляция)
[ ui_migrator.py (Playwright) ] ──► Автоматический поиск и клики в Web Player
       │
       ▼
[ Spotify Playlist ] (Готовая медиатека)
```

---

## ✨ Ключевые особенности

- **Smart Track Sanitization:** регулярные выражения очищают названия от специфичного для видеоклипов мусора (`Official Music Video`, `Remastered 2023`, `4K / HD`, `feat.`, `prod by`), максимизируя процент точных совпадений в Spotify.
- **Bypass Spotify API & Anti-Bot Protection:** миграция выполняется через нативную UI-автоматизацию браузера (Chromium / Playwright) с маскировкой под действия реального пользователя и подавлением флагов автоматизации (`--disable-blink-features=AutomationControlled`).
- **Session Injection:** поддержка беспарольной авторизации в Spotify через прямую подстановку сессионных кук `sp_dc` и `sp_t`, что предотвращает срабатывание reCAPTCHA и Cloudflare protection.
- **State Recovery (Resume):** отслеживание прогресса в реальном времени (`progress.txt`). В случае сетевого сбоя или перезапуска скрипт продолжит работу строго с прерванного места без дублирования треков.

---

## 📁 Структура проекта

```text
yt-to-spotify/
├── export_smart.py       # Выгрузка и Regex-очистка треков из YT Music
├── setup_auth.py         # Безопасная инициализация сессии YouTube Music
├── ui_migrator.py        # Основной модуль UI-миграции на базе Playwright
├── sync.py               # Альтернативный REST API клиент с обработкой 429 Retry-After
├── .env.example          # Шаблон переменных окружения
├── .gitignore            # Защита чувствительных данных (сессий, кук, профилей)
└── requirements.txt      # Зависимости проекта
```

---

## 🚀 Быстрый старт

### 1. Клонирование и установка зависимостей

```bash
git clone [https://github.com/ВАШ_НИКНЕЙМ/yt-to-spotify.git](https://github.com/ВАШ_НИКНЕЙМ/yt-to-spotify.git)
cd yt-to-spotify

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Для Linux/macOS
# или: .venv\Scripts\activate  # Для Windows

# Установка пакетов и браузерных бинарников
pip install -r requirements.txt
playwright install chromium
```

---

### 2. Экспорт треков из YouTube Music

1. Перейдите на [music.youtube.com](https://music.youtube.com), откройте вкладку **Network** (Сеть) в DevTools браузера.
2. Найдите любой сетевой запрос к сервису и скопируйте значения заголовков `cookie` и `authorization`.
3. Выполните скрипт первичной авторизации:
   ```bash
   python setup_auth.py
   ```
4. Выгрузите очищенный список понравившихся композиций:
   ```bash
   python export_smart.py
   ```
   В корне проекта появится готовый файл `my_cleaned_tracks.txt`.

---

### 3. Запуск мигратора в Spotify

1. Создайте в веб-плеере [Spotify](https://open.spotify.com) новый пустой плейлист и скопируйте ссылку на него.
2. Скопируйте значение сессионной куки `sp_dc` из Cookies браузера.
3. Запустите автоматизацию:
   ```bash
   python ui_migrator.py
   ```
4. Введите запрашиваемые параметры в консоли (или заранее укажите их в `.env`). Скрипт в фоновом/видимом режиме найдет и добавит каждый трек в целевой плейлист.

---

## 🔒 Безопасность

Проект спроектирован с учетом изоляции приватных данных:
- Сессионные файлы авторизации (`browser.json`, локальные профили браузера `chrome_session`) и файлы списков треков занесены в `.gitignore` и никогда не попадают в систему контроля версий.
- Конфигурация передается динамически через переменные окружения или защищенный консольный ввод.

