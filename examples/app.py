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

Session(app)


@app.route('/')
def index():
    cache_path = '.cache-'.join(str(uuid.uuid4()))
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
    if request.args.get("code"):
        session['token_info'] = auth_manager.get_access_token(request.args["code"], check_cache=False)
        return redirect('/')

    if not session['token_info']:
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'
    print(session['token_info'])
    spotify = spotipy.Spotify(auth=session['token_info']['access_token'])
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
           f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
           f'<a href="/playlists">my playlists</a>'


@app.route('/sign_out')
def sign_out():
    session.clear()
    return redirect('/')


@app.route('/playlists')
def playlists():
    token_info = session['token_info']
    if not token_info:
        return redirect('/')
    spotify = spotipy.Spotify(auth=token_info['access_token'])
    return spotify.current_user_playlists()
