import operator as op
import numpy as np
import talib
import matplotlib.pyplot as plt
import pandas as pd

from lib.yqObject import KObject

from lib.apiTools import KStockDataTool, KCommonDataTool


# sclient=uqer.Client(token='e337087e3844e51bc7b8cd285de6d0709f405401b2a599ffde013b7be9129d12')

def testDatacube(start, end):
    # 'sat'===>>>  s:key  ; value:refer to DataFrame;
    # a:attribute ,t: time;
    symbols = ['601619.XSHG']
    fields = ['highPrice', 'lowPrice', 'closePrice']

    data = get_data_cube(symbols, fields, start, end, style='sat', freq='60m')

    for symbol in symbols:
        current = data[symbol]
        d = current['highPrice'] - current['lowPrice']
        # print(d)
        c = current['closePrice']

    for symbol in symbols:
        current = data[symbol]
        c = current['closePrice']  # get the column from pandas.core.series.Series


mysymbols = ['601619.XSHG']
myfields = ['high', 'low', 'closePrice']
start = '2019-08-08'
end = '2019-08-09'

#################################################3
''' 
数据立方支持三种数据获取方式。可以根据使用场景，灵活选择。
AST Style (Attribute-Symbol-Time) 主要用于获取已有数据，如因子、连续合约、指数行情、基金净值等。
SAT Style (Symbol-Attribute-Time) 主要用于多属性运算，如使用量价信息计算指标，使用行情财务计算因子等。
TAS Style (Time-Attribute-Symbol) 主要用于获取横截面数据，进而进行其他数据处理。
'''


class KCommonDataTool:

    @staticmethod
    def getAStock_AllSym(fun_set_universe):
        # listStock=set_universe('A')
        listStock = fun_set_universe('A')

        return listStock

    @staticmethod
    def getDataCubeFieldList():
        myfields = ['highPrice', 'lowPrice', 'openPrice', 'closePrice']

        return myfields

    @staticmethod
    def getAPIFieldList():
        lstTest = list()
        lstTest.append('secID')
        lstTest.append('tradeDate')
        lstTest.append('openPrice')
        lstTest.append('highestPrice')
        lstTest.append('lowestPrice')
        lstTest.append('closePrice')
        lstTest.append('turnoverVol')
        lstTest.append('turnoverRate')

        return lstTest

    #########################


