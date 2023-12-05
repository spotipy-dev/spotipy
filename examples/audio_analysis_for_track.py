"""
Insert module docstring
"""

# shows audio analysis for the given track

from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys

# I would include logging here, similar to the other examples in this directory (e.g. add_a_saved_album)

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# I would make sure the way arguments are retrieved is consistent between the diffrent example scripts. See get_args() in add_a_saved_album.py (this method is also used in many other eaxamples). I find that this method is clearer about what inputs are needed from the user.
if len(sys.argv) > 1:
    tid = sys.argv[1]
else:
    tid = 'spotify:track:4TTV7EcfroSLWzXRY6gLv6'



start = time.time()
analysis = sp.audio_analysis(tid)
delta = time.time() - start
print(json.dumps(analysis, indent=4))
print("analysis retrieved in %.2f seconds" % (delta,))

# for consistency, I would put the above code in a main() function, and have a if __name__ == '__main__' block below