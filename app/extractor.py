import os
import re
import requests
from typing import Dict, Any, List, Optional
from html.parser import HTMLParser
import yt_dlp
import yt_dlp.extractor.instagram as ig_module

# Monkey-patch InstagramIE so photo posts don't raise 'There is no video in this post'
_orig_extract_product = ig_module.InstagramIE._extract_product

def _patched_extract_product(self, product_info, *args, **kwargs):
    res = _orig_extract_product(self, product_info, *args, **kwargs)
    if res and not res.get('formats'):
        thumbs = res.get('thumbnails', [])
        best_thumb = thumbs[-1].get('url') if thumbs else res.get('thumbnail')
        if best_thumb:
            res['formats'] = [{
                'format_id': 'photo_original',
                'url': best_thumb,
                'ext': 'jpg',
                'vcodec': 'none',
                'acodec': 'none',
                'resolution': 'Original Photo'
            }]
    return res

ig_module.InstagramIE._extract_product = _patched_extract_product

COOKIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.txt")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: List[Dict[str, str]] = []
        self.title: str = ""
        self.in_title: bool = False

    def handle_starttag(self, tag: str, attrs: list):
        if tag == "meta":
            self.tags.append(dict(attrs))
        elif tag == "title":
            self.in_title = True

    def handle_data(self, data: str):
        if self.in_title and not self.title:
            self.title = data.strip()

    def handle_endtag(self, tag: str):
        if tag == "title":
            self.in_title = False

def format_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "N/A"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def format_filesize(bytes_val: Optional[int]) -> str:
    if not bytes_val:
        return ""
    if bytes_val >= 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024 * 1024):.1f} GB"
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    if bytes_val >= 1024:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val} B"

def enhance_pinterest_url(image_url: str) -> str:
    if "pinimg.com" in image_url:
        return re.sub(r'/(?:236x|474x|564x|736x|1200x)/', '/originals/', image_url)
    return image_url

