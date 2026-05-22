import os
import sqlite3
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("8633828298:AAGK8C8Vp82FLxrsNGWfTEZy8zI3pJy05YQ")

conn = sqlite3.connect("db.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, bal INTEGER DEFAULT 0, last INTEGER DEFAULT 0)")
conn.commit()

def get_user(uid):
    cur.execute("SELECT * FROM users WHERE id=?", (uid,))
    u = cur.fetchone()
    if not u:
        cur.execute("INSERT INTO users VALUES (?,0,0)", (uid,))
        conn.commit()
        return get_user(uid)
    return u

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Баланс", callback_data="bal")],
        [InlineKeyboardButton("🎮 Фарм", callback_data="farm")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text("🚀 BOT ONLINE 24/7", reply_markup=menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid, bal, last = get_user(q.from_user.id)
    now = int(time.time())

    if q.data == "farm":
        if now - last < 86400:
            await q.answer("⏳ вже фармив", show_alert=True)
            return
        earn = random.randint(5, 20)
        cur.execute("UPDATE users SET bal=?, last=? WHERE id=?", (bal+earn, now, uid))
        conn.commit()
        await q.edit_message_text(f"+{earn} gold | {bal+earn}", reply_markup=menu())

    if q.data == "bal":
        await q.edit_message_text(f"💰 Баланс: {bal}", reply_markup=menu())

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("RUNNING 24/7 BOT")
app.run_polling()
