# Import required packages
from setuptools import setup

# Open the README file and read the contents into a variable
with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

# Define lists of test and documentation requirements
test_requirements = [
    "mock==2.0.0"
]

doc_requirements = [
    "Sphinx>=1.5.2"
]

# Define a dictionary of extra requirements
extra_requirements = {
    "doc": doc_requirements,
    "test": test_requirements
}

# Configure the setup function with required and optional parameters
setup(
    name="spotipy",
    version="2.23.0",
    description="A lightweight Python library for the Spotify Web API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="@plamere",
    author_email="paul@echonest.com",
    url="https://spotipy.readthedocs.org/",
    project_urls={
        "Source": "https://github.com/plamere/spotipy",
    },
    install_requires=[
        "redis>=3.5.3",
        "redis<4.0.0;python_version<'3.4'",
        "requests>=2.25.0",
        "six>=1.15.0",
        "urllib3>=1.26.0"
    ],
    tests_require=test_requirements,
    extras_require=extra_requirements,
    license="MIT",
    packages=["spotipy"]
)
