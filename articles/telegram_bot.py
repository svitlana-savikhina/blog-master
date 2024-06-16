import os
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I'm a blog bot. To find out the available commands, type /help."
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "List of available commands:\n/start - greeting\n/help - list of commands\n/latest - latest blog article"
    )


async def send_notification_to_telegram(title, content):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"New article: {title}\n\n{content}",
            },
        ) as response:
            if response.status != 200:
                print("Failed to send notification to Telegram.")


async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8001/api/latest/") as response:
            if response.status == 200:
                data = await response.json()
                article_title = data.get("title")
                article_content = data.get("content")
                message = f"Latest Article:\n\nTitle: {article_title}\n\nContent: {article_content}"
            else:
                message = "No articles found or an error occurred."

            await update.message.reply_text(message)


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("latest", latest))

    application.run_polling()


if __name__ == "__main__":
    main()
