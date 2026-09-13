import os
import re
from ytmusicapi import YTMusic

AUTH_FILE = "browser.json"
OUTPUT_FILE = "my_cleaned_tracks.txt"

def clean_track_title(title: str) -> str:
    """Удаляет лишний мусор клипов (Official Video, Remaster, HD и т.д.)."""
    patterns = [
        r'[\(\[\{].*?(official|video|audio|lyrics|hd|4k|prod|feat|ft\.|remastered|remaster|clip).*?[\)\]\}]',
        r'\|.*$',
        r'[-_]\s*(official|video|audio).*$',
    ]
    for p in patterns:
        title = re.sub(p, '', title, flags=re.IGNORECASE)
    return " ".join(title.split())

def main():
    if not os.path.exists(AUTH_FILE):
        print(f"Ошибка: файл авторизации '{AUTH_FILE}' не найден.")
        print("Сначала запустите 'setup_auth.py' для создания конфигурации.")
        return

    print(f"Подключение к YouTube Music через '{AUTH_FILE}'...")
    yt = YTMusic(AUTH_FILE)

    print("Выгрузка треков из плейлиста 'Понравившиеся'...")
    try:
        liked = yt.get_liked_songs(limit=None)
    except Exception as e:
        print(f"Не удалось получить треки: {e}")
        return

    tracks = liked.get("tracks", [])
    clean_lines = []

    for t in tracks:
        artists = t.get("artists", [])
        artist = artists[0]["name"] if artists else ""
        raw_title = t.get("title", "")

        title = clean_track_title(raw_title)
        if artist:
            clean_lines.append(f"{artist} - {title}")
        else:
            clean_lines.append(title)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in clean_lines:
            f.write(line + "\n")

    print(f"\nУспешно выгружено и очищено {len(clean_lines)} треков!")
    print(f"Список сохранен в '{OUTPUT_FILE}'.")

    if clean_lines:
        print("Первые треки для проверки:")
        for sample in clean_lines[:5]:
            print(f"  * {sample}")

if __name__ == "__main__":
    main()