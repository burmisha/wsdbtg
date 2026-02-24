import os

# Must be set before bot.main is imported, because Settings() is called at module level.
os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test:token')
os.environ.setdefault('LOGGING_LEVEL', 'INFO')
