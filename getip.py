import asyncio
import logging
import random
import time

import pymongo
import requests
import urllib3  # 新增导入
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class IPChecker:
    """
       IPChecker 类用于检查代理IP的可用性。
    """

    def __init__(self):
        self.client = AsyncIOMotorClient()
        self.collection = self.client['ip_proxy']['ip_proxy']
        self.headers = {'User-Agent': 'Your User Agent'}
        self.test_urls = [
            'http://httpbin.org/ip',
            'https://api.ipify.org',
            'http://ip-api.com/json'
        ]

    async def check_single_ip(self, ip, max_retries=3):
        """

        :param ip:
        :param max_retries:
        :return:
        """
        return await check_single_ip(ip, self.headers, self.test_urls, max_retries)

    async def process_ip(self, ip):
        """Process and update the IP in the database."""
        result = await self.check_single_ip(ip)
        if result:
            await self.collection.update_one({'http': ip['http']}, {'$set': {'time': time.time()}})
        else:
            await self.collection.delete_one({'http': ip['http']})

    async def check_ip_list(self):
        """
        检查IP列表
        :return:
        """
        logging.info("Starting check_ip_list")
        success = errors = 0
        tasks = []
        async for ip in self.collection.find({}):
            logging.info(f"Adding task for IP: {ip['http']}")
            tasks.append(self.process_ip(ip))

        if not tasks:
            logging.warning("No tasks created. Database might be empty.")
        else:
            await asyncio.gather(*tasks)

        logging.info(f"Check completed. Success: {success}, Errors: {errors}")
        return {"status": True, "success": success, 'errors': errors}


async def check_single_ip(ip, headers, test_urls, max_retries=3):
    """
    检查单个IP的可用性
    :param ip: 要检查的IP地址
    :param headers: 请求头
    :param test_urls: 测试URL列表
    :param max_retries: 最大重试次数
    :return: 可用的IP地址或False
    """
    for attempt in range(max_retries):
        ip_info = ip['http'].split("//")
        proxy = {ip_info[0].replace(':', ''): ip_info[1]}  # 构建代理字典
        logging.info(f"尝试代理: {proxy}")

        for test_url in test_urls:
            try:
                # 将同步请求封装到函数中
                def sync_request():
                    """
                    执行同步请求
                    :return: 请求响应
                    """
                    return requests.get(
                        test_url,
                        headers=headers,
                        proxies=proxy,
                        timeout=10
                    )

                # 在异步环境中运行同步请求
                res = await asyncio.get_running_loop().run_in_executor(None, sync_request)

                logging.info(f'IP {ip["http"]} 返回状态码 {res.status_code} 使用 URL {test_url}')
                if res.status_code == 200:
                    logging.info(f'IP可用-->{ip} 使用 URL {test_url}')
                    return ip['http']
            except requests.exceptions.ConnectTimeout:
                logging.error(f'尝试 {attempt + 1}/{max_retries} 连接超时 {ip["http"]} 使用 URL {test_url}')
            except urllib3.exceptions.MaxRetryError:  # 修正异常引用
                logging.error(f'尝试 {attempt + 1}/{max_retries} 重试次数超限 {ip["http"]} 使用 URL {test_url}')
            except requests.exceptions.ReadTimeout:  # 新增异常处理
                logging.error(f'尝试 {attempt + 1}/{max_retries} 读取超时 {ip["http"]} 使用 URL {test_url}')
            except Exception as e:
                logging.error(f'尝试 {attempt + 1}/{max_retries} 失败 {ip["http"]} 使用 URL {test_url}: {str(e)}', exc_info=True)
            if attempt == max_retries - 1:
                break
            await asyncio.sleep(1)  # 在重试之前等待1秒

    logging.info(f'IP不可用: {ip}')
    return False


async def check_ip_list():
    """
     清洗代理
    :return:
    """
    checker = IPChecker()
    result = await checker.check_ip_list()

    # Directly use the success and errors values from the result
    success = result.get('success', 0)
    errors = result.get('errors', 0)

    print(f"Check completed. Success: {success}, Errors: {errors}")

    return {
        "status": True,
        "success": success,
        'errors': errors,
        'result': result  # 包含详细结果
    }


class GETIP:
    """
        GETIP 类用于从 MongoDB 数据库中获取代理 IP。
    """

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
        """

        :return:
        """
        while True:
            # 从集合中获取所有不同的代理 IP
            ip_list = self.collection.distinct('http')
            logging.info(f'获取到 {len(ip_list)} 个 IP')

            if not ip_list:
                logging.warning("代理池为空，无法获取可用 IP")
                return None

            # 随机选择一个 IP
            ips = random.choice(ip_list)
            logging.info(f'尝试使用 IP ---> {ips}')
            ip_info = ips.split("//")
            try:
                # 测试代理 IP 是否可用
                res = requests.get(
                    'http://httpbin.org/ip',
                    headers=self.headers,
                    proxies={ip_info[0].replace(':', ''): ip_info[1]},
                    timeout=10
                )
                # 检查响应状态
                if res.status_code == 200 and 'origin' in res.json():
                    logging.info(f'IP 可用 ---> {ips}')
                    return ips
            except Exception as e:
                # 如果代理不可用
                logging.error(f'错误信息 ---> {e}')
                logging.info(f'IP 不可用，正在删除: {ips}')
                self.collection.delete_one({'http': ips})

    def get_all_ip_list(self):
        """

        :return:
        """
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

    def run(self):
        """

        :return:
        """
        ok_ip = self.get_ip()
        self.client.close()
        return ok_ip


if __name__ == '__main__':
    asyncio.run(check_ip_list())

