from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

memcache_cache_reqs = [
    'pymemcache>=3.5.2'
]

extra_reqs = {
    'memcache': memcache_cache_reqs
}

setup(
    name='spotipy',
    version='2.25.0',
    description='A light weight Python library for the Spotify Web API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@plamere",
    author_email="paul@echonest.com",
    url='https://spotipy.readthedocs.org/',
    project_urls={
        'Source': 'https://github.com/plamere/spotipy',
    },
    python_requires='>3.8',
    install_requires=[
        "redis>=3.5.3",  # TODO: Move to extras_require in v3
        "requests>=2.25.0",
        "urllib3>=1.26.0"
    ],
    extras_require=extra_reqs,
    license='MIT',
    packages=['spotipy'])
