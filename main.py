import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- SOZLAMALAR ---
TOKEN = "7919865584:AAH3R94oK8H6E_D63eL97N0jH6-o-p7X6_0"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# --- RENDER UCHUN SERVER ---
async def handle(request): return web.Response(text="Bot is running!")
async def run_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

# --- BAZA ---
def init_db():
    conn = sqlite3.connect('films.db')
    conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
    conn.close()

# --- HANDLERLAR ---

# 1. Start komandasi
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring va men sizga videoni topib beraman.")

# 2. Kino yuklash (Faqat siz yuborsangiz saqlaydi)
@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Video qabul qilindi. Endi kodni mana bunday yuboring: `kod:123`")

# 3. Kodni saqlash
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
            del user_data[message.from_user.id]
        else:
            await message.answer("⚠️ Avval videoni yuboring!")
    except Exception as e:
        await message.answer(f"Xato: {e}")

# 4. Kino qidirish (Hech qanday obunasiz)
@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    conn = sqlite3.connect('films.db')
    res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    conn.close()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kino kodi: {message.text}")
    else:
        await message.answer("😔 Kechirasiz, bu kod bilan kino topilmadi.")

async def main():
    init_db()
    asyncio.create_task(run_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
