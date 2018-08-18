#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2018/7/13 19:38
# @Author : Vimin
# @File : iptest.py
import requests

IPList = [

    "182.84.94.243:42804",
    "14.106.106.4:31339",
    "121.232.148.21:49046",
    "115.211.225.150:36933",
    "114.99.8.203:43179",
    "49.81.11.18:40239",
    "59.52.187.127:40580",
    "116.226.31.6:21228",
    "114.222.131.81:43519",
]


def is_available(ip):
    """
    检验IP是否可用
    :param ip:
    :return:
    """
    proxies = {
        'http': 'http://%s' % ip,
        'https': 'http://%s' % ip
    }
    try:
        res_data = requests.get('https://www.nyloner.cn/checkip',
                                proxies=proxies, timeout=5).json()
        remote_ip = res_data['remote_ip']
    except:
        return False
    if remote_ip in ip:
        return True
    return False


if __name__ == '__main__':
    for ip in IPList:
        print(is_available(ip))
