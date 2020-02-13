from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='spotipy',
    version='2.8.0',
    description='A light weight Python library for the Spotify Web API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@plamere",
    author_email="paul@echonest.com",
    url='http://spotipy.readthedocs.org/',
    install_requires=[
        'requests>=2.20.0',
        'six>=1.10.0',
    ],
    license='LICENSE.md',
    packages=['spotipy'])
