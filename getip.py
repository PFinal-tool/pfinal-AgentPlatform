import random
import time

import aiohttp
import pymongo
import requests
from motor.motor_asyncio import AsyncIOMotorClient


class IPChecker:
    def __init__(self):
        self.client = AsyncIOMotorClient()
        self.collection = self.client.your_database.your_collection
        self.headers = {'User-Agent': 'Your User Agent'}

    async def check_single_ip(self, ip):
        ip_info = ip['http'].split("//")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://httpbin.org/ip',
                                       headers=self.headers,
                                       proxy=f"{ip_info[0]}://{ip_info[1]}",
                                       timeout=10) as res:
                    if res.status == 200:
                        json_res = await res.json()
                        if json_res['origin']:
                            print('IP可用', ip)
                            ip['time'] = time.time()
                            await self.collection.update_one({'http': ip['http']}, {"$set": ip})
                            return True
        except Exception as e:
            print('error信息--->', e)
            print(f'IP不可用,正在删除:{ip}')
            await self.collection.delete_one({'http': ip['http']})
        return False

    async def check_ip_list(self):
        success = errors = 0
        async for ip in self.collection.find({}):
            result = await self.check_single_ip(ip)
            if result:
                success += 1
            else:
                errors += 1
        return {"status": True, "success": success, 'errors': errors}


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
        while True:
            # 从集合中获取所有不同的代理 IP
            ip_list = self.collection.distinct('http')
            print(f'获取到 {len(ip_list)} 个 IP')

            if not ip_list:
                print("代理池为空，无法获取可用 IP")
                return None

            # 随机选择一个 IP
            ips = random.choice(ip_list)
            print(f'尝试使用 IP ---> {ips}')
            ip_info = ips.split("//")
            try:
                # 测试代理 IP 是否可用
                res = requests.get(
                    'http://httpbin.org/ip',
                    headers=self.headers,
                    proxies={ip_info[0].replace(':',''):ip_info[1]},
                    timeout=10
                )
                # 检查响应状态
                if res.status_code == 200 and 'origin' in res.json():
                    print(f'IP 可用 ---> {ips}')
                    return ips
            except Exception as e:
                # 如果代理不可用
                print(f'错误信息 ---> {e}')
                print(f'IP 不可用，正在删除: {ips}')
                self.collection.delete_one({'http': ips})

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

    async def check_ip_list(self):
        success = errors = 0
        checker = IPChecker()
        result = await checker.check_ip_list()
        print(result)
        return {"status": True, "success": success, 'errors': errors}

    def run(self):
        ok_ip = self.get_ip()
        self.client.close()
        return ok_ip


if __name__ == '__main__':
    GETIP().run()
