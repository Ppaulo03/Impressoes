import os
import asyncio

from discord import Intents
from discord.ext import commands

import discord
import logging


logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


bot = commands.Bot(command_prefix="/", intents= Intents.all())

try:
    with open('Secrets/token.txt') as file: token = file.read()
    with open('Secrets/guild.txt') as file: guild = file.read()
except FileNotFoundError:
    token = os.environ['TOKEN']
    guild = os.environ['GUILD']

@bot.event
async def on_ready():
    print('Bot ready')
    try:
        synced = await bot.tree.sync(guild = discord.Object(id = int(guild)))
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)


async def load_extensions():
    bot.remove_command("help")
    for filename in os.listdir("./cogs"): 
        if filename.endswith(".py"): await bot.load_extension(f"cogs.{filename[:-3]}")



async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
