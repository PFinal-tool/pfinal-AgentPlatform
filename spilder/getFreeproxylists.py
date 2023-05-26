# -*- coding: utf-8 -*-
# @Time    : 2023/5/26 16:10
# @Author  : PFinal南丞 <lampxiezi@163.com
# @File    : getFreeproxylists.py
# @Software: PyCharm
import time

import pymongo
import requests
from lxml import etree


class GetFreeproxylists:
    def __init__(self):
        self.headers = {
            "authority": "freeproxylists.net",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://freeproxylists.net/zh/?c=CN&pt=&pr=HTTP&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0",
            "sec-ch-ua": "\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }

    def get_data(self, url):
        """get data from"""
        ip_list = []
        params = {
            "c": "CN",
            "pt": "",
            "pr": "HTTP",
            "a%5B%5D": "2",
            "u": "0"
        }
        res = requests.get(url, headers=self.headers, params=params)
        html = etree.HTML(res.content.decode('utf-8'))
        # /html/body/div/div[2]/table/tbody/tr[2]/td[2]
        trs = html.xpath('//table[@class="DataGrid"]//tr[position()>1]')
        for i in trs:
            # /html/body/div/div[2]/table/tbody/tr[2]/td[1]/a
            ip = i.xpath('./td[1]/text()')
            print(ip)
            prot = i.xpath('./td[2]/text()')[0]
            print(prot)
        # print(ip_port)
        # num = len(ip_port)
        # for q in range(0, num, 2):
        #     ip_a_port = 'http://' + str(ip_port[q]) + ':' + str(ip_port[q + 1])
        #     ip_list.append(ip_a_port)
        # print(ip_list)
        return ip_list

    def check_ip(self, ip):
        """Check ip"""
        try:
            res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={'http': ip},
                               timeout=2)
            if res.status_code == 200:
                print('IP可用-->', ip)
                return ip
        except:
            print('IP不可用-->', ip)

    def save_data(self, ok_ip_list):
        client = pymongo.MongoClient(host='0.0.0.0', port=27017)
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
        """ run code """
        start = time.time()
        url = "https://freeproxylists.net/zh/"
        ip_lists = self.get_data(url)
        # pool2 = Pool(processes=5)
        # check_ip_list = pool2.map(self.check_ip, ip_lists)
        # ok_ip = [i for i in check_ip_list if i is not None]
        # self.save_data(ok_ip)
        # print('用时:', time.time() - start)


if __name__ == '__main__':
    GetFreeproxylists().run()
