# 📁 douyin-fb-uploader CLI + Web App

# -------------------
# scraper/douyin_scraper.py
# -------------------

import os
from playwright.sync_api import sync_playwright

def download_douyin_videos_by_username(username, download_dir="downloads"):
    os.makedirs(download_dir, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        search_url = f"https://www.douyin.com/user/{username}"
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(5000)

        # NOTE: This logic is illustrative; real selectors may differ
        video_links = page.query_selector_all("video")

        for idx, video in enumerate(video_links[:3]):  # Limit to 3 for demo
            video_url = video.get_attribute("src")
            if video_url:
                video_bytes = page.request.get(video_url).body()
                with open(os.path.join(download_dir, f"video_{idx}.mp4"), "wb") as f:
                    f.write(video_bytes)

        browser.close()
    return os.listdir(download_dir)


# -------------------
# uploader/facebook_uploader.py
# -------------------

import os
import requests

def upload_video_to_facebook(video_path, access_token, page_id):
    url = f"https://graph-video.facebook.com/{page_id}/videos"
    files = {'source': open(video_path, 'rb')}
    data = {
        'access_token': access_token,
        'description': f'Uploaded: {os.path.basename(video_path)}'
    }
    response = requests.post(url, files=files, data=data)
    return response.json()


# -------------------
# cli/script.py
# -------------------

import argparse
from scraper.douyin_scraper import download_douyin_videos_by_username
from uploader.facebook_uploader import upload_video_to_facebook

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--page_id", required=True)
    args = parser.parse_args()

    files = download_douyin_videos_by_username(args.username)
    for file in files:
        result = upload_video_to_facebook(f"downloads/{file}", args.token, args.page_id)
        print(f"Uploaded: {file} => {result}")

if __name__ == "__main__":
    main()


# -------------------
# web/app.py
# -------------------

from flask import Flask, request, jsonify, render_template
from scraper.douyin_scraper import download_douyin_videos_by_username
from uploader.facebook_uploader import upload_video_to_facebook

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scrape-and-upload", methods=["POST"])
def scrape_and_upload():
    data = request.get_json()
    username = data['username']
    token = data['fbToken']
    page_id = data['pageId']

    files = download_douyin_videos_by_username(username)
    results = []
    for file in files:
        res = upload_video_to_facebook(f"downloads/{file}", token, page_id)
        results.append(res)
    return jsonify({"status": "complete", "results": results})

if __name__ == '__main__':
    app.run(debug=True)


# -------------------
# web/templates/index.html
# -------------------

<!DOCTYPE html>
<html>
<head>
  <title>Douyin to Facebook Uploader</title>
</head>
<body>
  <h1>Upload Douyin Videos to Facebook</h1>
  <input id="username" placeholder="Douyin Username"><br>
  <input id="pageId" placeholder="Facebook Page ID"><br>
  <input id="fbToken" placeholder="Facebook Access Token"><br>
  <button onclick="submitUpload()">Start Upload</button>

  <script>
    async function submitUpload() {
      const username = document.getElementById('username').value;
      const pageId = document.getElementById('pageId').value;
      const fbToken = document.getElementById('fbToken').value;

      const res = await fetch('/api/scrape-and-upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username, pageId, fbToken })
      });
      const data = await res.json();
      alert('Status: ' + data.status);
    }
  </script>
</body>
</html>
