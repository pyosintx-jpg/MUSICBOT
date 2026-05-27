import os
import yt_dlp
from pyrogram import Client, filters, idle

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo

# ================= ENV CONFIG =================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =============================================

app = Client(
    "render_vc_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call = PyTgCalls(app)

# ================= YT-DLP =================

ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True
}


def yt_search(query):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["title"], info["url"]

# ================= COMMANDS =================

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply(
        "🎵 VC Bot Ready\n\n"
        "/play song name - audio\n"
        "/vplay song name - video\n"
        "/stop - stop stream"
    )


@app.on_message(filters.command("play"))
async def play(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: /play song name")

    query = " ".join(msg.command[1:])
    wait = await msg.reply("🔍 Searching...")

    try:
        title, stream = yt_search(query)

        await call.join_group_call(
            msg.chat.id,
            AudioPiped(stream, HighQualityAudio())
        )

        await wait.edit(f"🎵 Playing Audio:\n{title}")

    except Exception as e:
        await wait.edit(f"❌ Error:\n{e}")


@app.on_message(filters.command("vplay"))
async def vplay(_, msg):

    if len(msg.command) < 2:
        return await msg.reply("Usage: /vplay song name")

    query = " ".join(msg.command[1:])
    wait = await msg.reply("🔍 Searching video...")

    try:
        title, stream = yt_search(query)

        await call.join_group_call(
            msg.chat.id,
            AudioVideoPiped(
                stream,
                HighQualityAudio(),
                HighQualityVideo()
            )
        )

        await wait.edit(f"📺 Playing Video:\n{title}")

    except Exception as e:
        await wait.edit(f"❌ Error:\n{e}")


@app.on_message(filters.command("stop"))
async def stop(_, msg):
    try:
        await call.leave_group_call(msg.chat.id)
        await msg.reply("⏹ Stopped")
    except Exception as e:
        await msg.reply(f"Error: {e}")


# ================= MAIN =================

async def main():
    await app.start()
    await call.start()
    print("Bot Started")
    await idle()
    await app.stop()

import asyncio
asyncio.get_event_loop().run_until_complete(main())
