import os
import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# Loglarni ko'rish (xatoni aniqlash uchun)
logging.basicConfig(level=logging.INFO)

# --- SOZLAMALAR ---
TOKEN = "8739101953:AAHPd1mMYLvgul-9KKASbXHcYTcEXXEZUj8"
PORT = int(os.environ.get("PORT", 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# --- BAZANI TEKSHIRISH ---
def init_db():
    conn = sqlite3.connect('films.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
    conn.commit()
    conn.close()

# --- WEB SERVER (Render talabi) ---
async def handle(request):
    return web.Response(text="Bot is online!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# --- BOT LOGIKASI ---

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring.")

@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Video olindi! Endi kodni yozing (Masalan: kod:123)")

@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    try:
        code = message.text.split(":")[1].strip()
        file_id = user_data.get(message.from_user.id)
        if file_id:
            conn = sqlite3.connect('films.db')
            conn.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (file_id, code))
            conn.commit()
            conn.close()
            await message.answer(f"✅ Saqlandi! Kod: {code}")
            user_data.pop(message.from_user.id, None)
        else:
            await message.answer("⚠️ Avval videoni yuboring!")
    except:
        await message.answer("❌ Xato! Kodni `kod:123` shaklida yozing.")

@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    conn = sqlite3.connect('films.db')
    res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    conn.close()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kod: {message.text}")
    else:
        await message.answer("😔 Bu kod bilan kino topilmadi.")

async def main():
    init_db()
    # Web serverni fonda ishga tushirish
    asyncio.create_task(start_server())
    # Pollingni boshlash
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
        
