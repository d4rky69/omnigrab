import re
import json

with open('insta_embed.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's search for "display_url" or "image_versions" or "src"
for term in ['display_url', 'image_versions2', 'candidates', 'display_resources', 'EmbeddedMediaImage', 'shortcode_media', 'graphql']:
    pos = html.find(term)
    print(f'Term "{term}" in html: {pos != -1}')
    if pos != -1:
        print(' Context:', html[max(0, pos-40):pos+120])

# Look for any url containing scontent or cdninstagram
scontent = re.findall(r'https:\\?/\\?/[^"\'\s]+?(?:scontent|cdninstagram)[^"\'\s]+', html)
print('Found scontent/cdninstagram matches:', len(scontent))
for s in scontent[:5]:
    cleaned = s.replace(r'\/', '/').replace(r'\u0026', '&')
    print('  ->', cleaned[:120])
