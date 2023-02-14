import json
import datetime
try:
    from cogs.modules.date import *
except Exception:
    from date import *

impressoras = []
calendar = {}

class Impressora():
    def __init__(self, name: str, materiais: list):
        self.name = name
        self.material = materiais

        
class Year():
    def __init__(self, year_num: int):
        self.year_num = year_num
        self.months = {i:Month(i, self.year_num) for i in range(1, 13)}


class Month(): 
    def __init__(self, month_num: int, year_num: int):

        self.month_num = month_num
        self.num_dias = get_last_day_month(month_num, year_num)     
        self.days = {i:Day(i) for i in range(1, self.num_dias+1)}


class Day():
    def __init__(self, day_num: int):
        self.day_num = day_num
        self.reservations = {}


#_____________________________________________JSON____________________________________________________________
def get_json_list(file):
    
    with open(file, 'r') as js:
        
        try: parsed = json.load(js)
        except json.decoder.JSONDecodeError: parsed = []

    return parsed


def write_json(file, parsed):
    with open(file, 'w') as js: 
        js.write(json.dumps(parsed))


def save_json(json_dict, file):
    
    parsed = get_json_list(file)
    if json_dict in parsed: return
    
    parsed.append(json_dict)
    write_json(file, parsed)


def delete_json(json_dict, file):
    
    parsed = get_json_list(file)
    if json_dict not in parsed: return
    
    parsed.remove(json_dict)
    write_json(file, parsed)


#_____________________________________________Impressoras________________________________________________________
def add_impressora(name: str, materiais: list):
    
    for printer in impressoras:
        if printer.name == name: return

    impressoras.append(Impressora(name, materiais))
    
    json_dict = {'name': name,'materiais': materiais,}
    save_json(json.dumps(json_dict), 'dados/impressoras.json')


def remove_impressora(name:str):
   
    for printer in impressoras:
        if printer.name == name: 
            materiais = printer.material
            impressoras.remove(printer)
            break

    json_dict = {'name': name, 'materiais': materiais}
    delete_json(json.dumps(json_dict), 'dados/impressoras.json')


#_____________________________________________Calendario_____________________________________________________
def get_day(dia: int, mes: int, ano: int):
    if ano not in list(calendar.keys()): calendar[ano] = Year(ano)
  

    if mes <= 0: mes = 1
    elif mes > 12: mes = 12
    month_calendar = calendar[ano].months[mes]


    if dia <= 0: dia = 1
    elif dia not in list(month_calendar.days.keys()): dia = list(month_calendar.days.keys())[-1]
    return month_calendar.days[dia]


def check_day(dia: int, mes: int, ano: int, impressora: Impressora, idx: bool = False):
    
    day = get_day(dia, mes, ano)

    if impressora.name not in list(day.reservations.keys()): day.reservations[impressora.name] = {}
    reservas_impressora = list(day.reservations[impressora.name].keys())

    msg = ""
    for i in range(0, 24):
        ending = i + 1 if i + 1 < 24 else 0
        if ending < 10: ending = str(ending) + 'h '
        else: ending = str(ending) + 'h'

        if i in reservas_impressora:
            if idx: 
                if i < 10: msg += str(i) + '  ->'
                else: msg += str(i) + ' ->'

            if i < 10: msg += f'{i}h  - '
            else: msg += f'{i}h - '
            msg += ending + '- Reservada por {' +  day.reservations[impressora.name][i][0] + '}\n'
        else:
            if idx: 
                if i < 10: msg += str(i) + '  ->'
                else: msg += str(i) + ' ->'
            if i < 10: msg += f'{i}h  - '
            else: msg += f'{i}h - '
            msg += ending + f'- Disponível\n'

    return msg


