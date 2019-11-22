# -*- coding:utf-8
import requests
import time
import pandas as pd
from collections import OrderedDict
from datetime import date, datetime, timedelta


# 提取网页信息
def getNewsDetail(item_list):
    '''item_list: list格式的返回报文'''
    news_list = []
    for item in item_list:  # 对每一条快讯循环
        news = OrderedDict()  # 每一条信息一个dict，所有信息组成一个list，方便转换为dataframe
        # 保存快讯的发布时间、内容、标签
        news['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['display_time']))
        news['id'] = item['id']
        news['content'] = item['content_text'].replace('\n', "")
        # 相关股票, 包括代码和股票名
        news['symbols'] = item['symbols']
        news_list.append(news)
    return news_list


# 计算指定日期的前N天的时间戳
def get_day_time(n, yyyy, mm, dd):
    the_date = datetime(yyyy, mm, dd)                              # 指定开始日期，datetime格式
    pre_date = the_date - timedelta(days=n)                        # 回溯日期，datetime格式
    pre_date = pre_date.strftime('%Y-%m-%d %H:%M:%S')              # 将回溯日期转换为指定的str格式
    pre_time = time.strptime(pre_date, "%Y-%m-%d %H:%M:%S")        # 将时间转化为数组形式
    pre_stamp = int(time.mktime(pre_time))                         # 将时间转化为时间戳形式
    return pre_stamp

# api_url
APIurl = 'https://api-prod.wallstreetcn.com/apiv1/content/lives'

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept': 'application/json, */*'}

# 参数
pc_params = {'channel': 'a-stock-channel',  # A股信息，可改为其他模块
             'client': 'pc',
             'cursor': 0,                   # 当前时间
             'limit': 100}                  # 单次请求最多100条


news_list = []

# 通过限制循环次数控制总爬取条数，单循环爬取200条。
# for Loop_count in range(1):
#     resp = requests.get(APIurl, headers=headers, params=pc_params)
#     content = resp.json()['data']
#     print(content)
#     pc_params['cursor'] = content['next_cursor']  # 在请求头中加入当前时间，保证爬取的连续性
#     news_list.extend(getNewsDetail(content['items']))


# 通过控制cursor参数精确到截止爬取日期

# 回溯时间戳，一周之前
forward_cursor = get_day_time(180, 2019, 5, 7)
# 当前时间戳
current_cursor = int(time.time())
i = 1
while current_cursor >= forward_cursor:
    print(i)
    resp = requests.get(APIurl, headers=headers, params=pc_params)
    print(resp)
    content = resp.json()['data']
    pc_params['cursor'] = content['next_cursor']  # 在请求头中加入当前时间，保证爬取的连续性
    news_list.extend(getNewsDetail(content['items']))
    current_cursor = int(content['next_cursor'])
    i += 1


df = pd.DataFrame(news_list)
df.to_csv(r'E:\my_project\spider\astock_newsflash.csv')

