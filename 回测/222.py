import tushare as ts
import pandas as pd
startdate = '2015/01/01'
enddate = '2017/12/31'
bench = ts.get_stock_basics()
bench.to_csv('~/Desktop/bench.csv')
bench = ts.get_stock_basics()
bench.to_csv('~/Desktop/bench.csv')
stock = pd.read_csv('~/Desktop/bench.csv', dtype=str)
stock = stock.loc[:, ['code']]
stock = list(stock['code'])
path = '~/Desktop/stock/'
# print(stock[11])
# df = ts.get_hist_data(stock[11], start=startdate, end=enddate)
# print(df)
for i in range(20):
    try:
        df = ts.get_hist_data(stock[i], start=startdate, end=enddate)
        print(df)
        df.to_csv(path + '%s.csv' %i)
    except:
        pass


