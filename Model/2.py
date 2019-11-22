# 单模块情况下, 多模块就import module1,  然后getattr(module1....)
import sys
def bar(a):
    return a

def foo():

    return 1
'''
stra 为传入函数的字符串名 vlist为需要传入函数的参数列表 不需要参数，请传入空列表
'''
def check_str(stra,vlist):
    mod = sys.modules[__name__]
    if hasattr(mod, stra):
        command_act= getattr(mod, stra)
        # 统计函数需要的参数个数
        parameter_count = command_act.__code__.co_argcount
        if parameter_count == 0:
            command_act()
        else:
            command_act(*vlist)
    else:
        print("No this module")

# 例子
check_str("bar",[1])
check_str("foo",[0])