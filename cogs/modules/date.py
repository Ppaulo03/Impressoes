import datetime

month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembor', 'Dezembro']


def get_last_day_month(month: int, year: int):
    last_days = [31,28,31,30,31,30,31,31,30,31,30,31]
    if month == 2 and verify_bisexto(year): return 29
    else: return last_days[month - 1]

def get_day_month_year():
    today = datetime.date.today()
    return today.day, today.month, today.year

def verify_bisexto(year_num: int):
    if year_num % 4 != 0: return False
    if year_num % 100 != 0: return True
    if year_num % 400 == 0: return True
    return False

def get_calendar_months():

    _, month, year = get_day_month_year()  
    month -= 1; month_list = ""
    for i in range(12):
        m_name = "{:<10}".format(month_names[(month + i)%12])
        year_n = "{:<10}".format(f"- {year} -> {(month + i)%12 + 1}")
        line = m_name + year_n
        month_list += line + '\n'
        if month + i == 11: year += 1

    return month_list

def get_calendar_days(month: int, year: int):

    today_day, today_month,  _ = get_day_month_year()
    last_day_month = get_last_day_month(month, year)
    first_w_day = datetime.date(year, month, 1).weekday()
    

    header = "\t\t{}\n\nS   T   Q   Q   S   S   D\n".format(month_names[month - 1])
    month_calendar = header + "    " * first_w_day

    day = 1; w_day = first_w_day; 
    while True:
        while w_day <7:
			
            if today_month == month and today_day > day: days = "X   ".format(day)       
            elif day < 10: days = "{}   ".format(day)
            else:  days = "{}  ".format(day)
	    
            month_calendar += days
            day += 1
            w_day += 1

            if day > last_day_month:  return month_calendar

        month_calendar = month_calendar + "\n"
        w_day = 0

def next_day(day, month, year):
    last_day = get_last_day_month(month, year)
    day += 1; 
    if day <= last_day: return day, month, year
    
    day = 1; month += 1
    if month <= 12: return day, month, year

    month = 1; year +=1 
    return day, month, year
			
def back_day(day, month, year):
    day -= 1; 
    if day >= 0: return day, month, year
    month -= 1
    
    if month > 0: 
        last_days = get_last_day_month(month, year)
        return day, month, year

    year = 31; month = 12; year -=1 
    return day, month, year