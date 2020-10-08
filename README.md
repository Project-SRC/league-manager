# League Manager - Project SRC - FastAPI

[![codecov](https://codecov.io/gh/Project-SRC/league-manager/branch/develop/graph/badge.svg)](https://codecov.io/gh/Project-SRC/league-manager)
[![Build Status](https://travis-ci.com/Project-SRC/league-manager.svg?branch=develop)](https://travis-ci.com/Project-SRC/league-manager)

The League Manager API is responsible to manage all leagues for the Project SRC stack.

## Dependencies

- Python 3.7.6
- FastAPI 0.48.0

## Configuration

The League Manager API configuration is through operating system environment variables. Therefore the configuration must be done in host or must be passed to the container environment.

The available settings are:

- `MOCK`: To indicates if the running version works with mocking data.
- `TEST`: To indicates if the running version is used for testing purposes.
- `VERSION`: Version of the API (service).
- `WS_ADDRESS`: The address of the WebSocket service to communicate with the database (see [Rethink Data Manager](https://github.com/Project-SRC/rethink-data-manager)).
- `WS_PORT`: The port of the WebSocket service.
- `RDB_DB`: Database name for the API data (this service uses Rethink DB with Rethink Data Manager service)
- `SECRET_KEY`: Encryption key for passwords (user related).
- `ALGORITHM`: Encryption algorithm.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration of the access tokens for users.

If you have questions about how to set environment variables check these links:

- [Environment Variables - Linux](https://www.digitalocean.com/community/tutorials/how-to-read-and-set-environmental-and-shell-variables-on-a-linux-vps)
- [Environment Variables - Docker](https://serverascode.com/2014/05/29/environment-variables-with-docker.html)

**Observation**: The system was developed to run in Linux and Docker environments. No official support for Windows.

## Development

### Installing VirtualEnvWrapper

We recommend using a virtual environment created by the **virtualenvwrapper** module. There is a virtual site with English instructions for installation that can be accessed [here](https://virtualenvwrapper.readthedocs.io/en/latest/install.html). But you can also follow these steps below for installing the environment:

```shell
sudo python3 -m pip install -U pip             # Update pip
sudo python3 -m pip install virtualenvwrapper  # Install virtualenvwrapper module
```

**Observation**: If you do not have administrator access on the machine remove `sudo` from the beginning of the command and add the flag `--user` to the end of the command.

Now configure your shell to use **virtualenvwrapper** by adding these two lines to your shell initialization file (e.g. `.bashrc`,` .profile`, etc.)

```shell
export WORKON_HOME=\$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

If you want to add a specific project location (will automatically go to the project folder when the virtual environment is activated) just add a third line with the following `export`:

```shell
export PROJECT_HOME=/path/to/project
```

Run the shell startup file for the changes to take effect, for example:

```shell
source ~/.bashrc
```

Now create a virtual environment with the following command (entering the name you want for the environment), in this example I will use the name **league**:

```shell
mkvirtualenv -p $(which python3) league
```

To use it:

```shell
workon league
sudo python3 -m pip install pipenv # Or
sudo apt install pipenv # On Debian based distributions
pipenv install # Will install all of the project dependencies
```

**Observaion**: Again, if necessary, add the flag `--user` to make the pipenv package installation for the local user.

### Local Execution

For local system execution, run the following command in the project root folder (assuming _virtualenv_ is already active):

```shell
python src/main.py
```

This will run the system on _localhost_ and will be available on the `HTTP_PORT` port configured for the system. This way you can test new implementations.

## Tests

To run the League API tests follow the script below:

1.  Enable _virtualenv_ **league**;
2.  Ensure that the dependencies are installed, especially:

        pytest
        pytest-coverage
        flake8

3.  Run the commands below:

```shell
export PYTHONPATH=$(pwd)                   # Set the python path as the project folder
pytest src/                                # Performs the tests
pytest --cov=league src/                     # Performs tests evaluating coverage
pytest --cov=league --cov-report xml src/    # Generate the XML report of coverage
flake8 src/                                # Run PEP8 linter
unset PYTHONPATH                           # Unset PYTHONPATH variable
```

During the tests the terminal will display a output with the test report (failures, skips and successes) and the system test coverage. For other configurations and supplemental documentation go to [pytest](https://pytest.org/en/latest/) and [coverage](https://pytest-cov.readthedocs.io/en/latest/).

During the lint process the terminal will report a bug report and warnings from the PEP8 style guide, for more configurations and additional documentation go to [flake8](http://flake8.pycqa.org/en/latest/index.html#quickstart) and [PEP8](https://www.python.org/dev/peps/pep-0008/)

## Build

To build the API Auth service just follow the script below:

```shell
docker build -t league-manager:<version> .
```

Setting the version on `<version>`. E.g.: `latest`, `stable`, `alpha`, `1.0.0` and etc.

Make sure you have logged in to the [docker hub](https://hub.docker.com/) service. If you do not, run the `docker login` command.

```shell
docker push league-manager:<version>
```

Finally, if the system will be executed by the built container docker, execute:

```shell
docker run -d --name league-manager -e .env league-manager
```

**Observation**: Assumes that the settings are listed in the `.env` file. For more settings, execution options, and supplemental documentation, go to [Docker](https://docs.docker.com/)
