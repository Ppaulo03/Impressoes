import os
import asyncio
from discord import Intents
from discord.ext import commands

bot = commands.Bot(command_prefix="!",intents= Intents.all())
with open('token.txt') as tk:
    token = tk.read()

async def load_extensions():
    bot.remove_command("help")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        print('Bot Loaded')
        
        await bot.start(token)

asyncio.run(main())