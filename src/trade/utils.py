# encoding=utf-8
import datetime
import pytz
import os

def unix_ms_to_str(unix_time_ms, time_format='%Y%m%d%H%M%S'):
    return datetime.datetime.fromtimestamp(float(unix_time_ms)/1000).astimezone(pytz.timezone('Asia/Shanghai')).strftime(time_format)

def get_now_time_str(time_format='%Y%m%d%H%M%S'):
    return datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime(time_format)

def time_format_change(time_str, input_format="%Y%m%d:%H%M%S", output_format="%Y%m%d%H%M%S"):
    date_obj = datetime.datetime.strptime(str(time_str), input_format)
    return datetime.datetime.strftime(date_obj, output_format)

def cal_date(start_time, offset):
    start_day = datetime.datetime.strptime(str(start_time), "%Y%m%d")
    delta_day = (start_day+datetime.timedelta(days=offset)).strftime("%Y%m%d")
    return delta_day

def get_readable_time(time_str):
    # input: 20220402160000
    # output: 2022-04-02/16:00:00
    return f'{time_str[0:4]}-{time_str[4:6]}-{time_str[6:8]}/{time_str[8:10]}:{time_str[10:12]}:{time_str[12:14]}'

def get_new_filename(dir_name, save_file_num=1000, name_format='%Y%m%d%H%M%S'):
    # dir
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    # clear old file
    filelist = os.listdir(dir_name)
    if len(filelist) > save_file_num:
        filelist.sort(reverse=True)
        for name in filelist[save_file_num:]:
            delete_path = os.path.join(dir_name, name)
            os.remove(delete_path)
    # new filename
    file_time = datetime.datetime.now().strftime(name_format)
    fpath = os.path.join(dir_name, file_time)
    return fpath

def print_dataframe(df):
    try:
        from tabulate import tabulate
        print(tabulate(df, headers='keys', tablefmt='psql'))
    except:
        print(df)

def random_split(max_val=10, num=1, sigma=1000):
    if num <= 1:
        return [max_val]
    import random
    max_val_sigma = abs(int(max_val * sigma))
    random_ret = random.sample(range(0, max_val_sigma), num-1)
    random_ret.sort()
    random_ret = [0] + [it/float(sigma) for it in random_ret] + [abs(max_val)]
    res = []
    for index in range(len(random_ret)-1):
        res.append(random_ret[index+1]-random_ret[index])
    if max_val < 0:
        res = [-it for it in res]
    return res

def random_num(min_val=0, max_val=10, num=1, sigma=1):
    import random
    min_val = int(min_val * sigma)
    max_val = int(max_val * sigma)
    random_ret = random.sample(range(min_val, max_val), num)
    random_ret = [it/float(sigma) for it in random_ret]
    return random_ret

if __name__ == '__main__':
    # print(time_format_change('20220406:000000'))
    print(random_split(-1))