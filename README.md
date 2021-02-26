Caltech DIBS<img width="70em" align="right" src="https://github.com/caltechlibrary/dibs/raw/main/docs/_static/media//dibs-icon.png">
============

Caltech DIBS ("_**Di**gital **B**orrowing **S**ystem_") is the Caltech Library's implementation of a basic [controlled digital lending](https://en.wikipedia.org/wiki/Controlled_digital_lending) system.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)


Table of contents
-----------------

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage: running the server on localhost](#running-the-server-on-localhost)
* [General information](#general-information)
* [License](#license)
* [Acknowledgments](#authors-and-acknowledgments)


Introduction
------------

The Caltech Library's DIBS enables members of Caltech to borrow materials (e.g., older books) that are not otherwise available in e-book or other electronic formats.  The system was implemented in the year 2021 to help Caltech students and faculty continue their studies and work during the global [COVID-19 pandemic](https://www.who.int/emergencies/diseases/novel-coronavirus-2019).

The concept of [controlled digital lending](https://en.wikipedia.org/wiki/Controlled_digital_lending) (CDL) is to allow libraries to loan items to digital patrons in a "lend like print" fashion.  The number of digital copies of an item allowed to be loaned at any given time is strictly controlled to match the number of physical print copies taken off the shelves, to ensure an exact "owned-to-loaned" ratio.  DIBS implements two main components of a CDL system: a patron loan tracking system, and an integrated digital content viewing interface.  DIBS makes use of the [Universal Viewer](http://universalviewer.io) to implement the viewer.

Access to materials in Caltech DIBS is limited to current Caltech faculty, students and staff, but the software for DIBS itself is open-sourced under a BSD type license.


Requirements
-----------

DIBS is written in Python 3 and depends on additional solftware to work.  The [installation instructions](#installation) below describe how to install all of the dependencies.  In summary, in addition to a number of Python packages, DIBS also needs: the [Universal Viewer](http://universalviewer.io), used to display content; [Node](https://nodejs.dev) modules used by the Universdal Viewer; [Redis](https://redis.io), a NoSQL datastore used by DIBS for session management; and [SQLite3](https://www.sqlite.org/), used as the main database for DIBS data.


Installation
------------

### ⓵ _Get the DIBS source code_

To install and run DIBS locally, you will need to clone not just the main repo contents but also submodules.  The minimum command for this involves using the `--recursive` option to `git clone`:

```sh
git clone --recursive https://github.com/caltechlibrary/dibs
```

If you want to get the `develop` branch as well, the easiest approach may be instead to use the script [`git-clone-complete`](https://github.com/mhucka/small-scripts/blob/main/git-scripts/git-clone-complete) for doing deep clones of github repositories:

```sh
git-clone-complete https://github.com/caltechlibrary/dibs
```

This will create a `dibs` subdirectory in your current directory.


### ⓶ _Install Python dependencies_

Next, install the Python dependencies on your system or your virtual environment:

```sh
cd dibs
python3 -m pip install -r requirements.txt
```

### ⓷ _Install Node dependencies_

Change into to the [`viewer`](viewer) subdirectory, and run the following command:

```sh
cd viewer
npm install
```


### ⓸ _Install Redis_

You also need to have a Redis database running on the local host.  If you are using Homebrew on macOS, the simplest way to do that is the following:

```sh
brew install redis
```

If you are using MacPorts on macOS, the simplest way to do that is the following:

```sh
sudo port install redis
```

On Debian/Ubuntu/Raspberry Pi OS do the following:

```sh
sudo apt install redis
```

You can leave the default Redis settings as-is for the DIBS demo.


Usage: running the server on localhost
--------------------------------------

### ⓵ _Start the Redis server_

First, start the Redis server.  If you are using Homebrew, this can be done using the following command:

```sh
brew services start redis
```

Using MacPorts you can start/stop with the following commands:

```sh
sudo port load redis
sudo port unload redis
```

On Debian/Ubuntu/Raspberry Pi OS you can start/stop with the following commands:

```sh
sudo systemctl start redis
sudo systemctl stop redis
```

You can test if Redis is running properly by issuing the command `redis-cli ping`.  It should return the answer `PONG`.


### ⓶ _Copy the sample `settings.ini` configuration file_

The file `settings.ini-example` is a sample configuration file for DIBS.  Copy the file to `settings.ini`,

```sh
cp settings.ini-example settings.ini
```

and edit the contents in a text editor to suit your local installation.


### ⓷ _Load a sample book into DIBS_

Prior to starting the DIBS server for the first time, for testing purposes, you may want to add some sample data. This can be done by running the script [`load-mock-data.py`](load-mock-data.py):

```sh
python3 load-mock-data.py
```


### ⓸ _Load a sample user into DIBS_

The program [`people-manager`](people-manager) is an interface to adding and manipulating user data.  To log in to the demo DIBS configuration, create at least one user with a role of "library":

```sh
./people-manager add uname= display_name= role="library" secret=
```


### ⓹ _Start the DIBS server_

The script [`run-server`](run-server) starts the server running; it assumes you are in the current directory, and it takes a few arguments for controlling its behavior:

```sh
./run-server -h
```

By default it starts the server on `localhost` port 8080.

To run with debug tracing, use the `--debug` option with an argument telling it where to send the output.  Using `-` as the argument value will send it to stdout and using a file name will redirect it to a file.  For example,

```sh
./run-server --debug /tmp/debug.log
```

It's useful to have 2 shell windows open in that case: one where you start the server, and with `tail -f /tmp/debug.log` to see the trace.


The pages of DIBS
------------------

Here is a summary of the endpoints implemented by the system:

| Endpoint                 | Type | Purpose              |
|--------------------------|------|----------------------|
| `/`                      | GET  | General information page about the system |
| `/info`                  | GET  | Same as `/` |
| `/login`                 | GET  | Shows the login page |
| `/login`                 | POST | Accepts form from login page |
| `/logout`                | GET  | Logs out current user |
| `/list`                  | GET  | Show what's available for loan |
| `/add`                   | GET  | Show the page to add an item |
| `/edit/<barcode>`        | GET  | Show the page to edit an item |
| `/update/add`            | POST | Accepts form input from add-item page |
| `/update/edit`           | POST | Accepts form input from edit-item page | 
| `/ready`                 | POST | Handles checkbox in `list` page to make an item ready to loan |
| `/remove`                | POST | Handles button in `list` page to remove an item |
| `/item/<barcode>`        | GET  | Shows item information page for a given item |
| `/loan`                  | POST | Handles Loan button from `/item` page |
| `/view/<barcode>`        | GET  | Show the item in the viewer page |
| `/return/<barcode>`      | GET  | Handles Return button from viewer page |
| `/manifests/<barcode>`   | GET  | Sends manifest to viewer |
| `/thankyou`              | GET  | Destination after user uses Return button |
| `/notauthenticated`      | GET  | Error page for unathenticated users |
| `/nonexistent`           | GET  | Error page for nonexistent items |
| `/nonexistent/<barcode>` | GET  | Error page for nonexistent items |


General information
-------------------

Settings are stored in the file [`settings.ini`](settings.ini).  This file is read at run time by the server and database components.

### _About Peewee_

The definition of the database is in [`dibs/database.py`](dibs/database.py).  The interface is defined in terms of high-level objects that are backed by an SQLite database back-end.  The ORM used is [Peewee](http://docs.peewee-orm.com/en/latest/).

Worth knowing: Peewee queries are lazy-executed: they return iterators that must be accessed before the query is actually executed.  Thus, when selecting items, the following returns a Peewee `ModelSelector`, and not a single result or a list of results:

```python
Item.select().where(Item.barcode == barcode)
```

and you can't call something like Python's `next(...)` on this because it's an iterator and not a generator.  You have to either use a `for` loop, or create a list from the above before you can do much with it.  Creating lists in these cases would be inefficient, but we have so few items to deal with that it's not a concern currently.


### _About Bottle_

The definition of the service endpoints and the behaviors is in [`dibs/server.py`](dibs/server.py).  The endpoints are implemented using [Bottle](https://bottlepy.org).

The web server used at the moment is the development server provided by Bottle.  It has live reload built-in, meaning that changes to the `.py` files are picked up automatically and the server updates its behavior on the fly.

See http://bottlepy.org/docs/dev/tutorial.html#auto-reloading for an important note about Bottle: when it's running in auto-reload mode, _"the main process will not start a server, but spawn a new child process using the same command line arguments used to start the main process. All module-level code is executed at least twice"_.  This means some care is needed in how the top-level code is written.  Useful to know is that code can distinguish whether it's in the parent or child process by looking for the presence of the environment variable `'BOTTLE_CHILD'` set by Bottle in the child process.


### _About the documentation_

The docs are available online at [https://caltechlibrary.github.io/dibs/](https://caltechlibrary.github.io/dibs/).  They are built using [Sphinx](https://www.sphinx-doc.org) and [MyST](https://myst-parser.readthedocs.io/en/latest/index.html).  The sources are kept in the [`docs`](./docs) subdirectory.  The [`README.md`](./docs/README.md) file in the [`docs`](./docs) subdirectory explains how to build and preview the documentation locally.


License
-------

Software produced by the Caltech Library is Copyright (C) 2021, Caltech.  This software is freely distributed under a BSD/MIT type license.  Please see the [LICENSE](LICENSE) file for more information.

This repository includes other software as submodules.  They have their own software licenses.


Acknowledgments
---------------

This work was funded by the California Institute of Technology Library.

The [vector artwork](https://thenounproject.com/term/book-waiting/1531542/) of a book with a clock on it, used as the icon for this project, was created by [Royyan Wijaya](https://thenounproject.com/roywj/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

<div align="center">
  <br>
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src="https://raw.githubusercontent.com/caltechlibrary/dibs/main/.graphics/caltech-round.png">
  </a>
</div>
