import functools
import json
import os

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import google_auth

import logging
import os
import random
import sys
import json
from threading import Thread
from time import sleep
from zipfile import ZipInfo

from flask import Flask, jsonify, request, redirect, request, url_for
from flask_cors import CORS
from flask_socketio import SocketIO

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.server import Server
from flask.templating import render_template
import flask

logging.basicConfig(filename="piKeuken/data/logging_webserver.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

app = Flask(__name__, static_folder="templates")
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')
authorization_error = 'You are not currently logged in.'

app.register_blueprint(google_auth.app)


endpoint = '/api/v1'

""" Objects """
server = Server()

""" Functions """
def time_status():
    global server
    while True:
        try:
            socketio.emit('status_coffee_left', {'status': server.check_coffee_status()})
            socketio.emit('status_dishwasher', {'status': server.check_status_dishwasher()})
            sleep(11)
        except Exception as ex:
            logging.error(ex)

try:
    t_mqtt = Thread(target=time_status)
    t_mqtt.start()
except Exception as ex:
    logging.error(ex)


""" Sockets """
@socketio.on('connect')
def connect():
    try:
        global server
        """ Ai on or off """
        socketio.emit('status_ai_meeting', {'status': server.status_ai["ai_meeting"]})
        socketio.emit('status_ai_coffee', {
                    'status': server.status_ai["ai_coffee"]})
        socketio.emit('status_ai_dishwasher', {
                    'status': server.status_ai["ai_dishwasher"]})

        """ Status coffee + dishwasher """
        socketio.emit('status_coffee_left', {
                    'status': server.check_coffee_status()})
        socketio.emit('status_dishwasher', {
                    'status': server.check_status_dishwasher()})

        """ Status of the rooms """
        socketio.emit('status_rooms', {'status': server.status_meeting_box})

        """ Send serverstatus to the clients """
        socketio.emit('status_server')
    except Exception as ex:
        logging.error(ex)


""" Ai on or off """
@socketio.on('ai_meeting')
def ai_meeting():
    try:
        if google_auth.is_logged_in():
            global server
            status = server.change_ai_status("ai_meeting")
            socketio.emit('status_ai_meeting', {
                        'status': server.status_ai["ai_meeting"]})
    except Exception as ex:
        logging.error(ex)


@socketio.on('ai_coffee')
def ai_coffee():
    try:
        global server
        status = server.change_ai_status("ai_coffee")
        socketio.emit('status_ai_coffee', {
                    'status': server.status_ai["ai_coffee"]})
    except Exception as ex:
        logging.error(ex)


@socketio.on('ai_dishwasher')
def ai_dishwasher():
    try:
        global server
        status = server.change_ai_status("ai_dishwasher")
        socketio.emit('status_ai_dishwasher', {
                    'status': server.status_ai["ai_dishwasher"]})
    except Exception as ex:
        logging.error(ex)


@socketio.on('status_room_change')
def status_rooms_change(data):
    try:
        global server
        status = server.change_meeting_boxs(data["room"])
        socketio.emit('status_rooms', {'status': server.status_meeting_box})
    except Exception as ex:
        logging.error(ex)


""" Routes """

@app.route('/')
def index():
    try:
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()
            return render_template("index.html", user_info = user_info)
            #return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        return redirect("/google/login")
    except Exception as ex:
        logging.error(ex)

@app.route('/<page>')
def html(page):
    try:
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()
            return render_template(f"{page}.html", user_info = user_info)
            #return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        return redirect("/google/login")
    except Exception as ex:
        logging.error(ex)

""" Router for the css """
@app.route('/css/<page>.css')
def css(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"/css/{page}.css")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

""" Route for the js """
@app.route('/js/<page>.js')
def js(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"/js/{page}.js")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

@app.route('/<page>.json')
def js_root(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.json")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

""" Router for img """
@app.route('/<page>.png')
def img_root_png(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.png")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

@app.route('/<page>.svg')
def img_root_svg(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.svg")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

@app.route('/images/<page>.jpg')
def img(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.svg")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

@app.route('/<page>.appache')
def cache(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.appache")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)

@app.route(endpoint + '/meetingbox/status')
def get_meetingbox_status():
    try:
        if google_auth.is_logged_in():
            return jsonify({'status': server.status_meeting_box})
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"

@app.route(endpoint + '/meetingbox/<box>/info')
def get_box_info(box):
    try:
        if google_auth.is_logged_in():
            return server.get_info_box(box)
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"


try:
    if __name__ == '__main__':
        app.run(host="0.0.0.0", port="5000", ssl_context='adhoc')
except Exception as ex:
    logging.error(ex)
