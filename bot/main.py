from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers import echo, help_command, start
from bot.logging import get_logger, setup_logging
from bot.settings import Settings

settings = Settings()
setup_logging(settings.logging_level)
logger = get_logger(__name__)


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
