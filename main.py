import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- SOZLAMALAR ---
TOKEN = "7919865584:AAH3R94oK8H6E_D63eL97N0jH6-o-p7X6_0"
PORT = int(os.environ.get("PORT", 8080)) # Render beradigan port

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# --- BAZA ---
def init_db():
    with sqlite3.connect('films.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
        conn.commit()

# --- SERVER (Render uchun majburiy) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webhook():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Server {PORT} portida ishga tushdi")

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring.")

@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Video qabul qilindi. Kodni yuboring (Masalan: `kod:123`)")

@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    code = message.text.split(":")[1].strip()
    file_id = user_data.get(message.from_user.id)
    if file_id:
        with sqlite3.connect('films.db') as conn:
            conn.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (file_id, code))
            conn.commit()
        await message.answer(f"✅ Saqlandi! Kod: {code}")
        del user_data[message.from_user.id]

@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    with sqlite3.connect('films.db') as conn:
        res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kod: {message.text}")
    else:
        await message.answer("😔 Topilmadi.")

async def main():
    init_db()
    # Web serverni fonda ishga tushirish
    loop = asyncio.get_event_loop()
    loop.create_task(start_webhook())
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
