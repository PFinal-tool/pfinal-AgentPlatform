import sys
import os

from spilder.get66ip import GetFreeIP
from spilder.getGeoNodeIp import GetGeoNodeIp
from spilder.getIp3366ip import GetIp3366ip
from spilder.getLumiproxy import GetLumiproxy
from spilder.getBeesproxy import GetBeesproxy
from spilder.getkxdailiip import Getkxdailiip

# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将 spilder 目录添加到 sys.path 中
spilder_dir = os.path.join(current_dir, 'spilder')
sys.path.append(spilder_dir)

import time
import schedule


def run():
    # 执行抓取任务
    GetFreeIP(start_page=21, end_page=200).run()
    GetLumiproxy().run()

    GetBeesproxy().run()
    GetGeoNodeIp().run()

    Getkxdailiip().run()
    GetIp3366ip().run()


if __name__ == '__main__':
    # 每天的 00:00 执行任务
    schedule.every().day.at("00:00").do(run)
    while True:
        schedule.run_pending()
        time.sleep(1)
