from flask import Flask, send_from_directory
import os
import ujson as json

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as file:
    config = json.load(file)

port = config['port']

app = Flask(__name__, static_folder='public')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)