from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.server import Server
import logging
import random

logging.basicConfig(filename="Logging.txt", level=logging.ERROR, format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")



app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

endpoint = '/api/v1'

""" Objects """
server = Server()


""" Sockets """


@socketio.on('connect')
def connect():
    global server
    """ Ai on or off """
    socketio.emit('status_ai_meeting', {'status': server.status_ai["ai_meeting"]})
    socketio.emit('status_ai_coffee', {'status': server.status_ai["ai_coffee"]})
    socketio.emit('status_ai_dishwasher', {'status': server.status_ai["ai_dishwasher"]})
    coffee_left = round(random.uniform(11, 31), 1)
    socketio.emit('status_coffee_left', {'status': coffee_left})
    socketio.emit('status_server')
    


""" Ai on or off """
@socketio.on('ai_meeting')
def ai_meeting():
    global server
    status = server.change_ai_status("ai_meeting")
    socketio.emit('status_ai_meeting', {'status': server.status_ai["ai_meeting"]})

@socketio.on('ai_coffee')
def ai_coffee():
    global server
    status = server.change_ai_status("ai_coffee")
    socketio.emit('status_ai_coffee', {'status': server.status_ai["ai_coffee"]})

@socketio.on('ai_dishwasher')
def ai_dishwasher():
    global server
    status = server.change_ai_status("ai_dishwasher")
    socketio.emit('status_ai_dishwasher', {'status': server.status_ai["ai_dishwasher"]})


""" Routes """


@app.route('/')
def hallo():
    return "Server is running"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")