class KDataTools(KObject):

    def setDynEnd(self, start1, freq1, delDefault):
        dateIndex = pd.date_range(start=start1, end=start1, freq=freq1)  # ?????????????

        # datatest=fun(sym,field,self.start,self.end,freq=self.freq,style=self.style)
        # dateIndex=datatest[sym][field].index
        end = dateIndex[0] + delDefault
        self.end = end

    def __init__(self, start, end, freq, style='sat'):
        self.start = start
        self.end = end
        self.style = style
        self.freq = freq
        self.lstField = list()
        # self.mapInfo=map()

    @staticmethod
    def getVaildTradeDay(nextSDate, endDate, during):
        # 暂时这样写，没有测试
        lstExchange = ['XSHG', 'XSHE', 'CCFX', 'XDCE', 'XSGE', 'XZCE', 'XHKG']

        date = DataAPI.TradeCalGet(exchangeCD=lstExchange, beginDate=nextSDate - during, endDate=nextend + during,
                                   field=u"isOpen", pandas="1")
        # data = data[data['isOpen'] == 1]

        testOpen = date['isOpen']
        while (True):

            test = testOpen[during]
            if (test == 1):
                break;

            nextSDate = nextSDate + stepStart
            during = during + stepStart

        return nextSDate

    def getNextSingleDate(self, sym, field, bUseApi, stepStart=1, during=25, bTraceTradeDay=False):

        if not (isinstance(sym, str) and isinstance(field, str)):
            assert False, 'sym and field must be str type'
            return None

        freq_yq = self.freq

        pdfreq, digital, alpha = KLineTools.converyq_pdDateFrq(freq_yq)
        dateIndex = pd.date_range(start=self.start, end=self.end, freq=pdfreq)

        # datatest=fun(sym,field,self.start,self.end,freq=self.freq,style=self.style)
        # dateIndex=datatest[sym][field].index

        nextSDate = dateIndex[0] + stepStart
        nextend = dateIndex[len(dateIndex) - 1]

        if (bTraceTradeDay == True and alpha == 'd'):
            nextSDate = KDataTools.getVaildTradeDay(nextSDate, nextend, during)

        ##########################################################

        if (nextSDate >= nextend):
            nextSDate = nextend

        if bUseApi == False:
            fun = KObject.get_getdata_cube_Interface()

            data = fun(sym, field, nextSDate, nextend, freq=self.freq, style=self.style)
            current = data[sym]
        else:
            fun = KStockDataTool.get_APIData_Interface()  # for API interface

            # getRawData(symLst,begin,end,field1,freq='1d',style=None):
            data = fun(sym, nextSDate, nextend, field)
            dataG1 = KStockDataTool.getRawDataBySym(data, sym)
            current = dataG1

        item = current[field]

        if alpha == 'm':  # item : from  the 9:30 ,15:00,whatever starttime

            if stepStart >= 0:
                return item.values[stepStart]
            else:
                assert False, 'minute interval must be great than Zero'

        # print(item)

        return item.values[0]

    # print(dateIndex.to_pydatetime())

    @staticmethod  # end_date.strftime('%Y%m%d'), 'freq': freq,
    # str或者datetime，注意str只支持"YYYY-MM-DD"和"YYYYMMDD"两种格式
    # 如果是5分钟，就会出现格式不对的问题。 ？？？？？？？？？？？？？？？
    def getFieldValueByIntervalTime(start, end, sym, field, deltest, freqTest, bUseApi):
        # sat
        # dateIndex=pd.date_range(start,end,freq='5min')

        # testIndex=dateIndex[0]+timeIndex

        # keyTime=testIndex.to_pydatetime()

        if bUseApi == False:
            fun = KObject.get_getdata_cube_Interface()
        else:
            fun = KObject.get_ApiData_Interface()

        data = fun(sym, field, start, end, style='sat', freq=freqTest)  # time:{attribute :sym}
        df = data[sym]
        timeIndex = df[field].index

        test = df.loc[timeIndex[deltest], field]
        return test

    def readAllField(self):

        self.context = context

    def getContext(self):
        return self.context

    def getParam(self):
        return self.start, self.end, self.freq

    def setFreq(self, freq):
        self.freq = freq

    def getFreq(self, freq):
        self.freq = freq

    def setDate(self, start, end):
        self.start = start
        self.end = end

    def setParm(self, freq='1d', style='sat'):
        self.freq = freq
        self.style = style

    def setSymbolAndField(self, symbols, fields):
        self.symbols = symbols
        self.fields = fields

    def setSymbol(self, symbols):
        self.symbols = symbols

    def setField(self, fields):
        self.fields = fields

    def check(self, sym, field):
        if (sym not in self.symbols) or (field not in self.fields):
            assert (False)
            return False
        return True

    def symbolsToTickerId(strtest):

        iIndex = strtest.find('.')
        if iIndex == -1:
            assert (False)
            return None, None, -1
        sfront = strtest[:(iIndex)]
        sEnd = strtest[(iIndex + 1):]
        return sfront, sEnd, iIndex

    '''      error  ???????s 
    def   teststatic(self):
            KDataTools.symbolsToTickerId('aa.bb') '''

    def getShortNameByTicked(self, tickerId):

        sInfo = DataAPI.SecIDGet(ticker=tickerId)
        return sInfo['secShortName']
        # return sInfo.getShortName()

    def getShortNameBySymbol(self, strtest):

        iIndex = strtest.find('.')
        if iIndex == -1:
            assert (False)
            return None, None, -1
        strfront = strtest[:(iIndex)]
        print(strtest)
        return self.getShortNameByTicked(strfront)

    def printmapData(self):

        data = get_data_cube(self.symbols, self.fields,
                             self.start, self.end, style=self.style)

        print(type(data))

        for symbol in self.symbols:
            print(symbol)
            current = data[symbol]
            # d=current['high']-current['low']
            for field in self.fields:
                # print(type(current[field])) #Series
                # print(current[field].index)  #index
                item = current[field]  # Series object
                for value in item.values:  # Series  value
                    print(type(item.values))  # narray object
                    print(value)

    #  singele data  ,sym and field are str type
    def getSingleData(self, sym, field, bUseApi):

        if not (isinstance(sym, str) and isinstance(field, str)):
            return None

        if bUseApi == False:
            fun = KObject.get_getdata_cube_Interface()

            data = fun(sym, field, self.begin, self.end, freq=self.freq, style=self.style)
            current = data[sym]
        else:
            fun = KObject.get_APIData_Interface()  # for API interface

            # getRawData(symLst,begin,end,field1,freq='1d',style=None):
            data = fun(sym, self.start, self.end, self.fields)
            dataG1 = KStockDataTool.getRawDataBySym(data, sym)
            current = dataG1
            # item=current[field]
        test = current.loc[:, field]
        return test

    def getCurrentPrice(self, sym):

        return self.context.current_price(sym)

    # 返回数据的K线周期，默认值为’1d’，共支持’1d’,‘1m’,‘5m’, ‘15m’, ‘30m’, '60m’六个频率类型
    def getRawDfData(self, symLst, field, freqtest, bUseApi):

        if bUseApi == False:
            fun = KObject.get_getdata_cube_Interface()

            data = fun(symLst, field, self.start, self.end, freq=freqtest, style=self.style)
        else:
            fun = KObject.get_APIData_Interface()  # for API interface

            # getRawData(symLst,begin,end,field1,freq='1d',style=None):

            data = fun(symLst, self.start, self.end, field)

        return data

    def getTimeSeries(self, start, end, sym, field):
        # sat
        fun = KObject.get_getdata_cube_Interface()
        data = fun(self.symbols, self.fields, start, end, style='sat')
        time_series = np.array(data[sym][field].index)
        return time_series

    def getDataTimembyAtr(self, start, end, sym, field):
        # sat
        if (sym not in self.symbols or (field not in self.fields)):
            return None
        fun = KObject.get_getdata_cube_Interface()
        data = fun(sym, field, start, end, style='ast')

        return data[field][sym].index.values

    @staticmethod
    def getSetDelDateTime(start, delTest, freqtest='d'):

        pdfreq, digital, alpha = KDataTools.converyq_pdDateFrq(freqtest)

        end = '2050-01-01'
        dateIndex = pd.date_range(start, end, freq=pdfreq)
        endIndex = dateIndex[0] + delTest

        dateTimePy = endIndex.to_pydatetime()
        endDate = None

        if alpha == 'd':
            endDate = dateTimePy.strftime("%Y-%m-%d")
        else:
            endDate = dateTimePy.strftime("%H-%M-%S")

        return endDate

    ##########################################


