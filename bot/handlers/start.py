from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters.state import State, StatesGroup

from bot.utils.parser import read_excel_file, Parser
from bot.create_bot import bot
from bot.config import settings


start_router = Router()



@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer("Приложите файл excel")


@start_router.message(
    F.document &
    F.document.file_name.endswith('.xlsx')
)
async def download_file_handler(message: Message):
    document = message.document
    file = await bot.get_file(document.file_id)
    file_path = file.file_path
    local_file_path = settings.DOWNLOAD_DIR + f"/{document.file_name}"
    await bot.download_file(file_path, local_file_path)
    with open(local_file_path, "br") as download_file:
        df = read_excel_file(download_file)
    parser = Parser(message.from_user.id)
    results = await parser.parse_df(df, save_db=True)
    await message.answer("Данные успешно собраны и записаны в БД")
    result_message = '\n'.join([str(i) for i in results])
    await message.answer(f"Результаты:\n\n"
                         f"{result_message}")
