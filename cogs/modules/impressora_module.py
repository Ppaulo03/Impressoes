import discord
import asyncio
from discord.ext import commands
from cogs.modules.calendario import *
from cogs.modules.date import *


class impressora_cog_module(commands.Cog):

	
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.channel_name = 'impressões'
		self.wrong_channel_msg = f'Please, use this command in the {self.channel_name} channel'
		self.disponivel = True
		self.last_message = None
		
    
	@commands.Cog.listener()
	async def on_message_delete(self, msg):
		if not self.disponivel and msg == self.last_message:
			self.disponivel = True
			

	async def send_dm(self, user: discord.User, msg):
		await self.bot.get_user(int(user)).send(msg)


	async def get_disponivel(self, interaction, need_printer = True):
		if not self.disponivel: 
			await interaction.response.send_message(content='Estou ocupado, por favor aguarde', ephemeral=True)
			return False
			
		if interaction.channel.name != self.channel_name:
			await interaction.response.send_message(content='Para realizar reservas use o canal impressões', ephemeral=True)
			return False
		
		if need_printer and len(impressoras) <= 0:
			await interaction.response.send_message("Não há impressoras disponíveis",  ephemeral=True)
			return False
		return True


	async def get_responce(self, channel, user, last_msg, action, need_number = True):
		def check(m):
			return m.channel == channel and m.author == user
		
		while True:
			try:	
				msg = await self.bot.wait_for('message', check=check, timeout=60.0)
				
				if msg.content == 'quit':
					self.disponivel = True
					await msg.delete()
					await last_msg.delete()
					return None
				
				elif msg.content == 'back':
					await msg.delete()
					return 'back'
			
				if need_number:
					if msg.content.isdigit(): flag_good = action(msg)
					else: flag_good = False		
				else: flag_good = action(msg)
							
				await msg.delete()
				if flag_good: return msg.content

			except asyncio.TimeoutError:
				self.disponivel = True
				await last_msg.delete()
				return None


	async def choose_month(self, message, page, channel, user):
		description =  '```python\nEscolha o mês (1-12)\n\n' + get_calendar_months()  + '```'
		
		page.description = description
		await message.edit(embed = page)


		def check_get_mes(msg):
			return int(msg.content) <= 12 and int(msg.content) > 0

		choosed_moonth = await self.get_responce(channel, user, message, check_get_mes)
		if choosed_moonth is None: return None
		elif choosed_moonth == 'back': return 'back'
		return int(choosed_moonth)
	

	async def choose_day(self, message, page, channel, user, choosed_month, choosed_year):

		month_calendar = get_calendar_days(choosed_month, choosed_year)
		description =  '```python\nEscolha a data\n\n' + month_calendar + '```'
		today_day, today_month, _ = get_day_month_year()
		last_day_month = get_last_day_month(choosed_month, choosed_year)

		page.description = description
		await message.edit(embed = page)

		def check_get_dia(msg):
			if today_month == choosed_month:
				return int(msg.content) <= last_day_month and int(msg.content) >= today_day
			else: return int(msg.content) <= last_day_month and int(msg.content) > 0

		choosed_day = await self.get_responce(channel, user, message, check_get_dia)
		if choosed_day is None: return
		elif choosed_day == 'back': return 'back'
		return int(choosed_day)


	async def choose_impresora(self, message, page, channel, user):
		description =  '```python\nEscolha a impressora\n\n'
		for idx, i in enumerate(impressoras):
			description += f'{i.name} -> {idx}\n'
		description += '```'

		page.description = description
		await message.edit(embed = page)

		def check_get_impressora(msg):
			return int(msg.content) < len(impressoras) and int(msg.content) >= 0

		impressora = await self.get_responce(channel, user, message, check_get_impressora)
		if impressora is None: return
		elif impressora == 'back': return 'back'
		return impressoras[int(impressora)]


	async def choose_time_length(self, message, page, channel, user):
		description =  '```python\nTempo de impressão\n\nMínimo - 1 hora\nMáximo - 50 horas```'
		
		page.description = description
		await message.edit(embed = page)

		def check_get_tempo(msg):
			return int(msg.content) <= 50 and int(msg.content) > 0

		tempo = await self.get_responce(channel, user, message, check_get_tempo)
		if tempo is None: return
		elif tempo == 'back': return 'back'
		return int(tempo)


	async def get_horarios(self, message, page, day, month, year, printer, num_dias):
		description =  '```python\nSelecione o horário\n\n'

		idx = True
		for i in range(num_dias + 1):

			if idx: description += f'Dia {day} / {month} / {year}\n'
			else: description += f'Dia {day} / {month} / {year} - consulta\n'
			
			description += check_day(day, month, year, printer, idx)
			description += '\n'

			idx = False
			day, month, year = next_day(day, month, year)
		description += '```'
		
		page.description = description
		await message.edit(embed = page)


	async def get_reserva_start(self, message, page, channel, user, day, month, year, printer, time_length):
		
		num_dias = int(time_length / 24)
		if time_length % 24 != 0: num_dias += 1
		await self.get_horarios(message, page, day, month, year, printer, num_dias)
		
		def check_get_inicio(msg):
			return int(msg.content) < 24 and int(msg.content) >= 0

		while True:
			inicio = await self.get_responce(channel, user, message, check_get_inicio)
			if inicio is None: return
			elif inicio == 'back': return 'back'
			inicio = int(inicio)

			inicio_t = inicio; flag_conflito = False
			for i in range(num_dias + 1):

				day_calendar = get_day(day, month, year)
				day, month, year = next_day(day, month, year)
				if printer.name not in list(day_calendar.reservations.keys()): continue

				reservas_impressora = list(day_calendar.reservations[printer.name].keys())
				while inicio_t < 24:
					if inicio_t in reservas_impressora:
						description = "Horario escolhido indisponivel\n" + description
						page.description = description
						flag_conflito = True
						break

					inicio_t += 1; time_length -= 1
					if time_length == 0: break

				inicio_t = 0
				if time_length == 0: break

			if not flag_conflito: return inicio
			await message.edit(embed = page)


	async def get_remove_reserva(self, message, page, channel, user, day, month, year, printer):
		
		await self.get_horarios(message, page, day, month, year, printer, 0)

		def check_get_inicio(msg):
			if int(msg.content) >= 24 and int(msg.content) < 0: return False
			day_calendar = get_day(day, month, year)
			if printer.name not in list(day_calendar.reservations.keys()): return False
			if int(msg.content) not in day_calendar.reservations[printer.name].keys(): return False
			return day_calendar.reservations[printer.name][int(msg.content)][1] == user.id
		
		inicio = await self.get_responce(channel, user, message, check_get_inicio)
		if inicio is None: return None
		elif inicio == 'back': return 'back'
		return int(inicio)
	
