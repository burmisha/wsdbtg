from unittest.mock import AsyncMock, MagicMock

from bot.main import echo, help_command, start


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

    await echo(update, MagicMock())

    update.message.reply_text.assert_called_once_with('hello world')
