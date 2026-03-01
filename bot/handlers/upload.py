from telegram import InputMediaPhoto, Update

from bot.charts import elevation_chart, pace_hr_chart
from bot.db import save_activity
from bot.handlers.context import BotCallbackContext
from bot.parsers import SUPPORTED_EXTENSIONS, parse


async def upload(update: Update, context: BotCallbackContext) -> None:
    file_name = update.message.document.file_name
    ext = '.' + file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    if ext not in SUPPORTED_EXTENSIONS:
        allowed = ', '.join(sorted(SUPPORTED_EXTENSIONS))
        await update.message.reply_text(f'Неподдерживаемый формат. Ожидается: {allowed}')
        return

    tg_file = await context.bot.get_file(update.message.document.file_id)
    data = bytes(await tg_file.download_as_bytearray())

    try:
        activity = parse(file_name, data)
    except Exception as e:
        await update.message.reply_text(f'Не удалось разобрать файл: {e}')
        return

    await save_activity(context.bot_data.db, update.effective_user.id, activity)

    parts = [f'Сохранено: {file_name}']
    if activity.recorded_at:
        parts.append(f'Дата: {activity.recorded_at.strftime("%Y-%m-%d %H:%M")}')
    if activity.distance_m:
        parts.append(f'Дистанция: {activity.distance_m / 1000:.2f} км')
    if activity.duration_s:
        m, s = divmod(int(activity.duration_s), 60)
        parts.append(f'Время: {m}:{s:02d}')
    if activity.avg_hr:
        parts.append(f'Пульс: {activity.avg_hr:.0f} уд/мин (макс {activity.max_hr})')
    parts.append(f'Точек: {len(activity.points)}')
    caption = '\n'.join(parts)

    charts = [c for c in (elevation_chart(activity), pace_hr_chart(activity)) if c is not None]

    if len(charts) >= 2:
        media = [InputMediaPhoto(media=charts[0], caption=caption), InputMediaPhoto(media=charts[1])]
        await update.message.reply_media_group(media)
    elif len(charts) == 1:
        await update.message.reply_photo(photo=charts[0], caption=caption)
    else:
        await update.message.reply_text(caption)
