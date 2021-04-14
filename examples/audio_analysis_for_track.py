# shows audio analysis for the given track

from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys


auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

if len(sys.argv) > 1:
    tid = sys.argv[1]
else:
    tid = 'spotify:track:4TTV7EcfroSLWzXRY6gLv6'

start = time.time()
analysis = sp.audio_analysis(tid)
delta = time.time() - start
print(json.dumps(analysis, indent=4))
print(f"analysis retrieved in {delta:.2f} seconds")
