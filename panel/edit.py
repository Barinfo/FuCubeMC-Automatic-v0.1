from flask import Blueprint, render_template, request, abort, redirect
from config import config
from auth import Auth

app = Blueprint('panel_edit', __name__)
auth = Auth()

id = request.cookies.get('id')

@app.route('/')
def index():
    if Auth.is_token_valid(Auth.get_token(), id):
        redirect("/panel/")
    abort(401)


@app.route('/user_info/')
def instance():
    if Auth.is_token_valid(Auth.get_token(), id):
        redirect("/panel/")
    abort(401)