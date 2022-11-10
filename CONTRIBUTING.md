## Contributing

If you would like to contribute to spotipy follow these steps:

### Export the needed environment variables

```bash
# Linux or Mac
export SPOTIPY_CLIENT_ID=client_id_here
export SPOTIPY_CLIENT_SECRET=client_secret_here
export SPOTIPY_CLIENT_USERNAME=client_username_here # This is actually an id not spotify display name
export SPOTIPY_REDIRECT_URI=https://localhost:8080/callback # Make url is set in app you created to get your ID and SECRET

# Windows
$env:SPOTIPY_CLIENT_ID="client_id_here"
$env:SPOTIPY_CLIENT_SECRET="client_secret_here"
$env:SPOTIPY_CLIENT_USERNAME="client_username_here"
$env:SPOTIPY_REDIRECT_URI="https://localhost:8080/callback"
```

### Create virtual environment, install dependencies, run tests:

```bash
$ virtualenv --python=python3.7 env
$ source env/bin/activate
(env) $ pip install --user -e .
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

### Tests

In order to commit and push your changes to the master files, all tests must be passing. If there are tests that are failing, due to your most recent commit, please fix prior to your commit or it will not be accepted.

### Code Coverage

To test the code coverage of the files, you will need to install coverage.py. In the terminal:

1. pip install coverage

2. python -m unittest discover --> this runs the coverage suite alongside unittests

3. coverage run -m unittest discover --> outputs the code coverage in each file

### Publishing (by maintainer)

- Bump version in setup.py
- Bump and date changelog
- Add to changelog:

      ## Unreleased

      // Add your changes here and then delete this line

- Commit changes
- Package to pypi:

      python setup.py sdist bdist_wheel
      python3 setup.py sdist bdist_wheel
      twine check dist/*
      twine upload --repository-url https://upload.pypi.org/legacy/ --skip-existing dist/*.(whl|gz|zip)~dist/*linux*.whl

- Create github release https://github.com/plamere/spotipy/releases with the changelog content
  for the version and a short name that describes the main addition
- Verify doc uses latest https://readthedocs.org/projects/spotipy/

### Changelog

Don't forget to add a short description of your change in the [CHANGELOG](CHANGELOG.md)
