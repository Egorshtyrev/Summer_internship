import os
from datetime import datetime
from telegram import Update, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TOKEN = "7844049761:AAG5_27DvsUGz26miLyGR29eYEDkfe6Me10"

# Handler for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send me a camera screenshot, and I'll post it with details!")

# Handler for receiving photos
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the photo file
    photo_file = await update.message.photo[-1].get_file()
    
    # Generate a filename with timestamp
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"camera_screenshot_{current_time}.jpg"
    
    # Download the photo
    await photo_file.download_to_drive(filename)
    
    # Extract additional info (e.g., from caption or hardcoded)
    camera_id = "Camera-1"  # Replace with dynamic data if needed
    description = update.message.caption or "No description provided."
    
    # Format the response message
    message = (
        f"🕒 **Time:** `{current_time}`\n"
        f"📷 **Camera:** `{camera_id}`\n"
        f"📝 **Description:** {description}\n"
    )
    
    # Send the image back with details
    with open(filename, 'rb') as photo:
        await update.message.reply_photo(
            photo=InputFile(photo),
            caption=message,
            parse_mode="Markdown"
        )
    
    # Optional: Delete the downloaded file
    os.remove(filename)

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Photo handler (only accepts images)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()