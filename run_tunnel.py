import os
import re
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_BIN = os.path.join(BASE_DIR, "bin", "cloudflared.exe")
TUNNEL_FILE = os.path.join(BASE_DIR, "tunnel_url.txt")

if not os.path.exists(CLOUDFLARED_BIN):
    print(f"Error: {CLOUDFLARED_BIN} not found", file=sys.stderr)
    sys.exit(1)

cmd = [CLOUDFLARED_BIN, "tunnel", "--url", "http://127.0.0.1:8000"]
print(f"Starting Cloudflare Quick Tunnel on port 8000...")

proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    encoding="utf-8",
    errors="replace"
)

url_found = False
for line in proc.stdout:
    sys.stdout.write(line)
    sys.stdout.flush()
    if not url_found:
        m = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if m:
            public_url = m.group(0)
            url_found = True
            with open(TUNNEL_FILE, "w", encoding="utf-8") as f:
                f.write(public_url)
            print("\n" + "="*60)
            print(f"🚀 LIVE PUBLIC HTTPS URL READY:")
            print(f"👉 {public_url}")
            print("="*60 + "\n")

proc.wait()