def extract_pinterest_pin(url: str) -> Optional[Dict[str, Any]]:
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(url, timeout=12, allow_redirects=True)
        final_url = resp.url
        html = resp.text

        if final_url.rstrip("/").endswith("pinterest.com"):
            return None

        # Clean canonical URL
        pin_match = re.search(r'https?://(?:www\.)?pinterest\.[a-z.]+/pin/(\d+)', final_url)
        clean_url = f"https://www.pinterest.com/pin/{pin_match.group(1)}/" if pin_match else final_url

        parser = MetaParser()
        try:
            parser.feed(html)
        except Exception:
            pass

        title = parser.title or "Pinterest Media"
        title = re.sub(r'\s*-\s*Pinterest.*$', '', title, flags=re.I).strip()
        if not title or title.lower() == "pinterest":
            title = "Pinterest Inspiration"

        og_images: List[str] = []
        og_videos: List[str] = []

        for meta in parser.tags:
            prop = (meta.get("property") or meta.get("name") or "").lower()
            content = meta.get("content") or ""
            if not content:
                continue
            if prop in ["og:image", "og:image:url", "twitter:image", "twitter:image:src"]:
                og_images.append(content)
            elif prop in ["og:video", "og:video:url", "og:video:secure_url", "twitter:player:stream"]:
                og_videos.append(content)

        secondary_images = re.findall(
            r'https://i\.pinimg\.com/(?:originals|\d+x)/[a-zA-Z0-9/_.-]+\.(?:jpg|jpeg|png|webp)',
            html
        )

        def is_valid_pinterest_img(img_url: str) -> bool:
            bad_tokens = [
                'avatars', '75x75', 'facebook_share', 'd53b014d86a6b6761bf649a0ed813c2b',
                'logo_transparent', 'favicon', 'badge'
            ]
            return not any(b in img_url for b in bad_tokens)

        ordered_candidates: List[str] = []
        for img in og_images:
            if is_valid_pinterest_img(img):
                ordered_candidates.append(img)
        for img in secondary_images:
            if is_valid_pinterest_img(img):
                ordered_candidates.append(img)

        options: List[Dict[str, Any]] = []
        seen = set()

        # 1. Check if yt-dlp can extract video streams for this pin
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "js_runtimes": {"node": {}},
                "remote_components": ["ejs:github"],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                yt_info = ydl.extract_info(clean_url, download=False)
                if yt_info:
                    if yt_info.get("title") and ("Pinterest" in title or title == "Pinterest Inspiration"):
                        title = yt_info["title"]
                    yt_formats = yt_info.get("formats", [])
                    sorted_vids = sorted(
                        [f for f in yt_formats if f.get("vcodec") != "none" and f.get("height")],
                        key=lambda x: x.get("height") or 0,
                        reverse=True
                    )
                    for f in sorted_vids:
                        h = f.get("height")
                        label = f"Video HD ({h}p)" if h else "Video (HD)"
                        v_url = f.get("url")
                        if v_url and v_url not in seen:
                            seen.add(v_url)
                            options.append({
                                "id": f"pin_vid_{f.get('format_id')}",
                                "label": label,
                                "type": "video",
                                "quality": f"{h}p" if h else "HD",
                                "ext": "mp4",
                                "direct_url": v_url,
                                "needs_download": True
                            })
        except Exception as e:
            pass

        # 2. Direct regex scan for Pinterest video streams in HTML
        pin_mp4s = set(re.findall(r'https?://[a-zA-Z0-9.-]*\.pinimg\.com/videos/[^\s"\'\\]+?\.mp4', html))
        pin_m3u8s = set(re.findall(r'https?://[a-zA-Z0-9.-]*\.pinimg\.com/videos/[^\s"\'\\]+?\.m3u8', html))

        for m3u in pin_m3u8s:
            mp4_candidate = m3u.replace('/hls/', '/720p/').replace('.m3u8', '.mp4')
            pin_mp4s.add(mp4_candidate)

        for mp4_url in pin_mp4s:
            if mp4_url not in seen:
                seen.add(mp4_url)
                options.append({
                    "id": f"pin_vid_direct_{len(options)}",
                    "label": "Video HD (720p MP4)",
                    "type": "video",
                    "quality": "720p HD",
                    "ext": "mp4",
                    "direct_url": mp4_url,
                    "needs_download": True
                })

        for v_url in og_videos:
            if v_url not in seen:
                seen.add(v_url)
                options.append({
                    "id": f"pin_vid_og_{len(options)}",
                    "label": "Original Video (MP4)",
                    "type": "video",
                    "quality": "Source HD",
                    "ext": "mp4",
                    "direct_url": v_url,
                    "needs_download": True
                })

        # 3. Add audio option if video exists
        if any(o["type"] == "video" for o in options):
            first_vid = next(o for o in options if o["type"] == "video")
            options.append({
                "id": "pin_audio_mp3",
                "label": "Audio Track (MP3 320kbps)",
                "type": "audio",
                "quality": "320 kbps MP3",
                "ext": "mp3",
                "direct_url": first_vid.get("direct_url"),
                "format_spec": "bestaudio/best",
                "needs_download": True
            })

        # 4. Add photos
        for idx, img in enumerate(ordered_candidates):
            orig_url = enhance_pinterest_url(img)
            if orig_url not in seen:
                seen.add(orig_url)
                ext = orig_url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    ext = 'jpg'
                options.append({
                    "id": f"pin_photo_{len(options)}",
                    "label": "Original HD Photo" if not any(o['type'] == 'photo' for o in options) else f"Photo {len(options)+1}",
                    "type": "photo",
                    "quality": "Original Resolution",
                    "ext": ext,
                    "direct_url": orig_url,
                    "needs_download": True
                })

        if options:
            thumb = None
            for opt in options:
                if opt["type"] == "photo":
                    thumb = opt["direct_url"]
                    break
            if not thumb:
                thumb = options[0].get("direct_url")

            return {
                "title": title,
                "url": final_url,
                "platform": "Pinterest",
                "uploader": "Pinterest",
                "duration": "N/A",
                "thumbnail": thumb,
                "options": options,
                "raw_info": None
            }
    except Exception as e:
        print("Error:", e)
    return None

def check_direct_content_type(url: str) -> Optional[Dict[str, Any]]:
    try:
        head = requests.head(url, headers=HEADERS, timeout=6, allow_redirects=True)
        ct = head.headers.get("content-type", "").lower()
        final_url = head.url

        if ct.startswith("image/"):
            ext = ct.split("/")[-1].split(";")[0]
            if ext == "jpeg":
                ext = "jpg"
            clean_name = final_url.split("?")[0].split("/")[-1] or f"image.{ext}"
            return {
                "title": clean_name,
                "url": final_url,
                "platform": "Direct Image",
                "uploader": "Web Image",
                "duration": "N/A",
                "thumbnail": final_url,
                "options": [{
                    "id": "direct_image",
                    "label": f"Download Original Image (.{ext.upper()})",
                    "type": "photo",
                    "quality": "Source Resolution",
                    "ext": ext,
                    "direct_url": final_url,
                    "needs_download": True
                }],
                "raw_info": None
            }
        elif ct.startswith("video/"):
            ext = ct.split("/")[-1].split(";")[0]
            clean_name = final_url.split("?")[0].split("/")[-1] or f"video.{ext}"
            return {
                "title": clean_name,
                "url": final_url,
                "platform": "Direct Video",
                "uploader": "Web Video",
                "duration": "N/A",
                "thumbnail": None,
                "options": [{
                    "id": "direct_video",
                    "label": f"Download Video (.{ext.upper()})",
                    "type": "video",
                    "quality": "Source HD",
                    "ext": ext,
                    "direct_url": final_url,
                    "needs_download": True
                }],
                "raw_info": None
            }
    except Exception:
        pass
    return None

