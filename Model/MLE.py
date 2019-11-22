from scipy.optimize import minimize
import pandas as pd
import numpy as np
import scipy.optimize as opt
import math

def model(x,x0,d,param):
    print(param)
    a = param[0]
    b = param[1]
    sigma = param[2]

    y = 2 / (math.sqrt(x) * sigma)
    y0 = 2 /(math.sqrt(x0) * sigma)
    sx = sigma * x ** (3 / 2)
    # print('sx=',sx)
    # print(math.log(sx))
    re = -math.log(2 * math.pi * d) / 2\
         - math.log(sx)+ (-(1 / 2)) * (y - y0) **2/d\
         + (a * (-y **2 + y0**2) * sigma**2 + (-8 * b + 6 * sigma**2) * math.log(y / y0)) / (4 * sigma**2)\
         + (-((1 / (24 * y * y0 * sigma**4)) * (48 * b ** 2 + 24 * b * (-2 + a * y * y0) * sigma**2 + (
            9 - 24 * a * y * y0 + a**2 * y * y0 * (y**2 + y * y0 + y0**2)) * sigma**4))) *d \
         + (-((48 * b**2 - 48 * b * sigma**2 + (9 + a**2 * y**2 * y0**2) * sigma**4) / (
            24 * y**2 * y0**2 * sigma**4))) * (d**2 / 2)
    return re

def logdensity2loglik(x,d,param):
    n = len(x) - 1
    re = 0
    for i in range(n):
        re = re + model(x[i+1], x[i], d, param)
    return re

def pre_price(x,d,p):
    re=[]
    for i in range(len(x)):
        max = x[i] * (1 + 0.1)
        min = x[i] * (1 - 0.1)
        ll = (max - min) / 0.01
        lg = []
        for j in range(ll + 1):
            aa= model(min+ 0.01 * j, x[i],d, p[i])
            lg.append(aa)
        bb = lg.index(max(lg))
        cc = bb* 0.01 + min
        re.append(cc)
    return re


def mle(x,d,param0):

    def objfun(param):
        return -logdensity2loglik(x,d,param)

    re=list(opt.fmin(objfun,param0,xtol=1e-2,ftol=1e-3,))
    #
    # re = minimize(objfun,x0=param0, method="L-BFGS-B",tol=1e-3,
    #               bounds=[(-50,50),(-50,50),(0.001, 100)])
    # out=list(re.x)
    # return out
    return re

# x=pd.read_excel('data.xlsx')
# x=x['data']
# d=1/252
# # #
# p=[0.05, 0.05, 0.05]
# p=[0.5,0.5,0.5]
# p=[0.78323481721275023, -0.091698870749236217, 0.014223479253006991]
# # #
# # re=-logdensity2loglik(x,d,p)
# #
# y=list(x[0:149])
# #
# # print(y)
# # re=logdensity2loglik(y,d,p)
# # # print(re)x
# # # print(y)
# re=mle(x,d,p)
# # a=list(re.x)
# print('re=',re,re[0],re[1],re[2])
# print(type(re))
# #
# if p==re:
#     print('Yes',re)
# else:
#     p=re
#     print('No',re)

# re=model(7.628038913,7.594149208,d,p)
# print(re)
