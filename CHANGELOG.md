# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

// Add your changes here and then delete this line

## [2.13.0] - 2020-06-25

### Added

 - Added `SpotifyImplicitGrant` as an auth manager option. It provides
 user authentication without a client secret but sacrifices the ability
   to refresh the token without user input. (However, read the class
   docstring for security advisory.)
 - Added built-in verification of the `state` query parameter
 - Added two new attributes: error and error_description to `SpotifyOauthError` exception class to show
   authorization/authentication web api errors details.
 - Added `SpotifyStateError` subclass of `SpotifyOauthError`
 - Allow extending `SpotifyClientCredentials` and `SpotifyOAuth`
 - Added the market paramter to `album_tracks`

### Deprecated

 - Deprecated `util.prompt_for_user_token` in favor of `spotipy.Spotify(auth_manager=SpotifyOAuth())`

## [2.12.0] - 2020-04-26

### Added

 - Added a method to update the auth token.

### Fixed

 - Logging regression due to the addition of `logging.basicConfig()` which was unneeded.

## [2.11.2] - 2020-04-19

### Changed

 - Updated the documentation to give more details on the authorization process and reflect
   2020 Spotify Application jargon and practices.

 - The local webserver is only started for localhost redirect_uri which specify a port,
   i.e. it is started for `http://localhost:8080` or `http://127.0.0.1:8080`, not for `http://localhost`.

### Fixed

 - Issue where using `http://localhost` as redirect_uri would cause the authorization process to hang.

## [2.11.1] - 2020-04-11

### Fixed

 - Fixed miscellaneous issues with parsing of callback URL

## [2.11.0] - 2020-04-11

### Added

 - Support for shows/podcasts and episodes
 - Added CONTRIBUTING.md

### Changed

 - Client retry logic has changed as it now uses urllib3's `Retry` in conjunction with requests `Session`
 - The session is customizable as it allows for:
    - status_forcelist
    - retries
    - status_retries
    - backoff_factor
 - Spin up a local webserver to auto-fill authentication URL
 - Use session in SpotifyAuthBase
 - Logging used instead of print statements

### Fixed

 - Close session when Spotipy object is unloaded
 - Propagate refresh token error

## [2.10.0] - 2020-03-18

### Added

 - Support for `add_to_queue`
    - **Parameters:**
        - track uri, id, or url
        - device id. If None, then the active device is used.
 - Add CHANGELOG and LICENSE to released package


## [2.9.0] - 2020-02-15

### Added

 - Support `position_ms` optional parameter in `start_playback`
 - Add `requests_timeout` parameter to authentication methods
 - Make cache optional in `get_access_token`

## [2.8.0] - 2020-02-12

### Added

 - Support for `playlist_cover_image`
 - Support `after` and `before` parameter in `current_user_recently_played`
 - CI for unit tests
 - Automatic `token` refresh
 - `auth_manager` and `oauth_manager` optional parameters added to `Spotify`'s init.
 - Optional `username` parameter to be passed to `SpotifyOAuth`, to infer a `cache_path` automatically
 - Optional `as_dict` parameter to control `SpotifyOAuth`'s `get_access_token` output type. However, this is going to be deprecated in the future, and the method will always return a token string
 - Optional `show_dialog` parameter to be passed to `SpotifyOAuth`

### Changed
  - Both `SpotifyClientCredentials` and `SpotifyOAuth` inherit from a common `SpotifyAuthBase` which handles common parameters and logics.

## [2.7.1] - 2020-01-20

### Changed

 - PyPi release mistake without pulling last merge first

## [2.7.0] - 2020-01-20

### Added

 - Support for `playlist_tracks`
 - Support for `playlist_upload_cover_image`

### Changed

 - `user_playlist_tracks` doesn't require a user anymore (accepts `None`)

### Deprecated

 - Deprecated `user_playlist` and `user_playlist_tracks`

## [2.6.3] - 2020-01-16

### Fixed

 - Fixed broken doc in 2.6.2

## [2.6.2] - 2020-01-16

### Fixed

 - Fixed broken examples in README, examples and doc

### Changed

 - Allow session keepalive
 - Bump requests to 2.20.0

## [2.6.1] - 2020-01-13

### Fixed
 - Fixed inconsistent behaviour with some API methods when
   a full HTTP URL is passed.
 - Fixed invalid calls to logging warn method

### Removed
 - `mock` no longer needed for install. Only used in `tox`.

## [2.6.0] - 2020-01-12

### Added
 - Support for `playlist` to get a playlist without specifying a user
 - Support for `current_user_saved_albums_delete`
 - Support for `current_user_saved_albums_contains`
 - Support for `user_unfollow_artists`
 - Support for `user_unfollow_users`
 - Lint with flake8 using Github action

### Changed
 - Fix typos in doc
 - Start following [SemVer](https://semver.org) properly

## [2.5.0] - 2020-01-11
Added follow and player endpoints

## [2.4.4] - 2017-01-04
Python 3 fix

## [2.4.3] - 2017-01-02
Fixed proxy issue in standard auth flow

## [2.4.2] - 2017-01-02
Support getting audio features for a single track

## [2.4.1] - 2017-01-02
Incorporated proxy support

## [2.4.0] - 2016-12-31
Incorporated a number of PRs

## [2.3.8] - 2016-03-31
Added recs, audio features, user top lists

## [2.3.7] - 2015-08-10
Added current_user_followed_artists

## [2.3.6] - 2015-06-03
Support for offset/limit with album_tracks API

## [2.3.5] - 2015-04-28
Fixed bug in auto retry logic

## [2.3.3] - 2015-04-01
Aadded client credential flow

## [2.3.2] - 2015-03-31
Added auto retry logic

## [2.3.0] - 2015-01-05
Added session support added by akx.

## [2.2.0] - 2014-11-15
Added support for user_playlist_tracks

## [2.1.0] - 2014-10-25
Added support for new_releases and featured_playlists

## [2.0.2] - 2014-08-25
Moved to spotipy at pypi

## [1.2.0] - 2014-08-22
Upgraded APIs and docs to make it be a real library

## [1.310.0] - 2014-08-20
Added playlist replace and remove methods. Added auth tests. Improved API docs

## [1.301.0] - 2014-08-19
Upgraded version number to take precedence over previously botched release (sigh)

## [1.50.0] - 2014-08-14
Refactored util out of examples and into the main package

## [1.49.0] - 2014-07-23
Support for "Your Music" tracks (add, delete, get), with examples

## [1.45.0] - 2014-07-07
Support for related artists endpoint. Don't use cache auth codes when scope changes

## [1.44.0] - 2014-07-03
Added show tracks.py example

## [1.43.0] - 2014-06-27
Fixed JSON handling issue

## [1.42.0] - 2014-06-19
Removed dependency on simplejson

## [1.40.0] - 2014-06-12
Initial public release.

## [1.4.2] - 2014-06-21
Added support for retrieving starred playlists

## [1.1.0] - 2014-06-17
Updates to match released API

## [1.1.0] - 2014-05-18
Repackaged for saner imports

## [1.0.0] - 2017-04-05
Initial release
