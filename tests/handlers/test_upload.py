from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from bot.db import BotContext
from bot.handlers.upload import upload
from bot.models import Activity


async def test_upload_rejects_unknown_extension():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.document.file_name = 'report.pdf'

    await upload(update, MagicMock())

    assert 'Неподдерживаемый формат' in update.message.reply_text.call_args[0][0]


async def test_upload_rejects_no_extension():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.document.file_name = 'activity'

    await upload(update, MagicMock())

    assert 'Неподдерживаемый формат' in update.message.reply_text.call_args[0][0]


async def test_upload_parses_and_saves():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.document.file_name = 'activity.fit'
    update.message.document.file_id = 'file123'
    update.effective_user.id = 42

    tg_file = AsyncMock()
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b'data'))

    context = MagicMock()
    context.bot_data = BotContext(db=AsyncMock())
    context.bot.get_file = AsyncMock(return_value=tg_file)

    mock_activity = Activity(
        filename='activity.fit',
        recorded_at=datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc),
        distance_m=10000.0,
        source_distance_m=10200.0,
        duration_s=3600.0,
        avg_hr=148.0,
        max_hr=165,
        points=[],
    )

    with patch('bot.handlers.upload.parse', return_value=mock_activity), \
         patch('bot.handlers.upload.save_activity', new_callable=AsyncMock) as mock_save:
        await upload(update, context)

    mock_save.assert_called_once()
    reply = update.message.reply_text.call_args[0][0]
    assert 'activity.fit' in reply
    assert '10.00 км' in reply
    assert '60:00' in reply
    assert '148' in reply


async def test_upload_replies_on_parse_error():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.document.file_name = 'activity.gpx'
    update.message.document.file_id = 'file123'

    tg_file = AsyncMock()
    tg_file.download_as_bytearray = AsyncMock(return_value=bytearray(b'bad data'))

    context = MagicMock()
    context.bot_data = BotContext(db=AsyncMock())
    context.bot.get_file = AsyncMock(return_value=tg_file)

    with patch('bot.handlers.upload.parse', side_effect=ValueError('bad xml')):
        await upload(update, context)

    assert 'Не удалось разобрать' in update.message.reply_text.call_args[0][0]
