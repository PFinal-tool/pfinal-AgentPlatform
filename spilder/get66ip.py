import time
from multiprocessing import Pool

import pymongo
import requests
from lxml import etree

import sys

sys.path.append("..")

from .base_proxy_scraper import BaseProxyScraper

class GetFreeIP(BaseProxyScraper):
    def __init__(self, start_page, end_page):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Referer": "http://www.66ip.cn/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        url = ["http://www.66ip.cn/", ]
        super().__init__(headers, url, start_page=start_page, end_page=end_page)

    def get_html(self):
        url_list = [self.url[0] + f'{p}.html' for p in range(self.start_page, self.end_page + 1)]
        return url_list

    def get_data(self, url):
        ip_list = []
        try:
            res = requests.get(url, headers=self.headers, timeout=2)
            html = etree.HTML(res.text)
            ip_port = [i.strip() for i in html.xpath('//tr[position()>1]/td[position()<=2]/text()')]
            num = len(ip_port)
            for q in range(0, num, 2):
                ip_a_port = 'http://' + str(ip_port[q]) + ':' + str(ip_port[q + 1])
                ip_list.append(ip_a_port)
        except Exception as e:
            print(f"获取数据失败: {url}, 错误: {e}")
        return ip_list

if __name__ == '__main__':
    GetFreeIP(start_page=21, end_page=200).run()