import os
import asyncio
import yt_dlp

from pyrogram import Client, filters, idle
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo

# ================= CONFIG =================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================================

app = Client(
    "vc_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call = PyTgCalls(app)

# ================= YT-DLP =================

def search_youtube(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["title"], info["url"]

# ================= COMMANDS =================

@app.on_message(filters.command("start"))
async def start(_, m):
    await m.reply(
        "🎵 VC Bot Ready\n\n"
        "/play song\n"
        "/vplay song\n"
        "/stop"
    )


@app.on_message(filters.command("play"))
async def play(_, m):

    if len(m.command) < 2:
        return await m.reply("Usage: /play song name")

    query = " ".join(m.command[1:])
    msg = await m.reply("🔍 Searching...")

    try:
        title, stream = search_youtube(query)

        await call.join_group_call(
            m.chat.id,
            AudioPiped(stream, HighQualityAudio())
        )

        await msg.edit(f"🎵 Playing Audio:\n{title}")

    except Exception as e:
        await msg.edit(f"Error:\n{e}")


@app.on_message(filters.command("vplay"))
async def vplay(_, m):

    if len(m.command) < 2:
        return await m.reply("Usage: /vplay song name")

    query = " ".join(m.command[1:])
    msg = await m.reply("🔍 Searching Video...")

    try:
        title, stream = search_youtube(query)

        await call.join_group_call(
            m.chat.id,
            AudioVideoPiped(
                stream,
                HighQualityAudio(),
                HighQualityVideo()
            )
        )

        await msg.edit(f"📺 Playing Video:\n{title}")

    except Exception as e:
        await msg.edit(f"Error:\n{e}")


@app.on_message(filters.command("stop"))
async def stop(_, m):
    try:
        await call.leave_group_call(m.chat.id)
        await m.reply("⏹ Stopped")
    except Exception as e:
        await m.reply(str(e))


# ================= MAIN =================

async def main():
    await app.start()
    await call.start()
    print("Bot Running...")
    await idle()
    await app.stop()

asyncio.get_event_loop().run_until_complete(main())
