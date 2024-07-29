from flask import Flask, send_from_directory, abort
import os
import ujson as json

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)

app = Flask(__name__, static_folder='templates')


@app.route('/<path:filename>')
def serve_static(filename):
    # 检查是否请求的是非HTML文件
    if '.' in filename and filename.rsplit('.', 1)[-1].lower() != 'html':
        try:
            return send_from_directory(app.static_folder, filename)
        except FileNotFoundError:
            abort(404)

    # 如果请求的是HTML文件或路径不确定，尝试查找带有.html后缀的文件
    html_filename = f'{filename}.html'
    try:
        return send_from_directory(app.static_folder, html_filename)
    except FileNotFoundError:
        abort(404)


@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
        config = json.load(file)
    app.run(host='0.0.0.0', port=config['port'], threaded=True)


@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config['port'], threaded=True)
