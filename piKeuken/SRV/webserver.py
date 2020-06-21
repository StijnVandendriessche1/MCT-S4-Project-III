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
from flask import make_response, send_from_directory

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.pub_sub_comment import PubSubComment
from Logic.server import Server
import secrets

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s %(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")
isUpdating = False

""" FLASK """
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
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
    """This thread-function emits every 11 seconds a new coffee-left and dishwasher-status to the frontend
    """    
    global server
    try:
        while True:
            try:
                socketio.emit('status_coffee_left', {
                            'status': server.check_coffee_status()})
                socketio.emit('status_dishwasher', {
                            'status': server.check_status_dishwasher()})
                socketio.emit('status_light', {
                            'status': server.get_light()})
                sleep(11)
            except Exception as ex:
                logging.error(ex)
    except Exception as ex:
        logging.error(ex)


def notifications():
    """This thread-function emits every new notification to the frontend.
    """    
    try:
        global server
        while True:
            try:
                message = server.notifications.notification_queue.get()
                socketio.emit('new_notification', {"newNotification": message})
                server.notifications.notification_queue.task_done()
            except Exception as ex:
                logging.error(ex)
    except Exception as ex:
        logging.error(ex)

def meetingroom_status():
    """This function emits every status-change from the meetingboxes to the frontend
    """    
    try:
        global server
        while True:
            try:
                message = server.meetingbox.meetingbox_queue.get()
                socketio.emit('status_rooms', {'status': server.meetingbox.get_status()})
                server.meetingbox.meetingbox_queue.task_done()
            except Exception as ex:
                logging.error(ex)
    except Exception as ex:
        logging.error(ex)


try:
    """Starting all threads for the webserver
    """    
    #Thread for the notifications
    t_notifications = Thread(target=notifications)
    t_notifications.start()

    #Thread for the time-status (coffee-left and dishwasher-status)
    t_time_status = Thread(target=time_status)
    t_time_status.start()

    # Thread for the meetingbox-status
    t_meetingboxsystem = Thread(target=meetingroom_status)
    t_meetingboxsystem.start()
except Exception as ex:
    logging.error(ex)


""" Sockets """
@socketio.on('connect')
def connect():
    """This socket must be called when the frontend makes a connection to the backend
    """    
    try:
        if google_auth.is_logged_in():
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
            socketio.emit('status_rooms', {'status': server.meetingbox.get_status()})

            """ Coffee settings """
            socketio.emit('coffee_settings', server.coffee.get_coffee_settings())
            
            """ Dishwasher settings """
            socketio.emit('dishwasher_settings', server.dishwasher.get_dishwasher_settings())

            """ Send serverstatus to the clients """
            socketio.emit('status_server')
    except Exception as ex:
        logging.error(ex)


""" Ai on or off """
@socketio.on('ai_meeting')
def ai_meeting():
    """This function is called by the frontend for setting the ai-meeting on or off
    """    
    try:
        if google_auth.is_logged_in():
            global server
            server.change_ai_status("ai_meeting")
            if server.status_ai["ai_meeting"]:
                pubsubMeeting.send_message(jsonpickle.encode({"people": "on"}))
            else:
                pubsubMeeting.send_message(jsonpickle.encode({"people":"off"}))
            socketio.emit('status_ai_meeting', {'status': server.status_ai["ai_meeting"]})
    except Exception as ex:
        logging.error(ex)


@socketio.on('ai_coffee')
def ai_coffee():
    """This function is called by the frontend for setting the ai-coffee on or off."""
    try:
        if google_auth.is_logged_in():
            global server
            server.change_ai_status("ai_coffee")
            if server.status_ai['ai_coffee']:
                pubsubCoffee.send_message(jsonpickle.encode({"coffee": "on"}))
            else:
                pubsubCoffee.send_message(jsonpickle.encode({"coffee": "off"}))
        socketio.emit('status_ai_coffee', {
                    'status': server.status_ai["ai_coffee"]})
    except Exception as ex:
        logging.error(ex)


@socketio.on('ai_dishwasher')
def ai_dishwasher():
    """This function is called by the frontend for setting the ai-dishwasher on or off."""
    try:
        if google_auth.is_logged_in():
            global server
            server.change_ai_status("ai_dishwasher")
            if server.status_ai["ai_dishwasher"]:
                pubsubKitchen.send_message(jsonpickle.encode({"dishwasher_ai":"on"}))
            else:
                pubsubKitchen.send_message(jsonpickle.encode({"dishwasher_ai": "off"}))
            socketio.emit('status_ai_dishwasher', {
                        'status': server.status_ai["ai_dishwasher"]})
    except Exception as ex:
        logging.error(ex)


@socketio.on('status_room_change')
def status_rooms_change(data):
    """This function is called by the frontend for setting the meetingroom buzzy or empty"""
    try:
        if google_auth.is_logged_in():
            global server
            status = server.meetingbox.change_meeting_box(data["room"])
            socketio.emit('status_rooms', {'status': server.meetingbox.get_status()})
    except Exception as ex:
        logging.error(ex)


""" Routes """


@app.route('/')
def index():
    """This route returns the index.html to the frontend + Checks if the user is authenticated + authorized --> Else: redirect to the login-page

    Returns:
        HTML-Page: If the user is logged in, then he returns the index.html-page
        Redirect: If the user isn't logged in, then he redirects the user to the login-page
    """    
    try:
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()
            return render_template("index.html", user_info=user_info)
            # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        return redirect("/google/login")
    except Exception as ex:
        logging.error(ex)
        return "Error"


""" @app.route('/sw.js', methods=['GET'])
def sw():
    For getting the service-worker

    Returns:
        Javascript: This route returns a Javascript-file
    
    return app.send_static_file('sw.js') """

@app.route('/<page>')
def html(page):
    """This route returns every html page if the user is logged in

    Args:
        page (string): This var must be the page-name

    Returns:
        html-page: If the user is logged in, he returns the html-page
        Redirect: If the user is not logged in, he redirect him to the login page
    """    
    try:
        if google_auth.is_logged_in():
            user_info = google_auth.get_user_info()
            return render_template(f"{page}.html", user_info=user_info)
        return redirect("/google/login")
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

@app.route("/sw.js")
def sw():
    try:
        response=make_response(send_from_directory("static",filename="sw.js"))
        #change the content header file
        response.headers["Content-Type"]="application/javascript"
        return response
    except Exception as ex:
        logging.error(ex)
        return "Error"

@app.route(endpoint + '/meetingbox/status')
def get_meetingbox_status():
    """Getting the meetingbox status with a get-request

    Returns:
        JSON: Returns a JSON-object with the status of each meetingbox
        string: If the user is not authenticated + authenticated, then he gets an error-message
    """    
    try:
        if google_auth.is_logged_in():
            return jsonify({'status': server.meetingbox.get_status()})
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route(endpoint + '/meetingbox/<box>/info')
def get_box_info(box):
    """Get-request for getting the information about a room (incl. kitchen)

    Args:
        box (string): This var must be the roomname

    Returns:
        JSON: This returns a JSON object with the information about the room
        string: If the user is not authenticated and authorized, then he gets an error message
    """
    try:
        if google_auth.is_logged_in():
            return server.get_info_box(box)
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route(endpoint + '/notifications')
def get_notifications():
    """Route for getting all notifications

    Returns:
        JSON: Returns a JSON object (if the user is logged in) with all the notifications
        string: He returns an error message if the user is not logged in
    """
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
    """Route that returns a json object with all the coffee-data for the graph.

    Returns:
        JSON: Returns a json object with all the coffee-data for the graph if the user is logged in
        string: Returns an error-message if the user is not logged in
    """
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
    """This route returns a json object with the mean temperature of each room if the user is logged in

    Returns:
        JSON: Returns a json object with the mean temperature if the user is logged in
        string: Returns an error message if the user is not logged in
    """
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
    """This route returns a json object with the mean humidity of each room if the user is logged in

    Returns:
        JSON: Json object with the mean humidity of each room if the user is logged in
        string: Returns an error-message if the user is not logged in
    """
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
    """This route can be called by a post for setting a notification as viewed. In the URL: notification_ID

    Args:
        notification_id (string): This is the notification ID

    Returns:
        JSON: If the user is logged in, it sends a json-object to the frontend
        string: If the user is not logged in, it sends an error message
    """    
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
    """POST for changing the coffee settings

    Returns:
        JSON: Returns a True if everything went well or a False if something went wrong
        string: If the user is not logged in, it returns an error message to the client
    """    
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

@app.route(endpoint + '/settings/dishwasher', methods = ['POST'])
def change_dishwasher_settings():
    """POST for changing the coffee settings

    Returns:
        JSON: Returns a True if everything went well or a False if something went wrong
        string: If the user is not logged in, it returns an error message to the client
    """ 
    try:
        if google_auth.is_logged_in():
            global server
            """ Check if the values are correct """
            user_info=google_auth.get_user_info()
            client_data=request.get_json()
            """ Check if all values are valid """
            if len(client_data["dishwasher_duration"])>0 and len(client_data["dishwasher_hour_notification"])>0 and len(client_data["dishwasher_email"])>0:
                server.dishwasher.change_settings(client_data, user_info["id"])
            else:
                return jsonify({'status': False})
            return jsonify({'status': True})
        return authorization_error
    except Exception as ex:
        logging.error(ex)
        return jsonify({'status': False})

def update_self():
    os.system('sudo rm -rf /home/pi/MCT-S4-Project-III/')
    os.system('sudo git clone https://github.com/StijnVandendriessche1/MCT-S4-Project-III.git /home/pi/MCT-S4-Project-III')
    os.system('sudo rm -rf /home/pi/project3/*')
    os.system('cp -r /home/pi/MCT-S4-Project-III/piKeuken/. /home/pi/project3/')
    os.system('cp /home/pi/settings.json /home/pi/project3')
    os.system('sudo shutdown -r')

def update_thread():
    """This function is for updating the devices
    """
    try:
        pubsubMeeting = PubSubComment(3052736401110405)
        pubsubKitchen = PubSubComment(2817465839732274)
        pubsubCoffee = PubSubComment(2938279615337930)
        try:
            pubsubMeeting.send_message(jsonpickle.encode({"update": "test"}))
            print("meeting command sent")
        except:
            print("update meeting took very long")
        finally:
            try:
                pubsubCoffee.send_message(jsonpickle.encode({"update": "test"}))
                print("coffee command sent")
            except:
                print("update coffee took very long")
            finally:
                try:
                    pubsubKitchen.send_message(jsonpickle.encode({"update": "test"}))
                    print("kitchen command sent")
                except:
                    print("update kitchen took very long")
                finally:
                    print("all commands were sent")
    except Exception as ex:
        logging.error(ex)
        print("update failed")
    finally:
        try:
            update_self()
        except:
            print("updating self failed")

@app.route(endpoint + '/update')
def update_devices():
    """This get-route is for updating the devices

    Returns:
        JSON: It returns a JSON object with the state
    """    
    global isUpdating
    if not isUpdating:
        isUpdating = True
        try:
            update = Thread(target=update_thread)
            update.start()
            return jsonify("update gestart")
        except Exception as ex:
            logging.error(ex)
            return jsonify("someting went wrong"), 500
    else:
        return jsonify("already updating")
    

try:
    """For starting the Flask app
    """    
    if __name__ == '__main__':
        app.run(host = "0.0.0.0", port = "5000", ssl_context = (
            f'{BASE_DIR}/SRV/cert.pem', f'{BASE_DIR}/SRV/key.pem'), threaded = True)
except Exception as ex:
    logging.error(ex)
finally:
    print("server afgesloten")