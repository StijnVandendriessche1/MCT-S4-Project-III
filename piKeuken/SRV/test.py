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

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from oauthlib.oauth2 import WebApplicationClient
import requests


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.server import Server
from Logic.get_vars import GetVars
from Models.user import User

logging.basicConfig(filename="Logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

get_vars = GetVars()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

login_manager = LoginManager()
login_manager.init_app(app)

endpoint = '/api/v1'

# Configuration
GOOGLE_CLIENT_ID = get_vars.get_var("Google_Login_ClientID")
GOOGLE_CLIENT_SECRET = get_vars.get_var("Google_Login_Secret")
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

client = WebApplicationClient(GOOGLE_CLIENT_ID)

""" Objects """
server = Server()

""" Functions """

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return user_id


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
    if current_user.is_authenticated:
        return "Server is running"
    else:
        return '<a class="button" href="/login">Google Login</a>'

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/login')
def login():
    try:
        
        # Find out what URL to hit for Google login
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Use library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)
    except Exception as ex:
        logging.error(ex)
        return "error"

@app.route("/login/callback")
def callback():
    try: 
        # Get authorization code Google sent back to you
        code = request.args.get("code")
        # Find out what URL to hit to get tokens that allow you to ask for
        # things on behalf of a user
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]

        logging.error("1")

        token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
        )
        
        logging.error("2")

        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

        logging.error("3")

        # Parse the tokens!
        client.parse_request_body_response(json.dumps(token_response.json()))

        logging.error("4")

        # Now that you have tokens (yay) let's find and hit the URL
        # from Google that gives you the user's profile information,
        # including their Google profile image and email
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        logging.error("5")

        # You want to make sure their email is verified.
        # The user authenticated with Google, authorized your
        # app, and now you've verified their email through Google!
        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
        else:
            return "User email not available or not verified by Google.", 400

        logging.error("6")

        # Create a user in your db with the information provided
        # by Google
        user = User(
            id_=unique_id, name=users_name, email=users_email, profile_pic=picture
        )

        logging.error("7")

        # Begin user session by logging the user in
        login_user(user)

        logging.error("8")

        # Send user back to homepage
        return "ok"

    except Exception as ex:
        logging.error(ex)
        return ex

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
