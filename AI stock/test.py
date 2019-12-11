import calendar as cal
import datetime


for year in range(2000,2001):
    for m in range(1, 13):
        d = cal.monthrange(year, m)
        if m<10:
            a=str('{}-0{}-01'.format(year,m))
        else:
            a = str('{}-{}-01'.format(year,m))
        print(a)
        startTime = datetime.datetime.strptime(a, '%Y-%m-%d').date()
        print(type(startTime))