# -*- coding: utf-8 -*-
# @Time    : 2023/4/6 14:54
# @Author  : PFinal南丞
# @Email   : lampxiezi@163.com
# @File    : getGeoNodeIp.py
# @Software: PyCharm
import time
from multiprocessing import Pool

import pymongo
import requests


class GetGeoNode:
    def __init__(self):
        self.url = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps'

    def get_data(self, url):
        ip_list = []
        res = requests.get(url)
        ips = res.json()['data']
        for ip in ips:
            ip_a_port = ip.get('protocols')[0] + '://' + str(ip.get('ip')) + ':' + str(ip.get('port'))
            ip_list.append(ip_a_port)
        return ip_list

    def save_data(self, ok_ip_list):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client["ip_proxy"]
        for d in ok_ip_list:
            exists = db.ip_proxy.count_documents({'http': d, 'time': time.time()})
            if exists == 0:
                db.ip_proxy.insert_one({'http': d, 'time': time.time()})
                print("录入新IP:", d)
            else:
                print("当前IP已经录入:", d)
        client.close()

    def check_ip(self, ip):
        ip_info = ip.split("//")
        try:
            res = requests.get('http://httpbin.org/ip', proxies={ip_info[0].replace(':',''): ip_info[1]},
                               timeout=2)
            if res.status_code == 200:
                print('IP可用-->', ip)
                return ip
        except Exception:
            pass

    def run(self):
        start = time.time()
        ip_lists = self.get_data(self.url)
        pool2 = Pool(processes=5)
        check_ip_list = pool2.map(self.check_ip, ip_lists)
        ok_ip = [i for i in check_ip_list if i is not None]
        self.save_data(ok_ip)
        print('用时:', time.time() - start)


if __name__ == '__main__':
    GetGeoNode().run()
