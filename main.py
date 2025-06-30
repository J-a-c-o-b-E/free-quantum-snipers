from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import re
import os

api_id = 29624898
api_hash = '5b4a9c274b2d7bc48847d527b2721330'

source_channel = -1001541002369
target_channel = -1002584918076

# ✅ Use dynamic session name based on environment
session_name = os.getenv("SESSION_NAME", "default_session")
client = TelegramClient(session_name, api_id, api_hash)

KEYWORDS = ['tp1', 'tp2', 'tp3', 'sl']
latest_signal_map = {}
NEWSIGNAL_PATH = 'NEWSIGNAL.png'

def is_video_or_gif(media):
    if isinstance(media, MessageMediaDocument):
        if media.document and media.document.mime_type:
            mime = media.document.mime_type.lower()
            return mime.startswith("video") or "gif" in mime
    return False

def replace_embedded_links(text):
    if not text:
        return text

    message = "I want to start making money with you for FREE 💰"
    encoded = message.replace(" ", "%20")

    def replacement(match):
        display_text = match.group(1).strip("*")
        return f'[{display_text}](https://t.me/QuantumSnipers?text={encoded})'

    return re.sub(
        r'\[([^\]]+)\]\(https?://[^)]+\)',
        replacement,
        text
    )

def replace_mentions(text):
    if not text:
        return text
    text = text.replace("@TheForexComplex", "@QuantumSnipers") \
               .replace("https://t.me/TheForexComplex", "https://t.me/QuantumSnipers")
    text = replace_embedded_links(text)
    return text

def build_fake_forward_text(msg):
    text = msg.text or ""
    return f"**Quantum Snipers Premium Group Member's Result:**\n\n{replace_mentions(text)}"

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Not authorized — run locally to generate session for:", session_name)
        return

    print(f"✅ Connected using session: {session_name}")

    messages = []
    async for message in client.iter_messages(source_channel, limit=100):
        messages.append(message)

    messages.reverse()

    for msg in messages:
        if is_video_or_gif(msg.media):
            print(f"⛔ Skipped GIF/video — id {msg.id}")
            continue

        if not msg.text:
            continue

        text = msg.text.lower()
        if "alex" in text or "tfxc" in text:
            print(f"⛔ Skipped due to blacklisted keyword — id {msg.id}")
            continue

        modified_text = replace_mentions(msg.text)

        if "signal alert" in text:
            if os.path.exists(NEWSIGNAL_PATH):
                await client.send_file(target_channel, NEWSIGNAL_PATH, caption=modified_text, link_preview=False)
                print(f"✅ SIGNAL ALERT image + caption sent — id {msg.id}")
            else:
                sent = await client.send_message(target_channel, modified_text, link_preview=False)
                print(f"✅ SIGNAL ALERT text-only forwarded — id {msg.id}")
            latest_signal_map[msg.id] = msg.id
            continue

        if any(k in text for k in KEYWORDS) and msg.reply_to_msg_id:
            original_id = msg.reply_to_msg_id
            if original_id in latest_signal_map:
                reply_to = latest_signal_map[original_id]
                if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                    await client.send_file(target_channel, msg.media, caption=modified_text, reply_to=reply_to, link_preview=False)
                    print(f"📷 Reply w/ media → SIGNAL ALERT — id {msg.id}")
                else:
                    await client.send_message(target_channel, modified_text, reply_to=reply_to, link_preview=False)
                    print(f"↪️ Reply text → SIGNAL ALERT — id {msg.id}")
                continue

        if msg.forward:
            fake_caption = build_fake_forward_text(msg)
            if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                await client.send_file(target_channel, msg.media, caption=fake_caption, link_preview=False)
                print(f"📸 Faked forward w/ media — id {msg.id}")
            else:
                await client.send_message(target_channel, fake_caption, link_preview=False)
                print(f"✉️ Faked forward (text only) — id {msg.id}")
            continue

        if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            await client.send_file(target_channel, msg.media, caption=modified_text, link_preview=False)
            print(f"🖼️ Generic media sent — id {msg.id}")
        else:
            await client.send_message(target_channel, modified_text, link_preview=False)
            print(f"📩 Generic text sent — id {msg.id}")

if __name__ == "__main__":
    import asyncio

    async def generate_session():
        await client.start()  # <— this will trigger the login prompt
        print(f"✅ Logged in — session saved as: {session_name}")

    asyncio.run(generate_session())
