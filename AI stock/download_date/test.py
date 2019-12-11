import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import tushare as ts
import pandas as pd
import numpy as np
import time

from sqlalchemy import create_engine



class download_date():

    def connect_database(self):
        engine1 = create_engine('mysql+pymysql://root:123456@localhost/stock?charset=utf8', encoding='utf-8')
        engine2 = create_engine('mysql+pymysql://root:123456@localhost/stock_data?charset=utf8', encoding='utf-8')
        engine3 = create_engine("mysql+pymysql://root:Tang123456!@116.85.28.78:3306/stock_data?charset=utf8")
        return engine1,engine2,engine3

    def get_api(self):
        pro = ts.pro_api('7844a61f5276d7889cdc4171e5081161ca3037e7a58be41487650a95')
        return pro

    def fina_indicator(self,stock_list,start_date,end_date):
        engine = download_date.connect_database()[0]
        pro = download_date.get_api()
        for n, i in enumerate(stock_list):
            #     print(n)
            #     print(i)
            try:
                df = pro.fina_indicator(ts_code=str(i),start_date=start_date, end_date=end_date)
                df = df.drop_duplicates(['end_date'], keep='first')
                print(df)
                df.to_sql("fina_indicator", con=engine, if_exists='append', index=False, index_label="id")
                # fina_indicator = pd.concat([fina_indicator, df], axis=0,ignore_index ='True')
            except:
                pass
        
        
    def balancesheet(self, stock_list, ):

        # balancesheet=pd.DataFrame([])
        # for n,i in enumerate(stock_list):
        #     print(n)
        #     print(i)
        #     try:
        #         if np.mod(n,50)==0 and n>0:
        #             time.sleep(30)
        #         df = pro.balancesheet(ts_code=str(i),start_date='20070101', end_date='20191118')
        #         df = df.drop_duplicates(['end_date'], keep='first')
        #         print(df)
        #         df.to_sql("balancesheet", con=engine, if_exists='append', index=False, index_label="id")
        #         # balancesheet = pd.concat([balancesheet, df], axis=0,ignore_index ='True')
        #     except:
        #         pass

        income = pd.DataFrame([])
        for n, i in enumerate(stock_list):
            print(n)
            print(i)
            try:
                if np.mod(n, 40) == 0 and n > 0:
                    time.sleep(60)
                df = pro.income(ts_code=str(i), start_date='20070101', end_date='20191118')
                df = df.drop_duplicates(['end_date'], keep='first')
                print(df)
                df.to_sql("income", con=engine, if_exists='append', index=False, index_label="id")
                # income = pd.concat([income, df], axis=0,ignore_index ='True')
            except:
                pass