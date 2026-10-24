import http.cookiejar
import requests
import json
import re

cj = http.cookiejar.MozillaCookieJar('cookies.txt')
cj.load(ignore_discard=True, ignore_expires=True)

session = requests.Session()
session.cookies = cj
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

url = 'https://www.instagram.com/p/De4Y9jcMRZg/'
r = session.get(url, timeout=10)
html = r.text

with open('insta_with_cookies.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved HTML length:", len(html))

# Look for image URLs
scontent_matches = set(re.findall(r'https://[^"\'\\<>\s]+?(?:scontent|cdninstagram)[^"\'\\<>\s]+', html.replace('\\/', '/').replace('\\u0026', '&')))
filtered = [u for u in scontent_matches if 'rsrc.php' not in u and not u.endswith('.js') and not u.endswith('.css')]
print("Found real image matches:", len(filtered))
for u in filtered[:5]:
    print(" ->", u[:120])