def getstockinfo():
    index = 0
    tickidLst = ['601619']
    tickid = '601619'
    assetClass = 'E'  # 证券类型，可供选择类型：E 股票,B 债券,F 基金,IDX 指数,FU 期货,OP 期权；默认为                                          E。

    # DataAPI.EquGet(secID=u"",ticker=u"",equTypeCD=u"A",listStatusCD=u"",field=u"",pandas="1")

    sId = '601619.XSHG'

    ticker = '601619'

    s = DataAPI.SecIDGet(
        ticker='601619')  # 证券类型，可供选择类型：E 股票,B 债券,F 基金,IDX 指数,FU 期货,OP 期权；                                                默认为E。

    print(s['secShortName'][index])
    sInfo = DataAPI.EquGet(secID=sId)  # just the full stock informations
    print(sInfo['secShortName'][index])


def testdata():
    symbols = set_universe('SH50')
    fields = ['closePrice']
    start = '2016-01-01'
    end = '2016-04-18'

    data = get_data_cube(symbols, fields, start, end, style='sat')

    # key is symbols of stock
    print(data['601328.XSHG'].head(3))

    # sat
    close_series = np.array(data['601328.XSHG']['closePrice'])

    # sat
    time_series = np.array(data['601328.XSHG']['closePrice'].index)

    print(time_series)

    ma_line = talib.MA(close_series, 10)

    plt.figure(figsize=(10, 5))

    # list ,x --->0,1,2,3

    plt.plot(list(close_series), label='closePrice')
    plt.plot(list(ma_line), label='MA')
    plt.legend()

    #################################################

    data = get_data_cube(symbols, fields, start, end, style='ast')

    # print(data['closePrice'].head(3))

    print(data['closePrice'].head(3))

    # by key date time is key
    symbols = set_universe('SH50')
    fields = ['PE']
    start = '2016-09-20'
    end = '2016-09-22'
    data = get_data_cube(symbols, fields, start, end, style='tas')
    data_now = data['2016-09-20']  #
    data_now['PE_after_winsorize'] = winsorize(data_now.PE)
    print
    data_now.head().to_html()
    data_now.plot(figsize=(12, 7))

    ######################################################
    symbols = set_universe('SH50')
    fields = ['PE']
    start = '2016-09-20'
    end = '2016-09-22'

    data = get_data_cube(symbols, fields, start, end, style='ast')

    print(type(data['PE']))
    data_PE = data['PE'].T
    print(type(data_PE))
    print(type(winsorize))

    PE_after_winsorize = data_PE.apply(winsorize)

    print
    data_PE.head().to_html()
    # print PE_after_winsorize.head().to_html()

    # data_PE['2016-09-20'].plot(figsize=(10,5), label='PE')
    # PE_after_winsorize['2016-09-20'].plot(figsize=(12,7), label='PE_after_winsorize')
    # plt.legend()

    #######################
    symbols = ['IFM0']
    fields = ['closePrice']
    start = '2017-01-01'
    end = '2017-04-18'

    data = get_data_cube(symbols, fields, start, end, freq='1d', style='ast')
    data.closePrice.head()
    ################################

    symbols = ['IFM0']
    fields = ['closePrice', 'openPrice', 'highPrice', 'lowPrice', 'turnoverVol']
    start = '2017-04-01'
    end = '2017-04-18'

    data = get_data_cube(symbols, fields, start, end, freq='1m', style='sat')
    data = data['IFM0']
    print
    data.head(10).to_html()

    from datetime import datetime

    # 转换为datetime类型的索引值
    data.index = map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M'), data.index)

    data = get_data_cube(symbols, fields, start, end, freq='5m', style='sat')
    data = data['IFM0']
    print
    data.head(10).to_html()


