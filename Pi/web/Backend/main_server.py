from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

import sys, os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

for path in sys.path:
    print(path)

from Logic.server import Server


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

endpoint = '/api/v1'

""" Vars """

ai_meeting = True
ai_coffee = True
ai_dishwasher = True


""" Sockets """

@socketio.on('connect')
def connect():
    socketio.emit('welcome', {'currentProgress': 0})

""" Ai on or off """
@socketio.on('ai_meeting')
def connect():
    global ai_meeting
    if ai_meeting:
        ai_meeting = False
    else:
        ai_meeting = True
    socketio.emit('ai_meeting_status', {'status': ai_meeting})


""" Routes """

@app.route('/')
def hallo():
    return "Server is running"



""" Class """
server = Server()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")