def extract_web_media_fallback(url: str) -> Dict[str, Any]:
    session = requests.Session()
    session.headers.update(HEADERS)
    response = session.get(url, timeout=12, allow_redirects=True)
    final_url = response.url
    html_text = response.text

    parser = MetaParser()
    try:
        parser.feed(html_text)
    except Exception:
        pass

    og_images: List[str] = []
    og_videos: List[str] = []
    og_title: Optional[str] = None

    for meta in parser.tags:
        prop = (meta.get("property") or meta.get("name") or "").lower()
        content = meta.get("content") or ""

        if not content:
            continue

        if prop in ["og:title", "twitter:title"] and not og_title:
            og_title = content
        elif prop in ["og:image", "og:image:url", "twitter:image", "twitter:image:src"]:
            og_images.append(content)
        elif prop in ["og:video", "og:video:url", "og:video:secure_url", "twitter:player:stream"]:
            og_videos.append(content)

    title = og_title or parser.title or "Media Item"
    title = re.sub(r'[\r\n\t]+', ' ', title).strip()

    platform = "Web"
    if "pinterest" in final_url or "pin.it" in final_url:
        platform = "Pinterest"
    elif "instagram" in final_url:
        platform = "Instagram"
    elif "tiktok" in final_url:
        platform = "TikTok"
    elif "unsplash" in final_url:
        platform = "Unsplash"

    options: List[Dict[str, Any]] = []

    for idx, v_url in enumerate(og_videos):
        options.append({
            "id": f"web_video_{idx}",
            "label": f"Video (MP4)" if idx == 0 else f"Video Track {idx+1}",
            "type": "video",
            "quality": "Source Quality",
            "ext": "mp4",
            "direct_url": v_url,
            "needs_download": True
        })

    seen_images = set()
    bad_tokens = ['avatars', '75x75', 'facebook_share', 'd53b014d86a6b6761bf649a0ed813c2b', 'logo_transparent', 'favicon', 'badge']
    for idx, img_url in enumerate(og_images):
        if any(b in img_url for b in bad_tokens):
            continue
        enhanced = enhance_pinterest_url(img_url)
        if enhanced not in seen_images:
            seen_images.add(enhanced)
            label = "Original High-Res Photo" if len(seen_images) == 1 else f"Photo {len(seen_images)}"
            options.append({
                "id": f"web_photo_{idx}",
                "label": label,
                "type": "photo",
                "quality": "Original Resolution",
                "ext": "jpg",
                "direct_url": enhanced,
                "needs_download": True
            })

    if not options:
        raise ValueError("No video stream or photo could be detected at this link.")

    thumbnail = options[0].get("direct_url")

    return {
        "title": title,
        "url": final_url,
        "platform": platform,
        "uploader": platform,
        "duration": "N/A",
        "thumbnail": thumbnail,
        "options": options,
        "raw_info": None
    }

