from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.logging import get_logger, setup_logging
from bot.settings import Settings

settings = Settings()
setup_logging(settings.logging_level)
logger = get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я эхо-бот.\n'
        'Напиши мне что-нибудь — я повторю.\n\n'
        '/help — список команд'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('/start — приветствие\n/help — эта справка')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def main() -> None:
    token = settings.telegram_bot_token.get_secret_value()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info('Bot started')
    app.run_polling()


if __name__ == '__main__':
    main()
