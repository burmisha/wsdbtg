from unittest.mock import AsyncMock, MagicMock

from bot.db import BotContext
from bot.handlers.admin import dbstats


async def test_dbstats_replies_to_admin():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 42

    db_mock = AsyncMock()
    db_mock.fetchrow.return_value = {'db_size': '8192 bytes', 'activities': 3, 'points': 150}
    context = MagicMock()
    context.bot_data = BotContext(db=db_mock, admin_user_id=42)

    await dbstats(update, context)

    update.message.reply_text.assert_called_once()
    reply = update.message.reply_text.call_args[0][0]
    assert '8192 bytes' in reply
    assert '3' in reply
    assert '150' in reply


async def test_dbstats_ignores_non_admin():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 99

    context = MagicMock()
    context.bot_data = BotContext(db=AsyncMock(), admin_user_id=42)

    await dbstats(update, context)

    update.message.reply_text.assert_not_called()


async def test_dbstats_ignores_when_no_admin_set():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 42

    context = MagicMock()
    context.bot_data = BotContext(db=AsyncMock(), admin_user_id=None)

    await dbstats(update, context)

    update.message.reply_text.assert_not_called()
