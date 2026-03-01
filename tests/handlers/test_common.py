from unittest.mock import AsyncMock, MagicMock

from bot.handlers.common import help_command, start


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
