# -*- coding: latin-1 -*-
import spotipy
import unittest
import pprint


class TestSpotipy(unittest.TestCase):

    creep_urn = 'spotify:track:3HfB5hBU0dmBt8T0iCmH42'
    creep_id = '3HfB5hBU0dmBt8T0iCmH42'
    creep_url = 'http://open.spotify.com/track/3HfB5hBU0dmBt8T0iCmH42'
    el_scorcho_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'
    pinkerton_urn = 'spotify:album:04xe676vyiTeYNXw15o9jT'
    weezer_urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
    pablo_honey_urn = 'spotify:album:6AZv3m27uyRxi8KyJSfUxL'
    radiohead_urn = 'spotify:artist:4Z8W4fKeB5YxbusRsdQVPb'

    bad_id = 'BAD_ID'

    def setUp(self):
        self.spotify = spotipy.Spotify()

    def test_artist_urn(self):
        artist = self.spotify.artist(self.radiohead_urn)
        self.assertTrue(artist['name'] == u'Radiohead')

    def test_artists(self):
        results = self.spotify.artists([self.weezer_urn, self.radiohead_urn])
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 2)

    def test_album_urn(self):
        album = self.spotify.album(self.pinkerton_urn)
        self.assertTrue(album['name'] == u'Pinkerton')

    def test_album_tracks(self):
        results = self.spotify.album_tracks(self.pinkerton_urn)
        self.assertTrue(len(results['items']) == 10)

    def test_albums(self):
        results = self.spotify.albums([self.pinkerton_urn, self.pablo_honey_urn])
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']) == 2)

    def test_track_urn(self):
        track = self.spotify.track(self.creep_urn)
        self.assertTrue(track['name'] == u'Creep')

    def test_track_id(self):
        track = self.spotify.track(self.creep_id)
        self.assertTrue(track['name'] == u'Creep')

    def test_track_url(self):
        track = self.spotify.track(self.creep_url)
        self.assertTrue(track['name'] == u'Creep')

    def test_tracks(self):
        results = self.spotify.tracks([self.creep_url, self.el_scorcho_urn])
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 2)

    def test_artist_top_tracks(self):
        results = self.spotify.artist_top_tracks(self.weezer_urn)
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 10)

    def test_artist_search(self):
        results = self.spotify.search(q='weezer', type='artist')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) > 0)
        self.assertTrue(results['artists'][0]['name'] == 'Weezer')

    def test_artist_albums(self):
        results = self.spotify.artist_albums(self.weezer_urn)
        self.assertTrue('items' in results)
        self.assertTrue(len(results['items']) > 0)

        found = False
        for album in results['items']:
            if album['name'] == 'Hurley':
                found = True

        self.assertTrue(found)

    def test_album_search(self):
        results = self.spotify.search(q='weezer pinkerton', type='album')
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']) > 0)
        self.assertTrue(results['albums'][0]['name'] == 'Pinkerton')

    def test_track_search(self):
        results = self.spotify.search(q='el scorcho weezer', type='track')
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) > 0)
        self.assertTrue(results['tracks'][0]['name'] == 'El Scorcho')

    def test_user(self):
        user = self.spotify.user(user_id='plamere')
        self.assertTrue(user['uri'] == 'spotify:user:plamere')

    def test_track_bad_id(self):
        try:
            track = self.spotify.track(self.bad_id)
            self.assertTrue(False)
        except spotipy.SpotifyException:
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
