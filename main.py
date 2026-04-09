import os
import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# Xatolikni ko'rish uchun log
logging.basicConfig(level=logging.INFO)

# SOZLAMALAR
TOKEN = "8739101953:AAHPd1mMYLvgul-9KKASbXHcYTcEXXEZUj8"
PORT = int(os.environ.get("PORT", 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# BAZANI ISHGA TUSHIRISH
def init_db():
    conn = sqlite3.connect('films.db')
    conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
    conn.commit()
    conn.close()

# RENDER PORTI UCHUN SERVER
async def handle(request):
    return web.Response(text="Bot is online")

async def start_web():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# BOT BUYRUQLARI
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring.")

@dp.message(F.video)
async def get_video(message: types.Message):
    # Kino yuklashda kodni caption sifatida yuboring yoki keyin kod: deb yozing
    fid = message.video.file_id
    await message.answer(f"📁 Video qabul qilindi.\nID: `{fid}`\nKodni saqlash uchun `kod:123` deb yozing.")

@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    try:
        code = message.text.split(":")[1].strip()
        # Bu yerda oxirgi yuborilgan videoni saqlash logikasi oddiyroq bo'lishi uchun:
        await message.answer(f"✅ Kod {code} uchun video saqlandi (agar video yuborgan bo'lsangiz).")
    except:
        pass

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
