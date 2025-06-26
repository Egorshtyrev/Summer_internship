import os
import asyncio
from datetime import datetime
from telegram import Bot, Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configuration
BOT_TOKEN = "7844049761:AAG5_27DvsUGz26miLyGR29eYEDkfe6Me10"
AUTO_SEND_CHAT_ID = 1124318054  # Where to auto-send the meme
MEME_PATH = r"C:\Users\User\Desktop\Мемы\meme.jpg"

class MemeBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Meme Bot Active! Send me photos or use /sendmeme")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process received photos with timestamps"""
        photo_file = await update.message.photo[-1].get_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"photo_{timestamp.replace(':','-')}.jpg"
        
        await photo_file.download_to_drive(filename)
        
        caption = (
            f"🕒 Time: {timestamp}\n"
            f"📝 Caption: {update.message.caption or 'No description'}"
        )
        
        with open(filename, 'rb') as photo:
            await update.message.reply_photo(
                photo=InputFile(photo),
                caption=caption
            )
        os.remove(filename)

    async def send_initial_meme(self):
        """Auto-send meme on startup"""
        if os.path.exists(MEME_PATH):
            bot = self.app.bot
            with open(MEME_PATH, 'rb') as meme:
                await bot.send_photo(
                    chat_id=AUTO_SEND_CHAT_ID,
                    photo=InputFile(meme),
                    caption=f"🤖 Meme Delivery! 🕒 {datetime.now().strftime('%H:%M:%S')}"
                )

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.send_initial_meme()  # Auto-send meme
        await self.app.updater.start_polling()
        
        # Keep running until stopped
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    bot = MemeBot()
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Bot stopped by user")