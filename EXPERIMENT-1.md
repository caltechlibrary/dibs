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

To run with debug tracing, use the `-@` option with an argument telling it where to send the output.  Using `-` will send it to stdout and using a file name will redirect it to a file.  For example,

```sh
./run-server -@ /tmp/debug.log
```

It's useful to have 2 shell windows open in that case: one where you start the server, and with `tail -f /tmp/debug.log` to see the trace.

To run the demo server, there needs to be one or more a manifest files put into the subdirectory `manifests`.


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

Most of the web pages use only HTTP GET methods.  A few use HTTP POST.  An explanation is warranted about about the way our POST actions work.  The POST actions are executed using a small bit of JavaScript in the associated HTML pages (see, e.g., [`dibs/templates/item.tpl`](dibs/templates/item.tpl).  That JavaScript uses AJAX to send the POST request with form data.  Our POST route handlers below do whatever action is needed, and then return a string (_not_ a page, _not_ a template).  The AJAX handler in our web page expects this and sets the value of the web page's `location.href` to the string returned, thus moving the user to whatever page we want to be shown after the action is done.

See http://bottlepy.org/docs/dev/tutorial.html#auto-reloading for an important note about Bottle: when it's running in auto-reload mode, _"the main process will not start a server, but spawn a new child process using the same command line arguments used to start the main process. All module-level code is executed at least twice"_.  This means some care is needed in how the top-level code is written.  Useful to know is that code can distinguish whether it's in the parent or child process by looking for the presence of the environment variable `'BOTTLE_CHILD'` set by Bottle in the child process.
