# System architecture

This page describes the goals, design, and operation of DIBS.

## Design goals

DIBS ("_**Di**gital **B**orrowing **S**ystem_") is intended to be a _basic_ controlled digital lending system with the following goals:

* _Simplicity_. the core server logic for serving loans and other DIBS web pages is less than 800 lines of Python. It should be possible for anyone interested to inspect the code, understand it, and fix or extend it as needed.
* _Patron privacy_. In designing DIBS, we sought to minimize the amount of patron data requested and stored, to maintain patron privacy and reduce the impact of potential data leaks. DIBS does not store any patron information when a loan is not in effect, and during a loan, it stores only the user's institutional SSO identity combined with the (single) barcode they have on loan during the loan period. There are no provisions in the software for retaining the information past the loan period, or tracking identities or loan statistics based on user identities.
* _Independence_. The system is deliberately not integrated tightly with an ILS.  The current interface to Caltech's TIND ILS is limited to one part of one Python function in the server, and the item metadata fields needed by DIBS are very basic: a barcode, a title, an author list, a year, and a couple of others.  There is zero dependence on data formats, too &ndash; no XML, no MARC, nothing. This should make it possible to replace the TIND-specific code with an interface to another ILS without great difficulty.
*  _Easy installation_. DIBS is written entirely in Python, and comes bundled with a copy of the JavaScript-based Universal Viewer. The only external things it needs are a WSGI-compliant web server such as Apache, a IIIF image server running under your control, and a single sign-on (SSO) system. Not only does this limited dependence on other software simplify maintenance, but it also should make migration to new servers easier.
* _Use of IIIF_. We chose IIIF because it is a highly flexible, widely-used, open standard for serving content, and there are many free and excellent resources for working with it (including servers and alternative viewers).


## Basic workflow

For any given item made available via DIBS, the scanned pages of the original are stored on an internal shared file system and identified by a barcode. A workflow written in Python is used to create a [IIIF](https://iiif.io) manifest; this manifest is added to the system, which then makes the scanned contents available via a data endpoint served by DIBS. This allows DIBS to implement the digital loan policies developed by our institution, such as that patrons can only borrow one item at a time.

<!--
## Database

The definition of the database is in [`dibs/database.py`](../dibs/database.py).  The interface is defined in terms of high-level objects that are backed by an SQLite database back-end.  The ORM used is [Peewee](http://docs.peewee-orm.com/en/latest/).

Worth knowing: Peewee queries are lazy-executed: they return iterators that must be accessed before the query is actually executed.  Thus, when selecting items, the following returns a Peewee `ModelSelector`, and not a single result or a list of results:

```python
Item.select().where(Item.barcode == barcode)
```

and you can't call something like Python's `next(...)` on this because it's an iterator and not a generator.  You have to either use a `for` loop, or create a list from the above before you can do much with it.  Creating lists in these cases would be inefficient, but we have so few items to deal with that it's not a concern currently.


## Server

## Endpoints

The definition of the service endpoints and the behaviors is in [`dibs/server.py`](../dibs/server.py).  The endpoints are implemented using [Bottle](https://bottlepy.org).  Here is a summary of the endpoints implemented by the system:

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



## Architectural notes

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

-->
