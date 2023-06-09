# -*- coding: utf-8 -*-
# @Time    : 2023/5/16 13:58
# @Author  : PFinal南丞 <lampxiezi@163.com
# @File    : run.py
# @Software: PyCharm
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from logger import logger

from spilder.get66ip import get66Ip
from spilder.get89ip import Get89IP
from spilder.getBeesproxy import GetBeesproxy
from spilder.getGeoNodeIp import GetGeoNode
from spilder.getIp3366ip import GetIp3366
from spilder.getkxdailiip import GetKxDaiLiIp


def run():
    """Run the"""
    logger.info("开始定时")
    # executors = {
    #     'default': ThreadPoolExecutor(30)  # 最大线程数30
    # }
    # scheduler = BackgroundScheduler(executors=executors)
    try:
        GetKxDaiLiIp(10).run()  # 导入快代理
        GetIp3366(1).run()  # 导入Ip3366
        GetGeoNode().run()
        Get89IP(2).run()
        get66Ip()
        GetBeesproxy(20).run()

    except Exception as e:
        print(e)

    # scheduler.start()


if __name__ == '__main__':
    run()
