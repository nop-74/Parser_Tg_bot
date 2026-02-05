import asyncio
from aiogram.types import BotCommand
from aiogram.types import BotCommandScopeDefault

from bot.create_bot import bot, dp
from bot.handlers.start import start_router

async def set_commands():
    commands = [
        BotCommand(command="start", description="Старт"),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main():
    dp.include_routers(
        start_router,
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
