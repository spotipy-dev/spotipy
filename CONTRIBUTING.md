## Contributing

If you would like to contribute to spotipy follow these steps:

### Fork Repository

To contribute to spotipy, you'll first need to fork the repository to your GitHub account. Click the "Fork" button at the top right of the repository page. This creates a copy of the repository under your account, allowing you to make changes without affecting the original project.

### Clone Forked Repo

After forking, clone your forked repository to your local machine using Git. Replace <your-username> with your GitHub username:
```bash
git clone https://github.com/<your-username>/spotipy.git
cd spotipy
```

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

### Create a Pull Request

Once you've made your changes and ensured they pass all tests and quality checks, it's time to submit them for review. Follow these steps to create a pull request:

1) Commit your changes:
```bash
Copy code
git add .
git commit -m "Brief description of your changes"
```
2) Push your changes to your forked repository:
```bash
Copy code
git push origin master
```
3) Visit your forked repository on GitHub. You should see a message prompting you to create a pull request based on the changes you just pushed.
4) Click on the "Compare & pull request" button to start creating the pull request. Ensure the base repository is set to plamere/spotipy and the base branch is master.
5) Provide a descriptive title and summary of your changes in the pull request description.
6) Click "Create pull request" to submit your changes for review.

### Review Process

Once you've submitted your pull request, project maintainers will review your changes. They may provide feedback or request additional changes. Be responsive to feedback and iterate on your changes as needed until they are approved.

## Publishing (by maintainer)

 - Bump version in setup.py
 - Bump and date changelog
 - Add to changelog:

       ## Unreleased

       ### Added
       - Replace with changes

       ### Fixed

       ### Removed

 - Commit changes
 - Push tag to trigger PyPI build & release workflow
 - Create github release https://github.com/plamere/spotipy/releases with the changelog content
   for the version and a short name that describes the main addition
 - Verify doc uses latest https://readthedocs.org/projects/spotipy/

### Authors and Contributors

Spotipy authored by Paul Lamere (plamere) with contributions by:

Daniel Beaudry (danbeaudry on Github)
Faruk Emre Sahin (fsahin on Github)
George (rogueleaderr on Github)
Henry Greville (sethaurus on Github)
Hugo van Kemanade (hugovk on Github)
José Manuel Pérez (JMPerez on Github)
Lucas Nunno (lnunno on Github)
Lynn Root (econchick on Github)
Matt Dennewitz (mattdennewitz on Github)
Matthew Duck (mattduck on Github)
Michael Thelin (thelinmichael on Github)
Ryan Choi (ryankicks on Github)
Simon Metson (drsm79 on Github)
Steve Winton (swinton on Github)
Tim Balzer (timbalzer on Github)
corycorycory on Github
Nathan Coleman (nathancoleman on Github)
Michael Birtwell (mbirtwell on Github)
Harrison Hayes (Harrison97 on Github)
Stephane Bruckert (stephanebruckert on Github)
Ritiek Malhotra (ritiek on Github)