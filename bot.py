import asyncio
import yt_dlp

from pyrogram import Client, filters
from pyrogram.idle import idle

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import (
    AudioPiped,
    AudioVideoPiped
)

from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo
)

# ================= CONFIG =================

API_ID = 34848798
API_HASH = "210df233d07183ee955143092259dabb"
BOT_TOKEN = "8713743302:AAHCiUsj36bl3nTPnjmGtlk0Ut-k0t4xae8"

# ==========================================

app = Client(
    "vcplayerbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call_py = PyTgCalls(app)

# ================= YTDLP =================

ydl_opts = {
    "format": "best",
    "quiet": True,
    "noplaylist": True
}


def yt_search(query):

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            f"ytsearch:{query}",
            download=False
        )["entries"][0]

        title = info["title"]
        url = info["url"]

        return title, url


# ================= START =================

@app.on_message(filters.command("start"))
async def start(_, message):

    text = """
🎵 Group VC Music Bot

Commands:

/play song name
→ audio stream

/vplay song name
→ video stream

/stop
→ stop streaming
"""

    await message.reply_text(text)


# ================= AUDIO PLAY =================

@app.on_message(filters.command("play"))
async def play(_, message):

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/play song name"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        "🔍 Searching audio..."
    )

    try:

        title, stream = yt_search(query)

        await call_py.join_group_call(
            message.chat.id,
            AudioPiped(
                stream,
                HighQualityAudio()
            )
        )

        await msg.edit_text(
            f"🎵 Playing Audio:\n\n{title}"
        )

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n{e}"
        )


# ================= VIDEO PLAY =================

@app.on_message(filters.command("vplay"))
async def vplay(_, message):

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/vplay song name"
        )

    query = " ".join(message.command[1:])

    msg = await message.reply_text(
        "🔍 Searching video..."
    )

    try:

        title, stream = yt_search(query)

        await call_py.join_group_call(
            message.chat.id,
            AudioVideoPiped(
                stream,
                HighQualityAudio(),
                HighQualityVideo()
            )
        )

        await msg.edit_text(
            f"📺 Playing Video:\n\n{title}"
        )

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n{e}"
        )


# ================= STOP =================

@app.on_message(filters.command("stop"))
async def stop(_, message):

    try:

        await call_py.leave_group_call(
            message.chat.id
        )

        await message.reply_text(
            "⏹ Stream stopped."
        )

    except Exception as e:

        await message.reply_text(
            f"❌ Error:\n{e}"
        )


# ================= MAIN =================

async def main():

    await app.start()

    await call_py.start()

    print("🎵 VC Player Bot Started")

    await idle()

    await app.stop()


asyncio.get_event_loop().run_until_complete(main())
