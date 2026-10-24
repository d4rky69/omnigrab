import re

with open('insta_embed.html', 'r', encoding='utf-8') as f:
    html = f.read()

scontent = re.findall(r'https:\\?/\\?/[^"\'\s]+?(?:scontent|cdninstagram)[^"\'\s]+', html)
non_rsrc = [s for s in scontent if 'rsrc.php' not in s]
print('Non-rsrc count:', len(non_rsrc))
for s in non_rsrc[:10]:
    cleaned = s.replace(r'\/', '/').replace(r'\u0026', '&')
    print('Cleaned:', cleaned[:150])
