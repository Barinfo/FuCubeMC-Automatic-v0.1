from flask import Blueprint, render_template
from config import config

app = Blueprint('panel', __name__)

@app.route('/')
def index():
    panel_addr = config["mcsm"]["url"]
    return render_template("panel/index.html", panel_addr=panel_addr)