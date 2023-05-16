# -*- coding: utf-8 -*-
# @Time    : 2023/5/16 13:58
# @Author  : PFinal南丞 <lampxiezi@163.com
# @File    : run.py
# @Software: PyCharm
from spilder.get66ip import Get66Ip
from spilder.get89ip import Get89IP
from spilder.getGeoNodeIp import GetGeoNode
from spilder.getIp3366ip import GetIp3366
from spilder.getkxdailiip import GetKxDaiLiIp


def run():
    """Run the"""
    print("Running Get Ip")
    try:
        GetKxDaiLiIp(10).run()  # 导入快代理
        GetIp3366(1).run()  # 导入Ip3366
        GetGeoNode().run()
        Get89IP(2).run()
        Get66Ip()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    run()
