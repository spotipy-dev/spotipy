## Frequently Asked Questions

### Is there a way to get this field?

spotipy can only return fields documented on the Spotify web API https://developer.spotify.com/documentation/web-api/reference/

### How to use spotipy in an API?

Check out [this example Flask app](examples/app.py)

### How can I store tokens in a database rather than on the filesystem?

See https://spotipy.readthedocs.io/en/latest/#customized-token-caching

### Incorrect user

Error:

 - You get `You cannot create a playlist for another user`
 - You get `You cannot remove tracks from a playlist you don't own`

Solution:

 - Verify that you are signed in with the correct account on https://spotify.com
 - Remove your current token: `rm .cache-{userid}`
 - Request a new token by adding `show_dialog=True` to `spotipy.Spotify(auth_manager=SpotifyOAuth(show_dialog=True))`
 - Check that `spotipy.me()` shows the correct user id

### Why do I get 401 Unauthorized?

Error:

    spotipy.exceptions.SpotifyException: http status: 401, code:-1 - https://api.spotify.com/v1/
    Unauthorized.

Solution:

 - You are likely missing a scope when requesting the endpoint, check
https://developer.spotify.com/documentation/web-api/concepts/scopes/

### Search doesn't find some tracks

Problem: you can see a track on the Spotify app but searching for it using the API doesn't find it.
 
Solution: by default `search("abba")` works in the US market.
To search for in your current country, the [country indicator](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
must be specified: `search("abba", market="DE")`.

### How do I obtain authorization in a headless/browserless environment?

If you cannot open a browser, set `open_browser=False` when instantiating SpotifyOAuth or SpotifyPKCE. You will be
prompted to open the authorization URI manually.  

See the [headless auth example](examples/headless.py).

### My application is not responding

This is still speculation, but it seems that Spotify has two limits. A rate limit and a request limit. 

- The rate limit prevents a script from requesting too much from the API in a short period of time.
- The request limit limits how many requests you can make in a 24 hour window.
The limits appear to be endpoint-specific, so each endpoint has its own limits.

If your application stops responding, it's likely that you've reached the request limit.
There's nothing Spotipy can do to prevent this, but you can follow Spotify's [Rate Limits](https://developer.spotify.com/documentation/web-api/concepts/rate-limits) guide to learn how rate limiting works and what you can do to avoid ever hitting a limit.

#### *Why* is the application not responding?
Spotipy (or more precisely `urllib3`) has a backoff-retry strategy built in, which is waiting until the rate limit is gone.
If you want to receive an error instead, then you can pass `retries=0` to `Spotify` like this:
```python
sp = spotipy.Spotify(
    retries=0,
    ...
)
```
The error raised is a `spotipy.exceptions.SpotifyException`

### I get a 404 when trying to access a Spotify-owned playlist

Spotify has begun restricting access to algorithmic and Spotify-owned editorial playlists.
Only applications with an existing extended mode will still have access to these playlists.
Read more about this change here: [Introducing some changes to our Web API](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api)
