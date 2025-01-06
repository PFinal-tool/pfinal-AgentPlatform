import logging

from quart import Quart, jsonify, request, render_template

import getip
from getip import GETIP

app = Quart(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 首页路由
@app.route('/', methods=['GET'])
async def home():
    """

    :return:
    """
    return await render_template('404.html')


# IP 列表页面
@app.route('/index', methods=['GET'])
async def index():
    """

    :return:
    """
    key = request.args.get('key')
    if key != '123321':
        logging.warning("Invalid key provided for /index route")
        return jsonify({'status': False, 'data': None})
    ip_list = GETIP().get_all_ip_list()
    return await render_template('index.html', **ip_list)


# 检查 IP 路由
@app.route('/check', methods=['GET'])
async def check():
    """

    :return:
    """
    key = request.args.get('key')
    print(key)
    if key != '123321':
        logging.warning("Invalid key provided for /check route")
        return jsonify({'status': False, 'data': None})
    result = await getip.check_ip_list()
    return jsonify({'status': True, 'data': result})


# 获取可用 IP 的 API
@app.route('/api', methods=['GET'])
async def api():
    """

    :return:
    """
    key = request.args.get('key')
    if key != '123321':
        logging.warning("Invalid key provided for /api route")
        return jsonify({'status': False, 'data': None})
    ok_ip = GETIP().run()
    return jsonify({'status': True, 'data': {'http': ok_ip}})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8456)
