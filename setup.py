from setuptools import setup


setup(
    name='spotipy',
    version='0.9',
    description='simple client for the Spotify Web API',
    author="@plamere",
    author_email="paul@echonest.com",
    url='http://github.com/plamere/spotipy',
    install_requires=['requests>=1.0', ],
    py_modules=['spotipy'],)
