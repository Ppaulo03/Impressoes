import discord
import datetime
import asyncio
from discord.ext import commands
from cogs.modules.calendario import *
from cogs.modules.date import *


class impressora_cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.channel_name = 'impressões'
		self.wrong_channel_msg = f'Please, use this command in the {self.channel_name} channel'
		self.disponivel = True


	async def send_dm(self, user: discord.User, msg):
		user = self.bot.get_user(int(user))
		await user.send(msg)


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
			
			return day_calendar.reservations[printer.name][int(msg.content)][1] == user.id

		
		inicio = await self.get_responce(channel, user, message, check_get_inicio)
		if inicio is None: return None
		elif inicio == 'back': return 'back'
		return int(inicio)


# __________________________________Comandos________________________________________________________________

	@commands.command(name = "reservar")
	async def reservar(self, ctx):
		await ctx.message.delete()

		if not self.disponivel: return
		if ctx.channel.name != self.channel_name: return
		if len(impressoras) <= 0:
			await ctx.send("Não há impressoras disponíveis")
			return
		
		self.disponivel = False
		user = ctx.author ; channel = ctx.channel
		_, today_month, today_year = get_day_month_year()

		page = discord.Embed(title=f"Reserva de Impressoras", color=0xffff00)
		last_msg = await ctx.send(embed = page)

		estado = 0
		while True:

			if estado == 0: #Mês
				choosed_month = await self.choose_month(last_msg, page, channel, user)
				if choosed_month is None: return
				elif choosed_month == 'back': continue
				choosed_year = today_year if choosed_month >= today_month else today_year + 1
				estado = 1

			elif estado == 1: #Dia
				choosed_day = await self.choose_day(last_msg, page, channel, user, choosed_month, choosed_year)
				if choosed_day is None: return
				elif choosed_day == 'back': estado -= 1
				else: estado += 1
			
			elif estado == 2: #Impressora
				choosed_printer = await self.choose_impresora(last_msg, page, channel, user)
				if choosed_printer is None: return
				elif choosed_printer == 'back': estado -= 1
				else: estado += 1
			
			elif estado == 3: #Tempo
				time_length = await self.choose_time_length(last_msg, page, channel, user)
				if time_length is None: return
				elif time_length == 'back': estado -= 1
				else: estado += 1
			
			elif estado == 4: #Inicio
				inicio = await self.get_reserva_start(last_msg, page, channel, user, choosed_day, choosed_month, choosed_year, choosed_printer, time_length)
				if inicio is None: return
				elif inicio == 'back': estado -= 1
				else: break

