# -*- coding: latin-1 -*-

import spotipy
from  spotipy import util
import unittest
import pprint
import sys
import simplejson as json

'''
    Since these tests require authentication they are maintained
    separately from the other tests.

    These tests try to be benign and leave your collection and
    playlists in a relatively stable state.
'''

class AuthTestSpotipy(unittest.TestCase):
    '''
        These tests require user authentication
    '''

    playlist = "spotify:user:plamere:playlist:2oCEWyyAPbZp9xhVSxZavx"
    four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp", 
                "spotify:track:7IHOIqZUUInxjVkko181PB",
                "4VrWlk8IQxevMvERoX08iC", 
                "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]

    two_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp", 
                "spotify:track:7IHOIqZUUInxjVkko181PB"]

    other_tracks=["spotify:track:2wySlB6vMzCbQrRnNGOYKa", 
            "spotify:track:29xKs5BAHlmlX1u4gzQAbJ",
            "spotify:track:1PB7gRWcvefzu7t3LJLUlf"]

    bad_id = 'BAD_ID'

    def test_track_bad_id(self):
        try:
            track = spotify.track(self.bad_id)
            self.assertTrue(False)
        except spotipy.SpotifyException:
            self.assertTrue(True)


    def test_basic_user_profile(self):
        user = spotify.user(username)
        self.assertTrue(user['id'] == username)

    def test_current_user(self):
        user = spotify.current_user()
        self.assertTrue(user['id'] == username)

    def test_me(self):
        user = spotify.me()
        self.assertTrue(user['id'] == username)

    def test_user_playlists(self):
        playlists = spotify.user_playlists(username, limit=5)
        self.assertTrue('items' in playlists)
        self.assertTrue(len(playlists['items']) == 5)

    def test_user_playlist_tracks(self):
        playlists = spotify.user_playlists(username, limit=5)
        self.assertTrue('items' in playlists)
        for playlist in playlists['items']:
            user = playlist['owner']['id']
            pid = playlist['id']
            results = spotify.user_playlist_tracks(user, pid)
            self.assertTrue(len(results['items']) >= 0)

    def user_playlist_tracks(self, user, playlist_id = None, fields=None, 
        limit=100, offset=0):

        # known API issue currently causes this test to fail
        # the issue is that the API doesn't currently respect the
        # limit paramter

        self.assertTrue(len(playlists['items']) == 5)

    def test_current_user_saved_tracks(self):
        tracks = spotify.current_user_saved_tracks()
        self.assertTrue(len(tracks['items']) > 0)

    def test_current_user_saved_albums(self):
        albums = spotify.current_user_saved_albums()
        self.assertTrue(len(albums['items']) > 0)

    def test_current_user_playlists(self):
        playlists = spotify.current_user_playlists(limit=10)
        self.assertTrue('items' in playlists)
        self.assertTrue(len(playlists['items']) == 10)

    def test_user_playlist_follow(self):
        spotify.user_playlist_follow_playlist('plamere', '4erXB04MxwRAVqcUEpu30O')
        follows = spotify.user_playlist_is_following('plamere', '4erXB04MxwRAVqcUEpu30O', ['plamere'])

        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertTrue(follows[0], 'is following')
        spotify.user_playlist_unfollow('plamere', '4erXB04MxwRAVqcUEpu30O')

        follows = spotify.user_playlist_is_following('plamere', '4erXB04MxwRAVqcUEpu30O', ['plamere'])
        self.assertTrue(len(follows) == 1, 'proper follows length')
        self.assertFalse(follows[0], 'is no longer following')


    def test_current_user_save_and_unsave_tracks(self):
        tracks = spotify.current_user_saved_tracks()
        total = tracks['total']

        spotify.current_user_saved_tracks_add(self.four_tracks)

        tracks = spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertTrue(new_total - total == len(self.four_tracks))

        tracks = spotify.current_user_saved_tracks_delete(self.four_tracks)
        tracks = spotify.current_user_saved_tracks()
        new_total = tracks['total']
        self.assertTrue(new_total == total)


    def test_categories(self):
        response = spotify.categories()
        self.assertTrue(len(response['categories']) > 0)

    def test_category_playlists(self):
        response = spotify.categories()
        for cat in response['categories']['items']:
            cat_id = cat['id']
            response = spotify.category_playlists(category_id=cat_id)
            self.assertTrue(len(response['playlists']["items"]) > 0)
    
    def test_new_releases(self):
        response = spotify.new_releases()
        self.assertTrue(len(response['albums']) > 0)

    def test_featured_releases(self):
        response = spotify.featured_playlists()
        self.assertTrue(len(response['playlists']) > 0)

    def test_current_user_follows(self):
        response = spotify.current_user_followed_artists()
        artists = response['artists']
        self.assertTrue(len(artists['items']) > 0)

    def test_current_user_top_tracks(self):
        response = spotify.current_user_top_tracks()
        items = response['items']
        self.assertTrue(len(items) > 0)

    def test_current_user_top_artists(self):
        response = spotify.current_user_top_artists()
        items = response['items']
        self.assertTrue(len(items) > 0)

    def get_or_create_spotify_playlist(self, username, playlist_name):
        playlists = spotify.user_playlists(username)
        while playlists:
            for item in playlists['items']:
                if item['name'] == playlist_name:
                    return item['id']
            playlists = spotify.next(playlists)
        playlist = spotify.user_playlist_create(username, playlist_name)
        playlist_id = playlist['uri']
        return playlist_id

    def test_user_playlist_ops(self):
        # create empty playlist
        playlist_id = self.get_or_create_spotify_playlist(username, 
                'spotipy-testing-playlist-1')

        # remove all tracks from it

        spotify.user_playlist_replace_tracks(username, playlist_id,[])

        playlist = spotify.user_playlist(username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 0)
        self.assertTrue(len(playlist['tracks']['items']) == 0)

        # add tracks to it

        spotify.user_playlist_add_tracks(username, playlist_id, self.four_tracks)
        playlist = spotify.user_playlist(username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 4)
        self.assertTrue(len(playlist['tracks']['items']) == 4)

        # remove two tracks from it

        spotify.user_playlist_remove_all_occurrences_of_tracks (username, 
                    playlist_id, self.two_tracks)

        playlist = spotify.user_playlist(username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 2)
        self.assertTrue(len(playlist['tracks']['items']) == 2)

        # replace with 3 other tracks
        spotify.user_playlist_replace_tracks(username, 
            playlist_id, self.other_tracks)

        playlist = spotify.user_playlist(username, playlist_id)
        self.assertTrue(playlist['tracks']['total'] == 3)
        self.assertTrue(len(playlist['tracks']['items']) == 3)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
        del sys.argv[1]

        scope = 'playlist-modify-public '
        scope += 'user-library-read '
        scope += 'user-follow-read '
        scope += 'user-library-modify '
        scope += 'user-read-private '
        scope += 'user-top-read'

        token = util.prompt_for_user_token(username, scope)
        spotify = spotipy.Spotify(auth=token)
        spotify.trace = False
        unittest.main()
    else:
        print("Usage: %s username" % (sys.argv[0],))
