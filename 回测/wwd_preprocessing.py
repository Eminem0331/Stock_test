# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle

def change_name(code,exch):
    if exch=='深圳':
        return code+'.SZ'
    if exch=='上海':
        return code+'.SH'
    #print('存在非沪深两市的证券','!!!!!!!!',exch)
    
def get_data_from_wind(save_file_path):
    import pyodbc
    userid='jrgc'
    pw='jrgc,20161229'
    cnxn_string='DRIVER={SQL SERVER};SERVER=10.88.2.201;DATABASE=Wind;DATABASE=LINK_ZG.FUNDRISKCONTROL;UID='+userid+';PWD='+pw
                        
    cnxn = pyodbc.connect(cnxn_string,unicode_results='True')
    cursor = cnxn.cursor()
    sql=u"""
    select F16_1090 as code,F5_1090 as exchange, F4_1425 as open_price, F5_1425 as high_price, F6_1425 as low_price, F7_1425 as close_price, F8_1425 as volume, F2_1425 as trading_date,F11_1425 as trading_state
    from wind.dbo.TB_OBJECT_1425 as A ,wind.dbo.TB_OBJECT_1090 as B
    where F1_1425 = F2_1090 and F2_1425>='20020101' and F4_1090='A'
    order by F5_1090, F16_1090, F2_1425
    """
    #从wind中提取：股票代码、交易所、开盘价、最高价、最低价、收盘价、成交量和交易日期
    data = pd.read_sql(sql,cnxn,index_col=None)
    cursor.close()
    cnxn.close()
    data.rename(columns={'open_price':'open', 'close_price':'close', 'high_price':'high','low_price':'low' }, inplace = True)
    data.to_csv(save_file_path, encoding = "gbk")
    return data
def preprocessing_data(raw_data):
    if list(raw_data.columns.values)[0]=='Unnamed: 0':
        del raw_data['Unnamed: 0']#删去第一列无用信息
    raw_data = raw_data[ raw_data['trading_state'] != 0 ]
    raw_data['code'] = raw_data['code'].astype(str)
    
    #补齐股票代码
    raw_data['code'] = list(map(lambda x : '0' * (6 - len(x)) + x ,raw_data['code']))
    raw_data['code'] = list(map(change_name, raw_data['code'],raw_data['exchange']))
    del raw_data['exchange']
    print('stocks id is OK')
    
    #获取所有股票ID
    stocks = list(raw_data.drop_duplicates(['code'])['code'])
    print('we have %d stocks in total'%(len(stocks)))
    
    #提取每隻股票并按交易时间排列
    stock_data_list = dict(list(raw_data.groupby('code')))
    return stocks, stock_data_list
#使用SQL从wind中提取原始数据
#raw_data = get_data_from_wind('data/raw_stock_data.csv')
#使用本地csv文件提取原始数据
raw_data = pd.read_csv ("data/raw_stock_data.csv" , encoding = "gbk")
print('data is ready')


#提取每只股票数据
pd.set_option('display.width', 200)
stock, nn = preprocessing_data(raw_data)
print(nn['300104.SZ'])
#存储数据
data_file = 'data/stock_price.pickle'
fw = open(data_file,'wb')
pickle.dump(stock, fw, -1)
pickle.dump(nn, fw, -1)
fw.close()
           