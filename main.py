import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- SOZLAMALAR ---
# Yangi tokeningiz joylashtirildi
TOKEN = "8739101953:AAHPd1mMYLvgul-9KKASbXHcYTcEXXEZUj8"
PORT = int(os.environ.get("PORT", 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# --- BAZA ---
def init_db():
    with sqlite3.connect('films.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
        conn.commit()

# --- SERVER (Render ishlashi uchun) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webhook():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring.")

# Kino yuklash
@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Video qabul qilindi. Kodni `kod:123` shaklida yuboring.")

# Kodni bazaga saqlash
@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    try:
        code = message.text.split(":")[1].strip()
        file_id = user_data.get(message.from_user.id)
        if file_id:
            with sqlite3.connect('films.db') as conn:
                conn.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (file_id, code))
                conn.commit()
            await message.answer(f"✅ Saqlandi! Kod: {code}")
            if message.from_user.id in user_data:
                del user_data[message.from_user.id]
        else:
            await message.answer("⚠️ Avval videoni yuboring!")
    except Exception:
        await message.answer("❌ Format xato. Misol: `kod:123`")

# Kino qidirish
@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    with sqlite3.connect('films.db') as conn:
        res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kod: {message.text}")
    else:
        await message.answer("😔 Bu kod bilan kino topilmadi.")

async def main():
    init_db()
    asyncio.create_task(start_webhook())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
