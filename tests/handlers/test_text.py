from unittest.mock import AsyncMock, MagicMock

from bot.db import BotContext
from bot.handlers.text import echo, history


async def test_echo_replies_with_same_text():
    update = MagicMock()
    update.message.text = 'hello world'
    update.message.reply_text = AsyncMock()

    db_mock = AsyncMock()
    context = MagicMock()
    context.bot_data = BotContext(db=db_mock)

    await echo(update, context)

    update.message.reply_text.assert_called_once_with('hello world')
    db_mock.execute.assert_called_once()


async def test_history_shows_prefixes():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 42

    db_mock = AsyncMock()
    db_mock.fetch.return_value = [{'prefix': 'hello'}, {'prefix': 'world'}]
    context = MagicMock()
    context.bot_data = BotContext(db=db_mock)

    await history(update, context)

    update.message.reply_text.assert_called_once_with('hello\nworld')


async def test_history_empty():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 42

    db_mock = AsyncMock()
    db_mock.fetch.return_value = []
    context = MagicMock()
    context.bot_data = BotContext(db=db_mock)

    await history(update, context)

    update.message.reply_text.assert_called_once_with('История пуста')
