# -------------------
# scraper/douyin_scraper.py
# -------------------

import os
import re
from playwright.sync_api import sync_playwright

def download_douyin_videos_by_username(username, download_dir="downloads"):
    os.makedirs(download_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the Douyin user's page
        user_url = f"https://www.douyin.com/user/{username}"
        page.goto(user_url, timeout=60000)
        page.wait_for_timeout(5000)  # Let videos load

        # Scroll down to load more videos
        for _ in range(3):
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(2000)

        # Extract video URLs from page content
        content = page.content()
        video_urls = list(set(re.findall(r"https://v\.douyin\.com/[a-zA-Z0-9]+/", content)))

        downloaded_files = []
        for i, short_url in enumerate(video_urls[:3]):
            try:
                # Resolve short URL to real video URL
                page.goto(short_url)
                page.wait_for_timeout(3000)
                real_video_url = page.url

                # Find direct mp4 url in page content
                video_src_match = re.search(r'(https://.+\.douyin\.com/.+?\.mp4)', page.content())
                if video_src_match:
                    video_url = video_src_match.group(1)
                    video_bytes = page.request.get(video_url).body()
                    filename = os.path.join(download_dir, f"video_{i}.mp4")
                    with open(filename, 'wb') as f:
                        f.write(video_bytes)
                    downloaded_files.append(f"video_{i}.mp4")
            except Exception as e:
                print(f"Failed to download from {short_url}: {e}")

        browser.close()
    return downloaded_files
