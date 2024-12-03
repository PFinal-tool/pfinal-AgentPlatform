# -*- coding: utf-8 -*-
# @Time    : 2024/12/3 14:38
# @Author  : PFinal南丞 <lampxiezi@163.com
# @File    : getFreeProxy.py
# @Software: PyCharm
import requests


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Proxy-Connection": "keep-alive",
    "Referer": "http://free-proxy.cz/zh/proxylist/country/all/http/ping/all",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

url = "http://free-proxy.cz/zh/proxylist/country/all/http/ping/all/2"
response = requests.get(url, headers=headers, verify=False)

print(response.text)
print(response)

# //*[@id="proxy_list"]/tbody/tr[1]