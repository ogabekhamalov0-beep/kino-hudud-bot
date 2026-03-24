import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# Render uchun soxta server (Port xatosini oldini olish uchun)
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

# Tokenni Render Variables-dan oladi
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Salom! Bu yangi bot. Yaratuvchi: Ogʻabek Hamalov")

async def main():
    await run_server() 
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
