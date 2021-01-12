Experiment 1 notes
==================

This uses [Bottle](https://bottlepy.org) and [Peewee](http://docs.peewee-orm.com/en/latest/). The database and server code are in the subdirectory [dibs](dibs).

Installation
------------

This is currently in a branch on GitHub.  To install it locally, you will need to clone not just the main repo contents but the branch as well.  There are multiple ways of doing this; I use a script I wrote called [`git-clone-complete`](https://github.com/mhucka/small-scripts/blob/main/git-scripts/git-clone-complete) for doing deep clones of github repositories:

```sh
git-clone-complete https://github.com/caltechlibrary/dibs
```

Then, switch to the branch `experiment1`:

```sh
git checkout experiment`
```


Running the server on localhost
-------------------------------

First, install the Python dependencies on your system or your virtual environment:

```sh
pip3 install -r requirements.txt
```

Prior to running the server for the first time, for testing purposes, you may want to add some sample data. This can be done by running the script [`load-mock-data.py`](load-mock-data.py) in the current directory:

```sh
python3 load-mock-data.py
```

The script [`run-server`](run-server) starts the server running; it assumes you are in the current directory, and it takes a few arguments for controlling its behavior:

```sh
./run-server -h
```

By default it starts the server on `localhost` port 8080.


General information
-------------------

Settings are stored in the file [`settings.ini`](settings.ini).  This file is read at run time by the server and database components.

The definition of the database is in [`dibs/database.py`](dibs/database.py).  The interface is defined in terms of high-level objects that are backed by an SQLite database back-end.  The ORM used is [Peewee](http://docs.peewee-orm.com/en/latest/).

The definition of the service endpoints and the behaviors is in [`dibs/server.py`](dibs/server.py).  The endpoints are implemented using [Bottle](https://bottlepy.org).

The web server used at the moment is the development server provided by Bottle.  It has live reload built-in, meaning that changes to the `.py` files are picked up automatically and the server updates its behavior on the fly.
