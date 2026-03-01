from telegram import Update

from bot.db import get_history, save_message
from bot.handlers.context import BotCallbackContext


async def echo(update: Update, context: BotCallbackContext) -> None:
    await update.message.reply_text(update.message.text)
    await save_message(context.bot_data.db, update.effective_user.id, update.message.text)


async def history(update: Update, context: BotCallbackContext) -> None:
    prefixes = await get_history(context.bot_data.db, update.effective_user.id)
    if prefixes:
        await update.message.reply_text('\n'.join(prefixes))
    else:
        await update.message.reply_text('История пуста')
