import sys
import spotipy
import pprint

sp = None
max_artists = 100
artist_queue = []
queued = set()

'''
    This example generates a collaboration network suitable for plotting with graphviz
    Typical usage:

    % python collaborations.py 32 deadmau5 > deadmau5.gv
    % graphviz deadmau5.gv
'''

def add_artists_from_albums(name, spid):
    offset = 0
    limit = 50
    while True:
        try:
            response = sp.artist_albums(spid, limit=limit, offset=offset)
        except spotipy.SpotifyException:
            # a known issue with the API occasionally yields an error when retrieving albums
            sys.stderr.write('trouble getting albums for %s' % (name,))
            return
        for album in response['albums']:
            for artist in album['artists']:
                add_artist(name, album['name'], artist)
        offset += limit

        if not response['paging']['next']:
            break

def fn(name):
    return name.replace('"', '').encode('utf-8')

def add_artist(name, album_name, artist):
    if not artist['spotify_uri'] in queued:
        if name:
            print('  "%s" -> "%s" [label="%s"];' % (fn(name), fn(artist['name']), fn(album_name)))
        queued.add(artist['spotify_uri'])
        artist_queue.append( ( artist['name'], artist['spotify_uri']) )

def process_artists():
    done = set()
    while len(artist_queue) > 0:
        name, spid = artist_queue.pop(0)
        if spid not in done:
            done.add(spid)
            if len(queued) > max_artists:
                break
            else:
                add_artists_from_albums(name, spid)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: %s max_artists artist name' % (sys.argv[0]))
        print('Example: %s 100 Rihanna' % (sys.argv[0]))
    else:
        max_artists = int(sys.argv[1])
        artist = ' '.join(sys.argv[2:])
        sp = spotipy.Spotify()

        results = sp.search(artist, type='artist')
        artists = results['artists']
        if len(artists) > 0:
            add_artist(None, None, artists[0])
            print('digraph G {')
            process_artists()
            print('}')

