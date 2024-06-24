# Spotipy App Directions

## Creating an App on Spotify
In order to get the requisite data from Spotify to allow Spotipy to work correctly, first you need to create an app on Spotify.

To begin, install spotipy and follow the below directions to [create an app on Spotify](https://developers.spotify.com/).

Click the link in the above line and make sure you are signed in to your Spotify account.

In the top right corner of the developer page, click the arrow next to your username and then select "Dashboard" from the drop down menu.

![image](https://github.com/spotipy-dev/spotipy/assets/79183545/ee9546e9-9277-4b93-a5d7-5c2fcfd49525)

After going to your dashboard, click "Create App". You will be redirected to a page where you will fill out information to create your app. Below are directions for filling out each field:

**App Name**: Fill this out with whatever you'd like your app to be called.  
**App Description**: Write a description of the app; this cannot be left blank.  
**Website**: This can be left blank.  
**Redirect URI**: This is just a URI that will be used to display the status of your authentication. You can use a local address for this, for example http://localhost:8000/

When you are done filling out all of these fields, select the checkbox next to "I understand and agree with Spotify's Developer Terms of Service and Design Guidelines", and then click Save.

Congratulations! You have now created a Spotify app.

## Extracting the Required Data for Spotipy
After creating your Spotify app, you will be taken to your app's homepage. Click Settings on the top rigt hand corner of the page. 

On your Settings page, you will see your client ID displayed and you can also click "View client secret" to display the secret client ID.

![image](https://github.com/spotipy-dev/spotipy/assets/79183545/8634dec0-720a-491f-be90-2caee110f602)

## Using the Data with Spotipy

Copy the Client ID, Secret Client, and Redirect URI from your Spotify app's Settings page into the YOUR_APP_CLIENT_ID, YOUR_APP_CLIENT_SECRET, and YOUR_APP_REDIRECT_URI fields shown in the screenshot from the README below.

<img width="751" alt="image" src="https://github.com/spotipy-dev/spotipy/assets/79183545/b2b9d55f-b52a-46eb-b153-cf1ac3303507">

You are now ready to start using Spotipy! Check out the [examples folder](https://github.com/spotipy-dev/spotipy/tree/master/examples) for samples of how to use all of the features you now have acces to!



