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

<p align="center"><img width="60%" src=".graphics/status-warning.svg"></p>


Requirements
-----------

DIBS is written in Python 3 and depends on additional software to work.  The [installation instructions](#installation) below describe how to install all of the dependencies.  In summary, in addition to a number of Python packages, DIBS also needs: the [Universal Viewer](http://universalviewer.io), used to display content; [Node](https://nodejs.dev) modules used by the Universal Viewer; and [SQLite3](https://www.sqlite.org/), used as the main database for DIBS data.


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
python3 -m pip install -r requirements.txt --upgrade
```

### ⓷ _Install Node dependencies_

Change into to the [`viewer`](viewer) subdirectory, and run the following command to install the Node dependencies for the Universal Viewer:

```sh
cd viewer
npm install
```


Usage: running the server locally
---------------------------------

For demonstration purposes as well as development, it's very convenient to run DIBS on your local machine.  The following instructions describe the process assuming that DIBS has never been configured or run on your system.


### ⓵ _Copy the sample `settings.ini` configuration file_

The file `settings.ini-example` is a sample configuration file for DIBS.  Copy the file to `settings.ini`,

```sh
cp settings.ini-example settings.ini
```

and edit its contents in a text editor to suit your local installation.


### ⓶ _Load a sample book into DIBS_

Prior to starting the DIBS server for the first time, for testing purposes, you may want to add some sample data. This can be done by running the script [`load-mock-data.py`](load-mock-data.py):

```sh
python3 load-mock-data.py
```


### ⓷ _Load a sample user into DIBS_

The program [`people-manager`](people-manager) is an interface to adding and manipulating user data.  To log into the demo DIBS configuration, create at least one user with a role of "library":

```sh
./people-manager add role="library" uname= secret=
```


### ⓸ _Start the DIBS server_

The script [`run-server`](run-server) can be used to start a local copy of the server for experimentation and development.  It assumes you are in the current directory, and it takes a few arguments for controlling its behavior:

```sh
./run-server -h
```

You can run it without any arguments to try out DIBS.  By default it starts the server on `localhost` port 8080.

```sh
./run-server
```

If you are doing development on DIBS, you may find the `--verbose` flag helpful, to see more information about what DIBS is doing in response to every request:

```sh
./run-server --verbose
```

The server will automatically reload the source files if any of them are edited.  If you need to put breakpoints in the code, the `--debug` flag is useful; it disables template caching and turns on other debugging features:

```sh
./run-server --debug
```

_Important_: debug mode also turns off auto-reloading of source files, so be aware you have to restart the server manually if you edit source files in debug mode.


General information
-------------------

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
