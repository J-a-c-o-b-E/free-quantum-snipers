from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import re
import os
import asyncio

api_id = 29624898
api_hash = '5b4a9c274b2d7bc48847d527b2721330'

source_channel = -1001541002369
target_channel = -1002584918076

client = TelegramClient('second_forwarder_session', api_id, api_hash)

KEYWORDS = ['tp1', 'tp2', 'tp3', 'sl']
latest_signal_map = {}
NEWSIGNAL_PATH = 'NEWSIGNALQS.png'
id_map = {}

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

def markdown_to_html(text):
    if not text:
        return text
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
    return text

def build_fake_forward_text(msg):
    text = msg.text or ""
    return f"<b>Quantum Snipers Premium Group Member's Result:</b>\n\n{markdown_to_html(replace_mentions(text))}"

async def handle_message(msg):
    if is_video_or_gif(msg.media):
        print(f"⛔ Skipped GIF/video — id {msg.id}")
        return

    if not msg.text:
        return

    text = msg.text.lower()
    if "alex" in text or "tfxc" in text:
        print(f"⛔ Skipped due to blacklisted keyword — id {msg.id}")
        return

    modified_text = markdown_to_html(replace_mentions(msg.text))

    reply_to = None
    if msg.reply_to_msg_id and msg.reply_to_msg_id in id_map:
        reply_to = id_map[msg.reply_to_msg_id]

    if "signal alert" in text:
        if os.path.exists(NEWSIGNAL_PATH):
            sent = await client.send_file(target_channel, NEWSIGNAL_PATH, caption=modified_text, reply_to=reply_to, link_preview=False, parse_mode='html')
            print(f"✅ SIGNAL ALERT image + caption sent — id {msg.id}")
        else:
            sent = await client.send_message(target_channel, modified_text, reply_to=reply_to, link_preview=False, parse_mode='html')
            print(f"✅ SIGNAL ALERT text-only forwarded — id {msg.id}")
        id_map[msg.id] = sent.id
        return

    if msg.forward:
        fake_caption = build_fake_forward_text(msg)
        if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            sent = await client.send_file(target_channel, msg.media, caption=fake_caption, reply_to=reply_to, link_preview=False, parse_mode='html')
            print(f"📸 Faked forward w/ media — id {msg.id}")
        else:
            sent = await client.send_message(target_channel, fake_caption, reply_to=reply_to, link_preview=False, parse_mode='html')
            print(f"✉️ Faked forward (text only) — id {msg.id}")
        id_map[msg.id] = sent.id
        return

    if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
        sent = await client.send_file(target_channel, msg.media, caption=modified_text, reply_to=reply_to, link_preview=False, parse_mode='html')
        print(f"🖼️ Generic media sent — id {msg.id}")
    else:
        sent = await client.send_message(target_channel, modified_text, reply_to=reply_to, link_preview=False, parse_mode='html')
        print(f"📩 Generic text sent — id {msg.id}")

    id_map[msg.id] = sent.id

@client.on(events.NewMessage(chats=source_channel))
async def live_forward_handler(event):
    await handle_message(event.message)

async def main():
    await client.start()
    print("🚀 Bot is running 24/7...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())