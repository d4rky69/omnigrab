import yt_dlp
from yt_dlp.extractor.instagram import InstagramIE

original_extract = InstagramIE._real_extract

def patched_extract(self, url):
    try:
        return original_extract(self, url)
    except yt_dlp.utils.ExtractorError as e:
        if 'There is no video in this post' in str(e):
            print("Intercepted 'There is no video in this post'!")
        raise e

print("Patched test ready")
