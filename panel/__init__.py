from flask import Blueprint, render_template
from config import config

app = Blueprint('panel', __name__)

@app.route('/')
def index():
    return render_template("panel/index.html")

@app.route('/instance/')
def instance():
    panel_addr = config["mcsm"]["url"]
    return render_template("panel/instance.html", panel_addr=panel_addr)