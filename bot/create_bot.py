import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import settings

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

storage = MemoryStorage()
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=storage)
