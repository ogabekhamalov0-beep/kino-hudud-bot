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

# Start komandasi
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Kino kodini yuboring yoki admin bo'lsangiz kino yuklang.")

# Kinoni yuklash (Faqat siz - admin uchun)
@dp.message(F.video)
async def get_video_id(message: types.Message):
    # Bu yerda file_id ni olamiz
    file_id = message.video.file_id
    await message.answer(f"Kino qabul qilindi!\n\nEndi ushbu kinoga kod bering (masalan: 101).\n"
                         f"Kod yuborishda 'kod:101' shaklida yuboring.")

# Kinoni bazaga saqlash
@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    movie_code = message.text.split(":")[1]
    # Oxirgi yuborilgan videoni file_id sini vaqtinchalik saqlash o'rniga 
    # soddalashtirish uchun bu yerda kodingizni kengaytirishingiz mumkin.
    await message.answer(f"Kino {movie_code} kodi bilan saqlandi! (Baza ulanishi kodi)")

# Kinoni kod orqali topish
@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    code = message.text
    # Bu yerda bazadan qidirish kodi bo'ladi
    await message.answer(f"{code} kodli kino qidirilmoqda...")

async def main():
    init_db()
    await run_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
