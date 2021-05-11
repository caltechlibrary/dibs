# System architecture

This page describes the goals, design, and operation of DIBS.

## Design goals

DIBS ("_**Di**gital **B**orrowing **S**ystem_") is intended to be a basic, standalone, [controlled digital lending](https://controlleddigitallending.org) system with the following goals:

* _Simplicity_. We wanted to keep everything as simple as we could -- simple user interfaces, simple internal logic, simple installation. This supported rapid development and deployment, and going forward, it will help continued maintenance and evolution.
* _Patron privacy_. In designing DIBS, we sought to minimize the amount of patron data requested and stored, to maintain patron privacy and reduce the impact of potential data leaks. DIBS does not store any patron information when a loan is not active, and during a loan, it stores only the user's institutional SSO identity combined with the (single) barcode they have on loan during the loan period. There are no provisions in the software for retaining the information past the loan period, or tracking identities or loan statistics based on user identities.
* _Single sign-on integration_. DIBS doesn't implement logins, and instead relies on an institutional single sign-on system to provide authentication. This simultaneously avoids having to implement user account logins and other complex, error-prone elements in DIBS itself, and makes the user experience consistent with other institutional software systems.
* _Independence_. The system is deliberately not integrated tightly with an ILS.  The current interface to Caltech's TIND ILS is limited to a very small section of code in the server, and the item metadata fields needed by DIBS are very basic: a barcode, a title, an author list, a year, and a couple of others.  There is zero dependence on data formats, too -- no XML, no MARC, nothing. This should make it possible to replace the TIND-specific code with an interface to another ILS without great difficulty.
* _Use of IIIF_. We chose IIIF because it is a highly flexible, widely-used, open standard for serving content, and there are many free and excellent resources for working with it (including servers and alternative viewers). However, DIBS does not rely on any particular workflow or system to create IIIF-compliant materials.  It only needs a IIIF manifest for each item that is to be made available for digital loans, and a IIIF server endpoint.


## Architectural overview

The following diagram illustrates the components of a complete CDL system using DIBS, as it is deployed at Caltech.

<figure>
    <img src="_static/media/architecture-diagram.svg">
</figure>

The following summarizes the components depicted above:
* A network attached storage (NAS) system in the Caltech Library is the destination for book scans made by the Library's staff in response to request from Caltech faculty. For each book, staff create a folder named after the book's barcode.
* A  [script written in Python](https://github.com/caltechlibrary/dibs-scripts) converts the scanned document images into a IIIF-compliant format, and also creates a [IIIF](https://iiif.io) manifest. The script copies the converted images to a location where our IIIF server will find them, and also copies the manifest to a directory on the server running DIBS.   The manifest is given a file name with the pattern <i><code>barcode</code></i><code>-manifest.json</code>, where <i><code>barcode</code></i> is the item's barcode.
* An Amazon S3 bucket is the location where the converted files are stored.
* An Amazon Lambda serverless application instance runs [serverless-iiif](https://github.com/nulib/serverless-iiif). This process responds to IIIF requests from DIBS, and returns the images stored in the Amazon S3 bucket.
* The compute server running DIBS is located in the Library's on-premises computing facility. The server runs an Apache web server that is configured to run DIBS as a [WSGI](https://wsgi.readthedocs.io/en/latest/what.html)-compliant application. The DIBS server uses an internal [SQLite](https://www.sqlite.org/index.html) database (not shown) to track active loans, the items available for loans, and the IIIF manifests for the items.
* DIBS contacts an SSO service operated by Caltech's campus information technology group. The SSO service runs separately from the Library's computing infrastructure.
* Each user's web browser runs an instance of the [Universal Viewer](http://universalviewer.io) to display borrowed item content. The viewer is configured to contact the DIBS server for all content requests, thus masking the storage location for the IIIF content and making the DIBS server the sole arbiter of loan status and loan duration.

The current implementation has some obvious bottlenecks, notably in the use of a single server for handling requests from users. Based on experience we gain from the currently-running pilot deployment at Caltech (in early 2021), we may revise some elements in the future to scale them up as needed.


## The DIBS server in more detail

DIBS is implemented on top of [Bottle](https://bottlepy.org), a lightweight WSGI micro web-framework for Python. The definition of the service endpoints and the behaviors is in [`dibs/server.py`](../dibs/server.py).   Here is a summary of the endpoints implemented by the system:

| Endpoint                 | Type | Access | Purpose              |
|--------------------------|------|--------|----------------------|
| `/`                      | GET  | Any    | Main landing page; gives brief info about site |
| `/about`                 | GET  | Any    | Describes the DIBS system and its origin |
| `/add`                   | GET  | Staff  | Show the page to add/edit an item |
| `/edit/<barcode>`        | GET  | Staff  | Show the page to add/edit an item |
| `/iiif/<args>`           | GET  | Any    | Send IIIF content to viewer |
| `/info`                  | GET  | Any    | Same as `/` |
| `/item-status/<args>`    | GET  | Any    | Get loan availability info about an item |
| `/item/<barcode>`        | GET  | Any    | Shows item information page for a given item |
| `/list`                  | GET  | Staff  | Show what's available for loans |
| `/loan`                  | POST | Any    | Handles Loan button from `/item` page |
| `/logout`                | GET  | Any    | Logs out the current SSO session |
| `/manage`                | GET  | Staff  | Show the page to manage the list of items |
| `/manifests/<barcode>`   | GET  | Any    | Sends manifest to viewer |
| `/notallowed`            | GET  | Any    | Error page for invalid requests |
| `/notallowed`            | POST | Any    | Error page for invalid rquests items |
| `/ready`                 | POST | Staff  | Handles checkbox in `list` page to make an item ready to loan |
| `/remove`                | POST | Staff  | Handles button in `list` page to remove an item |
| `/return/<barcode>`      | POST | Any    | Handles Return button from viewer page |
| `/static/<args>`         | GET  | Any    | Send static content (used by pages & viewer) |
| `/stats`                 | GET  | Staff  | Show the statistics page |
| `/status`                | GET  | Staff  | Show the statistics page |
| `/thankyou`              | GET  | Any    | Destination after user uses Return button |
| `/update/add`            | POST | Staff  | Accepts form input from add/edit page |
| `/update/edit`           | POST | Staff  | Accepts form input from add/edit page | 
| `/view/<args>`           | GET  | Any    | Show the item in the viewer page |
| `/viewer/<args>`         | GET  | Any    | Handles requests for components of the viewer page |


## The DIBS database in more detail

As mentioned above, DIBS maintains an internal database of item description and loan status.  The interface is defined in terms of high-level objects that are backed by an [SQLite](https://www.sqlite.org/index.html) database back-end.  The ORM used is [Peewee](http://docs.peewee-orm.com/en/latest/).


## The IIIF server in more detail

... _Forthcoming_ ...
