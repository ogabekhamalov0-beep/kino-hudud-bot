import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Loglarni yoqish (xatoni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

# Sizning yangi tokeningiz
TOKEN = "8739101953:AAHPd1mMYLvgul-9KKASbXHcYTcEXXEZUj8"

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# Bazani yaratish
def init_db():
    conn = sqlite3.connect('films.db')
    conn.execute('CREATE TABLE IF NOT EXISTS movies (file_id TEXT, movie_code TEXT UNIQUE)')
    conn.commit()
    conn.close()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring.")

# Video yuklash (Admin uchun)
@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Video qabul qilindi. Endi kodni `kod:123` shaklida yuboring.")

# Kodni saqlash
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
            await message.answer(f"✅ Saqlandi: {code}")
            user_data.pop(message.from_user.id, None)
        else:
            await message.answer("⚠️ Avval videoni yuboring!")
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi.")

# Kino berish (Faqat raqam yozsa)
@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    conn = sqlite3.connect('films.db')
    res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    conn.close()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kod: {message.text}")
    else:
        await message.answer("😔 Kechirasiz, bu kod bilan kino topilmadi.")

async def main():
    init_db()
    # Botni ishga tushirish (polling orqali)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                                   
