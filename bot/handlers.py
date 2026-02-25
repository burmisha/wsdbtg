from telegram import Update
from telegram.ext import ContextTypes

from bot.db import get_history, save_message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я эхо.\nНапиши мне что-нибудь — я повторю.\n\n/help — список команд')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('/start — приветствие\n/help — эта справка')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)
    await save_message(context.bot_data.db, update.effective_user.id, update.message.text)


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefixes = await get_history(context.bot_data.db, update.effective_user.id)
    if prefixes:
        await update.message.reply_text('\n'.join(prefixes))
    else:
        await update.message.reply_text('История пуста')
