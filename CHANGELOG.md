# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

 - Auto-Refresh token in long-running apps when using Authorization Code Flow

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