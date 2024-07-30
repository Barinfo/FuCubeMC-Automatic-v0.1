from flask import Blueprint, render_template
from config import config

app = Blueprint('panel', __name__)

@app.route('/')
def index():
    user_info = {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "avatar": "https://",
        "role": "admin"
    }
    return render_template("panel/index.html", user_info=user_info)

@app.route('/instance/')
def instance():
    panel_addr = config["mcsm"]["url"]
    return render_template("panel/instance.html", panel_addr=panel_addr)

@app.route('/qiandao/')
def qiandao():
    return render_template("panel/qiandao.html")