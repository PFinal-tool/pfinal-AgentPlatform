from flask import Flask, jsonify, request, render_template

from getip import GETIP

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('404.html')


@app.route('/index', methods=['GET'])
def index():
    key = request.args.get('key')
    if key != '123321':
        return jsonify({'status': False, 'data': None})
    ip_list = GETIP().get_all_ip_list()
    return render_template('index.html', **ip_list)


@app.route('/check', methods=['GET'])
def check():
    result = GETIP().check_ip_list()
    return jsonify({'status': True, 'data': result})


@app.route('/api', methods=['GET'])
def api():
    key = request.args.get('key')
    if key != '123321':
        return jsonify({'status': False, 'data': None})
    ok_ip = GETIP().run()
    return jsonify({'status': True, 'data': {'http': ok_ip}})


if __name__ == '__main__':
    from gevent import pywsgi
    server = pywsgi.WSGIServer(('0.0.0.0', 8456), app)
    server.serve_forever()
