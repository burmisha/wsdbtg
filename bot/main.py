from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from bot.db import BotContext, create_pool
from bot.handlers.admin import dbstats
from bot.handlers.common import help_command, start
from bot.handlers.text import echo, history
from bot.handlers.upload import upload
from bot.logging import get_logger, setup_logging
from bot.settings import Settings

settings = Settings()
setup_logging(settings.logging_level)
logger = get_logger(__name__)


async def post_init(application: Application) -> None:
    application.bot_data = BotContext(
        db=await create_pool(settings.database_url),
        admin_user_id=settings.admin_user_id,
    )


async def post_shutdown(application: Application) -> None:
    await application.bot_data.db.close()


def main() -> None:
    token = settings.telegram_bot_token.get_secret_value()
    context_types = ContextTypes(bot_data=BotContext)
    app = (
        Application.builder()
        .token(token)
        .context_types(context_types)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    app.add_handler(CommandHandler('dbstats', dbstats))
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('history', history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.Document.ALL, upload))

    logger.info('Bot started')
    app.run_polling()


if __name__ == '__main__':
    main()
