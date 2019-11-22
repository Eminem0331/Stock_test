import Pre_Para as pp
import data as dd
import MLE
# open=dd.handle_data()['open']
d=1/252
close=dd.handle_data('000858.SZ.xlsx')['close']
x=close[149::].reset_index()

can_close=pp.pre_Seq(close,150)
pre_close=[]
for i in range(len(x)):
    pre_close.append(MLE.mle())
    MLE.mle()


# print(pre_open,pre_close)


