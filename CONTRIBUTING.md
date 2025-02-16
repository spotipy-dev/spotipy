## Contributing

If you would like to contribute to spotipy follow these steps:

### Export the needed environment variables

```bash
# Linux or Mac
export SPOTIPY_CLIENT_ID=client_id_here
export SPOTIPY_CLIENT_SECRET=client_secret_here
export SPOTIPY_CLIENT_USERNAME=client_username_here # This is actually an id not spotify display name and can be found [here](https://www.spotify.com/us/account/overview/)
export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080 # Make url is set in app you created to get your ID and SECRET

# Windows
$env:SPOTIPY_CLIENT_ID="client_id_here"
$env:SPOTIPY_CLIENT_SECRET="client_secret_here"
$env:SPOTIPY_CLIENT_USERNAME="client_username_here" 
$env:SPOTIPY_REDIRECT_URI="http://127.0.0.1:8080" 
```

### Branch Overview

After restarting development on version 3, we decided to restrict commits to certain branches in order to push the development forward.
To give you a flavour of what we mean, here are some examples of what PRs go where:

**v3**:

- any kind of refactoring
- better documentation
- enhancements
- code styles

**master (v2)**:

- bug fixes
- deprecations
- new endpoints (until we release v3)
- basic functionality

Just choose v3 if you are unsure which branch to work on.


### Create virtual environment, install dependencies, run tests:

```bash
$ virtualenv --python=python3 env
$ source env/bin/activate
(env) $ pip install -e . 
(env) $ python -m unittest discover -v tests
```

### Lint

    pip install .[test]

To automatically fix some of the code style:

    autopep8 --in-place --aggressive --recursive .

To verify the code style:

    flake8 .

To make sure if the import lists are stored correctly:

    isort . -c

Sort them automatically with:

    isort .

### Changelog

Don't forget to add a short description of your change in the [CHANGELOG](CHANGELOG.md)

### Publishing (by maintainer)

 - Bump version in setup.py
 - Bump and date changelog
 - Add to changelog:

       ## Unreleased
       Add your changes below.

       ### Added

       ### Fixed

       ### Removed

 - Commit changes
 - Push tag to trigger PyPI build & release workflow
 - Create github release https://github.com/plamere/spotipy/releases with the changelog content
   for the version and a short name that describes the main addition
 - Verify doc uses latest https://readthedocs.org/projects/spotipy/
 