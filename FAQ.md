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

### Why do the versions on the GitHub page and the spotipy website differ?

The spotipy team updates the GitHub page more frequently than the website. As a result, the GitHub page will often have a more recent version of the documentation. Always refer to the GitHub page for the most accurate and current information. 

### How do I set up the necessary environment variables for spotipy?

spotipy requires certain environment variables to function properly. Detailed instructions on setting these up can be found in the `CONTRIBUTING.md` guide on the GitHub page.

### How are contributions to spotipy recognized?

spotipy appreciates all forms of contributions from the community, whether it be feature enhancements, bug fixes, or improvements to documentation. While the project does not formally recognize contributions, your changes, if merged, will be part of spotipy's codebase and benefit its users. Your contribution history will also be visible on GitHub, serving as a testament to your active participation in open-source development. 

Note that while making contributions, please adhere to spotipy's contribution guidelines outlined in the `CONTRIBUTING.md` file.

### Are there any limitations as to what I can create with spotipy and the Spotify API?

Yes, there are certain types of applications and functionality that Spotify explicitly prohibits in their [developer policy](https://developer.spotify.com/policy#iii-some-prohibited-applications). Some of these include:

1. Creating ringtone, alert tone, or alarm functionality in an application, unless you receive Spotify’s written approval.
2. Creating a game, including trivia quizzes.
3. Creating any product or service which includes any non-interactive internet webcasting service.
4. Synchronizing any sound recordings with any visual media, including any advertising, film, television program, slideshow, video, or similar content.
5. Building products and services that mimic, replicate or attempt to replace a core user experience of Spotify without their prior written permission.

Please note this is not an exhaustive list, and developers are advised to read the full policy to ensure their application complies with all guidelines. Violating these rules may lead to the suspension or termination of your access to the Spotify Developer Platform.
