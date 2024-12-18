# -*- coding: utf-8 -*-
# @Time    : 2023/4/6 09:43
# @Author  : PFinal南丞
# @Email   : lampxiezi@163.com
# @File    : getkxdailiip.py
# @Software: PyCharm
# import requests

import time
from multiprocessing import Pool

import pymongo
import requests
from lxml import etree


class GetKxDaiLiIp:
    def __init__(self, page):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://www.kxdaili.com/dailiip/1/2.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        self.url = 'http://www.kxdaili.com/dailiip/'
        self.page = page

    def get_html(self):
        url_list = [self.url + f'2/{p}.html' for p in range(1, self.page + 1)]
        return url_list

    def get_data(self, url):
        ip_list = []
        print(url)
        res = requests.get(url, headers=self.headers)
        res.encoding = res.apparent_encoding
        html = etree.HTML(res.content)
        ip_port = [i.strip() for i in html.xpath('//tr/td[position()<=2]/text()')]
        for q in range(0, 10, 2):
            ip_a_port = 'http://' + str(ip_port[q]) + ':' + str(ip_port[q + 1])
            ip_list.append(ip_a_port)
        return ip_list

    def check_ip(self, ip):
        try:
            res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={'http': ip},
                               timeout=2)
            if res.status_code == 200:
                print('IP可用-->', ip)
                return ip
        except Exception:
            pass

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

    def run(self):
        start = time.time()
        pool = Pool(processes=2)
        url_list = self.get_html()
        ip_list = pool.map(self.get_data, url_list)
        ip_lists = []
        for i in ip_list:
            ip_lists += i
        pool2 = Pool(processes=5)
        check_ip_list = pool2.map(self.check_ip, ip_lists)
        ok_ip = [i for i in check_ip_list if i is not None]
        self.save_data(ok_ip)
        print('用时:', time.time() - start)


if __name__ == '__main__':
    GetKxDaiLiIp(10).run()
