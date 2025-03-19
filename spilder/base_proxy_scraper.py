import time
import multiprocessing
import pymongo
import requests
from lxml import etree

class BaseProxyScraper:
    def __init__(self, headers, url, page=None, start_page=None, end_page=None):
        self.headers = headers
        self.url = url
        self.page = page
        self.start_page = start_page
        self.end_page = end_page

    def get_html(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def get_data(self, url):
        raise NotImplementedError("Subclasses should implement this method.")

    def check_ip(self, ip):
        try:
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
        multiprocessing.set_start_method('spawn', force=True)
        start = time.time()
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            url_list = self.get_html()
            ip_list = pool.map(self.get_data, url_list)
            ip_lists = [ip for sublist in ip_list for ip in sublist]
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool2:
                check_ip_list = pool2.map(self.check_ip, ip_lists)
                ok_ip = [i for i in check_ip_list if i is not None]
                if ok_ip:
                    self.save_data(ok_ip)
                else:
                    print('没有可用的IP')
        print('用时:', time.time() - start)
