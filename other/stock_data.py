from queue import Queue
import threading
import os
import datetime

import tushare as ts
from sqlalchemy import create_engine
from sqlalchemy import types

# 创建myql数据库引擎，便于后期链接数据库
mysql_info = {'host':'106.15.32.226','port':3306,'user':'root','passwd':'yuecai666!All','db':'stock','charset':'utf8'}
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' %(mysql_info['user'],mysql_info['passwd'],
                                                             mysql_info['host'],mysql_info['port'],
                                                             mysql_info['db'],mysql_info['charset']),
                       echo=False)


# 获取所有股票数据，利用股票代码获取复权数据
stock_basics = ts.get_stock_basics()
stock_basics.columns


# 获取数据库现有数据的时间日期
def get_old_date():
    con = engine.connect()
    sql1 = 'show tables;'
    tables = con.execute(sql1)
    if ('fq_day',) not in tables:
        date_old = datetime.date(2001,1,1)
        return date_old
    sql2 = 'select max(date) from fq_day;'
    date_old = con.execute(sql2).fetchall()[0][0].date()
    if date_old < datetime.date.today() - datetime.timedelta(1):
        return date_old
    else:
        con.close()
        print('今天已经获取过数据，不需重新获取')
        os._exit(1)


# 声明队列，用于存取股票以代码数据，以便获取复权明细
stock_code_queue = Queue()
for code in stock_basics.index:
    stock_code_queue.put(code)

type_fq_day = {'code':types.CHAR(6),'open':types.FLOAT,'high':types.FLOAT,'close':types.FLOAT,'low':types.FLOAT,
              'amount':types.FLOAT,'factor':types.FLOAT}


# 获取复权数据
def process_data(old_date,task_qeue):
    #queueLock.acquire()
    while not task_qeue.empty():
        data = task_qeue.get()
        print("正在获取%s;数据还有%s条:" %(data,task_qeue.qsize()))
        #queueLock.release()
        date_begin = old_date + datetime.timedelta(1)
        date_end = datetime.date.today()
        try:
            qfq_day = ts.get_h_data(data,start = str(date_begin),end=str(date_end),autype='qfq',drop_factor=False)
            qfq_day['code'] = data
            qfq_day.to_sql('fq_day',engine,if_exists='append',dtype=type_fq_day)
        except:
            task_qeue.put(data)  # 如果数据获取失败，将该数据重新存入到队列，便于后期继续执行
    #else:
        #queueLock.release()



old_date=get_old_date()
b=process_data(old_date,stock_code_queue)
print(b)