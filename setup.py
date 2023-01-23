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
    version='2.22.1',
    description='A light weight Python library for the Spotify Web API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@plamere",
    author_email="paul@echonest.com",
    url='https://spotipy.readthedocs.org/',
    project_urls={
        'Source': 'https://github.com/plamere/spotipy',
    },
    install_requires=[
        "redis>=3.5.3",
        "redis<4.0.0;python_version<'3.4'",
        "requests>=2.25.0",
        "six>=1.15.0",
        "urllib3>=1.26.0"
    ],
    tests_require=test_reqs,
    extras_require=extra_reqs,
    license='MIT',
    packages=['spotipy'])
