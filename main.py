import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- SOZLAMALAR ---
TOKEN = os.getenv("BOT_TOKEN")

# Kanallar ID ro'yxati
CHANNELS = ["-1003830955697", "-1003780100726", "-1003739050214"]

# Tugmalar uchun linklar
CHANNEL_LINKS = [
    ["📢 Kanal 1", "https://t.me/o_hamalov"],
    ["📢 Kanal 2", "https://t.me/kanal123b"],
    ["🔐 Kanal 3 (Maxfiy)", "https://t.me/+XekuwXtOBUdhY2I6"]
]

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_data = {}

# --- OBUNANI TEKSHIRISH FUNKSIYASI ---
async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

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

# 1. Start komandasi (Ism olib tashlandi)
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🎬 Salom! Men kino qidiruv botiman. Kino olish uchun uning kodini yuboring.")

# 2. Avtomatik a'zolikni tasdiqlash
@dp.chat_join_request()
async def auto_approve(chat_join_request: types.ChatJoinRequest):
    await chat_join_request.approve()
    try:
        await bot.send_message(
            chat_id=chat_join_request.from_user.id, 
            text="✅ Kanallarga a'zo bo'lganingiz tasdiqlandi! Endi botga qaytib kino kodini yuborishingiz mumkin."
        )
    except:
        pass

# 3. Kino yuklash
@dp.message(F.video)
async def get_video(message: types.Message):
    user_data[message.from_user.id] = message.video.file_id
    await message.answer("📁 Kino qabul qilindi! Endi kodni `kod:123` shaklida yuboring.")

# 4. Kodni saqlash
@dp.message(F.text.startswith("kod:"))
async def save_movie(message: types.Message):
    code = message.text.split(":")[1].strip()
    file_id = user_data.get(message.from_user.id)
    if file_id:
        conn = sqlite3.connect('films.db')
        conn.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (file_id, code))
        conn.commit()
        conn.close()
        await message.answer(f"✅ Saqlandi! Kino kodi: {code}")
        del user_data[message.from_user.id]

# 5. Kino qidirish (Majburiy obuna bilan)
@dp.message(F.text.isdigit())
async def send_movie(message: types.Message):
    is_subscribed = await check_sub(message.from_user.id)
    
    if not is_subscribed:
        keyboard_buttons = []
        for name, link in CHANNEL_LINKS:
            keyboard_buttons.append([InlineKeyboardButton(text=name, url=link)])
        
        keyboard_buttons.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check")])
        btn = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(
            "⚠️ **Kino ko'rish uchun avval kanallarimizga a'zo bo'lishingiz kerak!**", 
            reply_markup=btn,
            parse_mode="Markdown"
        )
        return

    conn = sqlite3.connect('films.db')
    res = conn.execute("SELECT file_id FROM movies WHERE movie_code = ?", (message.text,)).fetchone()
    conn.close()
    
    if res:
        await message.answer_video(video=res[0], caption=f"🍿 Kino kodi: {message.text}")
    else:
        await message.answer("😔 Bunday kodli kino hali bazaga qo'shilmagan.")

# 6. Callback
@dp.callback_query(F.data == "check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Endi kino kodini yuboravering.")
    else:
        await call.answer("❌ Hali hamma kanallarga a'zo bo'lmadingiz!", show_alert=True)

async def main():
    init_db()
    await run_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
