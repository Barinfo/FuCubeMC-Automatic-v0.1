from flask import Blueprint, render_template, request, abort
from config import config
import auth

app = Blueprint('panel', __name__)
auth = Auth()

@app.route('/')
def index():
    if Auth.is_token_valid(Auth.get_token(), request.cookies.get('id')):
        user_info = auth.get_info(request.cookies.get("id"))
        return render_template("panel/index.html", user_info=user_info)
    abort(401)

@app.route('/instance/')
def instance():
    if Auth.is_token_valid(Auth.get_token(), request.cookies.get('id')):
        panel_addr = config["mcsm"]["url"]
        return render_template("panel/instance.html", panel_addr=panel_addr)
    abort(401)

@app.route('/qiandao/')
def qiandao():
    if Auth.is_token_valid(Auth.get_token(), request.cookies.get('id')):
        return render_template("panel/qiandao.html")
    abort(401)