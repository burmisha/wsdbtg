from typing import Any

from telegram.ext import CallbackContext

from bot.db import BotContext

BotCallbackContext = CallbackContext[Any, Any, Any, BotContext]
