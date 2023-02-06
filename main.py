import os
import asyncio
from discord import Intents
from discord.ext import commands


bot = commands.Bot(command_prefix="!",intents= Intents.all())

async def load_extensions():
    bot.remove_command("help")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        print('Bot Loaded')
        await bot.start('ODA4NDYyNDYyODk4Nzk4NjI0.GFx6C2.db-sQfAnqZfE6LOyWm8V3wcwIXbHA49SYfu2NY')

asyncio.run(main())