"""
Prerequisites

    pip3 install spotipy Flask Flask-Session

    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // added to your [app settings](https://developer.spotify.com/dashboard/applications)
    // on Windows, use `SET` instead of `export`

Run app.py

    python3 -m flask run --port=8080
"""

import os
from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path(session.get('uuid')))

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        session['token_info'] = auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not session.get('token_info'):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth=session.get('token_info')['access_token'])
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a>'


@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path(session.get('uuid')))
    session.clear()
    return redirect('/')


@app.route('/playlists')
def playlists():
    token_info = session.get('token_info')

    if not token_info:
        return redirect('/')

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    return spotify.current_user_playlists()


def session_cache_path(session_uuid):
    return caches_folder + session_uuid