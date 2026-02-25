from unittest.mock import AsyncMock, MagicMock

from bot.handlers import echo, help_command, history, start


async def test_start_replies():
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await start(update, MagicMock())

    update.message.reply_text.assert_called_once()


async def test_help_replies():
    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await help_command(update, MagicMock())

    update.message.reply_text.assert_called_once()


async def test_echo_replies_with_same_text():
    update = MagicMock()
    update.message.text = 'hello world'
    update.message.reply_text = AsyncMock()

    db_mock = AsyncMock()
    context = MagicMock()
    context.bot_data = {'db': db_mock}

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
    context.bot_data = {'db': db_mock}

    await history(update, context)

    update.message.reply_text.assert_called_once_with('hello\nworld')


async def test_history_empty():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user.id = 42

    db_mock = AsyncMock()
    db_mock.fetch.return_value = []
    context = MagicMock()
    context.bot_data = {'db': db_mock}

    await history(update, context)

    update.message.reply_text.assert_called_once_with('История пуста')
