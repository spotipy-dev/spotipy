import requests

''' A simple and thin Python library for the Spotify Web API
'''


class SpotifyException(Exception):
    def __init__(self, http_status, code, msg):
        self.http_status = http_status
        self.code = code
        self.msg = msg

    def __str__(self):
        return u'http status: {0}, code:{1} - {2}'.format(
            self.http_status, self.code, self.msg)


class Spotify(object):
    def __init__(self):
        self.prefix = 'https://api.spotify.com/v1/'

    def _internal_call(self, verb, method, params):
        url = self.prefix + method
        args = dict(params=params)
        r = requests.request(verb, url, **args)
        if r.status_code >= 400 and r.status_code < 500:
            self._error(u'ERROR {0} {1}'.format(r.status_code, r.url))
        if r.status_code != 200:
            raise SpotifyException(r.status_code, -1, u'the requested resource could not be found')
        return r.json()

    def get(self, method, args=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('GET', method, kwargs)

    def _error(self, msg):
        print('ERROR - ' + msg)

    def _warn(self, msg):
        print('warning:' + msg)

    def track(self, track_id):
        ''' returns a single track given the track's ID, URN or URL
        '''

        trid = self._get_id('track', track_id)
        return self.get('tracks/' + trid)

    def tracks(self, tracks):
        ''' returns a list of tracks given the track IDs, URNs, or URLs
        '''

        tlist = [self._get_id('track', t) for t in tracks]
        return self.get('tracks/?ids=' + ','.join(tlist))

    def artist(self, artist_id):
        ''' returns a single artist given the artist's ID, URN or URL
        '''

        trid = self._get_id('artist', artist_id)
        return self.get('artists/' + trid)

    def artists(self, artists):
        ''' returns a list of artists given the artist IDs, URNs, or URLs
        '''

        tlist = [self._get_id('artist', a) for a in artists]
        return self.get('artists/?ids=' + ','.join(tlist))

    def album(self, album_id):
        ''' returns a single album given the album's ID, URN or URL
        '''

        trid = self._get_id('album', album_id)
        return self.get('albums/' + trid)

    def albums(self, albums):
        ''' returns a list of albums given the album IDs, URNs, or URLs
        '''

        tlist = [self._get_id('album', a) for a in albums]
        return self.get('albums/?ids=' + ','.join(tlist))

    def search(self, q, limit=10, offset=0, type='track'):
        ''' searches for an item
        '''
        return self.get('search', q=q, limit=limit, offset=offset, type=type)

    def user(self, user_id):
        ''' Gets basic profile information about a Spotify User
        '''
        return self.get('users/' + user_id)

    def _get_id(self, type, id):
        fields = id.split(':')
        if len(fields) == 3:
            if type != fields[1]:
                self._warn('expected id of type ' + type + ' but found type ' + fields[2] + " " + id)
            return fields[2]
        fields = id.split('/')
        if len(fields) >= 3:
            itype = fields[-2]
            if type != itype:
                self._warn('expected id of type ' + type + ' but found type ' + itype + " " + id)
            return fields[-1]
        return id
