## Frequently Asked Questions

### Is there a way to get this field?

spotipy can only return fields documented on the Spotify web API https://developer.spotify.com/documentation/web-api/reference/

### How to use spotipy in an API?

Check out [this example Flask app](examples/app.py)

### Incorrect user

Error:

 - You get `You cannot create a playlist for another user`
 - You get `You cannot remove tracks from a playlist you don't own`

Solution:

 - Verify that you are signed in with the correct account on https://spotify.com
 - Remove your current token: `rm .cache-{userid}`
 - Request a new token by adding `show_dialog=True` to `spotipy.Spotify(auth_manager=SpotifyOAuth(show_dialog=True))`
 - Check that `spotipy.me()` shows the correct user id

### 401 Unauthorized

Error:

    spotipy.exceptions.SpotifyException: http status: 401, code:-1 - https://api.spotify.com/v1/
    Unauthorized.

Solution:

 - You are likely missing a scope when requesting the endpoint, check
https://developer.spotify.com/web-api/using-scopes/