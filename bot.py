import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8480096137:AAEG6mLJkerqrDeWIRSXC3C1Bedoo3HjHLk"
ADMIN_ID = 6270874333  # <-- PASTE YOUR TELEGRAM ID HERE

COOLDOWN = 10
DELAY_BETWEEN_CHECKS = 2

last_used = {}

def check_username(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 404:
            return "Available ✅"
        elif response.status_code == 200:
            return "Taken ❌"
        else:
            return "Error ⚠️"
    except:
        return "Failed ⚠️"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Not authorized.")
        return
    await update.message.reply_text("Send up to 20 usernames separated by space.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("Not authorized.")
        return

    if user_id in last_used:
        remaining = COOLDOWN - (asyncio.get_event_loop().time() - last_used[user_id])
        if remaining > 0:
            await update.message.reply_text(f"Wait {int(remaining)} seconds.")
            return

    last_used[user_id] = asyncio.get_event_loop().time()

    usernames = update.message.text.replace(",", " ").split()

    if len(usernames) > 20:
        await update.message.reply_text("Max 20 usernames per request.")
        return

    results = []

    for username in usernames:
        result = check_username(username)
        results.append(f"{username} → {result}")
        await asyncio.sleep(DELAY_BETWEEN_CHECKS)

    await update.message.reply_text("\n".join(results))

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
