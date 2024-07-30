from flask import Blueprint, render_template

app = Blueprint('panel', __name__)

@app.route('/')
def index():
    return render_template("panel/index.html")