# -*- coding: utf-8 -*-
import time
import multiprocessing
import pymongo
import requests
from .base_proxy_scraper import BaseProxyScraper
from lxml import etree


class GetIp3366:
    def __init__(self, page):
        # 保持原有初始化代码
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
        # 修复URL生成
        url_list = [f'{self.url}/?page={p}.html' for p in range(1, self.page + 1)]
        return url_list

    def get_data(self, url):
        ip_list = []
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            html = etree.HTML(res.text)
            ip_trs = html.xpath('//*[@id="list"]/table/tbody/tr')
            for tr in ip_trs:
                try:
                    ip = tr.xpath("./td[1]/text()")[0]
                    prot = tr.xpath("./td[2]/text()")[0]
                    xy = tr.xpath("./td[4]/text()")[0].lower()
                    ip_list.append(f"{xy}://{ip}:{prot}")
                except IndexError:
                    continue
        except Exception as e:
            print(f"获取数据失败: {url}, 错误: {e}")
        return ip_list

    def check_ip(self, ip):
        try:
            # 修复代理设置
            protocol, address = ip.split('://')
            proxies = {protocol: ip}

            res = requests.get(
                'http://httpbin.org/ip',
                headers=self.headers,
                proxies=proxies,
                timeout=5
            )

            if res.status_code == 200:
                print('IP可用-->', ip)
                return ip
        except Exception as e:
            print(f"IP {ip} 检查失败: {e}")
        return None

    def save_data(self, ok_ip_list):
        try:
            client = pymongo.MongoClient(host='localhost', port=27017)
            db = client["ip_proxy"]
            collection = db.ip_proxy

            for d in ok_ip_list:
                # 使用update_one with upsert
                collection.update_one(
                    {'http': d},
                    {'$set': {'time': time.time()}},
                    upsert=True
                )
                print("录入新IP:", d)

            client.close()
        except Exception as e:
            print(f"保存数据失败: {e}")

    def run(self):
        # 设置多进程启动方法
        multiprocessing.set_start_method('spawn', force=True)

        start = time.time()

        # 使用上下文管理器管理进程池
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            url_list = self.get_html()
            ip_list = pool.map(self.get_data, url_list)

            # 展平ip_list
            ip_lists = [ip for sublist in ip_list for ip in sublist]

            # 过滤和检查IP
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool2:
                check_ip_list = pool2.map(self.check_ip, ip_lists)

                # 过滤有效IP
                ok_ip = [i for i in check_ip_list if i is not None]

                if ok_ip:
                    self.save_data(ok_ip)
                else:
                    print('没有可用的IP')

        print('用时:', time.time() - start)


class GetIp3366ip(BaseProxyScraper):
    def __init__(self):
        headers = {
            # 这里根据实际情况设置请求头
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }
        url = ["http://www.ip3366.net"]
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
    GetIp3366ip().run()


if __name__ == '__main__':
    GetIp3366(1).run()