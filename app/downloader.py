import os
import uuid
import re
import shutil
import requests
from typing import Tuple, Optional
import yt_dlp

COOKIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.txt")
BASE_DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads")
os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r'[\s_]+', '_', cleaned).strip()
    return cleaned[:60] if cleaned else "download"

def is_direct_file_url(url: str) -> bool:
    clean = url.split("?")[0].lower()
    return any(clean.endswith(ext) for ext in [
        ".mp4", ".webm", ".mkv", ".mov", ".avi",
        ".mp3", ".wav", ".m4a", ".aac",
        ".jpg", ".jpeg", ".png", ".webp", ".gif"
    ])

def stream_direct_url(url: str, output_path: str):
    with requests.get(url, headers=HEADERS, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1048576):
                if chunk:
                    f.write(chunk)

def download_media(
    url: str,
    option_type: str,
    format_spec: Optional[str] = None,
    direct_url: Optional[str] = None,
    ext: str = "mp4",
    title: str = "download"
) -> Tuple[str, str]:
    task_id = str(uuid.uuid4())[:8]
    task_dir = os.path.join(BASE_DOWNLOAD_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    safe_title = sanitize_filename(title)
    final_filename = f"{safe_title}.{ext}"
    final_path = os.path.join(task_dir, final_filename)

    # 1. Direct file download (Photos or Direct video links)
    target_direct = direct_url or (url if is_direct_file_url(url) else None)
    if option_type == "photo" or (target_direct and option_type != "audio"):
        target_download_url = target_direct or url
        stream_direct_url(target_download_url, final_path)
        return final_path, final_filename

    # 2. Audio extraction (MP3)
    if option_type == "audio":
        ydl_opts = {
            "format": format_spec or "bestaudio/best",
            "outtmpl": os.path.join(task_dir, f"{safe_title}.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
            "quiet": True,
            "no_warnings": True,
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
        }
        if os.path.exists(COOKIES_PATH) and os.path.getsize(COOKIES_PATH) > 0:
            ydl_opts["cookiefile"] = COOKIES_PATH

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        expected_mp3 = os.path.join(task_dir, f"{safe_title}.mp3")
        if os.path.exists(expected_mp3):
            return expected_mp3, f"{safe_title}.mp3"
        files = os.listdir(task_dir)
        if files:
            return os.path.join(task_dir, files[0]), files[0]
        raise RuntimeError("Audio extraction failed to produce an audio file.")

    # 3. Video download (Merged with FFmpeg)
    ydl_opts = {
        "format": format_spec or "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(task_dir, f"{safe_title}.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
    }
    if os.path.exists(COOKIES_PATH) and os.path.getsize(COOKIES_PATH) > 0:
        ydl_opts["cookiefile"] = COOKIES_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        if direct_url:
            stream_direct_url(direct_url, final_path)
            return final_path, final_filename
        raise e

    expected_mp4 = os.path.join(task_dir, f"{safe_title}.mp4")
    if os.path.exists(expected_mp4):
        return expected_mp4, f"{safe_title}.mp4"

    files = os.listdir(task_dir)
    if files:
        actual_name = files[0]
        return os.path.join(task_dir, actual_name), actual_name

    raise RuntimeError("Video download failed to produce a file.")

def cleanup_file(filepath: str):
    import time
    try:
        time.sleep(15)
        if os.path.exists(filepath):
            os.remove(filepath)
            parent_dir = os.path.dirname(filepath)
            if os.path.exists(parent_dir) and parent_dir != BASE_DOWNLOAD_DIR:
                shutil.rmtree(parent_dir, ignore_errors=True)
    except Exception as e:
        print(f"Error cleaning up {filepath}: {e}")
