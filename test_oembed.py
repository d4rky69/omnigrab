import requests
import json

url = "https://www.instagram.com/p/De4Y9jcMRZg/"
oembed_url = f"https://api.instagram.com/oembed/?url={url}"
r = requests.get(oembed_url, timeout=6)
print("Instagram oembed status:", r.status_code)
if r.status_code == 200:
    print(r.json())
else:
    print("Response:", r.text[:200])
