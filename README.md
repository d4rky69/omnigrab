# 🚀 OmniGrab — Universal Media & Photo Downloader

OmniGrab is a high-performance, self-hosted web application capable of extracting and downloading videos, audio tracks, and high-resolution photos from over **1,700+ websites** including **YouTube, Instagram, Pinterest, TikTok, Twitter/X, Reddit, Facebook, Vimeo**, and generic web media.

---

## ✨ Features

- **Multi-Platform Support**: Powered by `yt-dlp` and an automated OpenGraph metadata scraper.
- **Full Video Quality Selection**: Download in 4K (2160p), 2K (1440p), 1080p Full HD, 720p, 480p, or 360p.
- **Audio Extraction**: Converts any video into high-bitrate MP3 (320 kbps) using FFmpeg.
- **Photo & Pin Scraping**:
  - Automatically fetches original, uncompressed camera resolution from Pinterest pins (transforms `/736x/` to `/originals/`).
  - Supports public Instagram image posts, covers, and direct media URLs.
- **Server-Side FFmpeg Merging**: Automatically stitches separate video and high-quality audio streams into a clean `.mp4` file before delivering it to your browser.
- **Zero-Storage Footprint**: Files are delivered via streaming responses with background cleanup tasks that delete the temporary files after download.
- **Cyberpunk Dark UI**: Built with Tailwind CSS, clipboard paste integration, filter tabs, live download indicators, and local download history.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, yt-dlp, Requests
- **Media Engine**: FFmpeg 9.0+
- **Frontend**: Tailwind CSS, Vanilla JavaScript, Responsive Mobile-friendly Glassmorphic UI

---

## 🚀 Quick Start

### 1. Launch the Server
In PowerShell or Command Prompt, run:

```powershell
cd "C:\Users\shrss\.gemini\antigravity\scratch\universal-media-downloader"
.\run.bat
```

Or using python directly:

```powershell
.\.venv\Scripts\python.exe main.py
```

### 2. Open the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 📋 API Endpoints

- `POST /api/inspect`: Analyzes the link, extracts titles, thumbnails, durations, and returns format options.
- `GET /api/download`: Downloads the selected format, processes via FFmpeg, streams the file attachment, and triggers automatic cleanup.
