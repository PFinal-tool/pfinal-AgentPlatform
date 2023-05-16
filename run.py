# -*- coding: utf-8 -*-
# @Time    : 2023/5/16 13:58
# @Author  : PFinal南丞 <lampxiezi@163.com
# @File    : run.py
# @Software: PyCharm
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from logger import logger


def run():
    """Run the"""
    logger.info("开始定时")
    executors = {
        'default': ThreadPoolExecutor(30)  # 最大线程数30
    }
    scheduler = BackgroundScheduler(executors=executors)
    # try:
    #     GetKxDaiLiIp(10).run()  # 导入快代理
    #     GetIp3366(1).run()  # 导入Ip3366
    #     GetGeoNode().run()
    #     Get89IP(2).run()
    #     Get66Ip()
    # except Exception as e:
    #     print(e)

    scheduler.start()


if __name__ == '__main__':
    run()
