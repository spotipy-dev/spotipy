from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

test_reqs = [
    'mock==2.0.0'
]

doc_reqs = [
    'Sphinx~=7.3.7',
    'sphinx-rtd-theme~=2.0.0'
]

extra_reqs = {
    'doc': doc_reqs,
    'test': test_reqs
}

setup(
    name='spotipy',
    version='2.23.0',
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
        "redis>=3.5.3",
        "requests>=2.25.0",
        "urllib3>=1.26.0"
    ],
    tests_require=test_reqs,
    extras_require=extra_reqs,
    license='MIT',
    packages=['spotipy'])