#_________________________________________________Realiza reserva________________________________________________
		confirmation_str = f"Impressora {choosed_printer.name} reservada para o dia {choosed_day}/{choosed_month}, a partir das {inicio}h por {time_length}h"
		while True:
			if inicio + time_length >= 24: tempo_ef = 23
			else: tempo_ef = inicio + time_length
			time_length -= tempo_ef - inicio

			add_reserva(choosed_day, choosed_month, choosed_year, choosed_printer,inicio,tempo_ef , [user.name, user.id])
			if time_length == 0:break
				
			inicio = 0
			choosed_day, choosed_month, choosed_year = next_day(choosed_day, choosed_month, choosed_year)


		await self.send_dm(user.id, confirmation_str)
		self.disponivel = True
		await last_msg.delete()
		return
		
		
	@commands.command(name = "remover")
	async def remover(self, ctx):
		await ctx.message.delete()

		if not self.disponivel: return
		if ctx.channel.name != self.channel_name: return
		if len(impressoras) <= 0:
			await ctx.send("Não há impressoras disponíveis")
			return
		
		self.disponivel = False
		user = ctx.author ; channel = ctx.channel
		_, today_month, today_year = get_day_month_year()

		page = discord.Embed(title=f"Remover Reserva", color=0xffff00)
		last_msg = await ctx.send(embed = page)

		estado = 0

		while True:

			if estado == 0: #Mês
				choosed_month = await self.choose_month(last_msg, page, channel, user)
				if choosed_month is None: return
				elif choosed_month == 'back': continue
				choosed_year = today_year if choosed_month >= today_month else today_year + 1
				estado = 1
			
			elif estado == 1: #Dia
				choosed_day = await self.choose_day(last_msg, page, channel, user, choosed_month, choosed_year)
				if choosed_day is None: return
				elif choosed_day == 'back': estado -= 1
				else: estado += 1

			elif estado == 2: #Impressora
				choosed_printer = await self.choose_impresora(last_msg, page, channel, user)
				if choosed_printer is None: return
				elif choosed_printer == 'back': estado -= 1
				else: estado += 1

			elif estado == 3: #Inicio
				inicio = await self.get_remove_reserva(last_msg, page, channel, user, choosed_day, choosed_month, choosed_year, choosed_printer)
				if inicio is None: return
				elif inicio == 'back': estado -= 1
				else: break
		
		day_calendar = get_day(choosed_day, choosed_month, choosed_year)
		confirmation_str = f"Reserva da impressora {choosed_printer.name} para o dia {choosed_day}/{choosed_month} removida"
		inicio_t = inicio; dia_t = choosed_day; mes_t = choosed_month; ano_t = choosed_year

		flag_ = True
		while inicio_t >= 0:
			if inicio_t not in list(day_calendar.reservations[choosed_printer.name].keys()) or day_calendar.reservations[choosed_printer.name][inicio_t] != user.name:
				flag_ = False
				break
			inicio_t -= 1

		if flag_: 
			dia_t, mes_t, ano_t = back_day(dia_t, mes_t, ano_t)
			remove_reserva(dia_t, mes_t, ano_t, choosed_printer, inicio, user.name)
		
		dia_t = choosed_day; mes_t = choosed_month; ano_t = choosed_year
		inicio_t = inicio + 1; flag_ = True
		
		while inicio_t < 24:
			if inicio_t not in list(day_calendar.reservations[choosed_printer.name].keys()) or day_calendar.reservations[choosed_printer.name][inicio_t] != user.name:
				flag_ = False
				break
			inicio_t += 1

		if flag_: 
			dia_t, mes_t, ano_t = next_day(dia_t, mes_t, ano_t)
			remove_reserva(dia_t, mes_t, ano_t, choosed_printer, inicio, user.name)
		
		remove_reserva(choosed_day, choosed_month, choosed_year, choosed_printer, inicio, [user.name, user.id])
		await self.send_dm(user.id, confirmation_str)
		
		self.disponivel = True
		await last_msg.delete()	
		return
		
	
	@commands.command(name="add_impressora")
	async def adicionar_impressora(self, ctx):
		await ctx.message.delete()
		role = discord.utils.get(ctx.guild.roles, name="Admin")
		if role not in ctx.author.roles: return

		if not self.disponivel: return
		if ctx.channel.name != self.channel_name: 
			await ctx.send(self.wrong_channel_msg)
			return
		
		self.disponivel = False
		user = ctx.author ; channel = ctx.channel
		
		description =  '```python\nEscreva o nome da impressora\n\n```'
		page = discord.Embed(title=f"Adicionar Impressoras", description= description, color=0xffff00)
		last_msg = await ctx.send(embed = page)

		def check_get_impressora(msg):
			return True

		name = await self.get_responce(channel, user, last_msg, check_get_impressora, need_number=False)
		if name is None: return

		add_impressora(name, " ")
		self.disponivel = True
		await last_msg.delete()
	

	@commands.command(name="remove_impressora")
	async def remover_impressora(self, ctx):
		await ctx.message.delete()
		role = discord.utils.get(ctx.guild.roles, name="Admin")
		if role not in ctx.author.roles: return
		if not self.disponivel: return
		if ctx.channel.name != self.channel_name: 
			await ctx.send(self.wrong_channel_msg)
			return
		if len(impressoras) <= 0:
			await ctx.send("Não há impressoras disponíveis")
			return
		
		self.disponivel = False
		user = ctx.author ; channel = ctx.channel
		
		description =  '```python\nEscolha a impressora\n\n'

		for idx, i in enumerate(impressoras):
			description += f'{i.name} -> {idx}\n'
		description += '```'


		page = discord.Embed(title=f"Remover Impressoras", description= description, color=0xffff00)
		last_msg = await ctx.send(embed = page)

		def check_get_impressora(msg):
			return int(msg.content) < len(impressoras) and int(msg.content) >= 0

		idx = await self.get_responce(channel, user, last_msg, check_get_impressora)
		if idx is None: return
		idx = int(idx)

		description =  '```python\nRazão da remoção:\n\n```'


		page.description = description
		await last_msg.edit(embed = page)

		def check_get_razao(msg):
			return True

		razao = await self.get_responce(channel, user, last_msg, check_get_razao, need_number=False)
		if razao is None: return

		ids = []
		today = datetime.date.today()
		for ano_num, ano_obj in calendar.items():
			flag_ = False
			if ano_num < today.year: continue
			elif ano_num == today.year: flag_ = True

			for mes_num, mes_obj in ano_obj.months.items():
				if flag_ and mes_num < today.month: continue
				elif flag_ and mes_num != today.month: flag_ = False

				for dia_num, dia_obj in mes_obj.days.items():
					if flag_ and dia_num < today.day: continue
					if impressoras[idx].name not in list(dia_obj.reservations.keys()): continue

					for reserva in dia_obj.reservations[impressoras[idx].name].values():
						if reserva[1] in ids: continue
						ids.append(reserva[1])
						msg = f'A impressora {impressoras[idx].name} está desabilitada. Motivo:\n' + razao
						msg	+= f'\nVocê possui uma reserva no dia {dia_num}/{mes_num},'
						msg +='se necessário, por favor realize uma reserva em uma impressora diferente'
						await self.send_dm(reserva[1], msg)



		remove_impressora(impressoras[idx].name)
		self.disponivel = True
		await last_msg.delete()




async def setup(bot):
    await bot.add_cog(impressora_cog(bot))