def testTools():
    mysymbols = ['601619.XSHG']
    myfields = ['highPrice', 'lowPrice', 'openPrice', 'closePrice']
    start = '2019-09-11'
    end = '2019-09-11'
    tools = KDataTools(start, end, 'd')
    tools.readAllField()
    tools.setSymbolAndField(mysymbols, myfields)
    op = tools.getSingleData('601619.XSHG', 'openPrice')
    # print(op)

    ##############3
    symbols = set_universe('SH50')
    fields = ['PE', 'highPrice', 'lowPrice', 'openPrice', 'closePrice']
    start = '2019-09-10'
    end = '2019-09-12'

    tools = KDataTools(start, end, '5m')
    tools.setSymbolAndField(symbols, fields)
    tools.setDate(start, end)

    # print(tools.getTimeSeries(start,end,'601328.XSHG','openPrice'))
    # print(tools.getDataTimembyAtr(start,end,'601328.XSHG','openPrice'))

    nextPrice = tools.getNextSingleDate('600525.XSHG', 'closePrice', 1)
    print(nextPrice)
    nextPrice = tools.getNextSingleDate('600525.XSHG', 'closePrice', 2)
    print(nextPrice)

    start = '2019-09-10'
    end = '2019-09-12'
    tools = KDataTools(start, end, '1d')

    nextPrice = tools.getNextSingleDate('600525.XSHG', 'closePrice', 1)  # max is 48
    print(nextPrice)

    print('###################################')
    # def   getFieldValueByTime(start,end,sym,field,timeIndex,freqTest):

    start = '2019-09-12'
    end = '2019-09-12'
    nextPrice = tools.getFieldValueByIntervalTime(start, end, '600525.XSHG', 'closePrice', 1, '60m')  # max is 48
    print(nextPrice)
    nextPrice = tools.getFieldValueByIntervalTime(start, end, '600525.XSHG', 'closePrice', 2, '60m')  # max is 48
    print(nextPrice)
    nextPrice = tools.getFieldValueByIntervalTime(start, end, '600525.XSHG', 'closePrice', 3, '60m')  # max is 48
    print(nextPrice)
    nextPrice = tools.getFieldValueByIntervalTime(start, end, '600525.XSHG', 'closePrice', 4, '60m')  # max is 48
    print(nextPrice)


