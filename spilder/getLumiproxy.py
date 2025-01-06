# -*- coding: utf-8 -*-
# @Time    : 2024/12/3 14:04
# @Author  : PFinal南丞 <lampxiezi@163.com>
# @File    : getLumiproxy.py
# @Software: PyCharm
import time
from multiprocessing import Pool

import pymongo
import requests


class GetLumiproxy:
    def __init__(self, page):
        self.url = 'https://api.lumiproxy.com/web_v1/free-proxy/list'
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self.max_page = page
        self.params = {
            "page_size": "60",
            "page": "1",
            "language": "zh-hans"
        }

    def check_ip(self, ip):
        """check_ip"""
        ip_info = ip.split("//")
        try:
            res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={ip_info[0].replace(':',''): ip_info[1]}, timeout=2)
            if res.status_code == 200:
                return ip
        except Exception:
            return None

    def params_list(self):
        params_list = []
        for i in range(1, self.max_page + 1):
            self.params['page'] = str(i)
            params_list.append(self.params)
        return params_list

    def get_data(self, params_list):
        """get_data"""
        ip_list = []
        try:
            res = requests.get(self.url, headers=self.headers, params=params_list, timeout=2)
            res.encoding = res.apparent_encoding
            data = res.json()['data']['list']
            for i in data:
                ip = i['ip']
                port = i['port']
                ip_a_port = 'http://' + str(ip) + ':' + str(port)
                ips_a_port = 'https://' + str(ip) + ':' + str(port)
                ip_list.append(ip_a_port)
                ip_list.append(ips_a_port)
            return ip_list
        except Exception as e:
            print(e)
            return []

    def save_data(self, ok_ip_list):
        """save_data"""
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

    def run(self):
        start = time.time()
        pool = Pool(processes=2)
        params_list = self.params_list()
        ip_list = pool.map(self.get_data, params_list)
        ip_lists = []
        for i in ip_list:
            ip_lists += i
        print(ip_lists)
        pool2 = Pool(processes=5)
        check_ip_list = pool2.map(self.check_ip, ip_lists)
        ok_ip = [i for i in check_ip_list if i is not None]
        self.save_data(ok_ip)
        print('用时:', time.time() - start)


if __name__ == '__main__':
    GetLumiproxy(20).run()