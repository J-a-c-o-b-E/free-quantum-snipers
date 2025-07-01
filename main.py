from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import os
import re

# --- Config ---
api_id = 29624898
api_hash = '5b4a9c274b2d7bc48847d527b2721330'
source_channel = -1001541002369  # private channel you’re watching
target_channel = -1002584918076  # your own Telegram channel

session_name = os.getenv("SESSION_NAME", "railway_session")
client = TelegramClient(session_name, api_id, api_hash)

# --- Settings ---
KEYWORDS = ['tp1', 'tp2', 'tp3', 'sl']
BLACKLIST = ['alex', 'tfxc']
NEWSIGNAL_PATH = 'NEWSIGNAL.png'
latest_signal_map = {}

# --- Helpers ---
def is_video_or_gif(media):
    if isinstance(media, MessageMediaDocument):
        if media.document and media.document.mime_type:
            mime = media.document.mime_type.lower()
            return mime.startswith("video") or "gif" in mime
    return False

def replace_embedded_links(text):
    if not text:
        return text

    link = "https://t.me/QuantumSnipers?text=I%20want%20to%20start%20making%20money%20with%20you%20for%20FREE"

    def replacement(match):
        display_text = match.group(1).strip("*")
        return f'[{display_text}]({link})'

    return re.sub(r'\[([^\]]+)\]\(https?://[^)]+\)', replacement, text)

def replace_mentions(text):
    if not text:
        return text
    text = text.replace("@TheForexComplex", "@QuantumSnipers") \
               .replace("https://t.me/TheForexComplex", "https://t.me/QuantumSnipers")
    return replace_embedded_links(text)

def build_fake_forward_text(msg):
    text = msg.text or ""
    return f"**Quantum Snipers Premium Group Member's Result:**\n\n{replace_mentions(text)}"

# --- Live Listener ---
@client.on(events.NewMessage(chats=source_channel))
async def forward_handler(event):
    msg = event.message
    text = (msg.text or "").lower()

    print(f"📨 New msg: id {msg.id} | has media: {'yes' if msg.media else 'no'}")

    if any(black in text for black in BLACKLIST):
        print(f"⛔ Blocked (blacklist match) — id {msg.id}")
        return

    if is_video_or_gif(msg.media):
        print(f"⛔ Blocked (GIF or video) — id {msg.id}")
        return

    modified_text = replace_mentions(msg.text or "")

    if "signal alert" in text:
        if os.path.exists(NEWSIGNAL_PATH):
            await client.send_file(target_channel, NEWSIGNAL_PATH, caption=modified_text, link_preview=False)
            print(f"✅ SIGNAL ALERT img sent — id {msg.id}")
        else:
            await client.send_message(target_channel, modified_text, link_preview=False)
            print(f"✅ SIGNAL ALERT text sent — id {msg.id}")
        latest_signal_map[msg.id] = msg.id
        return

    if any(k in text for k in KEYWORDS) and msg.reply_to_msg_id:
        reply_to = latest_signal_map.get(msg.reply_to_msg_id)
        if reply_to:
            if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                await client.send_file(target_channel, msg.media, caption=modified_text, reply_to=reply_to, link_preview=False)
                print(f"📷 Replied media → SIGNAL ALERT — id {msg.id}")
            else:
                await client.send_message(target_channel, modified_text, reply_to=reply_to, link_preview=False)
                print(f"↪️ Replied text → SIGNAL ALERT — id {msg.id}")
            return

    if msg.forward:
        fake_caption = build_fake_forward_text(msg)
        if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            await client.send_file(target_channel, msg.media, caption=fake_caption, link_preview=False)
            print(f"📸 Faked forward (media) — id {msg.id}")
        else:
            await client.send_message(target_channel, fake_caption, link_preview=False)
            print(f"✉️ Faked forward (text) — id {msg.id}")
        return

    if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
        await client.send_file(target_channel, msg.media, caption=modified_text, link_preview=False)
        print(f"🖼️ Media forwarded — id {msg.id}")
    else:
        await client.send_message(target_channel, modified_text, link_preview=False)
        print(f"📩 Text forwarded — id {msg.id}")

# --- Start ---
if __name__ == "__main__":
    print("🚀 Bot started — now forwarding live messages...")
    client.start()
    client.run_until_disconnected()
