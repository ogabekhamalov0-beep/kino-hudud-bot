import os
import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# Xatolarni logda ko'rish
logging.basicConfig(level=logging.INFO)

TOKEN = "8739101953:AAHPd1mMYLvgul-9KKASbXHcYTcEXXEZUj8"
PORT = int(os.environ.get("PORT", 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

def init_db():
    conn = sqlite3.connect('films.db')
    conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
    conn.commit()
    conn.close()

# Render o'chirib yubormasligi uchun kichik server
async def handle(request):
    return web.Response(text="Bot is running")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring.")

@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Video olindi. Kodni `kod:123` deb yozing.")

@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    code = message.text.split(":")[1].strip()
    f_id = user_data.get(message.from_user.id)
    if f_id:
        conn = sqlite3.connect('films.db')
        conn.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (f_id, code))
        conn.commit()
        conn.close()
        await message.answer(f"✅ Saqlandi: {code}")
        user_data.pop(message.from_user.id, None)

@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    conn = sqlite3.connect('films.db')
    res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    conn.close()
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kod: {message.text}")
    else:
        await message.answer("😔 Topilmadi.")

async def main():
    init_db()
    asyncio.create_task(start_web())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
