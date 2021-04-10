# -*- coding: utf-8 -*-

from spotipy import (
    Spotify,
    SpotifyClientCredentials,
    SpotifyException
)
import spotipy
import unittest
import requests


class AuthTestSpotipy(unittest.TestCase):
    """
    These tests require client authentication - provide client credentials
    using the following environment variables

    ::

        'SPOTIPY_CLIENT_ID'
        'SPOTIPY_CLIENT_SECRET'
    """

    playlist = "spotify:user:plamere:playlist:2oCEWyyAPbZp9xhVSxZavx"
    four_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                   "spotify:track:7IHOIqZUUInxjVkko181PB",
                   "4VrWlk8IQxevMvERoX08iC",
                   "http://open.spotify.com/track/3cySlItpiPiIAzU3NyHCJf"]

    two_tracks = ["spotify:track:6RtPijgfPKROxEzTHNRiDp",
                  "spotify:track:7IHOIqZUUInxjVkko181PB"]

    other_tracks = ["spotify:track:2wySlB6vMzCbQrRnNGOYKa",
                    "spotify:track:29xKs5BAHlmlX1u4gzQAbJ",
                    "spotify:track:1PB7gRWcvefzu7t3LJLUlf"]

    bad_id = 'BAD_ID'

    creep_urn = 'spotify:track:6b2oQwSGFkzsMtQruIWm2p'
    creep_id = '6b2oQwSGFkzsMtQruIWm2p'
    creep_url = 'http://open.spotify.com/track/6b2oQwSGFkzsMtQruIWm2p'
    el_scorcho_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQJ'
    el_scorcho_bad_urn = 'spotify:track:0Svkvt5I79wficMFgaqEQK'
    pinkerton_urn = 'spotify:album:04xe676vyiTeYNXw15o9jT'
    weezer_urn = 'spotify:artist:3jOstUTkEu2JkjvRdBA5Gu'
    pablo_honey_urn = 'spotify:album:6AZv3m27uyRxi8KyJSfUxL'
    radiohead_urn = 'spotify:artist:4Z8W4fKeB5YxbusRsdQVPb'
    angeles_haydn_urn = 'spotify:album:1vAbqAeuJVWNAe7UR00bdM'
    heavyweight_urn = 'spotify:show:5c26B28vZMN8PG0Nppmn5G'
    heavyweight_id = '5c26B28vZMN8PG0Nppmn5G'
    heavyweight_url = 'https://open.spotify.com/show/5c26B28vZMN8PG0Nppmn5G'
    reply_all_urn = 'spotify:show:7gozmLqbcbr6PScMjc0Zl4'
    heavyweight_ep1_urn = 'spotify:episode:68kq3bNz6hEuq8NtdfwERG'
    heavyweight_ep1_id = '68kq3bNz6hEuq8NtdfwERG'
    heavyweight_ep1_url = 'https://open.spotify.com/episode/68kq3bNz6hEuq8NtdfwERG'
    reply_all_ep1_urn = 'spotify:episode:1KHjbpnmNpFmNTczQmTZlR'

    @classmethod
    def setUpClass(self):
        self.spotify = Spotify(
            client_credentials_manager=SpotifyClientCredentials())
        self.spotify.trace = False

    def test_audio_analysis(self):
        result = self.spotify.audio_analysis(self.four_tracks[0])
        assert('beats' in result)

    def test_audio_features(self):
        results = self.spotify.audio_features(self.four_tracks)
        self.assertTrue(len(results) == len(self.four_tracks))
        for track in results:
            assert('speechiness' in track)

    def test_audio_features_with_bad_track(self):
        bad_tracks = ['spotify:track:bad']
        input = self.four_tracks + bad_tracks
        results = self.spotify.audio_features(input)
        self.assertTrue(len(results) == len(input))
        for track in results[:-1]:
            if track is not None:
                assert('speechiness' in track)
        self.assertTrue(results[-1] is None)

    def test_recommendations(self):
        results = self.spotify.recommendations(
            seed_tracks=self.four_tracks,
            min_danceability=0,
            max_loudness=0,
            target_popularity=50)
        self.assertTrue(len(results['tracks']) == 20)

    def test_artist_urn(self):
        artist = self.spotify.artist(self.radiohead_urn)
        self.assertTrue(artist['name'] == 'Radiohead')

    def test_artists(self):
        results = self.spotify.artists([self.weezer_urn, self.radiohead_urn])
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 2)

    def test_album_urn(self):
        album = self.spotify.album(self.pinkerton_urn)
        self.assertTrue(album['name'] == 'Pinkerton')

    def test_album_tracks(self):
        results = self.spotify.album_tracks(self.pinkerton_urn)
        self.assertTrue(len(results['items']) == 10)

    def test_album_tracks_many(self):
        results = self.spotify.album_tracks(self.angeles_haydn_urn)
        tracks = results['items']
        total, received = results['total'], len(tracks)
        while received < total:
            results = self.spotify.album_tracks(
                self.angeles_haydn_urn, offset=received)
            tracks.extend(results['items'])
            received = len(tracks)

        self.assertEqual(received, total)

    def test_albums(self):
        results = self.spotify.albums(
            [self.pinkerton_urn, self.pablo_honey_urn])
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']) == 2)

    def test_track_urn(self):
        track = self.spotify.track(self.creep_urn)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_id(self):
        track = self.spotify.track(self.creep_id)
        self.assertTrue(track['name'] == 'Creep')
        self.assertTrue(track['popularity'] > 0)

    def test_track_url(self):
        track = self.spotify.track(self.creep_url)
        self.assertTrue(track['name'] == 'Creep')

    def test_track_bad_urn(self):
        try:
            self.spotify.track(self.el_scorcho_bad_urn)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_tracks(self):
        results = self.spotify.tracks([self.creep_url, self.el_scorcho_urn])
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 2)

    def test_artist_top_tracks(self):
        results = self.spotify.artist_top_tracks(self.weezer_urn)
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']) == 10)

    def test_artist_related_artists(self):
        results = self.spotify.artist_related_artists(self.weezer_urn)
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']) == 20)
        for artist in results['artists']:
            if artist['name'] == 'Jimmy Eat World':
                found = True
        self.assertTrue(found)

    def test_artist_search(self):
        results = self.spotify.search(q='weezer', type='artist')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']['items']) > 0)
        self.assertTrue(results['artists']['items'][0]['name'] == 'Weezer')

    def test_artist_search_with_market(self):
        results = self.spotify.search(q='weezer', type='artist', market='GB')
        self.assertTrue('artists' in results)
        self.assertTrue(len(results['artists']['items']) > 0)
        self.assertTrue(results['artists']['items'][0]['name'] == 'Weezer')

    def test_artist_search_with_multiple_markets(self):
        total = 5
        countries_list = ['GB', 'US', 'AU']
        countries_tuple = ('GB', 'US', 'AU')

        results_multiple = self.spotify.search_markets(q='weezer', type='artist',
                                                       markets=countries_list)
        results_all = self.spotify.search_markets(q='weezer', type='artist')
        results_tuple = self.spotify.search_markets(q='weezer', type='artist',
                                                    markets=countries_tuple)
        results_limited = self.spotify.search_markets(q='weezer', limit=3, type='artist',
                                                      markets=countries_list, total=total)

        self.assertTrue(
            all('artists' in results_multiple[country] for country in results_multiple))
        self.assertTrue(all('artists' in results_all[country] for country in results_all))
        self.assertTrue(all('artists' in results_tuple[country] for country in results_tuple))
        self.assertTrue(all('artists' in results_limited[country] for country in results_limited))

        self.assertTrue(
            all(len(results_multiple[country]['artists']['items']) > 0 for country in
                results_multiple))
        self.assertTrue(all(len(results_all[country]['artists']
                                ['items']) > 0 for country in results_all))
        self.assertTrue(
            all(len(results_tuple[country]['artists']['items']) > 0 for country in results_tuple))
        self.assertTrue(
            all(len(results_limited[country]['artists']['items']) > 0 for country in
                results_limited))

        self.assertTrue(all(results_multiple[country]['artists']['items']
                            [0]['name'] == 'Weezer' for country in results_multiple))
        self.assertTrue(all(results_all[country]['artists']['items']
                            [0]['name'] == 'Weezer' for country in results_all))
        self.assertTrue(all(results_tuple[country]['artists']['items']
                            [0]['name'] == 'Weezer' for country in results_tuple))
        self.assertTrue(all(results_limited[country]['artists']['items']
                            [0]['name'] == 'Weezer' for country in results_limited))

        total_limited_results = 0
        for country in results_limited:
            total_limited_results += len(results_limited[country]['artists']['items'])
        self.assertTrue(total_limited_results <= total)

    def test_artist_albums(self):
        results = self.spotify.artist_albums(self.weezer_urn)
        self.assertTrue('items' in results)
        self.assertTrue(len(results['items']) > 0)

        found = False
        for album in results['items']:
            if album['name'] == 'Hurley':
                found = True

        self.assertTrue(found)

    def test_search_timeout(self):
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(requests_timeout=0.01,
                             client_credentials_manager=client_credentials_manager)

        # depending on the timing or bandwidth, this raises a timeout or connection error"
        self.assertRaises((requests.exceptions.Timeout, requests.exceptions.ConnectionError),
                          lambda: sp.search(q='my*', type='track'))

    def test_max_retries_reached_get(self):
        spotify_no_retry = Spotify(
            client_credentials_manager=SpotifyClientCredentials(),
            retries=0)
        i = 0
        while i < 100:
            try:
                spotify_no_retry.search(q='foo')
            except SpotifyException as e:
                self.assertIsInstance(e, SpotifyException)
                self.assertEqual(e.http_status, 429)
                return
            i += 1
        self.fail()

    def test_album_search(self):
        results = self.spotify.search(q='weezer pinkerton', type='album')
        self.assertTrue('albums' in results)
        self.assertTrue(len(results['albums']['items']) > 0)
        self.assertTrue(results['albums']['items'][0]
                        ['name'].find('Pinkerton') >= 0)

    def test_track_search(self):
        results = self.spotify.search(q='el scorcho weezer', type='track')
        self.assertTrue('tracks' in results)
        self.assertTrue(len(results['tracks']['items']) > 0)
        self.assertTrue(results['tracks']['items'][0]['name'] == 'El Scorcho')

    def test_user(self):
        user = self.spotify.user(user='plamere')
        self.assertTrue(user['uri'] == 'spotify:user:plamere')

    def test_track_bad_id(self):
        try:
            self.spotify.track(self.bad_id)
            self.assertTrue(False)
        except SpotifyException:
            self.assertTrue(True)

    def test_show_urn(self):
        show = self.spotify.show(self.heavyweight_urn, market="US")
        self.assertTrue(show['name'] == 'Heavyweight')

    def test_show_id(self):
        show = self.spotify.show(self.heavyweight_id, market="US")
        self.assertTrue(show['name'] == 'Heavyweight')

    def test_show_url(self):
        show = self.spotify.show(self.heavyweight_url, market="US")
        self.assertTrue(show['name'] == 'Heavyweight')

    def test_show_bad_urn(self):
        with self.assertRaises(SpotifyException):
            self.spotify.show("bogus_urn", market="US")

    def test_shows(self):
        results = self.spotify.shows([self.heavyweight_urn, self.reply_all_urn], market="US")
        self.assertTrue('shows' in results)
        self.assertTrue(len(results['shows']) == 2)

    def test_show_episodes(self):
        results = self.spotify.show_episodes(self.heavyweight_urn, market="US")
        self.assertTrue(len(results['items']) > 1)

    def test_show_episodes_many(self):
        results = self.spotify.show_episodes(self.reply_all_urn, market="US")
        episodes = results['items']
        total, received = results['total'], len(episodes)
        while received < total:
            results = self.spotify.show_episodes(
                self.reply_all_urn, offset=received, market="US")
            episodes.extend(results['items'])
            received = len(episodes)

        self.assertEqual(received, total)

    def test_episode_urn(self):
        episode = self.spotify.episode(self.heavyweight_ep1_urn, market="US")
        self.assertTrue(episode['name'] == '#1 Buzz')

    def test_episode_id(self):
        episode = self.spotify.episode(self.heavyweight_ep1_id, market="US")
        self.assertTrue(episode['name'] == '#1 Buzz')

    def test_episode_url(self):
        episode = self.spotify.episode(self.heavyweight_ep1_url, market="US")
        self.assertTrue(episode['name'] == '#1 Buzz')

    def test_episode_bad_urn(self):
        with self.assertRaises(SpotifyException):
            self.spotify.episode("bogus_urn", market="US")

    def test_episodes(self):
        results = self.spotify.episodes(
            [self.heavyweight_ep1_urn, self.reply_all_ep1_urn],
            market="US"
        )
        self.assertTrue('episodes' in results)
        self.assertTrue(len(results['episodes']) == 2)

    def test_unauthenticated_post_fails(self):
        with self.assertRaises(SpotifyException) as cm:
            self.spotify.user_playlist_create(
                "spotify", "Best hits of the 90s")
        self.assertTrue(cm.exception.http_status == 401 or cm.exception.http_status == 403)

    def test_custom_requests_session(self):
        sess = requests.Session()
        sess.headers["user-agent"] = "spotipy-test"
        with_custom_session = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(),
            requests_session=sess)
        self.assertTrue(
            with_custom_session.user(
                user="akx")["uri"] == "spotify:user:akx")
        sess.close()

    def test_force_no_requests_session(self):
        with_no_session = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(),
            requests_session=False)
        self.assertNotIsInstance(with_no_session._session, requests.Session)
        user = with_no_session.user(user="akx")
        self.assertEqual(user["uri"], "spotify:user:akx")

    def test_available_markets(self):
        markets = self.spotify.available_markets()["markets"]
        self.assertTrue(isinstance(markets, list))
        self.assertIn("US", markets)
        self.assertIn("GB", markets)
