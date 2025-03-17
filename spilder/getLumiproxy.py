# -*- coding: utf-8 -*-
# @Time    : 2024/12/3 14:04
# @Author  : PFinal南丞 <lampxiezi@163.com>
# @File    : getLumiproxy.py
# @Software: PyCharm
import asyncio
import logging
import time

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

from getip import check_single_ip

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class GetLumiproxy:
    """
    GetLumiproxy class for fetching and processing proxy data from the API.
    """

    def __init__(self, page, mongo_host='localhost', mongo_port=27017):
        self.url = 'https://api.lumiproxy.com/web_v1/free-proxy/list'
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        self.max_page = page
        self.params = {
            "page_size": "60",
            "page": "1",
            "language": "zh-hans"
        }
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        self.client = AsyncIOMotorClient(mongo_host, mongo_port)
        self.collection = self.client['ip_proxy']['ip_proxy']

    def params_list(self):
        """Generate list of parameters for each page."""
        params_list = []
        for i in range(1, self.max_page + 1):
            params = self.params.copy()
            params['page'] = str(i)
            params_list.append(params)
        return params_list

    async def fetch_data(self, session, params):
        """Fetch proxy data from the API asynchronously."""
        ip_list = []
        try:
            async with session.get(self.url, headers=self.headers, params=params, timeout=10) as res:
                if res.status == 200:
                    data = await res.json()
                    for i in data['data']['list']:
                        ip = i['ip']
                        port = i['port']
                        ip_a_port = f'http://{ip}:{port}'
                        ips_a_port = f'https://{ip}:{port}'
                        ip_list.append(ip_a_port)
                        ip_list.append(ips_a_port)
        except Exception as e:
            logging.error(f"Error fetching data with params {params}: {e}")
        return ip_list

    async def process_ip(self, ip):
        """Process and update the IP in the database."""
        test_urls = [
            'http://httpbin.org/ip',
            'https://api.ipify.org',
            'http://ip-api.com/json'
        ]
        result = await check_single_ip(ip, self.headers, test_urls)
        if result:
            await self.collection.update_one({'http': ip}, {'$set': {'time': time.time()}})
        else:
            await self.collection.delete_one({'http': ip})

    async def run(self):
        """Run the proxy fetching process."""
        start = time.time()
        params_list = self.params_list()
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_data(session, params) for params in params_list]
            all_ip_lists = await asyncio.gather(*tasks)

        ip_lists = [ip for sublist in all_ip_lists for ip in sublist]
        logging.info(f"Fetched IPs: {ip_lists}")

        tasks = [self.process_ip(ip) for ip in ip_lists]
        await asyncio.gather(*tasks)
        logging.info(f"Total time taken: {time.time() - start} seconds")


if __name__ == '__main__':
    asyncio.run(GetLumiproxy(20).run())
