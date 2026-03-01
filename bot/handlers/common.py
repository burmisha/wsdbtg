from telegram import Update

from bot.handlers.context import BotCallbackContext


async def start(update: Update, context: BotCallbackContext) -> None:
    await update.message.reply_text('Привет! Я эхо.\nНапиши мне что-нибудь — я повторю.\n\n/help — список команд')


async def help_command(update: Update, context: BotCallbackContext) -> None:
    await update.message.reply_text('/start — приветствие\n/help — эта справка')
