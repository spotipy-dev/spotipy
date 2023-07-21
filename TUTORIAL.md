# Spotipy Tutorial for Beginners
Hello and welcome to the Spotipy Tutorial for Beginners. If you have limited experience coding in Python and have never used Spotipy or the Spotify API before, you've come to the right place. This tutorial will walk you through all the steps necessary to set up Spotipy and use it to accomplish a simple task.

## Prerequisites
In order to complete this tutorial successfully, there are a few things that you should already have installed:

**1. pip package manager** 

You can check to see if you have pip installed by opening up Terminal and typing the following command: pip --version
If you see a version number, pip is installed and you're ready to proceed. If not, instructions for downloading the latest version of pip can be found      here: https://pip.pypa.io/en/stable/cli/pip_download/

<img width="566" alt="Screenshot 2023-07-21 at 11 58 28 AM" src="https://github.com/kevin-mistler/spotipy/assets/75301282/be8a9148-eae7-4414-bc01-617f54366ee9">

**2. python3**

Spotipy is written in Python, so you'll need to have the lastest version of Python installed in order to use Spotipy. Check if you already have Python installed with the Terminal command: python --version
If you see a version number, Python is already installed. If not, you can download it here: https://www.python.org/downloads/

<img width="566" alt="Screenshot 2023-07-21 at 12 01 14 PM" src="https://github.com/kevin-mistler/spotipy/assets/75301282/edc96c49-aa6a-4442-abf7-505896bb8464">

**3. experience with basic Linux commands**

This tutorial will be easiest if you have some knowledge of how to use Linux commands to create and navigate folders and files on your computer. If you're not sure how to create, edit and delete files and directories from Terminal, learn about basic Linux commands [here](https://ubuntu.com/tutorials/command-line-for-beginners#1-overview) before continuing.

Once those three setup items are taken care of, you're ready to start learning how to use Spotipy!

## Step 1. Creating a Spotify Account
Spotipy relies on the Spotify API. In order to use the Spotify API, you'll need to create a Spotify developer account.

A. Visit the [Spotify developer portal](https://developer.spotify.com/dashboard/). If you already have a Spotify account, click "Log in" and enter your username and password. Otherwise, click "Sign up" and follow the steps to create an account. After you've signed in or signed up, click on the dropdown arrow in the top right corner of the window and click "Dashboard".

<img width="1021" alt="Screenshot 2023-07-21 at 12 02 39 PM" src="https://github.com/kevin-mistler/spotipy/assets/75301282/a661db6c-0f41-4719-8d2d-6dd3d3388b32">

B. Click the "Create an App" button. Enter any name and description you'd like for your new app. Accept the terms of service and click "Create."

C. In your new app's Overview screen, click the "Edit Settings" button and scroll down to "Redirect URIs." Add "http://localhost:1234" (or any other port number of your choosing). Hit the "Save" button at the bottom of the Settings panel to return to you App Overview screen.

D. On your new app's page, click "Settings". Under the "Client ID" box, you'll see a "view client secret" link. Click that link to reveal your Client Secret, then copy both your Client Secret and your Client ID somewhere on your computer. You'll need to access them later.

<img width="1429" alt="Screenshot 2023-07-21 at 12 11 03 PM" src="https://github.com/kevin-mistler/spotipy/assets/75301282/4aeedc2f-21b3-48b0-adb1-830d35ac8a88">


## Step 2. Installation and Setup

A. Create a folder somewhere on your computer where you'd like to store the code for your Spotipy app. You can create a folder in terminal with this command: mkdir folder_name

B. In that folder, create a Python file named main.py. You can create the file directly from Terminal using a built in text editor like Vim, which comes preinstalled on Linux operating systems. To create the file with Vim, ensure that you are in your new directory, then run: vim main.py

C. Paste the following code into your main.py file:
```
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",
                                               client_secret="YOUR_APP_CLIENT_SECRET",
                                               redirect_uri="YOUR_APP_REDIRECT_URI",
                                               scope="user-library-read"))
```
D. Replace YOUR_APP_CLIENT_ID and YOUR_APP_CLIENT_SECRET with the values you copied and saved in step 1D. Replace YOUR_APP_REDIRECT_URI with the URI you set in step 1C.

## Step 3. Start Using Spotipy

After completing steps 1 and 2, your app is fully configured and ready to fetch data from the Spotify API. All that's left is to tell the API what data we're looking for, and we do that by adding some additional code to main.py. The code that follows is just an example - once you get it working, you should feel free to modify it in order to get different results.

For now, let's assume that we want to print the names of all of the albums on Spotify by Taylor Swift:

A. First, we need to find Taylor Swift's Spotify URI (Uniform Resource Indicator). Every entity (artist, album, song, etc.) has a URI that can identify it. To find Taylor's URI, navigate to [her page on Spotify](https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02) and look at the URI in your browser. Everything there that follows the last backslash in the URL path is Taylor's URI, in this case: 06HL4z0CvFAxyc27GXpf02

<img width="744" alt="Screenshot 2023-07-21 at 12 15 50 PM" src="https://github.com/kevin-mistler/spotipy/assets/75301282/022a1439-2b0c-4a81-a24f-96ab9e706304">


B. Add the URI as a variable in main.py. Notice the prefix added the the URI:
```
taylor_uri = 'spotify:artist:06HL4z0CvFAxyc27GXpf02'
```
C. Add the following code that will get all of Taylor's album names from Spotify and iterate through them to print them all to standard output.
```
results = sp.artist_albums(taylor_uri, album_type='album')
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])
```

D. Close main.py and return to the directory that contains main.py. You can then run your app by entering the following command: python main.py

E. You may see a window open in your browser asking you to authorize the application. Do so - you will only have to do this once.

F. Return to your terminal - you should see all of Taylor's albums printed out there.

For more information on how to use Spotipy, a full set of examples can be found in the [online documentation](http://spotipy.readthedocs.org/) and in the [Spotipy examples directory](https://github.com/plamere/spotipy/tree/master/examples).
