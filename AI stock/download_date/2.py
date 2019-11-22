import threading
import datetime


def do_job():
    print('I Love YOU')
    global timer
    timer = threading.Timer(86400, do_job) # 86400秒就是一天
    timer.start()

# 计算当前时间到指定时间点的描述差
def get_interval_secs(target_time):
    today = (datetime.date.today()).strftime('%Y%m%d')
    today_time = today + "-" + target_time
    today_time_date = datetime.datetime.strptime(today_time, '%Y%m%d-%H:%M:%S')
    now = datetime.datetime.now()
    interval = today_time_date - now
    secs = interval.total_seconds()
    if (secs > 0): return secs
    else: return secs + 86400

timer = threading.Timer(get_interval_secs("11:50:00"), do_job)
timer.start()