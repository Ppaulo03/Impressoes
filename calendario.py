import datetime

class Impressora():
    def __init__(self, name: str, materiais: list):
        self.name = name
        self.material = materiais

class Year():
    def __init__(self, year_num: int):
        self.year_num = year_num
        self.months = {i:Month(i, self.year_num) for i in range(1, 13)}

class Month():
    
    num_dias_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    def __init__(self, month_num: int, year_num: int):

        self.month_num = month_num
        if self.month_num == 2 and self.verify_bisexto(year_num):  self.num_dias = 29
        else: self.num_dias = self.num_dias_mes[month_num - 1]        
        self.days = {i:Day(i) for i in range(1, self.num_dias+1)}

        
    def verify_bisexto(self, year_num: int):
        if year_num % 4 != 0: return False
        if year_num % 100 != 0: return True
        if year_num % 400 == 0: return True
        return False

class Day():
    def __init__(self, day_num: int):
        self.day_num = day_num
        self.reservations = {}
        self.generate_day()

    def generate_day(self):
        for i in range(24):
            self.reservations[i] = []

    def make_reservation(self, impressora: Impressora, user, periodo: int):
        self.reservations[periodo].append([impressora, user])
    
    def remove_reservation(self, impressora: Impressora, user, periodo: int):
        self.reservations[periodo].remove([impressora, user])


calendar = {}

def get_day(dia: int, mes: int, ano: int):
    if ano not in list(calendar.keys()):  calendar[ano] = Year(ano)

    if mes <= 0: mes = 1
    elif mes > 12: mes = 12
    month_calendar = calendar[ano].months[mes]

    if dia <= 0: dia = 1
    elif dia not in list(month_calendar.days.keys()): dia = list(month_calendar.days.keys())[-1]
    return month_calendar.days[dia]


if __name__ == '__main__':
    print(get_day(20, 2, 2000))


