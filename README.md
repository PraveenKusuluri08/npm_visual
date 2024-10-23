# NPM Visual

This tool creates a visual graph of popular NPM packages. Data is scraped from various package.json files. We then analyize them to identify interesting package relationships.

One goal is to identify packages that are not well maintained, but are heavily relied on by massive companies. It would also be nice to find packages that are heavily relied on that have unusual liscences.

# Installation and Environment Setup

Clone the repo to your local machine

```
git clone git@github.com:PraveenKusuluri08/npm_visual.git
```

## Install Python

First install pyenv on your system. Follow instructions here. Be sure to update the path and install all packages pyenv depends on.
https://github.com/pyenv/pyenv

Install Python 3.12.5

```
pyenv install 3.12.5
```

## Install pipx

Install pipx via instructions here
https://pipx.pypa.io/stable/installation/
be sure to update path info

```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

I had to install python3.8-venv on my machine to install poetry (this was before installing 3.12.5, maybe it will be different for you)

```
pip install pipx
sudo apt install python3.8-venv
```

## Install Poetry

Install poetry. Know that you may need to use the --force option

```
pipx install poetry
pipx upgrade poetry
```

Make sure poetry is installed

```
poetry --version
```

My version is 1.8.3 installed using Python 3.8.10
Poetry requires a python version ^=3.8 to install. but the Python version can be different.

# Using Poetry

Once you got Poetry installed, navigate to this directory and run

```
poetry install
```

If poetry ever freezes during installs. you might be seeing the following [https://github.com/python-poetry/poetry/pull/6471](error). If this happens, run:

```
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
poetry install
```

# Running Development Server

```
poetry run flask run
```

# ToDo

Add additional notes here. We should use Github tasks.
Change React app configuration to compile to a static folder in Flask
Change React dev server to connect to flask proxy.

# Warnings

We should consider carefully if we want to commit poetry.toml to git. In the future, later, it may have sensitive user-specific information.

# Install Neo4j

follow instructions <a href="https://neo4j.com/docs/operations-manual/current/installation/">https://neo4j.com/docs/operations-manual/current/installation/</a>

## Install Java 17

```
sudo apt-get install openjdk-17-jdk
```

## Neo4j debian install I used.

```
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/neotechnology.gpg
echo 'deb [signed-by=/etc/apt/keyrings/neotechnology.gpg] https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
```
