# -*- coding: utf-8 -*-
# @Time    : 2023/4/6 13:46
# @Author  : PFinal南丞
# @Email   : lampxiezi@163.com
# @File    : apscheduler.py
# @Software: PyCharm
from concurrent.futures import ThreadPoolExecutor

from apscheduler.schedulers.background import BackgroundScheduler
from logger import logger

from spilder.get66ip import run_get66ip


def main():
    logger.info("开始定时")

    executors = {
        'default': ThreadPoolExecutor(30)  # 最大线程数30
    }
    scheduler = BackgroundScheduler(executors=executors)
    scheduler.add_job(run_get66ip, "cron", hour="0-6")
    scheduler.start()


if __name__ == '__main__':
    main()
