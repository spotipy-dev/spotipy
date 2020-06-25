from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

test_reqs = [
    'mock==2.0.0'
]

doc_reqs = [
    'Sphinx>=1.5.2'
]

extra_reqs = {
    'doc': doc_reqs,
    'test': test_reqs
}

setup(
    name='spotipy',
    version='2.13.0',
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
    tests_require=test_reqs,
    extras_require=extra_reqs,
    license='LICENSE.md',
    packages=['spotipy'])
