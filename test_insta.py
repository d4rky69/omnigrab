import requests
import re
import json

url = 'https://www.instagram.com/p/De4Y9jcMRZg/embed/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

r = requests.get(url, headers=headers, timeout=10)
print('Embed Status:', r.status_code)
html = r.text

with open('insta_embed.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Saved HTML length:', len(html))

# Search for image URLs in HTML
matches = re.findall(r'https://[^"\'\\<>\s]+(?:\.jpg|\.jpeg|\.png|\.webp)[^"\'\\<>\s]*', html)
print('Found image URLs count:', len(matches))
for m in matches:
    if 'rsrc.php' not in m:
        print('Real image URL:', m[:120])
