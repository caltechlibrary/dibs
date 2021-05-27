# Installation and configuration

## Requirements

The core DIBS server is written in [Python 3](https://www.python.org) and makes use of some additional Python software libraries that are installed automatically during the [installation step](#installation) described below.

Separately, DIBS also relies on the existence of a IIIF image server (and some content to serve). At Caltech, we use a serverless component running on an Amazon cloud instance, but [many other IIIF server options exist](https://github.com/IIIF/awesome-iiif#image-servers). For exploration and demonstration purposes, you could reference content located in any of a number of publicly-accessible IIIF servers around the world, and DIBS includes a sample [IIIF manifest](https://iiif.io/explainers/using_iiif_resources/#iiif-manifest) as an example of that.

To deploy DIBS for production use, two more things are needed: a web server to host the system, and an authentication layer.  The current version of DIBS has only been tested with Apache2 on Linux (specifically, Ubuntu 20) and macOS (specifically 10.13, High Sierra). For authentication, DIBS assumes that the web server takes care of user authentication in such a way that DIBS is behind the authentication layer and only needs to recognize users who are allowed to access restricted pages. In Caltech's case, we use the [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) single sign-on system for the authentication layer, but it is possible to use other schemes.  The installation and configuration of a single sign-on system depends on the specifics of a given institution, and are not described here.

## Installation

The current version of DIBS does not have a separate installation process; using DIBS currently means having to get the source code from this repository and running it from the source directory.

### ⓵ _Get the DIBS source code_

There are several ways of getting the latest release of the DIBS source code. Here is one of the simplest:

1. Go to the [releases page](https://github.com/caltechlibrary/dibs/releases) in the GitHub repository for DIBS.
2. Find the latest release there (normally the first one on the page). <img align="right" width="200px" src="https://github.com/caltechlibrary/dibs/raw/main/.graphics/assets.png"/>
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


## Configuration

Certain characteristics of DIBS are configured using a file named `settings.ini`, which DIBS looks for in the `dibs` directory. The file `settings.ini-example` is a sample configuration file for DIBS.  Copy the file to `settings.ini`,

```sh
cp settings.ini-example settings.ini
```

and edit its contents in a text editor to suit your local installation. The comments explain what each of the variables does, but we elaborate on some of the variables below.

### `MANIFEST_DIR`

This variable sets the path to the directory where DIBS looks for manifest files.  Each file name should follow the pattern <i><code>N</code></i><code>-manifest.json</code>, where <i><code>N</code></i> is the item barcode.  The source distribution of DIBS comes with a sample manifest for illustration purposes.

### `IIIF_BASE_URL`

The value of this variable should have the form `https://youriiifserver.com/iiif/2`, and it should be the common base for IIIF URLs served by your IIIF server. (This means that the value should appear throughout your manifest files, as the common root of all page images.) This URL will not be shared with clients.  **You should protect this URL from becoming public** if you are making copyrighted works available via DIBS, because knowledge of this URL would allow anyone with familiarity with IIIF to bypass restrictions in DIBS and access your IIIF content directly.

When DIBS reads a manifest, it replaces all instances of the value of `IIIF_BASE_URL` with a URL rooted at the DIBS server's address, and this modified manifest is what it serves to clients. When a client requests page images via the translated URL, DIBS reverses the transformation to construct the IIIF URL from where it can get the page image, and then returns that data back to the client. The client never sees the real URL of the IIIF server or the images. The _controlled digital lending_ aspect of DIBS is that it also refuses to return IIIF content unless the client has been authenticated and the user has borrowed the item through DIBS' loan system.


## Management of staff roles

As mentioned above, DIBS assumes that another mechanism in the web server handles authentication of users. However, DIBS needs to distinguish between users who are allowed to perform administrative tasks (such as adding new items for loans and setting loan parameters) and other users. DIBS employs a simple "people" table in its database, and a program, [`people-manager`](people-manager), that provides an interface for adding user role information to this table.

To be able to manage DIBS content, you must create at least one user with a role of "library". As an example, suppose you want to name your sample user `dibsuser`, then you could run the following command:

```sh
./people-manager add role="library" uname="dibsuser"
```


## Operation

### Running DIBS locally for demonstration and development

For demonstration purposes as well as development, it's convenient to run DIBS on your local machine.  The following instructions describes how you can do this. Prior to starting the DIBS server for the first time, for testing purposes, you may want to add some sample data. This can be done by running the script [`load-mock-data.py`](load-mock-data.py):

```sh
python3 load-mock-data.py
```

For local experimentation and development only, the script [`run-server`](run-server) can be used to start a local copy of the server.  It assumes you are in the current directory, and it takes a few arguments for controlling its behavior:

```sh
./run-server -h
```

As mentioned above, in a real installation, DIBS needs a single sign-on system such as [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) on the server to provide user authentication.  This is not the situation in a local development server, and so for demo/debugging purposes, the `run-server` command lets you tell DIBS that a specific user has already been authenticated.  Using the example user from above, you can start a local DIBS server in debug mode like this:

```sh
./run-server -m debug -u dibsuser
```

By default it starts the server on `localhost` port 8080.  Using the `debug` run mode flag changes the behavior in various useful ways, such as to reload the source files automatically if any of them are edited, and to run `pdb` upon any exceptions.  (These would not be enabled in a production server.)

Note that `run-server` is **not intended for use in production servers**. For actual use, you must configure a web server such as [Apache](https://httpd.apache.org) to host the system. DIBS comes with an [`adapter.wsgi`](adapter.wsgi) and an example [Apache conf file](dibs.conf-example) for this purpose to help you get started.


### Running DIBS in production

DIBS comes with a sample Apache configuration file in `dibs.conf-example`. This file configures the web server and tells it to use `adapter.wsgi` (also provided with DIBS) to define a WSGI application for DIBS.
