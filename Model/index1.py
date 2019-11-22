大机构仓位:100*(1-WINNER(CLOSE)),colorred,LINETHICK3;
VAR2:=1/WINNER(CLOSE);
VAR3:=MA(CLOSE,13);
VAR4:=100-ABS((CLOSE-VAR3)/VAR3*100);
VAR5:=LLV(LOW,120);周期内最低价
VAR6:=HHV(HIGH,120);周期内最高价
VAR7:=(VAR6-VAR5)/100;
VAR8:=SMA((CLOSE-VAR5)/VAR7,20,1);移动平均
VAR9:=SMA((OPEN-VAR5)/VAR7,20,1);
VARA:=3*VAR8-2*SMA(VAR8,10,1);
VARB:=3*VAR9-2*SMA(VAR9,10,1);
VARC:=100-VARB;

# def WINNER(x):

def MA(x,n):
    re=0
    for i in range(n):
        re=re+x(i)
    return re

def SMA(x,n,m):
    re=


def LLV(x,n):
    xx=x[0:n-1]
    re=min(x)
    return re

def HHV(x,n):
    xx=x[0:n-1]
    re=max(x)
    return re

