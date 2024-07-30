from flask import Blueprint, render_template, request
from config import config
import auth

app = Blueprint('panel', __name__)

@app.route('/')
def index():
    user_info = auth.get_info(request.cookies.get("ID"))
    return render_template("panel/index.html", user_info=user_info)

@app.route('/instance/')
def instance():
    panel_addr = config["mcsm"]["url"]
    return render_template("panel/instance.html", panel_addr=panel_addr)

@app.route('/qiandao/')
def qiandao():
    return render_template("panel/qiandao.html")