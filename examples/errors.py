# shows acoustic features for tracks for the given artist

from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys


client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
sp.trace=True
try:
    print ('bad call 0')
    bad_artist_call = sp.artist('spotify:artist:12341234')
except spotipy.client.SpotifyException:
    print ('bad call 0 exception' )

print ('bad call 1')
bad_artist_call = sp.artist('spotify:artist:12341234')
print ('bad artist', bad_artist_call)

