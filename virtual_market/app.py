# -*- coding=utf-8 -*-
from flask import Flask, render_template, redirect, url_for, Response, jsonify
import os
import json
import sys
from flask import request
from werkzeug.routing import BaseConverter


app = Flask(__name__)
app.secret_key = 'some_secret'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def hello_world():
    # return 'Hello World!'
    return render_template('layuimini/index.html')

@app.route('/api/init', methods=['GET'])
def init_data():
    with open(os.path.join(BASE_DIR,"templates/layuimini/api/init.json"), "r", encoding="utf-8") as fr:
        data = json.load(fr)
    return data

@app.route('/api/table', methods=['GET'])
def table_data():
    with open(os.path.join(BASE_DIR,"templates/layuimini/api/table.json"), "r", encoding="utf-8") as fr:
        data = json.load(fr)
    return data

@app.route('/api/tableselect', methods=['GET'])
def table_select_data():
    with open(os.path.join(BASE_DIR,"templates/layuimini/api/tableSelect.json"), "r", encoding="utf-8") as fr:
        data = json.load(fr)
    return data

@app.route('/api/menus', methods=['GET'])
def menus_data():
    with open(os.path.join(BASE_DIR,"templates/layuimini/api/menus.json"), "r", encoding="utf-8") as fr:
        data = json.load(fr)
    return data

@app.before_request
def handle_before_request():
    """在每次请求之前都被执行"""
    full_path = request.path
    full_path = full_path.split("?")[0]
    if ".html/" in full_path:
        full_path = full_path.split(".html/")[0] + ".html"
    if full_path.endswith(".html"):
        return render_template('layuimini/%s' % full_path)

if __name__ == '__main__':
    # app.wsgi_app = Middleware(app.wsgi_app)
    app.run()
