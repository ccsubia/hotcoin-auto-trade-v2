# -*- coding:utf-8 -*-
# Author : Hu
# Data : 2022/4/5 21:00
import csv

import numpy as np
from pandas import read_csv


# 读csv
def read_csv_file(path):
    return read_csv(path)


# 保存csv
def save_csv(path, data):
    data.to_csv(path, encoding='utf_8_sig', index=False, sep=',')


# 保存行
def add_csv_rows(path, data):
    np_data = np.array(data)
    csv_data = np_data.tolist()
    with open(path, 'a', encoding="utf_8_sig", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)


# 保存列名
def save_csv_head(head, path):
    with open(path, 'w', encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(head)
