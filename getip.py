import random
import time

import pymongo
import requests


class GETIP:
    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.collection = self.client["ip_proxy"]['ip_proxy']

    def get_ip(self):
        ip_list = self.collection.distinct('http')
        print(f'获取ip{len(ip_list)}个', )
        ips = random.choice(ip_list)
        print('用这个ip请求--->', ips)
        try:
            res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={'http': f'{ips}'}, timeout=2)
            if res.json()['origin'] and res.status_code == 200:
                print('IP可用', ips)
                return ips
        except Exception as e:
            print('error信息--->', e)
            print(f'IP不可用,正在删除:{ips}')
            ip_list.remove(ips)
            self.collection.delete_one({'http': ips})
            self.get_ip()

    def get_all_ip_list(self):
        ip_list = self.collection.find({})
        ips = []
        for ip in ip_list:
            timeArray = time.localtime(int(ip['time']))
            ips.append({
                'ip': ip['http'].split("//")[1].split(":")[0],
                'port': ip['http'].split(":")[2],
                'http': ip['http'].split("//")[0],
                'time': time.strftime("%Y-%m-%d", timeArray)
            })
        return {"ip_list": ips, "ip_count": len(ips)}

    def check_ip_list(self):
        success = errors = 0
        for ip in self.collection.find({}):
            try:
                res = requests.get('http://httpbin.org/ip', headers=self.headers, proxies={'http': f"{ip['http']}"},
                                   timeout=2)
                if res.json()['origin'] and res.status_code == 200:
                    print('IP可用', ip)
                    ip['time'] = time.time()
                    self.collection.update_one({'http': ip['http']}, {"$set": ip})
                    success += 1
            except Exception as e:
                print('error信息--->', e)
                print(f'IP不可用,正在删除:{ip}')
                self.collection.delete_one({'http': ip['http']})
                errors += 1
        return {"status": True, "success": success, 'errors': errors}

    def run(self):
        ok_ip = self.get_ip()
        self.client.close()
        return ok_ip


if __name__ == '__main__':
    print(GETIP().run())
