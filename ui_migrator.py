import os
import time
from playwright.sync_api import sync_playwright

TRACKS_FILE = "my_cleaned_tracks.txt"
PROGRESS_FILE = "progress.txt"

# Считываем конфиденциальные данные из окружения или запрашиваем ввод
SP_DC = os.getenv("SPOTIFY_SP_DC") or input("Введите значение куки sp_dc: ").strip()
SP_T = os.getenv("SPOTIFY_SP_T") or input("Введите значение куки sp_t (или оставьте пустым): ").strip()
PLAYLIST_URL = os.getenv("SPOTIFY_PLAYLIST_URL") or input("Введите ссылку на целевой плейлист Spotify: ").strip()

COOKIES = [
    {
        "name": "sp_dc",
        "value": SP_DC,
        "domain": ".spotify.com",
        "path": "/",
        "secure": True,
        "httpOnly": True
    }
]

if SP_T:
    COOKIES.append({
        "name": "sp_t",
        "value": SP_T,
        "domain": ".spotify.com",
        "path": "/",
        "secure": True
    })

def load_processed_tracks() -> set:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def mark_track_done(track_name: str):
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(track_name + "\n")

def main():
    if not os.path.exists(TRACKS_FILE):
        print(f"Ошибка: файл треков '{TRACKS_FILE}' не найден. Сначала запустите 'export_smart.py'.")
        return

    with open(TRACKS_FILE, "r", encoding="utf-8") as f:
        all_tracks = [line.strip() for line in f if line.strip()]

    processed_set = load_processed_tracks()
    tracks_to_process = [t for t in all_tracks if t not in processed_set]

    print(f"Всего треков: {len(all_tracks)} | Уже обработано: {len(processed_set)} | Осталось: {len(tracks_to_process)}")

    if not tracks_to_process:
        print("Все треки уже успешно перенесены!")
        return

    with sync_playwright() as p:
        print("\nЗапуск браузера Chrome...")
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(no_viewport=True)
        context.add_cookies(COOKIES)

        page = context.new_page()
        print(f"Открываем плейлист: {PLAYLIST_URL}")
        page.goto(PLAYLIST_URL, timeout=60000)
        time.sleep(4)

        # Раскрываем блок поиска при необходимости
        find_more_btn = page.locator('button:has-text("Find more"), button:has-text("Найти еще"), button:has-text("Шукати ще")')
        if find_more_btn.count() > 0 and find_more_btn.first.is_visible():
            find_more_btn.first.click()
            time.sleep(1)

        search_input = page.locator('input[data-testid="search-input"], input[data-testid*="search"], input[role="searchbox"], input[type="search"]').first

        if not search_input.is_visible():
            print("Поле поиска внутри плейлиста не обнаружено. Проверьте правильность URL плейлиста.")
            browser.close()
            return

        print("\nСтарт добавления треков...\n")
        added_session = 0
        unmatched_session = []

        for idx, raw_track in enumerate(tracks_to_process, start=len(processed_set) + 1):
            query = raw_track.replace(" - ", " ").replace("-", " ")
            try:
                search_input.click()
                search_input.fill("")
                search_input.fill(query)
                search_input.press("Enter")

                add_btn = page.locator('button[data-testid="add-to-playlist-button"], button:has-text("Add"), button:has-text("Добавить"), button:has-text("Додати")').first
                add_btn.wait_for(state="visible", timeout=3000)
                add_btn.click()

                added_session += 1
                mark_track_done(raw_track)
                print(f"[{idx}/{len(all_tracks)}] Добавлен: {raw_track}")
                time.sleep(1.2)

            except Exception:
                unmatched_session.append(raw_track)
                mark_track_done(raw_track)
                print(f"[{idx}/{len(all_tracks)}] Не найден: {raw_track}")
                time.sleep(0.5)

        print("\n" + "=" * 50)
        print(f"Миграция завершена! Добавлено за эту сессию: {added_session}")

        if unmatched_session:
            with open("ui_unmatched.txt", "a", encoding="utf-8") as f:
                for item in unmatched_session:
                    f.write(item + "\n")
            print("Список ненайденных треков дополнен в 'ui_unmatched.txt'")

        input("\nНажмите Enter для закрытия окна браузера...")
        browser.close()

if __name__ == "__main__":
    main()