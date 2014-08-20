from setuptools import setup

setup(
    name='SpotipyWebApi',
    version='1.320',
    description='simple client for the Spotify Web API',
    author="@plamere",
    author_email="paul@echonest.com",
    url='http://github.com/plamere/spotipy',
    install_requires=['requests>=1.0'],
    license='LICENSE.txt',
    py_modules=['spotipy.spotipy', 'spotipy.oauth2', 'spotipy.util'],)
