from telegram import Update

from bot.db import get_db_stats
from bot.handlers.context import BotCallbackContext


async def dbstats(update: Update, context: BotCallbackContext) -> None:
    if context.bot_data.admin_user_id is None:
        return
    if update.effective_user.id != context.bot_data.admin_user_id:
        return
    stats = await get_db_stats(context.bot_data.db)
    await update.message.reply_text(
        f'БД: {stats["db_size"]}\nАктивностей: {stats["activities"]}\nТочек: {stats["points"]}'
    )
