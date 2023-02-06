import discord
import datetime
from discord.ext import commands
from dateutil.parser import parse

class impressora_cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.channel_name = 'impressões'
		self.wrong_channel_msg = f'Please, use this command in the {self.channel_name} channel'
		self.last_msg = ''
		self.last_user = None

	@commands.command(name = "reservar", alias='p')
	async def ping(self, ctx):

		
		if ctx.channel.name == self.channel_name:
			user = ctx.author 
			channel = ctx.channel
			response = ''

			page = discord.Embed(title=f"Reserva de Impressoras", description= 'Prencha a data que deseja reservar:\n dd/mm/aa\n ex: 07/10/23')
			last_msg = await ctx.send(embed = page)

						
			def check(m):
				return m.channel == channel and m.author == user
			
			while True:
				msg = await self.bot.wait_for('message', check=check)
				try: 
					date = parse(msg.content, fuzzy=False)
					page.description = msg.content

					print(date)
					response += "Data: msg.content\n"
					await last_msg.edit(embed=page)
					await msg.delete()
					break

				except ValueError:
					page.description = 'Formato inválido\nPrencha a data que deseja reservar:\n dd/mm/aa\n ex: 07/10/23'
					await last_msg.edit(embed=page)
					await msg.delete()

			page.description = 'Formato inválido\nPrencha por quantas horas deseja reservar'
			await last_msg.edit(embed=page)

			while True:
				msg = await self.bot.wait_for('message', check=check)
				try: 
					time = int(msg.content)
					response += 
					page.description = msg.content
					await last_msg.edit(embed=page)
					await msg.delete()
					break

				except ValueError:
					page.description = 'Formato inválido\nPrencha por quantas horas deseja reservar'
					await last_msg.edit(embed=page)
					await msg.delete()
					
		else: await ctx.send(self.wrong_channel_msg)



	
	@commands.command(name="mude")
	async def mude(self, ctx):
		if ctx.channel.name == self.channel_name:  
			if ctx.author == self.last_user: await self.last_msg.edit(content="ping")
		else: await ctx.send(self.wrong_channel_msg)

async def setup(bot):
    await bot.add_cog(impressora_cog(bot))
