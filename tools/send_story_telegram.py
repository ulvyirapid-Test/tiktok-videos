#!/usr/bin/env python3
"""Send a rendered story video to Ravy's Telegram for approval.

    TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 tools/send_story_telegram.py videos/stories/ID.json

Buttons send callback_data "approve:ID" / "redo:ID" — handled by the Make scenario
"Story Approval (Telegram)". Skips quietly when the secrets are not set.
"""
import json, os, sys, urllib.request, uuid

token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
if not token or not chat:
    print("Telegram secrets not set — skipping send.")
    sys.exit(0)

meta = json.load(open(sys.argv[1], encoding="utf-8"))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
video = os.path.join(root, meta["video"])
raw = "https://raw.githubusercontent.com/" + os.environ.get("GITHUB_REPOSITORY", "ulvyirapid-Test/tiktok-videos") + "/main/"

caption = (f"🎬 វីដេអូថ្មីរង់ចាំការពិនិត្យ\n<b>{meta['id']}</b> · {meta['duration']} វិនាទី\n\n"
           f"{meta['caption']}\n\n🖼 Cover: {raw}{meta['cover']}")[:1024]
markup = {"inline_keyboard": [[{"text": "✅ អនុម័ត", "callback_data": f"approve:{meta['id']}"[:64]},
                               {"text": "❌ កែឡើងវិញ", "callback_data": f"redo:{meta['id']}"[:64]}]]}

fields = {"chat_id": chat, "caption": caption, "parse_mode": "HTML", "supports_streaming": "true",
          "reply_markup": json.dumps(markup, ensure_ascii=False)}
b = uuid.uuid4().hex
body = b""
for k, v in fields.items():
    body += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
body += (f"--{b}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{meta['id']}.mp4\"\r\n"
         f"Content-Type: video/mp4\r\n\r\n").encode() + open(video, "rb").read() + f"\r\n--{b}--\r\n".encode()
req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendVideo", data=body,
                             headers={"Content-Type": f"multipart/form-data; boundary={b}"})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.load(r)
except urllib.error.HTTPError as e:
    sys.exit(f"Telegram error {e.code}: {e.read().decode()[:300]}")
print("sent" if res.get("ok") else res)
