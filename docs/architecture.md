# System architecture

This page describes the goals, design, and operation of DIBS.

## Design goals

DIBS ("_**Di**gital **B**orrowing **S**ystem_") is intended to be a basic, standalone, [controlled digital lending](https://controlleddigitallending.org) system with the following goals:

* _Simplicity_. We wanted to keep everything as simple as we could -- simple user interfaces, simple internal logic, simple installation. This supported rapid development and deployment, and going forward, it will help continued maintenance and evolution.
* _Single sign-on integration_. DIBS doesn't implement logins, and instead relies on an institutional single sign-on system to provide authentication. This simultaneously avoids having to implement user account logins and other complex, error-prone elements in DIBS itself, and makes the user experience consistent with other institutional software systems.
* _Patron privacy_. In designing DIBS, we sought to minimize the amount of patron data requested and stored, to maintain patron privacy and reduce the impact of potential data leaks. DIBS does not store any patron information when a loan is not active, and during a loan, it stores only the user's institutional SSO identity combined with the (single) barcode they have on loan during the loan period. There are no provisions in the software for retaining the user information past the loan period, or tracking identities or loan statistics based on user identities. Lastly, an anonymization process is applied when writing log files to prevent writing user's identities to the logs produced by DIBS.
* _Decoupling_. The system is deliberately not integrated tightly with an ILS.  DIBS uses an object-oriented abstraction layer to isolate ILS-specific code to a small number of lines. It currently supports FOLIO and TIND, but the abstraction layer is extensible.  The record metadata needed by DIBS is very basic and consists of just 8 fields: a barcode, a title, an author list, a year, and a few others.  There is zero dependence on data formats, too -- no XML, no MARC, nothing. This should make it possible to replace the TIND-specific code with an interface to another ILS without great difficulty.
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
| `/edit/BARCODE`        | GET  | Staff  | Show the page to add/edit an item |
| `/iiif/<args>`           | GET  | Any    | Send IIIF content to viewer |
| `/info`                  | GET  | Any    | Same as `/` |
| `/item-status/<args>`    | GET  | Any    | Get loan availability info about an item |
| `/item/BARCODE`        | GET  | Any    | Shows item information page for a given item |
| `/list`                  | GET  | Staff  | Show what's available for loans |
| `/loan`                  | POST | Any    | Handles Loan button from `/item` page |
| `/logout`                | GET  | Any    | Logs out the current SSO session |
| `/manage`                | GET  | Staff  | Show the page to manage the list of items |
| `/manifests/BARCODE`   | GET  | Any    | Sends manifest to viewer |
| `/notallowed`            | GET  | Any    | Error page for invalid requests |
| `/notallowed`            | POST | Any    | Error page for invalid rquests items |
| `/ready`                 | POST | Staff  | Handles checkbox in `list` page to make an item ready to loan |
| `/remove`                | POST | Staff  | Handles button in `list` page to remove an item |
| `/return/BARCODE`      | POST | Any    | Handles Return button from viewer page |
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

DIBS does not include a IIIF server. Instead, it can work with any compliant IIIF server that you wish to set up or already have access to.

Before choosing and setting up a IIIF server, it may be helpful to understand how DIBS will use it. The process of accessing content and serving it goes roughly like this:

1. A IIIF viewer client (such as the [Universal Viewer](http://universalviewer.io) included with DIBS) requests a [IIIF manifest file](https://iiif.io/explainers/using_iiif_resources/#iiif-manifest) from DIBS at the endpoint `/manifests/BARCODE`, where `BARCODE` is the item barcode.
2. DIBS checks if the user making the request has an active loan on `BARCODE`. If not, it responds with an error code; otherwise, DIBS performs the following steps:
    1. retrieves the manifest file from disk and reads it into memory;
    2. modifies the contents of the manifest file in memory, replacing every instance of the IIIF base URL (set in the site `settings.ini` file) with a URL that points at DIBS' address rather than the real IIIF server; and
    3. sends the adjusted manifest file contents to the client.
3. The IIIF client parses the manifest to learn the URLs for the page images.
4. The client starts fetching images at the URLs following the IIIF protocol. (Since these URLs all point to a location under `/iiif` on the DIBS server by virtue of the transformation applied in step 2b, the requests actually go to the DIBS server, not the actual IIIF server.)
5. For every URL request from the client, DIBS checks if the user has an active loan on the associated item. If the user does, then DIBS reverses the the transformation it previously applied to the URL so it can determine the real IIIF URL, fetches the image data from the IIIF server, and returns the image data to the client.  To improve performance, the DIBS server also caches images in memory, so that subsequent client requests are answered more quickly.

The most important implication of this scheme is the following: **for content that you host in your instance of DIBS, clients never contact the IIIF server directly**. Everything goes through DIBS, which acts as a conduit between the client and the IIIF server. The only exception is if your manifest file contains references to a IIIF server address for which DIBS is _not_ configured to rewrite URLs; then clients will contact that server directly.

This approach gives you the freedom to set up your IIIF server in many ways. All that DIBS needs to know is a base URL, and all that DIBS does is request pages using the IIIF protocol.  As long as DIBS can communicate with the IIIF server you use, things should work.

At Caltech, we use a copy of [serverless-iiif](https://github.com/samvera-labs/serverless-iiif) hosted on an Amazon AWS server. That server is configured to read images from an Amazon S3 bucket where we store the book content for DIBS. Clients do not know the details, however, and we could equally have used a different IIIF server hosted on our own hardware, or something else. We can also change the IIIF server setup at any time without clients needing to make any changes.
