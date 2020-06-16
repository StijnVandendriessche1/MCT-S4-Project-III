import json
import logging
import os
import sys
# from crypt import methods
from threading import Thread
from time import sleep
import jsonpickle

import google_auth
from flask import Flask, jsonify, redirect, request
from flask.templating import render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sslify import SSLify

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.pub_sub_comment import PubSubComment
from Logic.server import Server

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s %(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'Secret!'
socketio = SocketIO(app, cors_allowed_origins='*')
authorization_error = 'You are not currently logged in.'

app.register_blueprint(google_auth.app)
sslify = SSLify(app)


endpoint = '/api/v1'

""" Objects """
server = Server()
pubsubMeeting = PubSubComment(3052736401110405)
pubsubKitchen = PubSubComment(2817465839732274)
pubsubCoffee = PubSubComment(2938279615337930)

""" Functions """


def time_status():
    global server
    try:
        # if google_auth.is_logged_in():
        while True:
            try:
                socketio.emit('status_coffee_left', {
                            'status': server.check_coffee_status()})
                socketio.emit('status_dishwasher', {
                            'status': server.check_status_dishwasher()})
                sleep(11)
            except Exception as ex:
                logging.error(ex)
    except Exception as ex:
        logging.error(ex)


def notifications():
    try:
        global server
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()
            while True:
                try:
                    message = server.notifications.notification_queue.get()
                    socketio.emit('new_notification', json.dumps(
                        server.get_notifications(user_info)))
                    server.notifications.notification_queue.task_done()
                except Exception as ex:
                    logging.error(ex)
    except Exception as ex:
        logging.error(ex)


try:
    t_mqtt = Thread(target=notifications)
    t_mqtt.start()

    t_notifications = Thread(target=time_status)
    t_notifications.start()
except Exception as ex:
    logging.error(ex)


""" Sockets """
@socketio.on('connect')
def connect():
    try:
        global server
        """ Ai on or off """
        socketio.emit('status_ai_meeting', {
                      'status': server.status_ai["ai_meeting"]})
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

        """ Coffee settings """
        socketio.emit('coffee_settings', server.coffee.get_coffee_settings())

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
            if server.status_ai["ai_meeting"]:
                pubsubMeeting.send_message(jsonpickle.encode({"people": "on"}))
            else:
                pubsubMeeting.send_message(jsonpickle.encode({"people":"off"}))
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
            return render_template("index.html", user_info=user_info)
            # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        return redirect("/google/login")
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')

@app.route('/<page>')
def html(page):
    try:
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()
            return render_template(f"{page}.html", user_info=user_info)
        return redirect("/google/login")
    except Exception as ex:
        logging.error(ex)
        return "Error"


""" Router for the css """
@app.route('/css/<page>.css')
def css(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"/css/{page}.css")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


""" Route for the js """
@app.route('/js/<page>.js')
def js(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"/js/{page}.js")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/<page>.json')
def js_root(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.json")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


""" Router for img """
@app.route('/<page>.png')
def img_root_png(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.png")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/<page>.svg')
def img_root_svg(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.svg")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/images/<page>.jpg')
def img(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.svg")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/<page>.appache')
def cache(page):
    try:
        if google_auth.is_logged_in():
            return render_template(f"{page}.appache")
        return 'You are not currently logged in.'
    except Exception as ex:
        logging.error(ex)
        return "Error"


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


@app.route(endpoint + '/notifications')
def get_notifications():
    try:
        if google_auth.is_logged_in():
            global server
            user_info = google_auth.get_user_info()
            return json.dumps(server.get_notifications(user_info))
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"

@app.route(endpoint + '/graph/coffee/week')
def get_graph_coffee_week():
    try:
        if google_auth.is_logged_in():
            global server
            user_info = google_auth.get_user_info()
            return server.get_coffee_day_of_week()
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"

@app.route(endpoint + '/graph/temperature/room')
def get_graph_temperature_room():
    try:
        if google_auth.is_logged_in():
            global server
            user_info = google_auth.get_user_info()
            return server.get_temperature_by_room()
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"

@app.route(endpoint + '/graph/humidity/room')
def get_graph_humidity_room():
    try:
        if google_auth.is_logged_in():
            global server
            user_info = google_auth.get_user_info()
            return server.get_humidity_by_room()
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"

@app.route(endpoint + '/notifications/<notification_id>', methods=['POST'])
def notifications_viewed(notification_id):
    try:
        if google_auth.is_logged_in():
            global server
            """ When the user viewed the notification """
            user_info = google_auth.get_user_info()
            server.notifications.notification_viewed(
                notification_id, user_info["id"])
            return jsonify({'status': True, 'nid': notification_id})
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return jsonify({'status': False})

@app.route(endpoint + '/settings/coffee', methods = ['POST'])
def change_coffee_settings():
    try:
        if google_auth.is_logged_in():
            global server
            """ Check if the values are correct """
            user_info=google_auth.get_user_info()
            client_data=request.get_json()
            coffee_left_threshold=float(
                client_data["coffee_left_threshold"])*1000.0
            delivery_time=int(client_data["delivery_time"])
            mail_supplier=client_data["mail_supplier"]
            client_data["coffee_left_threshold"]=str(coffee_left_threshold)
            client_data["mail_message"]=client_data["mail_message"].replace(
                '\n', '<br>')
            """ Check if all values are valid """
            if coffee_left_threshold > 0 and coffee_left_threshold <= 90000 and delivery_time > 0 and delivery_time <= 111 and len(mail_supplier) > 0:
                server.coffee.change_settings(client_data, user_info["id"])
            else:
                return jsonify({'status': False})
            return jsonify({'status': True})
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return jsonify({'status': False})

try:
    if __name__ == '__main__':
        app.run(host = "0.0.0.0", port = "5000", ssl_context = (
            f'{BASE_DIR}/SRV/cert.pem', f'{BASE_DIR}/SRV/key.pem'), threaded = True)
except Exception as ex:
    logging.error(ex)


""" 🚚 Your coffee is on it's way!
☕ Your coffee has arrived to the office!
😢 Oh no! Coffee is finished, Time for starbucks 🚶‍♀️
🍽 The Dishwasher is empty! Time to empty it!
💩 Don't forget to fill in the dishwasher! """
