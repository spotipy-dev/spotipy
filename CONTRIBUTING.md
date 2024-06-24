## Contributing

If you would like to contribute to spotipy follow these steps:

### Export the needed environment variables

```bash
# Linux or Mac
export SPOTIPY_CLIENT_ID=client_id_here
export SPOTIPY_CLIENT_SECRET=client_secret_here
export SPOTIPY_CLIENT_USERNAME=client_username_here # This is actually an id not spotify display name and can be found [here](https://www.spotify.com/us/account/overview/)
export SPOTIPY_REDIRECT_URI=http://localhost:8080 # Make url is set in app you created to get your ID and SECRET

# Windows
$env:SPOTIPY_CLIENT_ID="client_id_here"
$env:SPOTIPY_CLIENT_SECRET="client_secret_here"
$env:SPOTIPY_CLIENT_USERNAME="client_username_here" 
$env:SPOTIPY_REDIRECT_URI="http://localhost:8080" 
```

### Create virtual environment, install dependencies, run tests:

```bash
$ virtualenv --python=python3 env
$ source env/bin/activate
(env) $ pip install -e . 
(env) $ python -m unittest discover -v tests
```

### Lint

To automatically fix the code style:

    pip install autopep8
    autopep8 --in-place --aggressive --recursive .

To verify the code style:

    pip install flake8
    flake8 .

To make sure if the import lists are stored correctly:

    pip install isort
    isort . -c -v

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
 