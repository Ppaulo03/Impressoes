import os
import discord
from discord.ext import commands
from discord import app_commands

class help_cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.help_message = """
```
Comandos gerais:
help - Mostra os comandos disponiveis

Commandos impressora:
reservar -> inicia processo para reserva de impressora

reservar -h  -> inicia processo para reserva de impressora para o dia atual

remover  -> inicia processo para remoção de reserva de impressora

listar_reservas  -> inicia processo para exibir reservas de até uma semana a partir de dia selecionado

listar_reservas  -h  -> inicia processo para exibir reservas de até uma semana partir do dia atual
```
"""


  @app_commands.command(name="help", description="Mostra os comandos disponiveis")
  async def help(self, interaction: discord.Interaction):
    await interaction.response.send_message(self.help_message, ephemeral=True)


async def setup(bot):
    try:
       with open(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'Secrets/guild.txt'))) as file: guild = file.read()
    except FileNotFoundError:
        guild = os.environ['GUILD']

    await bot.add_cog(help_cog(bot), guilds=[discord.Object(id = int(guild))])