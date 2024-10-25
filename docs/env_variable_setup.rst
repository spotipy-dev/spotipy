.. container:: WordSection1

   Spotipy Environment Variables Setup Walkthrough for MacOS

   **Description**

   This document will walk you through setting up the SPOTIPY_CLIENT_ID
   and SPOTIPY_CLIENT_SECRET environment variables necessary for use of
   the Spotipy Python library. Note: This tutorial assumes you have
   Python3 installed on your system. If you do not, please go to
   `Python <https://www.python.org/>`_ and install that first.

   **Getting Started**

   - Open ‘Terminal’ or your favorite terminal emulator

   - Navigate to your preferred working directory and run the following command:

     - python3 -m venv tutorial-env

     - Confirm that this has created a folder called “tutorial-env”

   .. image:: images/image001.png

   - Now run the following command from to activate the virtual environment

     - source tutorial-env/bin/activate

   .. image:: images/image002.png

   - Now install Spotipy with the following command

     - python3 -m pip install spotipy

   .. image:: images/image003.png

   - Log into your Spotify Developer dashboard

     - `Spotify Developer Dashboard <https://developer.spotify.com/dashboard>`_

   .. image:: images/image004.png

   - Click the ‘Create App’ button and fill out the forms with your desired information. For “Redirect URI”, we can use 'https://localhost:8888/callback'
      
      .. image:: images/image005.png

     - Click ‘Save’

   - You can now see the app home screen

      .. image:: images/image006.png

     - Click ‘Settings’ to get to the app settings page

      .. image:: images/image007.png

     - Copy down the Client ID and Client Secret (click ‘View Client Secret’ to view)

   - Back in Terminal, in the same working directory as before, run the following commands with the codes (the text after the equal sign) replaced with your own ID and SECRET codes

     - export SPOTIPY_CLIENT_ID=6c12c5b29cde4f4593613521eb850e64

     - export SPOTIPY_CLIENT_SECRET=ddeb6f49904b4b799d7e9bf233e21b4a

     - export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback
      
      .. image:: images/image008.png

     - Note: You won’t get any text confirmation after running the commands

   - You can confirm that the values took hold with the following commands

     - echo $SPOTIPY_CLIENT_ID

     - echo $SPOTIPY_CLIENT_SECRET

     - echo $SPOTIPY_REDIRECT_URI

      .. image:: images/image009.png

   Your environment variables are now configured to work with the Spotipy API!
