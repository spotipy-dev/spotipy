from setuptools import setup

setup(
    name='spotipy',
    version='2.4.4',
    description='simple client for the Spotify Web API',
    author="@plamere",
    author_email="paul@echonest.com",
    url='http://spotipy.readthedocs.org/',
    install_requires=[
        'mock>=2.0.0',
        'requests>=2.3.0',
        'six>=1.10.0',
        'simplejson==3.13.2',
  ],
    license='LICENSE.txt',
    packages=['spotipy'])
