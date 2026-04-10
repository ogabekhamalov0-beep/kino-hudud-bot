import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- SOZLAMALAR ---
# Sizning yangi tokeningiz joylandi
TOKEN = "8739101953:AAHPd1mMYLvgul-9KKASbXHcYTcEXXEZUj8"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# --- RENDER UCHUN SERVER ---
async def handle(request): 
    return web.Response(text="Bot is running!")

async def run_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- BAZA ---
def init_db():
    conn = sqlite3.connect('films.db')
    conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
    conn.commit()
    conn.close()

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Men kino qidiruv botiman. Kino olish uchun uning kodini yuboring.")

@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Kino qabul qilindi! Endi kodni `kod:123` shaklida yuboring.")

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
            await message.answer(f"✅ Saqlandi! Kino kodi: {code}")
            del user_data[message.from_user.id]
        else:
            await message.answer("⚠️ Avval videoni yuboring!")
    except:
        await message.answer("❌ Xato! `kod:123` shaklida yuboring.")

@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    conn = sqlite3.connect('films.db')
    res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    conn.close()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kino kodi: {message.text}")
    else:
        await message.answer("😔 Bunday kodli kino hali bazaga qo'shilmagan.")

async def main():
    init_db()
    # Render'da "No open ports" xatosini oldini olish uchun
    asyncio.create_task(run_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
