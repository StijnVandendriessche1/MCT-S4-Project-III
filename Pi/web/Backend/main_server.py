from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

endpoint = '/api/v1'

""" Sockets """

@socketio.on('connect')
def connect():
    socketio.emit('welcome', {'currentProgress': 0})


""" Routes """

@app.route('/')
def hallo():
    return "Server is running"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")