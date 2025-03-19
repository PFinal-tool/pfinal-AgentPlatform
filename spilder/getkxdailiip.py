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
from .base_proxy_scraper import BaseProxyScraper
from lxml import etree


class Getkxdailiip(BaseProxyScraper):
    def __init__(self):
        headers = {
            # 这里根据实际情况设置请求头
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        url = ["http://www.kxdaili.com"]
        super().__init__(headers, url)

    def get_html(self):
        return self.url

    def get_data(self, url):
        ip_list = []
        try:
            res = requests.get(url, headers=self.headers, timeout=2)
            html = etree.HTML(res.text)
            # 这里需要根据实际网页结构解析出 IP 地址
            # 示例代码假设 IP 地址在特定的 XPath 路径下
            ip_port = [i.strip() for i in html.xpath('//tr[position()>1]/td[position()<=2]/text()')]
            num = len(ip_port)
            for q in range(0, num, 2):
                ip_a_port = 'http://' + str(ip_port[q]) + ':' + str(ip_port[q + 1])
                ip_list.append(ip_a_port)
        except Exception as e:
            print(f"获取数据失败: {url}, 错误: {e}")
        return ip_list

if __name__ == '__main__':
    Getkxdailiip().run()