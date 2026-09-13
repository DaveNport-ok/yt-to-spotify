# YouTube Music to Spotify Migrator

Кастомный инструмент для миграции музыкальной библиотеки из **YouTube Music** в **Spotify**, разработанный для обхода ограничений официального API Spotify (Rate Limit 429 и блокировки сторонних приложений в Development Mode).

## Особенности

- **Умная нормализация названий:** удаление мусорных тегов клипов (`Official Video`, `Remastered`, `HD`, `4K` и др.) с помощью регулярных выражений.
- **Двухэтапная архитектура:**
  1. Выгрузка и очистка треков из YouTube Music через сессионные заголовки (`ytmusicapi`).
  2. Автоматическое добавление треков в плейлист через браузерную автоматизацию на **Playwright** с эмуляцией действий реального пользователя (CDP / Chromium).
- **Механизм восстановления (Resume):** отслеживание прогресса добавления для предотвращения повторной обработки треков при сбоях.

## Стек технологий

- Python 3.10+
- [Playwright](https://playwright.dev/python/) (UI Automation)
- [ytmusicapi](https://ytmusicapi.readthedocs.io/) (YouTube Music API interaction)
- Requests / Regular Expressions

## Инструкция по запуску

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
playwright install chromium
