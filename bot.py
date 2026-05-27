#!/usr/bin/env python3
import os, asyncio, logging, re, glob, sys
from pyrogram import Client, filters, idle
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ChatType

# ==================== py-tgcalls Imports (Fixed) ====================
from pytgcalls import PyTgCalls
try:
    from pytgcalls.types.input_stream import AudioPiped
    from pytgcalls.types.input_stream.quality import HighQualityAudio
except ImportError:
    # Fallback for some versions
    from pytgcalls.types import AudioPiped
    from pytgcalls.types import HighQualityAudio

from pytgcalls.types import Update

import yt_dlp

# ===================== Railway Fixes =====================
os.makedirs("/tmp/music_cache", exist_ok=True)
downloads_dir = "/tmp/music_cache"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ===================== Config =====================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION = os.getenv("SESSION_STRING")

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)

calls = PyTgCalls(user)

queues = {}
active = {}


def format_duration(sec):
    if not sec: return "Live"
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def clean_artist(title, uploader):
    patterns = [r'^(.+?)\s*[-–—]\s*(.+)$', r'^(.+?)\s*[:|]\s*(.+)$']
    for p in patterns:
        match = re.match(p, title)
        if match:
            return re.sub(r'\s*(official|video|audio).*$', '', match.group(1), flags=re.IGNORECASE).strip()
    return re.sub(r'\s*(music|vevo|official).*$', '', uploader or "Unknown", flags=re.IGNORECASE).strip()


def download_audio(q):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{downloads_dir}/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    search = q if q.startswith('http') else f'scsearch:{q}'

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search, download=True)
        if 'entries' in info:
            info = info['entries'][0]

        vid_id = info.get('id', 'unknown')
        filename = f'{downloads_dir}/{vid_id}.mp3'

        if not os.path.exists(filename):
            files = glob.glob(f'{downloads_dir}/{vid_id}.*')
            if files:
                filename = files[0]

        return {
            'file': filename,
            'title': info.get('title', 'Unknown'),
            'artist': clean_artist(info.get('title', ''), info.get('uploader', '')),
            'duration': info.get('duration', 0),
            'thumb': info.get('thumbnail') or 'https://telegra.ph/file/2f7debf856695e0a17296.png',
        }


async def ensure_assistant_joined(cid):
    try:
        await user.get_chat_member(cid, "me")
        return True
    except:
        pass

    try:
        me = await user.get_me()
        await app.add_chat_members(cid, me.id)
        await asyncio.sleep(2)
        return True
    except:
        pass

    try:
        link = await app.export_chat_invite_link(cid)
        await user.join_chat(link)
        await asyncio.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Join failed: {e}")
        return False


async def send_now_playing(cid, song, queue_list):
    caption = (
        "🎵 **𝐍𝐨𝐰 𝐏𝐥𝐚𝐲𝐢𝐧𝐠**\n\n"
        f"🎼 **Song :** {song['title']}\n"
        f"🎙 **Artist :** {song['artist']}\n"
        f"⏳ **Duration :** {format_duration(song['duration'])}\n"
        f"🙋‍♂️ **Requested By :** {song.get('requester', 'Anonymous')}\n\n"
    )

    if queue_list:
        caption += "📋 **Up Next:**\n"
        for i, s in enumerate(queue_list[:5], 1):
            caption += f"**{i}.** {s['title']}\n"
        if len(queue_list) > 5:
            caption += f"\n➕ +{len(queue_list)-5} more"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏸", callback_data="pause"),
         InlineKeyboardButton("▶️", callback_data="resume")],
        [InlineKeyboardButton("⏭", callback_data="skip"),
         InlineKeyboardButton("⏹", callback_data="end")]
    ])

    try:
        await app.send_photo(cid, song['thumb'], caption=caption, reply_markup=buttons)
    except:
        await app.send_message(cid, caption, reply_markup=buttons)


