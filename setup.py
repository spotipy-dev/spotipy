from setuptools import setup

desc = """### A light weight Python library for the Spotify Web API"""

setup(
    name='spotipy',
    version='2.6.0',
    long_description=desc,
    long_description_content_type='text/markdown',
    author="@plamere",
    author_email="paul@echonest.com",
    url='http://spotipy.readthedocs.org/',
    install_requires=[
        'mock>=2.0.0',
        'requests>=2.3.0',
        'six>=1.10.0',
    ],
    license='LICENSE.md',
    packages=['spotipy'])
