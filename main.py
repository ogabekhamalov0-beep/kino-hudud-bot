import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# --- BAZA BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect('films.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS movies 
                      (file_id TEXT, movie_code TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def add_movie(file_id, code):
    try:
        conn = sqlite3.connect('films.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO movies (file_id, movie_code) VALUES (?, ?)", (file_id, code))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_movie(code):
    conn = sqlite3.connect('films.db')
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM movies WHERE movie_code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# --- RENDER UCHUN SERVER ---
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def run_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- BOT SOZLAMALARI ---
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Vaqtinchalik file_id ni saqlash uchun lug'at
user_data = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(f"Salom! Men kino botman.\nKino olish uchun kodini yuboring.\n\nYaratuvchi: Ogʻabek Hamalov")

# Admin kino yuborganda
@dp.message(F.video)
async def get_video_id(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("Kino qabul qilindi! Endi kodni mana bunday yuboring:\n\n`kod:101` (xuddi shu ko'rinishda)", parse_mode="Markdown")

# Kodni bazaga saqlash
@dp.message(F.text.startswith("kod:"))
async def save_movie_handler(message: types.Message):
    if message.from_user.id not in user_data:
        await message.answer("Avval kino (video) yuboring!")
        return
    
    movie_code = message.text.split(":")[1].strip()
    file_id = user_data[message.from_user.id]
    
    if add_movie(file_id, movie_code):
        await message.answer(f"✅ Tayyor! Kino {movie_code} kodi bilan saqlandi.")
        del user_data[message.from_user.id]
    else:
        await message.answer("Xatolik yuz berdi. Balki bu kod banddir?")

# Kinoni kod orqali olish
@dp.message(F.text.isdigit())
async def send_movie_handler(message: types.Message):
    code = message.text
    file_id = get_movie(code)
    
    if file_id:
        await message.answer_video(video=file_id, caption=f"Mana siz qidirgan kino (Kod: {code})")
    else:
        await message.answer("Afsus, bu kod bilan kino topilmadi. 😔")

async def main():
    init_db()
    await run_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
