from discord.ext import commands

class help_cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.text_channel_list = []
    self.help_message = """
```
Comandos gerais:
!help(h) - Mostra os comandos disponiveis

Commandos impressora:
!reservar(r) -> inicia processo para reserva de impressora

!reservar(r) -h  -> inicia processo para reserva de impressora para o dia atual

!remover(rm)  -> inicia processo para remoção de reserva de impressora

!listar_reservas(lr)  -> inicia processo para exibir reservas de até uma semana a partir de dia selecionado

!listar_reservas(lr)  -h  -> inicia processo para exibir reservas de até uma semana partir do dia atual
```
"""

  @commands.Cog.listener()
  async def on_ready(self):
    print('Bot ready')
    for guild in self.bot.guilds:
      for channel in guild.text_channels:
        self.text_channel_list.append(channel)     

  @commands.command(name="help",aliases=["h"], help="Mostra os comandos disponiveis")
  async def help(self, ctx):
    await ctx.send(self.help_message)

  async def send_to_all(self, msg):
    for text_channel in self.text_channel_list:
      await text_channel.send(msg)

async def setup(bot):
    await bot.add_cog(help_cog(bot))