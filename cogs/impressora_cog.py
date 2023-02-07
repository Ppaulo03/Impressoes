import discord
import datetime
import asyncio
from discord.ext import commands
from cogs.modules.calendario import *


def verify_bisexto(year_num: int):
    if year_num % 4 != 0: return False
    if year_num % 100 != 0: return True
    if year_num % 400 == 0: return True
    return False

def get_calendar_months():
    month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembor', 'Dezembro']
    today = datetime.date.today()
    month = today.month - 1
    year = today.year
    list = ""
    for i in range(12):
        m_name = "{:<10}".format(str(month_names[(month + i)%12]))
        year_n = "{:<10}".format(f"- {year} -> {(month + i)%12 + 1}")
        line = m_name + year_n
        list += line + '\n'
        if month + i == 11: year += 1
    return list

def get_calendar_days(month: int, year: int):
    today = datetime.date.today()
    hj = today.day
    mes_hj = today.month
 
    month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembor', 'Dezembro']
    
    last_days = [0,31,28,31,30,31,30,31,31,30,31,30,31]

    if month == 2 and verify_bisexto(year): last_day = 29
    else: last_day = last_days[month]
    

    first_w_day = datetime.date(year, month, 1).weekday()
    

    header = "\t\t{}\n\nS   T   Q   Q   S   S   D\n".format(month_names[month - 1])
    
    month_calendar = header + "    " * first_w_day

    w_day = first_w_day

    day = 1
	
    while True:
        while w_day <7:
			
            if mes_hj == month and hj > day: days = "X   ".format(day)       
            elif day < 10: days = "{}   ".format(day)
            else:  days = "{}  ".format(day)
	    
		
            month_calendar += days
            day += 1
            w_day += 1

            if day > last_day:  return month_calendar, last_day

        month_calendar = month_calendar + "\n"
        w_day = 0

class impressora_cog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.channel_name = 'impressões'
		self.wrong_channel_msg = f'Please, use this command in the {self.channel_name} channel'
		self.last_msg = ''
		self.last_user = None
		self.disponivel = True

		
	async def get_responce(self, channel, user, last_msg, action):
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
				
				if msg.content.isdigit(): flag_good = action(msg)
				else: flag_good = False			
							
				await msg.delete()
				if flag_good: return msg.content

			except asyncio.TimeoutError:
				self.disponivel = True
				await last_msg.delete()
				return None

	@commands.command(name = "reservar", alias='p')
	async def reservar(self, ctx):
		if not self.disponivel: return
		
		if ctx.channel.name != self.channel_name: 
			await ctx.send(self.wrong_channel_msg)
			return
		
		if len(impressoras) <= 0:
			await ctx.send("Não há impressoras disponíveis")
			return
		
		self.disponivel = False
		user = ctx.author ; channel = ctx.channel
		today = datetime.date.today()


#________________________________________________Mês_____________________________________________________

		description =  '```python\nEscolha o mês (1-12)\n\n' + get_calendar_months()  + '```'
		
		page = discord.Embed(title=f"Reserva de Impressoras", description= description, color=0xffff00)
		last_msg = await ctx.send(embed = page)

		def check_get_mes(msg):
			return int(msg.content) <= 12 and int(msg.content) > 0

		mes = await self.get_responce(channel, user, last_msg, check_get_mes)
		if mes is None: return
		mes = int(mes)
		
		ano = today.year if mes >= today.month else today.year + 1
		month_calendar, last_day = get_calendar_days(mes, ano)
		
#________________________________________________Data_____________________________________________________
		
		description =  '```python\nEscolha a data\n\n' + month_calendar + '```'

		page.description = description
		await last_msg.edit(embed = page)

		def check_get_dia(msg):
			if today.month == mes:
				return int(msg.content) <= last_day and int(msg.content) >= today.day
			else: return int(msg.content) <= last_day and int(msg.content) > 0

		dia = await self.get_responce(channel, user, last_msg, check_get_dia)
		if dia is None: return
		dia = int(dia)

		
