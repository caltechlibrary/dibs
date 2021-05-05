# Installation and configuration

DIBS is a web-based system.


## Requirements

DIBS is written in [Python 3](https://www.python.org) and makes use of additional, third-party software to run.  The [installation instructions](#installation) below describe how to install the additional software packages it needs.

Separately, DIBS also assumes that the web server takes care of user authentication in such a way that DIBS is behind the authentication layer and does not need to do anything beyond distinguishing between regular users and those who have staff priviledges. (The latter are allowed to manage the content served by DIBS; the former can only view it.) In Caltech's case, we use the [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) single-signon system for the authentication layer, but it is possible to use other schemes.  The installation and configuration of a single-signon system depends on the specifics of a given institution, and are not described here.

## Installation

The current version of DIBS does not have a separate installation process; using DIBS currently means having to get the source code from this repository and running it from the source directory.


### ⓵ _Get the DIBS source code_

You can use `git` to clone this repository:

```sh
git clone https://github.com/caltechlibrary/dibs
```

This will create a `dibs` subdirectory in your current directory.


### ⓶ _Install Python dependencies_

Next, install the Python dependencies on your system or your virtual environment:

```sh
cd dibs
python3 -m pip install -r requirements.txt --upgrade
```


## Configuration

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


## Operation


### ⓸ _Start a local DIBS server_ for testing

For local experimentation and development only, the script [`run-server`](run-server) can be used to start a local copy of the server.  It assumes you are in the current directory, and it takes a few arguments for controlling its behavior:

```sh
./run-server -h
```

In a real installation, DIBS needs a single-signon system such as [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) on the server to provide user authentication.  This is not the situation in a local development server, and so for demo/debugging purposes, the `run-server` command lets you tell DIBS that a specific user has already been authenticated.  Using the example user from above, you can start a local DIBS server in debug mode like this:

```
./run-server -m debug -u dibsuser
```

By default it starts the server on `localhost` port 8080.  Using the `debug` run mode flag changes the behavior in various useful ways, such as to reload the source files automatically if any of them are edited, and to run `pdb` upon any exceptions.  (These would not be enabled in a production server.)

Note that `run-server` is **not intended for use in production servers**. For actual use, you must configure a web server such as [Apache](https://httpd.apache.org) to host the system. DIBS comes with an [`adapter.wsgi`](adapter.wsgi) and an example [Apache conf file](dibs.conf-example) for this purpose to help you get started.