def add_reserva(dia: int, mes: int, ano: int, impressora: Impressora, inicio: int, fim: int, user: list):
   
    day = get_day(dia, mes, ano)

    if inicio < 0: inicio = 0
    if inicio >= 24: inicio = 23
    if inicio > fim: fim = inicio + 1
    if fim >= 24: fim = 23
 

    for i in range(inicio, fim):
        if impressora.name not in list(day.reservations.keys()): 
            day.reservations[impressora.name] = {}
        day.reservations[impressora.name][i] = user

    json_dict = { 'user': user,'impressora': impressora.name,
                  'dia': dia,'mes': mes, 'ano': ano, 'inicio': inicio, 'fim': fim}
    
    save_json(json.dumps(json_dict), 'dados/reservas.json')


def remove_reserva(dia: int, mes: int, ano: int, impressora: Impressora, inicio: int, user: list):
    
    day = get_day(dia, mes, ano)
    if impressora.name not in list(day.reservations.keys()): return

    if inicio < 0: inicio = 0
    if inicio >= 24: inicio = 23
    reservas = list(day.reservations[impressora.name].keys())
    i = inicio
    while i >= 0:
        if i in reservas and day.reservations[impressora.name][i][1] == user[1]:
            day.reservations[impressora.name].pop(i)
        else: break
        i -= 1
    real_inicio = i+1

    i = inicio + 1
    while i < 24:
        if i in reservas and day.reservations[impressora.name][i][1] == user[1]:
            day.reservations[impressora.name].pop(i)
        else: break
        i += 1
    real_fim = i
    
    json_dict = { 'user': user,'impressora': impressora.name,
                  'dia': dia,'mes': mes, 'ano': ano, 'inicio': real_inicio, 'fim': real_fim}

    delete_json(json.dumps(json_dict), 'dados/reservas.json')


def check_week(dia: int, mes: int, ano: int, impressora: Impressora):
    weekday_name = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    weekday_num = datetime.date(ano, mes, dia).weekday()
  
    reserva_days = []; header = ' '*7; subheader = header
    for i in range(7):
<<<<<<< HEAD
       
=======
        header += '{:<6}'.format(f'{dia}/{mes}'[:6])

>>>>>>> 737e80f76352d8b72e4eae24974ffdd929000c73
        day = get_day(dia, mes, ano)
        if impressora.name not in list(day.reservations.keys()): day.reservations[impressora.name] = {}
        reserva_days.append(list(day.reservations[impressora.name].keys()))
        dia, mes, ano = next_day(dia, mes, ano)
        
        weekday = weekday_name[weekday_num%7]
        subheader += '{:<6}'.format(weekday[:6])
        weekday_num += 1

    msg = header + '\n' + subheader + '\n'
    for i in range(0, 24):
        if i < 10: msg += f'0{i}' 
        else: msg += f'{i}' 
        msg += 'h -  '

        for reservas_impressora in reserva_days:
<<<<<<< HEAD
            tmp_msg = 'res.' if i in reservas_impressora else ' o '
=======
            tmp_msg = ' X' if i in reservas_impressora else 'dis.'
>>>>>>> 737e80f76352d8b72e4eae24974ffdd929000c73
            msg += '{:<6}'.format(tmp_msg[:6])
        msg +='\n'
            

    return msg
#_________________________________________________Init Configuration___________________________________________
def setup():

    json_impressoras = get_json_list('dados/impressoras.json')
    for r in json_impressoras:
        r = json.loads(r)
        add_impressora(r['name'], r['materiais'])

    json_reservas = get_json_list('dados/reservas.json')
    for r in json_reservas:
        r= json.loads(r)

        impressora = None
        for x in impressoras:
            if x.name == r['impressora']:
                impressora = x
                break
        
        if not impressora: 
            add_impressora(r['impressora'], ' ')
            impressora = Impressora(r['impressora'], ' ')

        add_reserva(r['dia'], r['mes'], r['ano'], impressora, r['inicio'], r['fim'], r['user'])

setup()

if __name__ == '__main__':
    print(check_week(10,12,2022,Impressora('z', 'x')))