async def play_next(cid):
    if cid not in queues or not queues[cid]:
        return

    song = queues[cid].pop(0)
    try:
        audio = AudioPiped(song['file'], HighQualityAudio())
        await calls.change_stream(cid, audio)
        active[cid] = song
        await send_now_playing(cid, song, queues.get(cid, []))
        logger.info(f"Now Playing: {song['title']}")
    except Exception as e:
        logger.error(f"Play next error: {e}")
        await asyncio.sleep(2)
        await play_next(cid)


# ===================== Handlers =====================

@app.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    data = query.data
    cid = query.message.chat.id

    if data == "pause":
        await calls.pause_stream(cid)
        await query.answer("⏸ Paused")
    elif data == "resume":
        await calls.resume_stream(cid)
        await query.answer("▶️ Resumed")
    elif data == "skip":
        await query.answer("⏭ Skipping...")
        await play_next(cid)
    elif data == "end":
        await calls.leave_group_call(cid)
        queues.pop(cid, None)
        active.pop(cid, None)
        await query.answer("⏹ Stopped")
        await query.message.edit_caption("⏹ **Music Stopped**")


@app.on_message(filters.command("play"))
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("❌ `/play <song name or link>`")

    q = m.text.split(None, 1)[1]
    cid = m.chat.id
    msg = await m.reply("🔍 **Searching...**")

    try:
        if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            if not await ensure_assistant_joined(cid):
                return await msg.edit("❌ Bot ko **Admin** banao (Invite Users permission)")

        await msg.edit("⬇️ **Downloading...**")
        song = await asyncio.to_thread(download_audio, q)
        song['requester'] = m.from_user.mention if m.from_user else "Anonymous"

        if cid not in queues:
            queues[cid] = []

        if cid not in active:
            audio = AudioPiped(song['file'], HighQualityAudio())
            await calls.join_group_call(cid, audio)
            active[cid] = song
            await msg.delete()
            await send_now_playing(cid, song, [])
        else:
            queues[cid].append(song)
            await msg.edit(f"✅ **Queued:** {song['title'][:45]}...")
    except Exception as e:
        logger.error(f"Play error: {e}")
        await msg.edit(f"❌ Error: {str(e)[:150]}")


@app.on_message(filters.command(["skip"]))
async def skip(_, m: Message):
    if m.chat.id in active:
        await m.reply("⏭ **Skipped**")
        await play_next(m.chat.id)
    else:
        await m.reply("❌ Nothing is playing")


@app.on_message(filters.command("pause"))
async def pause(_, m: Message):
    try:
        await calls.pause_stream(m.chat.id)
        await m.reply("⏸ **Paused**")
    except:
        await m.reply("❌ Not playing")


@app.on_message(filters.command("resume"))
async def resume(_, m: Message):
    try:
        await calls.resume_stream(m.chat.id)
        await m.reply("▶️ **Resumed**")
    except:
        await m.reply("❌ Not paused")


@app.on_message(filters.command(["stop", "end"]))
async def stop(_, m: Message):
    try:
        await calls.leave_group_call(m.chat.id)
        queues.pop(m.chat.id, None)
        active.pop(m.chat.id, None)
        await m.reply("⏹ **Music Stopped**")
    except:
        await m.reply("❌ Not in voice chat")


@app.on_message(filters.command("queue"))
async def queue_cmd(_, m: Message):
    cid = m.chat.id
    if cid not in active:
        return await m.reply("📭 **Nothing playing**")
    text = "📋 **QUEUE**\n\n"
    if cid in queues and queues[cid]:
        for i, s in enumerate(queues[cid], 1):
            text += f"**{i}.** {s['title']}\n"
    else:
        text += "Empty"
    await m.reply(text)


@calls.on_stream_end()
async def on_stream_end(_, update: Update):
    await play_next(update.chat_id)


# ===================== Main =====================
async def main():
    await app.start()
    await user.start()
    await calls.start()
    logger.info("🎵 Music Bot Started Successfully on Railway!")
    await idle()


if __name__ == "__main__":
    asyncio.run(main())