def extract_media_info(url: str) -> Dict[str, Any]:
    url = url.strip()

    # 1. Quick check for direct media URL / Content-Type
    direct = check_direct_content_type(url)
    if direct:
        return direct

    # 2. Check for Pinterest
    if "pinterest." in url.lower() or "pin.it" in url.lower():
        pin_data = extract_pinterest_pin(url)
        if pin_data and pin_data.get("options"):
            return pin_data

    # 3. Try yt-dlp with Node.js JS runtime and EJS challenge solver
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "noplaylist": True,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "ignore_no_formats_error": True,
    }
    if os.path.exists(COOKIES_PATH) and os.path.getsize(COOKIES_PATH) > 0:
        ydl_opts["cookiefile"] = COOKIES_PATH

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("No media info returned by extractor.")

            title = info.get("title") or "Media Download"
            thumbnail = info.get("thumbnail")
            duration = format_duration(info.get("duration"))
            uploader = info.get("uploader") or info.get("channel") or info.get("creator") or info.get("extractor_key") or "Unknown"
            platform = info.get("extractor_key") or "Universal"

            formats = info.get("formats", [])
            options: List[Dict[str, Any]] = []

            thumbnails = info.get("thumbnails", [])
            has_video = any(f.get("vcodec") != "none" for f in formats)

            # If it's a video platform
            if has_video:
                resolutions_seen = set()
                sorted_formats = sorted(
                    [f for f in formats if f.get("vcodec") != "none" and f.get("height")],
                    key=lambda x: x.get("height", 0),
                    reverse=True
                )

                for f in sorted_formats:
                    h = f.get("height")
                    if h and h not in resolutions_seen:
                        resolutions_seen.add(h)
                        res_label = f"{h}p"
                        if h >= 2160:
                            res_label = "4K (2160p)"
                        elif h >= 1440:
                            res_label = "2K (1440p)"
                        elif h == 1080:
                            res_label = "Full HD (1080p)"
                        elif h == 720:
                            res_label = "HD (720p)"

                        options.append({
                            "id": f"video_{h}",
                            "format_spec": f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best",
                            "label": f"Video - {res_label}",
                            "type": "video",
                            "quality": res_label,
                            "ext": "mp4",
                            "size": format_filesize(f.get("filesize") or f.get("filesize_approx")),
                            "needs_download": True
                        })

                if not options:
                    options.append({
                        "id": "video_best",
                        "format_spec": "bestvideo+bestaudio/best",
                        "label": "Best Video Quality",
                        "type": "video",
                        "quality": "Best Quality",
                        "ext": "mp4",
                        "size": "",
                        "needs_download": True
                    })

                # Audio MP3 option
                options.append({
                    "id": "audio_mp3",
                    "format_spec": "bestaudio/best",
                    "label": "Audio Only (MP3)",
                    "type": "audio",
                    "quality": "320 kbps (Audio)",
                    "ext": "mp3",
                    "needs_download": True
                })

            # Check if there are high-res photos
            if not has_video or platform.lower() in ["pinterest", "instagram"]:
                best_img = thumbnail
                if thumbnails:
                    best_img = thumbnails[-1].get("url") or thumbnail
                if best_img:
                    best_img = enhance_pinterest_url(best_img)
                    options.insert(0, {
                        "id": "original_photo",
                        "label": "Original High-Res Photo",
                        "type": "photo",
                        "quality": "Original Photo",
                        "ext": "jpg",
                        "direct_url": best_img,
                        "needs_download": True
                    })

            # Cover thumbnail for videos
            if thumbnail and has_video:
                options.append({
                    "id": "video_thumbnail",
                    "label": "Cover / Thumbnail",
                    "type": "photo",
                    "quality": "Original Cover",
                    "ext": "jpg",
                    "direct_url": thumbnail,
                    "needs_download": True
                })

            if not options:
                return extract_web_media_fallback(url)

            return {
                "title": title,
                "url": url,
                "platform": platform,
                "uploader": uploader,
                "duration": duration,
                "thumbnail": thumbnail or (options[0].get("direct_url") if options else None),
                "options": options,
                "raw_info": None
            }

    except yt_dlp.utils.DownloadError as e:
        err_str = str(e)
        clean_err = re.sub(r'^(?:ERROR:\s*)?(?:\[.*?\]\s*)?', '', err_str).strip()
        clean_err = re.sub(r'^[a-zA-Z0-9_-]+:\s*', '', clean_err).strip()

        lower_err = clean_err.lower()
        if "this video is unavailable" in lower_err:
            raise ValueError("This video is unavailable on YouTube. It may be deleted, set to private, or the link has a typo.")
        elif "private video" in lower_err:
            raise ValueError("This video is marked as Private by the uploader and cannot be accessed.")
        elif "sign in to confirm" in lower_err or "bot" in lower_err:
            raise ValueError("YouTube requires account authentication (bot check) for this video. You can add YouTube cookies using the '🍪 Cookies' button at the top to bypass this check.")
        elif "there is no video in this post" in lower_err or "empty media response" in lower_err:
            # Instagram photo post blocked or lacking session
            raise ValueError("This Instagram post contains photos. Instagram requires you to be logged in to view photo posts. Please make sure your cookies in the '🍪 Cookies' button include your Instagram session, or check if the post is public.")
        elif "429" in lower_err or "too many requests" in lower_err:
            raise ValueError("Instagram has temporarily rate-limited anonymous requests (HTTP 429). To bypass this limit and download Instagram photos freely, log into instagram.com and export your cookies using the '🍪 Cookies' button at the top.")
        elif "members-only" in lower_err:
            raise ValueError("This video is restricted to channel members only.")
        elif "unsupported url" in lower_err:
            return extract_web_media_fallback(url)
        
        try:
            return extract_web_media_fallback(url)
        except Exception:
            raise ValueError(clean_err)

    except Exception:
        return extract_web_media_fallback(url)
