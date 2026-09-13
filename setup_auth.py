import json
import os

HEADERS_FILE = "browser.json"

def main():
    print("=== Первоначальная настройка сессии YouTube Music ===")

    # Считываем данные из окружения или запрашиваем ввод у пользователя
    auth_header = os.getenv("YTM_AUTH") or input("Вставьте заголовок 'authorization' (SAPISIDHASH...): ").strip()
    cookie_header = os.getenv("YTM_COOKIE") or input("Вставьте заголовок 'cookie': ").strip()

    if not auth_header or not cookie_header:
        print("Ошибка: заголовок авторизации и куки обязательны для заполнения!")
        return

    headers_data = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6",
        "content-type": "application/json",
        "x-goog-authuser": "0",
        "x-origin": "https://music.youtube.com",
        "authorization": auth_header,
        "cookie": cookie_header
    }

    with open(HEADERS_FILE, "w", encoding="utf-8") as f:
        json.dump(headers_data, f, indent=4, ensure_ascii=False)

    print(f"\nСессия успешно сохранена в '{HEADERS_FILE}'.")

    # Проверка валидности сессии
    try:
        from ytmusicapi import YTMusic
        print("Проверка подключения к библиотеке...")
        yt = YTMusic(HEADERS_FILE)
        liked_songs = yt.get_liked_songs(limit=5)
        count = liked_songs.get("trackCount", len(liked_songs.get("tracks", [])))
        print(f"Авторизация успешна! Найдено треков: {count}")
    except Exception as e:
        print(f"Ошибка проверки сессии: {e}")

if __name__ == "__main__":
    main()