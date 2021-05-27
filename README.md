# Caltech DIBS<img width="70em" align="right" src="https://github.com/caltechlibrary/dibs/raw/main/docs/_static/media//dibs-icon.png">

Caltech DIBS ("_**Di**gital **B**orrowing **S**ystem_") is the Caltech Library's implementation of a basic, standalone, [controlled digital lending](https://archive.org/details/controlled-digital-lending-explained) system.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg?style=flat-square)](https://www.python.org/downloads/release/python-380/)
[![Latest release](https://img.shields.io/github/v/release/caltechlibrary/dibs.svg?style=flat-square&color=b44e88)](https://github.com/caltechlibrary/dibs/releases)
[![DOI](https://img.shields.io/badge/dynamic/json.svg?label=DOI&style=flat-square&color=lightgray&query=$.metadata.doi&uri=https://data.caltech.edu/api/record/1959)](https://data.caltech.edu/records/1959)

## Table of contents

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage: running the server locally](#usage-running-the-server-locally)
* [General information](#general-information)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#getting-help)
* [Contributing](#contributing)
* [License](#license)
* [Authors and history](#authors-and-history)
* [Acknowledgments](#authors-and-acknowledgments)


## Introduction

DIBS is a web-based system that enables members of Caltech to borrow materials that are not otherwise available in e-book or other electronic formats.  The system was developed in the year 2021 to help Caltech students and faculty continue their studies and work during the global [COVID-19 pandemic](https://www.who.int/emergencies/diseases/novel-coronavirus-2019). Access to content in Caltech's live DIBS server is limited to members of Caltech, but the software for DIBS itself is open-sourced under a BSD type license.

The concept of [controlled digital lending](https://controlleddigitallending.org/faq) (CDL) is to allow libraries to loan items to digital patrons in a "lend like print" fashion.  It is the digital equivalent of traditional library lending. Libraries digitize a physical item from their collection, then lend out a secured digital version to one user at a time while the original, printed copy is simultaneously marked as unavailable. The number of digital copies of an item allowed to be loaned at any given time is strictly controlled to match the number of physical print copies taken off the shelves, to ensure an exact "owned-to-loaned" ratio.

DIBS provides two main components of a CDL system: a loan tracking system, and an integrated digital content viewing interface.  DIBS embeds the [Universal Viewer](http://universalviewer.io) to display materials that comply with the [International Image Interoperability Framework](https://iiif.io) (IIIF). To use DIBS as part of a complete CDL system at another institution, you only need to set up a IIIF server and a web server that implements user authentication.

<p align="center"><img width="60%" src=".graphics/status-warning.svg"></p>


## Requirements

The core DIBS server is written in [Python 3](https://www.python.org) and makes use of some additional Python software libraries that are installed automatically during the [installation step](#installation) described below.

Separately, DIBS also relies on the existence of a IIIF image server (and some content to serve). At Caltech, we use a serverless component running on an Amazon cloud instance, but [many other IIIF server options exist](https://github.com/IIIF/awesome-iiif#image-servers). For initial exploration and demonstration purposes, you could reference content located in any of a number of publicly-accessible IIIF servers around the world, and DIBS includes a sample [IIIF manifest](https://iiif.io/explainers/using_iiif_resources/#iiif-manifest) as an example of that.

To deploy DIBS for production use, two more things are needed: a web server to host the system, and an authentication layer.  The current version of DIBS has only been tested with Apache2 on Linux (specifically, Ubuntu 20) and macOS (specifically 10.13, High Sierra). For authentication, DIBS assumes that the web server takes care of user authentication in such a way that DIBS is behind the authentication layer and all users who can reach the DIBS pages are allowed to view content. DIBS only implements checks to distinguish between regular users versus staff who are allowed to access restricted pages. For the authentication layer, at Caltech we use the [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) single sign-on system, but it is possible to use other schemes.  The installation and configuration of a single sign-on system depends on the specifics of a given institution, and are not described here.


## Installation

The current version of DIBS does not have a separate installation process; using DIBS currently means having to get the source code from this repository and running it from the source directory.


### ⓵ _Get the DIBS source code_

There are several ways of getting the latest release of the DIBS source code. Here is one of the simplest:

1. Go to the [releases page](https://github.com/caltechlibrary/dibs/releases) in the GitHub repository for DIBS.
2. Find the latest release there (normally the first one on the page). <img align="right" width="225px" src="https://github.com/caltechlibrary/dibs/raw/main/.graphics/assets.png"/>
3. Find the **Assets** section of the release.
4. Click on the link titled **Source code** (zip); it will be downloaded.
5. Unzip the file.

The result will be a subdirectory named `dibs`, which contains the source code.

### ⓶ _Install Python dependencies_

Next, install the Python dependencies on your system or your virtual environment:

```sh
cd dibs
python3 -m pip install -r requirements.txt
```

That is all you should need to run a demo of DIBS on a Linux or macOS system.  As mentioned above, if you plan on deploying DIBS, you will also need to install and configure Apache, and an authentication system running in conjunction with the Apache server. Instructions for doing this vary too widely based on individual site requirements, and are outside the scope of this document.


## Usage: running a server locally for demo/development

For demonstration purposes as well as development, it's convenient to run DIBS on your local machine.  The following instructions describe the process, assuming that DIBS has never been configured or run on your system.


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

The program [`people-manager`](people-manager) is an interface for adding user and role information.  To be able to manage DIBS content, create at least one user with a role of "library".  Suppose you want to name your sample user "dibsuser", then you could run the following command:

```sh
./people-manager add role="library" uname=dibsuser
```


### ⓸ _Start a local DIBS server for testing_

For local experimentation and development only, the script [`run-server`](run-server) can be used to start a local copy of the server.  It assumes you are in the current directory, and it takes a few arguments for controlling its behavior:

```sh
./run-server -h
```

In a real installation, DIBS needs the web server to provide user authentication.  This is not the situation in a local development server, and so for demo/debugging purposes, the `run-server` command lets you tell DIBS that a specific user has already been authenticated.  Using the example user from above, you can start a local DIBS server in debug mode like this:

```
./run-server -m debug -u dibsuser
```

By default it starts the server on `localhost` port 8080.  Using the `debug` run mode flag changes the behavior in various useful ways, such as to reload the source files automatically if any of them are edited, and to run `pdb` upon any exceptions.  (These would not be enabled in a production server.)

Note that `run-server` is **not intended for use in production servers**. For actual use, you must configure a web server such as [Apache](https://httpd.apache.org) to host the system. DIBS comes with an [`adapter.wsgi`](adapter.wsgi) and an example [Apache conf file](dibs.conf-example) for this purpose to help you get started.


## General information

The docs are available online at [https://caltechlibrary.github.io/dibs/](https://caltechlibrary.github.io/dibs/).  They are built using [Sphinx](https://www.sphinx-doc.org) and [MyST](https://myst-parser.readthedocs.io/en/latest/index.html).  The sources are kept in the [`docs`](./docs) subdirectory.  The [`README.md`](./docs/README.md) file in the [`docs`](./docs) subdirectory explains how to build and preview the documentation locally.


## Known issues and limitations

DIBS is in active development.  The current version was produced rapidly, and has a limited scope and streamlined design.  We continue to improve DIBS in various ways.

It is worth mentioning that DIBS does not (currently) implement a queue or wait list for loan requests.  This is a conscious design decision.  Queuing systems tend to lead to complexity quickly, and we want to delay implementing a queue until it becomes clear that it's really essential.  (After all, in a physical library, there are no queues for borrowing books: you go to see if it's available, and if it's not, you can't borrow it.)  Perhaps we can implement interfaces and behaviors in DIBS that avoid the need for a queue at all!


## Getting help and support

If you find an issue, please submit it in [the GitHub issue tracker](https://github.com/caltechlibrary/dibs/issues) for this repository.


## Contributing

We would be happy to receive your help and participation with enhancing DIBS!  Please visit the [guidelines for contributing](CONTRIBUTING.md) for some tips on getting started.


## License

Software produced by the Caltech Library is Copyright (C) 2021, Caltech.  This software is freely distributed under a BSD-type license.  Please see the [LICENSE](LICENSE) file for more information.

This software repository includes a copy of the [Universal Viewer](http://universalviewer.io) version 3.1.1, obtained from the [GitHub repository](https://github.com/UniversalViewer/universalviewer/releases/tag/v3.1.1) as it existed on 2021-04-27.  The Universal Viewer is released under the MIT license.   Please see the Universal Viewer website and documentation for more information about any applicable copyrights or licensing terms.


## Authors and history

DIBS was designed and implemented by [Michael Hucka](https://github.com/mhucka), [Robert Doiel](https://github.com/rsdoiel), [Tommy Keswick](https://github.com/t4k) and [Stephen Davison](https://github.com/nosivads) of the Caltech Library's [Digital Library Development team](https://www.library.caltech.edu/staff?&field_directory_department%5B0%5D=754).


## Acknowledgments

This work was funded by the California Institute of Technology Library.

The [vector artwork](https://thenounproject.com/term/book-waiting/1531542/) of a book with a clock on it, used as the icon for this project, was created by [Royyan Wijaya](https://thenounproject.com/roywj/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.

DIBS makes use of numerous open-source packages, without which it would have been effectively impossible to develop DIBS with the resources we had.  We want to acknowledge this debt.  In alphabetical order, the packages are:

* [Arrow](https://pypi.org/project/arrow/) &ndash; a library for creating & manipulating dates
* [Boltons](https://github.com/mahmoud/boltons/) &ndash; package of miscellaneous Python utilities
* [Bottle](https://bottlepy.org) &ndash; a lightweight WSGI micro web framework for Python
* [CommonPy](https://github.com/caltechlibrary/commonpy) &ndash; a collection of commonly-useful Python functions
* [expiringdict](https://pypi.org/project/expiringdict/) &ndash; an ordered dictionary class with auto-expiring values
* [humanize](https://github.com/jmoiron/humanize) &ndash; make numbers more easily readable by humans
* [ipdb](https://github.com/gotcha/ipdb) &ndash; the IPython debugger
* [mod_wsgi](http://www.modwsgi.org) &ndash; an Apache module for hosting Python WSGI web applications
* [Peewee](http://docs.peewee-orm.com/en/latest/) &ndash; a simple ORM for Python
* [Plac](https://github.com/ialbert/plac) &ndash; a command line argument parser
* [Python Decouple](https://github.com/henriquebastos/python-decouple/) &ndash; a high-level configuration file interface
* [Rich](https://rich.readthedocs.io/en/latest/) &ndash; library for writing styled text to the terminal
* [Sidetrack](https://github.com/caltechlibrary/sidetrack) &ndash; simple debug logging/tracing package
* [str2bool](https://github.com/symonsoft/str2bool) &ndash; convert a string to a Boolean value
* [Topi](https://github.com/caltechlibrary/topi) &ndash; a simple package for getting data from a TIND.io ILS instance
* [Universal Viewer](https://github.com/UniversalViewer/universalviewer) &ndash; a browser-based viewer for content in [IIIF](https://iiif.io) format

<div align="center">
  <br>
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src="https://raw.githubusercontent.com/caltechlibrary/dibs/main/.graphics/caltech-round.png">
  </a>
</div>
