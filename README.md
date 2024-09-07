# NPM Visual

This tool creates a visual graph of popular NPM packages. Data is scraped from various package.json files. We then analyize them to identify interesting package relationships. 

One goal is to identify packages that are not well maintained, but are heavily relied on by massive companies. It would also be nice to find packages that are heavily relied on that have unusual liscences.

# Installation and Environment Setup
Clone the repo to your local machine
~~~
git clone git@github.com:PraveenKusuluri08/npm_visual.git
~~~
Install Python 3.6.9
First install pyenv on your system. Follow instructions here. Be sure to update the path and install all packages pyenv depends on.
https://github.com/pyenv/pyenv

Install Python 3.6.9
~~~
pyenv install 3.6.9
~~~

Install pipx via instructions here
https://pipx.pypa.io/stable/installation/
be sure to update path info

~~~
pipx install poetry
pipx upgrade poetry
~~~

# ToDo
Add additional notes here. We should use Github tasks. 
