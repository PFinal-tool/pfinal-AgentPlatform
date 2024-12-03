# -*- coding: utf-8 -*-
# @Time    : 2023/4/6 10:15
# @Author  : PFinal南丞
# @Email   : lampxiezi@163.com
# @File    : getIp3366ip.py
# @Software: PyCharm

import time
from multiprocessing import Pool

import pymongo
import requests
from lxml import etree


class GetIp3366:
    def __init__(self, page):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://www.ip3366.net/free/?stype=1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }
        self.url = 'http://www.ip3366.net/free'
        self.page = page

    def get_html(self):
        url_list = [self.url + f'/?page{p}.html' for p in range(1, self.page + 1)]
        return url_list

    def get_data(self, url):
        ip_list = []
        res = requests.get(url, headers=self.headers)
        html = etree.HTML(res.text)
        ip_trs = html.xpath('//*[@id="list"]/table/tbody/tr')
        for tr in ip_trs:
            ip = tr.xpath("./td[1]/text()")[0]
            prot = tr.xpath("./td[2]/text()")[0]
            xy  = tr.xpath("./td[4]/text()")[0].lower()
            ip_list.append(xy + "://" + str(ip) +":" + str(prot)) 
        return ip_list

    def check_ip(self, ip):
        ip_info = ip.split("//")
        print(ip_info)
        try:
            res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={ip_info[0].replace('.',''): ip_info[1]},
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
        print(ip_lists)
        check_ip_list = pool2.map(self.check_ip, ip_lists)
        ok_ip = [i for i in check_ip_list if i is not None]
        if (ok_ip):  
            self.save_data(ok_ip)
        else:
            print('======')    
        print('用时:', time.time() - start)


if __name__ == '__main__':
    GetIp3366(1).run()
