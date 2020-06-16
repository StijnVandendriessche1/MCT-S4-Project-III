import functools
import os

import flask

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, BASE_DIR)

from Logic.get_vars import GetVars
import logging

logging.basicConfig(filename=f"{BASE_DIR}/data/logging.txt", level=logging.ERROR,
                    format="%(asctime)s	%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s")


get_vars = GetVars()


ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE = 'openid email profile'

AUTH_REDIRECT_URI = get_vars.get_var("RedirectURL")
BASE_URI = get_vars.get_var("BaseURL")
CLIENT_ID = get_vars.get_var("Google_Login_ClientID")
CLIENT_SECRET = get_vars.get_var("Google_Login_Secret")

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

app = flask.Blueprint('google_auth', __name__)


def is_logged_in():
    try:
        return True if AUTH_TOKEN_KEY in flask.session else False
    except Exception as ex:
        logging.error(ex)
        raise ex


def build_credentials():
    try:
        if not is_logged_in():
            raise Exception('User must be logged in')
        oauth2_tokens = flask.session[AUTH_TOKEN_KEY]
        return google.oauth2.credentials.Credentials(
            oauth2_tokens['access_token'],
            refresh_token=oauth2_tokens['refresh_token'],
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri=ACCESS_TOKEN_URI)
    except Exception as ex:
        logging.error(ex)
        raise ex




def get_user_info():
    try:
        credentials = build_credentials()

        oauth2_client = googleapiclient.discovery.build(
            'oauth2', 'v2',
            credentials=credentials)

        return oauth2_client.userinfo().get().execute()
    except Exception as ex:
        logging.error(ex)
        raise ex


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        try:
            response = flask.make_response(view(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response
        except Exception as ex:
            logging.error(ex)
    return functools.update_wrapper(no_cache_impl, view)


@app.route('/google/login')
@no_cache
def login():
    try:
        session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                                scope=AUTHORIZATION_SCOPE,
                                redirect_uri=AUTH_REDIRECT_URI)

        uri, state = session.authorization_url(AUTHORIZATION_URL)

        flask.session[AUTH_STATE_KEY] = state
        flask.session.permanent = True

        return flask.redirect(uri, code=302)
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    try:
        req_state = flask.request.args.get('state', default=None, type=None)

        if req_state != flask.session[AUTH_STATE_KEY]:
            response = flask.make_response('Invalid state parameter', 401)
            return response

        session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                                scope=AUTHORIZATION_SCOPE,
                                state=flask.session[AUTH_STATE_KEY],
                                redirect_uri=AUTH_REDIRECT_URI)

        oauth2_tokens = session.fetch_access_token(
            ACCESS_TOKEN_URI,
            authorization_response=flask.request.url)

        flask.session[AUTH_TOKEN_KEY] = oauth2_tokens

        return flask.redirect(BASE_URI, code=302)
    except Exception as ex:
        logging.error(ex)
        return "Error"


@app.route('/google/logout')
@no_cache
def logout():
    try:
        flask.session.pop(AUTH_TOKEN_KEY, None)
        flask.session.pop(AUTH_STATE_KEY, None)

        return flask.redirect(BASE_URI, code=302)
    except Exception as ex:
        logging.error(ex)
        return "Error"
