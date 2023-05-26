# -*- coding: utf-8 -*-
# @Time    : 2023/5/26 15:42
# @Author  : PFinal南丞 <lampxiezi@163.com
# @File    : getBeesproxy.py
# @Software: PyCharm
import time
from multiprocessing import Pool

import pymongo
import requests
from lxml import etree


class GetBeesproxy:
    def __init__(self, page):
        self.url = 'https://www.beesproxy.com/free/page/'
        self.headers = {
            "authority": "www.beesproxy.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://www.beesproxy.com/free",
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
        self.page = page

    def get_html(self):
        """

        :return:
        """
        url_list = [self.url + str(p) for p in range(1, self.page + 1)]
        return url_list

    def get_data(self, url):
        """get_data"""
        ip_list = []
        res = requests.get(url, headers=self.headers)
        html = etree.HTML(res.text)
        ip_port = [i.strip() for i in html.xpath('//tr/td[position()<=2]/text()')]
        num = len(ip_port)
        for q in range(0, num, 2):
            ip_a_port = 'http://' + str(ip_port[q]) + ':' + str(ip_port[q + 1])
            ip_list.append(ip_a_port)
        return ip_list

    def check_ip(self, ip):
        """check_ip"""
        try:
            res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={'http': ip},
                               timeout=2)
            if res.status_code == 200:
                print('IP可用-->', ip)
                return ip
        except Exception:
            print('IP不可用-->', ip)

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
        """ run code """
        start = time.time()
        pool = Pool(processes=2)
        url_list = self.get_html()
        ip_list = pool.map(self.get_data, url_list)
        ip_lists = []
        for i in ip_list:
            ip_lists += i
        # print(ip_lists)
        pool2 = Pool(processes=5)
        check_ip_list = pool2.map(self.check_ip, ip_lists)
        ok_ip = [i for i in check_ip_list if i is not None]
        self.save_data(ok_ip)
        print('用时:', time.time() - start)


if __name__ == '__main__':
    GetBeesproxy(20).run()
