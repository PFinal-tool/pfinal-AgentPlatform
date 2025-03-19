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

from .base_proxy_scraper import BaseProxyScraper
import json

class GetGeoNodeIp(BaseProxyScraper):
    def __init__(self):
        headers = {
            # 这里根据实际情况设置请求头
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        url = ["https://proxylist.geonode.com/api/proxy-list"]
        super().__init__(headers, url)

    def get_html(self):
        return self.url

    def get_data(self, url):
        ip_list = []
        try:
            res = requests.get(url, headers=self.headers, timeout=2)
            data = json.loads(res.text)
            if 'data' in data:
                for item in data['data']:
                    ip = item.get('ip')
                    port = item.get('port')
                    if ip and port:
                        ip_list.append(f'http://{ip}:{port}')
        except Exception as e:
            print(f"获取数据失败: {url}, 错误: {e}")
        return ip_list

if __name__ == '__main__':
    GetGeoNodeIp().run()