 # 上山爬坡型, s, m, l对应短、中、长期, t是回溯天数, x1,x2,x3分别对应短中长期均线差值的标准差阈值
    def status14(self, lll, average_line):
        t, x1, x2, x3 = lll[0], lll[1], lll[2], lll[3]
        print('calculate_status14')
        signal_list = {}
        stocks_data = self.stocks_data.copy()
        stocks = self.stocks.copy()
        n_count = 0
        
        for stock in stocks:
            n_count +=1
            if n_count%100==0 :
                print(n_count)
            data = stocks_data[stock]
            data['mas'] = MA(data['close'], average_line[0], self.tolerance_rate)
            data['mam'] = MA(data['close'], average_line[1], self.tolerance_rate)
            data['mal'] = MA(data['close'], average_line[2], self.tolerance_rate)
            
            data['para'] = data.apply(lambda x: 1 if x['mas'] > x['mam'] > x['mal'] else 0, axis=1)
            data['para_count'] = data['para'].rolling(t, round(t * self.tolerance_rate)).sum()
            #前t天内，80%的天数都是满足短线在上，长线在下的形态
            data['signal1'] = data.apply(lambda x: 1 if x['para_count'] / t >= 0.8 else 0, axis=1)
            
            # 均线值与前一日之差
            data['mas_delta'] = DELTA(data['mas'], 1)
            data['mam_delta'] = DELTA(data['mam'], 1)
            data['mal_delta'] = DELTA(data['mal'], 1)
            data['std_sd'] = STD(data['mas_delta'], t, self.tolerance_rate)
            data['std_md'] = STD(data['mam_delta'], t, self.tolerance_rate)
            data['std_ld'] = STD(data['mal_delta'], t, self.tolerance_rate)
            data['signal2'] = data.apply(lambda x: 1 if x['std_ld'] < x3 < x['std_md'] < x2 < x['std_sd'] < x1 else 0, axis=1)
            
            # 上涨趋势
            data['close_delta'] = DELTA(data['close'], t)
            data['signal3'] = data.apply(lambda x: 1 if x['close_delta'] > 0 else 0, axis=1)
            
            data['signal'] = data['signal1'] * data['signal2'] * data['signal3']
            data = data.loc[:, ['signal','close','open','trading_date']]
            signal_list[stock] = data
        save_siganl(signal_list,'data/signal_record/signal_%s_%s_%s.pickle'%('status14', str(average_line), str(lll)))