#________________________________________________Impressora_____________________________________________________

		description =  '```python\nEscolha a impressora\n\n'
		for idx, i in enumerate(impressoras):
			description += f'{i.name} -> {idx}\n'
		description += '```'

		page.description = description
		await last_msg.edit(embed = page)

		def check_get_impressora(msg):
			return int(msg.content) < len(impressoras) and int(msg.content) >= 0

		impressora = await self.get_responce(channel, user, last_msg, check_get_impressora)
		if impressora is None: return
		impressora = int(impressora)


#________________________________________________Tempo_____________________________________________________

		description =  '```python\nTempo de impressão\n\nMínimo - 1 hora\nMáximo - 50 horas```'

		page.description = description
		await last_msg.edit(embed = page)

		def check_get_tempo(msg):
			return int(msg.content) <= 50 and int(msg.content) > 0

		tempo = await self.get_responce(channel, user, last_msg, check_get_tempo)
		if tempo is None: return
		tempo = int(tempo)


#________________________________________________Inicio_____________________________________________________
		

		def next_day(d, m, a):
			d += 1; 
			if d <= last_day: return d, m, a
			
			d = 1; m += 1
			if m <= 12: return d, m, a

			m = 1; a +=1 
			return d, m, a
			
		num_dias = int(tempo / 24)
		if tempo % 24 != 0: num_dias += 1
		
		description =  '```python\nSelecione o horário de incio\n\n'

		dia_t = dia; mes_t = mes; ano_t = ano
		idx = True
		for i in range(num_dias + 1):

			if idx: description += f'Dia {dia_t} / {mes_t} / {ano_t}\n'
			else: description += f'Dia {dia_t} / {mes_t} / {ano_t} - consulta\n'
			
			description += check_day(dia_t, mes_t, ano_t, impressoras[impressora], idx)
			description += '\n'

			idx = False
			dia_t, mes_t, ano_t = next_day(dia_t, mes_t, ano_t)
		description += '```'
		
		page.description = description
		await last_msg.edit(embed = page)
		

		'''
		def check_get_inicio(msg):
			if int(msg.content) > 24 or int(msg.content) < 0:  return False
			inicio = int(msg.content)
			dia_t = dia; mes_t = mes; ano_t = year
			tempo_t = tempo; inicio_t = inicio

			flag_conflito = False
			for i in range(num_dias + 1):
				day = get_day(dia_t, mes_t, ano_t)
				dia_t += 1
				if dia_t > last_day:
					dia_t = 1
					mes_t += 1
					if mes_t > 12:
						ano_t += 1
						mes_t = 1

				if impressora.name not in list(day.reservations.keys()): continue
				reservas_impressora = list(day.reservations[impressora.name].keys())
				while inicio_t < 24:
					if i in reservas_impressora:
						description = "Horario escolhido choca com outras reservas\n" + description_t
						flag_conflito = True
						break

					inicio_t += 1
					tempo_t -= 1
					if tempo_t == 0: break
				inicio_t = 0
				if tempo_t == 0: break

			if flag_conflito:
				await last_msg.edit(embed = page)
				await msg.delete()
				continue
			
			inicio_t = inicio

			for i in range(num_dias + 1):
				if inicio_t + tempo_t >= 24: tempo_ef = 23
				else: tempo_ef = inicio_t + tempo_t
				tempo_t -= tempo_ef - inicio_t
				add_reserva(dia_t, mes_t, year, ano_t, inicio_t,tempo_ef , user)
				if tempo_t == 0: return
				dia_t += 1
				inicio_t = 0
				if dia_t > last_day:
					dia_t = 1
					mes_t += 1
					if mes_t > 12:
						ano_t += 1
						mes_t = 1

				while inicio_t < 24:
					if i in reservas_impressora:
						description = "Horario escolhido choca com outras reservas\n" + description_t
						flag_conflito = True
						break

					inicio_t += 1
					tempo_t -= 1
					if tempo_t == 0: break
				inicio_t = 0
				if tempo_t == 0: break
				


		inicio = await self.get_responce(channel, user, last_msg, check_get_inicio)
		if inicio is None: return
		inicio = int(inicio)
		'''

		self.disponivel = True
		
	
	
	@commands.command(name="mude")
	async def mude(self, ctx):
		if ctx.channel.name == self.channel_name:  
			if ctx.author == self.last_user: await self.last_msg.edit(content="ping")
		else: await ctx.send(self.wrong_channel_msg)

async def setup(bot):
    await bot.add_cog(impressora_cog(bot))
