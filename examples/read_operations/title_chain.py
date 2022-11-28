from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import random

'''
    generates a list of songs where the first word in each subsequent song
    matches the last word of the previous song.

    usage: python title_chain.py [song name]
'''

client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


skiplist = set(['dm', 'remix'])
max_offset = 500
seen = set()


def find_songs_that_start_with_word(word):
    max_titles = 20
    max_offset = 200
    offset = 0

    out = []
    while offset < max_offset and len(out) < max_titles:
        results = sp.search(q=word, type='track', limit=50, offset=offset)
        if len(results['tracks']['items']) == 0:
            break

        for item in results['tracks']['items']:
            name = item['name'].lower()
            if name in seen:
                continue
            seen.add(name)
            if '(' in name:
                continue
            if '-' in name:
                continue
            if '/' in name:
                continue
            words = name.split()
            if len(words) > 1 and words[0] == word \
                    and words[-1] not in skiplist:
                # print "        ", name, len(out)
                out.append(item)
        offset += 50
    # print "found", len(out), "matches"
    return out


def make_chain(word):
    which = 1
    while True:
        songs = find_songs_that_start_with_word(word)
        if len(songs) > 0:
            song = random.choice(songs)
            print(which, song['name'] + " by " + song['artists'][0]['name'])
            which += 1
            word = song['name'].lower().split()[-1]
        else:
            break


if __name__ == '__main__':
    import sys
    title = ' '.join(sys.argv[1:])
    make_chain(sys.argv[1].lower())
