# -------------------
# scraper/douyin_scraper.py
# -------------------

import os
import re
import json
from urllib.parse import quote
from playwright.sync_api import sync_playwright

def download_douyin_videos_by_topic(topic, download_dir="downloads", headless=True):
    os.makedirs(download_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the Douyin topic search page
        search_url = f"https://www.douyin.com/search/{quote(topic)}"
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)

        for _ in range(3):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(2000)

        video_elements = page.query_selector_all('a[href*="video/"]')
        video_urls = list(set([el.get_attribute("href") for el in video_elements if el]))

        downloaded_files = []

        for i, path in enumerate(video_urls[:3]):
            try:
                video_page_url = f"https://www.douyin.com{path}"
                page.goto(video_page_url, timeout=60000)
                page.wait_for_timeout(3000)

                content = page.content()
                video_src_match = re.search(r'(https://.+\.douyin\.com/.+?\.mp4)', content)
                title_match = re.search(r'<title>(.*?)</title>', content)

                if video_src_match:
                    video_url = video_src_match.group(1)
                    title = title_match.group(1).strip() if title_match else f"video_{i}"

                    video_bytes = page.request.get(video_url).body()
                    filename = os.path.join(download_dir, f"{title[:50].replace('/', '-')}.mp4")
                    with open(filename, 'wb') as f:
                        f.write(video_bytes)

                    meta = {
                        "title": title,
                        "filename": filename,
                        "source_url": video_page_url
                    }
                    with open(filename + ".json", "w", encoding='utf-8') as meta_file:
                        json.dump(meta, meta_file, ensure_ascii=False, indent=2)

                    downloaded_files.append(filename)
            except Exception as e:
                print(f"Failed to download {path}: {e}")

        browser.close()
    return downloaded_files
