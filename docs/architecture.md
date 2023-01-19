# System architecture

This page describes the goals, design, and organization of the DIBS software.

## Design goals

DIBS ("_**Di**gital **B**orrowing **S**ystem_") is intended to be a basic, standalone, [controlled digital lending](https://controlleddigitallending.org) system with the following goals:

* _Simplicity_. We wanted to keep everything as simple as we could -- simple user interfaces, simple internal logic, simple installation. This supported rapid development and deployment, and going forward, it will help continued maintenance and evolution.
* _Single sign-on integration_. DIBS doesn't implement logins, and instead relies on the web server to provide authentication via an institutional single sign-on system or other mechanism. This simultaneously avoids having to implement user account logins and other complex, error-prone elements in DIBS itself, and makes the user experience consistent with other institutional software systems.
* _Patron privacy_. In designing DIBS, we sought to minimize the amount of patron data requested and stored, to maintain patron privacy and reduce the impact of potential data leaks. DIBS does not store any patron information when a loan is not active, and during a loan, it stores only the user's institutional SSO identity combined with the (single) barcode they have on loan during the loan period. There are no provisions in the software for retaining the user information past the cooling-off period after the loan, or tracking identities or loan statistics based on user identities. In addition, a one-way anonymization process is applied when writing log files to prevent writing user's identities to the logs produced by DIBS.
* _Use of IIIF_. We chose IIIF because it is a highly flexible, widely-used, open standard for serving content, and there are many free and excellent resources for working with it (including servers and alternative viewers). However, DIBS does not rely on any particular workflow or system to create IIIF-compliant materials.  It only needs a IIIF manifest for each item that is to be made available for digital loans, and a IIIF server endpoint.
* _Decoupling_. The system is deliberately not integrated tightly with a particular LSP or ILS.  There is an object-oriented abstraction layer to isolate LSP-specific code to a small number of lines. It currently supports FOLIO and TIND, but the abstraction layer is extensible.  The record metadata needed by DIBS is very basic and consists of just 8 fields such as a barcode, a title, an author list, a year, and a few others.  There is zero dependence on particular data formats, too -- no XML, no MARC, nothing. This should make it possible to replace the TIND-specific code with an interface to another LSP without great difficulty.


## Architectural overview

The following diagram illustrates the components of a complete CDL system using DIBS, as it is deployed at Caltech.

<figure>
    <img width="75%" src="_static/media/architecture-diagram.svg">
</figure>

The following summarizes the components depicted above:
* A book scanner is used by Library staff to scan the pages of books or other items in response to requests from Caltech faculty.
* A network attached storage (NAS) system in the Caltech Library is the destination for the TIFF images produced during the scanning procedure.  For each book to be put in DIBS, staff create a folder named after the book's barcode.
* A  [script written in Python](https://github.com/caltechlibrary/dibs-scripts) converts the scanned document images into a IIIF-compliant format, and also creates a [IIIF](https://iiif.io) manifest. The script copies the converted images to a location where our IIIF server will find them, and also copies the manifest to a directory on the server running DIBS.   The manifest is given a file name with the pattern <i><code>barcode</code></i><code>-manifest.json</code>, where <i><code>barcode</code></i> is the item's barcode.
* An Amazon S3 bucket is the location where the converted files are stored. The files are placed there by the script mentioned in the previous bullet point.
* An Amazon Lambda serverless application instance runs [serverless-iiif](https://github.com/nulib/serverless-iiif). This process responds to IIIF requests from DIBS, and returns the images stored in the Amazon S3 bucket. (However, DIBS is not dependent on `serverless-iiif`, and other IIIF servers can be used.)
* The compute server running DIBS is located in the Library's on-premises computing facility. The server runs an Apache web server that is configured to run DIBS as a [WSGI](https://wsgi.readthedocs.io/en/latest/what.html)-compliant application. The DIBS server uses an internal [SQLite](https://www.sqlite.org/index.html) database (not shown) to track active loans, the items available for loans, and the IIIF manifests for the items.
* The Apache web server contacts an SSO network service operated by Caltech's campus information technology group. The SSO service runs separately from the Library's computing infrastructure.
* The LSP used by Caltech ([FOLIO](https://www.folio.org)) runs in a hosted service provider's facilities. DIBS only needs to contact the LSP to get basic metadata when an item is first added to DIBS by library staff.
* Each user's web browser runs an instance of the [Universal Viewer](http://universalviewer.io) to display borrowed item content. The viewer is configured to contact the DIBS server for all content requests, thus masking the storage location for the IIIF content and making the DIBS server the sole arbiter of loan status and loan duration.

The current implementation has some potential bottlenecks, notably in the use of a single server for handling requests from users. Based on experience we gain from the currently-running pilot deployment at Caltech (in early 2021), we may revise some elements in the future to scale them up as needed.


## The DIBS server in detail

DIBS is implemented on top of [Bottle](https://bottlepy.org), a lightweight WSGI micro web-framework for Python. The definitions of the service endpoints and the behaviors reside in [`dibs/server.py`](../dibs/server.py).  Information about available items, ongoing loans, history of loans, and user access permissions are kept in an [SQLite](https://www.sqlite.org/index.html) database accessed via an object-relational mapping ([Peewee](http://docs.peewee-orm.com/en/latest/)). The web pages shown to users are generated by Bottle using HTML templates stored in in [`dibs/templates`](../dibs/templates); static elements such as CSS files are stored in [`dibs/static`](../dibs/static).


### Authentication/access control

There are 2 layers of access control in DIBS when deployed in a web server:

1. can an incoming user access any part of DIBS at all?
2. can the user access staff pages, or only patron pages?

Layer #1 is implemented in the web server environment, and the details of how it's done depends on the specifics of the installation.  As far as DIBS is concerned, it only cares about whether a user has been authenticated or not.  When a page or API endpoint is requested from DIBS, the request environment given to DIBS by the web server will either include a user identity (if the use has been authenticated) or not.  DIBS simply refuses access to everything it controls if a user identity is not present in the request environment.

Layer #2 is implemented in DIBS itself.  DIBS uses `Person` objects to distinguish between people known to have staff access (i.e., who can access pages like `/list`), and everyone else.  When a request for a page or an endpoint comes in, DIBS looks for the user identifier in the HTTP request environment passed in from the web server, checks if that user is in the `Person` table in the database, and checks if the user has a role of `"library"`.  If the role is `"library"`, access to staff pages is granted; if not, the user is not shown links to the staff pages nor can they access the relevant endpoints.


### Actions implemented by the server

   Here is a summary of the endpoints implemented by the system:

| Endpoint                    | Type | Access | Purpose                                        |
| --------------------------- | ---- | ------ | ---------------------------------------------- |
| `/`                         | GET  | Any    | Main landing page; gives brief info about site |
| `/about`                    | GET  | Any    | Describes the DIBS system and its origin       |
| `/add`                      | GET  | Staff  | Show the page to add/edit an item              |
| `/delete-thumbnail/BARCODE` | GET  | Staff  | Delete the thumbnail image for BARCODE         |
| `/download/<type>/<data>`   | GET  | Staff  | Download the item list or loan history         |
| `/edit/BARCODE`             | GET  | Staff  | Show the page to add/edit an item              |
| `/iiif/<args>`              | GET  | Any    | Send IIIF content to viewer                    |
| `/info`                     | GET  | Any    | Same as `/`                                    |
| `/item-status/<args>`       | GET  | Any    | Get loan availability info about an item       |
| `/item/BARCODE`             | GET  | Any    | Shows item information page for a given item   |
| `/list`                     | GET  | Staff  | Show what's available for loans                |
| `/loan`                     | POST | Any    | Handles Loan button from `/item` page          |
| `/logout`                   | GET  | Any    | Logs out the current SSO session               |
| `/manage`                   | GET  | Staff  | Show the page to manage the list of items      |
| `/manifests/BARCODE`        | GET  | Any    | Sends manifest to viewer                       |
| `/notallowed`               | GET  | Any    | Error page for invalid requests                |
| `/notallowed`               | POST | Any    | Error page for invalid rquests items           |
| `/ready`                    | POST | Staff  | Toggles item ready status in `list` page       |
| `/remove`                   | POST | Staff  | Handles button in `manage` page                |
| `/return/BARCODE`           | POST | Any    | Handles Return button from viewer page         |
| `/start-processing`         | POST | Staff  | Write the workflow init file for an item       |
| `/static/<args>`            | GET  | Any    | Send static content (used by pages & viewer)   |
| `/stats`                    | GET  | Staff  | Show the statistics page                       |
| `/status`                   | GET  | Staff  | Show the statistics page                       |
| `/thankyou`                 | GET  | Any    | Destination after user uses Return button      |
| `/thumbnails/BARCODE.jpg`   | GET  | Any    | Fetch the thumbnail image for BARCODE          |
| `/update/add`               | POST | Staff  | Accepts form input from add/edit page          |
| `/update/edit`              | POST | Staff  | Accepts form input from add/edit page          |
| `/view/<args>`              | GET  | Any    | Show the item in the viewer page               |
| `/viewer/<args>`            | GET  | Any    | Handles requests for viewer elements           |


### The LSP interface

To save library staff the trouble of having to enter book metadata manually when adding a new item to DIBS, the system gets basic title/author/year/etc information from an institutional ILS or LSP automatically. DIBS features a straightforward abstraction layer that separates the details of contacting ILS/LSP servers from the main code. At Caltech, we originally used [TIND](https://tind.io) but in mid-2021 switched to [FOLIO](https://www.folio.org); the abstraction layer in DIBS currently has interfaces to both systems, and the use of one or the other is determined by a variable in the site `settings.ini` file.

The LSP abstraction layer consists of three main object classes, `LSP`, `LSPRecord` and `LSPInterface`, defined in [`dibs/lsp.py`](../dibs/lsp.py). 

* The class `LSPRecord` defines the metadata fields that are used by the DIBS server. These are title, author, year, and a few others.
* For every ILS/LSP system to which DIBS can interface, there is a subclass of `LSPInterface` that implements the details of communicating with the ILS/LSP server and getting metadata about an item given a barcode.
* The `LSP` class handles the miscellaneous details of reading configuration data from `settings.ini` and creating the appropriate subclass of interface. This is what is actually used by the code in [`dibs/server.py`](../dibs/server.py) to get an interface object for communicating with the ILS/LSP service at run time.


## The DIBS database in detail

As mentioned above, DIBS maintains an internal database.  The interface is defined in terms of high-level objects that are backed by an [SQLite](https://www.sqlite.org/index.html) database back-end.  The ORM used is [Peewee](http://docs.peewee-orm.com/en/latest/).

The database consists of four object models:

*  `Item`: this describes an item available via DIBS. Each item available for loaning out gets a separate `Item` object in the database. The object fields include the following: the barcode used by the LSP to identify the item, the page in the LSP for displaying information about the item, the number of copies being made available through DIBS, the loan duration, whether the item is ready/available or not, and staff notes.  A number of metadata fields that are not strictly necessary for loans are also stored in the `Item`, such as the title and authors of the work; these are to avoid having to do lookups in the LSP every time the information is needed.
* `Loan`: loan objects describe an active or recently-ended loan. The object fields include the start time, end time, reloan time, and user login.
* `History`: after a loan has ended and the reloan time has expired, DIBS creates a `History` object to keep a basic record of the item that was borrowed for purposes of reporting statistics. The fields stored are very limited: the item borrowed, the start time, and the end time &ndash; that's all. User logins are not retained.
* `Person`: in order to determine whether a given user can be shown staff pages, DIBS uses objects called `Person`. The object has fields for the user's login, and a role. DIBS _only_ an object for every staff user: non-staff users don't need to be listed in the `Person` table, and thus patron identities are not stored in the database.




## The IIIF server in detail

DIBS does not include a IIIF server. Instead, it can work with any compliant IIIF server that you wish to set up or already have access to.

Before choosing and setting up a IIIF server, it may be helpful to understand how DIBS will use it. The process of accessing content and serving it proceeds roughly like this:

1. A IIIF viewer client (such as the [Universal Viewer](http://universalviewer.io) included with DIBS) requests a [IIIF manifest file](https://iiif.io/explainers/using_iiif_resources/#iiif-manifest) from DIBS at the endpoint `/manifests/BARCODE`, where `BARCODE` is the item barcode.
2. DIBS checks if the user making the request has an active loan on `BARCODE`. If not, it responds with an error code; otherwise, DIBS performs the following steps:
    1. retrieves the manifest file from disk and reads it into memory;
    2. modifies the contents of the manifest file in memory, replacing every instance of the IIIF base URL (set in the site `settings.ini` file) with a URL that points at DIBS' address rather than the real IIIF server; and
    3. sends the adjusted manifest file contents to the client.
3. The IIIF client parses the manifest to learn the URLs for the page images.
4. The client starts fetching images at the URLs following the IIIF protocol. (Since these URLs all point to a location under `/iiif` on the DIBS server by virtue of the transformation applied in step 2b, the requests actually go to the DIBS server, not the actual IIIF server.)
5. For every URL request from the client, DIBS checks if the user has an active loan on the associated item. If the user does, then DIBS reverses the transformation it previously applied to the URL so it can determine the real IIIF URL, fetches the image data from the IIIF server, and returns the image data to the client.  To improve performance, the DIBS server also caches images in memory, so that subsequent client requests are answered more quickly.

The most important implication of this scheme is the following: **for content that you host in your instance of DIBS, clients never contact the IIIF server directly**. Everything goes through DIBS, which acts as a conduit between the client and the IIIF server. The only exception is if your manifest file contains references to a IIIF server address for which DIBS is _not_ configured to rewrite URLs; then clients will contact that server directly.

This approach gives you the freedom to set up your IIIF server in many ways. All that DIBS needs to know is a base URL, and all that DIBS does is request pages using the IIIF protocol.  As long as DIBS can communicate with the IIIF server you use, things should work.

At Caltech, we use a copy of [serverless-iiif](https://github.com/samvera-labs/serverless-iiif) hosted on an Amazon AWS server. That server is configured to read images from an Amazon S3 bucket where we store the book content for DIBS. Clients do not know the details, however, and we could equally have used a different IIIF server hosted on our own hardware, or something else. We can also change the IIIF server setup at any time without clients needing to make any changes.
