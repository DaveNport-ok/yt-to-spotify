import os
import re
import time
import requests
from difflib import SequenceMatcher
from ytmusicapi import YTMusic

SPOTIFY_TOKEN = os.getenv("SPOTIFY_TOKEN") or input("Введите временный Bearer-токен Spotify: ").strip()

HEADERS = {
    "Authorization": f"Bearer {SPOTIFY_TOKEN.replace('Bearer ', '').strip()}",
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36",
    "Origin": "https://open.spotify.com",
    "Referer": "https://open.spotify.com/",
    "app-platform": "WebPlayer"
}

def safe_request(method: str, url: str, **kwargs):
    for _ in range(5):
        resp = requests.request(method, url, headers=HEADERS, **kwargs)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 10))
            print(f"[Rate Limit] Сервер запросил паузу {retry_after} сек...")
            time.sleep(retry_after + 1)
            continue
        return resp
    return resp

def clean_string(text: str) -> str:
    patterns = [
        r'[\(\[\{].*?(official|video|audio|lyrics|hd|4k|prod|feat|ft\.|remastered|remaster|clip).*?[\)\]\}]',
        r'\|.*$',
        r'[-_]\s*(official|video|audio).*$',
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s]', ' ', text)
    return " ".join(text.split())

def string_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_spotify_match(yt_title: str, yt_artist: str, yt_duration_sec: int):
    c_title = clean_string(yt_title)
    c_artist = clean_string(yt_artist)

    queries = [
        f"track:{c_title} artist:{c_artist}",
        f"{c_artist} {c_title}",
        c_title
    ]

    for idx, query in enumerate(queries):
        if not query.strip():
            continue
        try:
            resp = safe_request(
                "GET",
                "https://api.spotify.com/v1/search",
                params={"q": query, "type": "track", "limit": 5},
                timeout=10
            )
            if not resp or resp.status_code != 200:
                continue

            tracks = resp.json().get("tracks", {}).get("items", [])
            for item in tracks:
                sp_dur_sec = item["duration_ms"] / 1000
                sp_title = item["name"]
                sp_artist = item["artists"][0]["name"] if item.get("artists") else ""

                if yt_duration_sec > 0 and abs(sp_dur_sec - yt_duration_sec) > 14:
                    continue

                title_score = string_similarity(c_title, clean_string(sp_title))
                artist_score = string_similarity(c_artist, clean_string(sp_artist))

                if title_score > 0.6 and (artist_score > 0.45 or idx == 2):
                    return item["uri"], f"{sp_artist} — {sp_title}"
        except Exception:
            continue

    return None, None

def main():
    if not os.path.exists("browser.json"):
        print("Ошибка: отсутствует 'browser.json'. Запустите 'setup_auth.py'.")
        return

    print("Проверка соединения со Spotify...")
    user_resp = safe_request("GET", "https://api.spotify.com/v1/me")
    if not user_resp or user_resp.status_code != 200:
        print(f"Ошибка авторизации Spotify (код {user_resp.status_code if user_resp else 'None'}): {user_resp.text if user_resp else ''}")
        return

    user_data = user_resp.json()
    user_id = user_data["id"]
    print(f"Подключен Spotify аккаунт: {user_data.get('display_name', user_id)}")

    print("\nЗагрузка треков из YouTube Music...")
    yt = YTMusic("browser.json")
    liked = yt.get_liked_songs(limit=None)
    yt_tracks = liked.get("tracks", [])
    total_tracks = len(yt_tracks)
    print(f"Получено треков: {total_tracks}")

    playlist_name = "YouTube Music Migrated"
    pl_resp = safe_request(
        "POST",
        f"https://api.spotify.com/v1/users/{user_id}/playlists",
        json={"name": playlist_name, "public": False, "description": "Синхронизировано кастомным скриптом."}
    )
    if not pl_resp or pl_resp.status_code not in (200, 201):
        print("Не удалось создать плейлист.")
        return

    playlist_id = pl_resp.json()["id"]
    print(f"Создан плейлист: '{playlist_name}'")

    matched_uris = []
    unmatched_list = []

    for i, t in enumerate(yt_tracks, start=1):
        title = t.get("title", "")
        artists = t.get("artists", [])
        artist_name = artists[0]["name"] if artists else ""
        duration_sec = t.get("duration_seconds", 0)

        uri, match_name = find_best_spotify_match(title, artist_name, duration_sec)
        if uri:
            matched_uris.append(uri)
            print(f"[{i}/{total_tracks}]  {artist_name} - {title}  ===>  {match_name}")
        else:
            unmatched_list.append(f"{artist_name} - {title}")
            print(f"[{i}/{total_tracks}]  ПРОПУЩЕНО: {artist_name} - {title}")

        if len(matched_uris) >= 50:
            safe_request("POST", f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", json={"uris": matched_uris})
            matched_uris.clear()
            time.sleep(1)

        time.sleep(0.3)

    if matched_uris:
        safe_request("POST", f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", json={"uris": matched_uris})

    print(f"\nГотово! Перенесено: {total_tracks - len(unmatched_list)} из {total_tracks}")
    if unmatched_list:
        with open("unmatched.txt", "w", encoding="utf-8") as f:
            for item in unmatched_list:
                f.write(item + "\n")

if __name__ == "__main__":
    main()