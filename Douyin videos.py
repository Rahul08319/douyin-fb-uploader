import requests
import re
import os
from urllib.parse import urlparse, parse_qs

# For video downloading, Douyin videos URLs often require some scraping via their API or web.
# Here is a basic approach to get video URL from Douyin video page by scraping the video play URL from response.

# Because Douyin uses dynamic content and anti-scraping methods, in real-world usage, a headless browser or official APIs may be needed.
# This code tries simple requests method for demonstration.

def get_douyin_video_url(video_url):
    """Get downloadable video URL from Douyin video page URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        response = requests.get(video_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get page: {response.status_code}")
            return None
        text = response.text

        # Regex to find the "playAddr" (video url) in the page source
        match = re.search(r'playAddr":"(https:[^\"]+)', text)
        if match:
            raw_url = match.group(1)
            # The URL may be escaped, fix that
            video_download_url = raw_url.replace('\\u0026', '&')
            return video_download_url
        else:
            print("Video URL not found in page.")
            return None
    except Exception as e:
        print(f"Error fetching video URL: {e}")
        return None


def download_video(video_url, output_filename):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        response = requests.get(video_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Video downloaded to {output_filename}")
            return True
        else:
            print(f"Failed to download video, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading video: {e}")
        return False


def upload_video_to_facebook(file_path, access_token):
    """Upload video to the user's Facebook using Graph API"""
    try:
        url = 'https://graph-video.facebook.com/v17.0/me/videos'
        files = {
            'file': open(file_path, 'rb')
        }
        data = {
            'access_token': access_token,
            'title': 'Douyin Video Upload',
            'description': 'Uploaded via Douyin Scraper Tool'
        }
        response = requests.post(url, files=files, data=data)
        files['file'].close()
        if response.status_code == 200:
            resp_json = response.json()
            if 'id' in resp_json:
                print(f"Video uploaded successfully. Video ID: {resp_json['id']}")
                return True
            else:
                print(f"Upload failed: {resp_json}")
                return False
        else:
            print(f"Upload failed, status code: {response.status_code}, response: {response.text}")
            return False

    except Exception as e:
        print(f"Error uploading video: {e}")
        return False


def main():
    print("Douyin Video Downloader & Facebook Uploader")
    choice = input("Enter 1 to download from Douyin video link, 2 to download by username/topic (not implemented, placeholder): ")
    video_url = None

    if choice == '1':
        video_url = input("Enter Douyin video URL: ")
    elif choice == '2':
        print("Feature for username/topic scraping not implemented in this prototype.")
        return
    else:
        print("Invalid choice.")
        return

    # Get downloadable video URL
    real_video_url = get_douyin_video_url(video_url)
    if not real_video_url:
        print("Could not extract video URL.")
        return

    # Download video
    output_file = 'douyin_video.mp4'
    if not download_video(real_video_url, output_file):
        print("Video download failed.")
        return

    # Upload to Facebook
    fb_token = input("Enter your Facebook Graph API access token: ")
    upload_video_to_facebook(output_file, fb_token)


if __name__ == '__main__':
    main()
