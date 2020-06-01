import logging
import os
import random
import sys
from threading import Thread
from time import sleep
from zipfile import ZipInfo

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.server import Server

logging.basicConfig(filename="Logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

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
def hallo():
    return "Server is running"

@app.route(endpoint + '/meetingbox/status')
def get_meetingbox_status():
    try:
        return jsonify({'status': server.status_meeting_box})
    except Exception as ex:
        logging.error(ex)

@app.route(endpoint + '/meetingbox/<box>/info')
def get_box_info(box):
    try:
        return server.get_info_box(box)
    except Exception as ex:
        logging.error(ex)

try:
    if __name__ == '__main__':
        socketio.run(app, host="0.0.0.0", port="5000")
except Exception as ex:
    logging.error(ex)