# testTools()


'''
静态证券池可以指定固定的个别资产或资产列表：

universe = ['000001.XSHE', 'IFM0']  # 指定平安银行和股指期货为策略证券池    
universe = DynamicUniverse('HS300')  # 使用沪深300成分股动态证券池
支持动态证券池和普通列表取并集。

universe = DynamicUniverse('HS300') + ['000001.XSHE']   
# 包含沪深300成分股动态证券池和平安银行
6.4.7 get_universe获取当前交易日证券池

context.get_universe(asset_type, exclude_halt=False)
universe = DynamicUniverse('HS300').apply_filter(Factor.PE.nsmall(100))    
# 获得沪深300成分股中PE最小的100只股票列表


'''

'''
context.get_symbol_history(symbol, time_range=1, attribute=['closePrice'], freq='1d', style='sat', rtype='frame')
需要获取数据的证券列表，支持单个证券或证券列表，必须是初始化参数 universe 涵盖的证券范围。
需要回溯的历史K线条数，和freq属性相对应。

日线数据默认最大值为30，分钟线数据默认最大值为240；可以使用max_history_window设置最大限度取值范围。
context.history(symbol, attribute=['closPrice'], time_range=1, freq='1d', style='sat', rtype='frame')


'''


class KHistoryDataTool:  # 需要回溯的历史K线条数，和freq属性相对应。

    def __init__(self, context, freq, time_range, style='sat'):
        self.freq = freq
        self.context = context
        self.time_range = time_range
        self.style = style
        self.history = None

    def get_HistorybyAtr(self, sym, atr):
        history = self.context.history(sym, atr, self.time_range, freq=self.freq, style=self.style, rtype='frame')

        data = history[sym].loc[:, atr]
        return data

        # [1,1,1,1]     b[-4]

    def getHistoryData(self, sym, atr, timeDel):
        if (timeDel > self.time_range):
            self.time_range = timeDel

        history = self.context.history(sym, atr, self.time_range, freq=self.freq, style=self.style, rtype='frame')
        # self.history=history
        testabs = abs(timeDel)  # for>0
        # data=history[sym][atr][-1-testabs+1]

        df = history[sym]

        timeIndex = df[atr].index
        test = df.loc[timeIndex[-timeDel], atr]

        return test


def test2():
    mysymbols = ['601619.XSHG']

    start = '2019-08-12'
    end = '2019-08-15'
    tools = KDataTools(start, end, 'd')
    tools.readAllField()

    lsttest = ['PE', 'PB'] + KCommonDataTool.getAPIFieldList()
    tools.setSymbolAndField(mysymbols, lsttest)
    op = tools.getSingleData('601619.XSHG', 'openPrice', True)
    print(op)
    op = tools.getSingleData('601619.XSHG', 'PE', True)
    print(op)
    op = tools.getSingleData('601619.XSHG', 'PB', True)
    print(op)

    print(op.values)

    print(tools.getShortNameByTicked('601619'))
    print(tools.getShortNameBySymbol('601619.XSHG'))

    # start,end,freq=tools.getParam()
    # print(freq)
    # print(tools.getData('601619.XSHG','closePrice'))


########################################


if __name__ == '__main__':
    # test2()
    testTools()




































