# Caltech DIBS<img width="70em" align="right" src="https://github.com/caltechlibrary/dibs/raw/main/docs/_static/media/dibs-icon.png">

Caltech DIBS ("_**Di**gital **B**orrowing **S**ystem_") is the Caltech Library's implementation of a basic, standalone, [controlled digital lending](https://archive.org/details/controlled-digital-lending-explained) system.

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=flat-square)](https://choosealicense.com/licenses/bsd-3-clause)
[![Python](https://img.shields.io/badge/Python-3.8+-brightgreen.svg?style=flat-square)](https://www.python.org/downloads/release/python-380/)
[![Latest release](https://img.shields.io/github/v/release/caltechlibrary/dibs.svg?style=flat-square&color=b44e88&label=Latest%20release)](https://github.com/caltechlibrary/dibs/releases)
[![DOI](https://img.shields.io/badge/dynamic/json.svg?label=DOI&style=flat-square&color=lightgray&query=$.metadata.doi&uri=https://data.caltech.edu/api/record/2192)](https://data.caltech.edu/records/2192)

## Table of contents

* [Introduction](#introduction)
* [Requirements](#requirements)
* [Installation and operation](#installation-and-operation)
* [General information](#general-information)
* [Known issues and limitations](#known-issues-and-limitations)
* [Getting help](#getting-help-and-support)
* [Contributing](#contributing)
* [License](#license)
* [Authors and history](#authors-and-history)
* [Acknowledgments](#authors-and-acknowledgments)


## Introduction

DIBS ("_**Di**gital **B**orrowing **S**ystem_") is a web-based system that enables users to borrow, in a time-limited fashion, scanned materials that are not otherwise available in electronic format. The concept of [controlled digital lending](https://controlleddigitallending.org/faq) (CDL) is to provide the digital equivalent of traditional library lending. Libraries digitize a physical item from their collection, then lend out a secured digital version to one user at a time while the original, printed copy is simultaneously marked as unavailable. The number of digital copies of an item allowed to be loaned at any given time is strictly controlled to match the number of physical print copies taken off the shelves, to ensure an exact "owned-to-loaned" ratio.

DIBS was developed in the year 2021 to help Caltech students and faculty continue their studies and work during the global [COVID-19 pandemic](https://www.who.int/emergencies/diseases/novel-coronavirus-2019). The open-source system provides three main components for CDL: a loan tracking system, an integrated digital content viewing interface, and basic administrative interface.  DIBS embeds the [Universal Viewer](http://universalviewer.io) to display materials that comply with the [International Image Interoperability Framework](https://iiif.io) (IIIF). To help library staff convert scans of materials into IIIF format, DIBS also provides a way to connect to an external workflow, and Caltech's workflow automation for this purpose is available as an example in a [separate repository](https://github.com/caltechlibrary/dibsiiif).

DIBS can currently interface to either [FOLIO](https://www.folio.org) or [TIND](https://tind.io) to get metadata about books, but its interface layer should be straightforward to extend for other [LSP](https://journals.ala.org/index.php/ltr/article/view/5686/7063) (library services platform) implementations.

<p align="center">
<img width="650rem" align="center" src="https://github.com/caltechlibrary/dibs/raw/main/docs/_static/media/item-page.png">
<br>
<img width="650rem" align="center" src="https://github.com/caltechlibrary/dibs/raw/main/docs/_static/media/loan-in-viewer-thumbnails.png">
</p>


## Requirements

The core DIBS server is written in [Python 3](https://www.python.org) and makes use of some additional Python software libraries that are installed automatically during the [installation step](#installation) steps.

### _Requirements to run a demo_

Although DIBS relies on the existence of a IIIF image server (and content to serve), for initial exploration and demonstration purposes, you don't need to set up a IIIF server; you can reference content located in any of a number of publicly-accessible IIIF servers around the world, and DIBS includes a sample [IIIF manifest](https://iiif.io/explainers/using_iiif_resources/#iiif-manifest) to illustrate that.  You shouldn't need anything else to run the DIBS demo on your local computer.


### _Requirements to use DIBS for real use at another institution_

In order to run a multiuser DIBS server at another institution, certain additional things are needed. 

1. A **IIIF server**. At Caltech, we use a [serverless component](https://github.com/nulib/serverless-iiif) running on an Amazon cloud instance, but [many other IIIF server options exist](https://github.com/IIIF/awesome-iiif#image-servers). If you're looking at DIBS, presumably it means you want to serve content that is not freely available in a public IIIF server, which means you will need to set up a server of your own.
2. A **web server** to host DIBS.  The current version of DIBS has only been tested with Apache2 on Linux (specifically, Ubuntu 20) and macOS (specifically 10.14, Mojave). DIBS comes with a [WSGI adapter file](https://github.com/caltechlibrary/dibs/blob/main/adapter.wsgi) and [sample config file for Apache](https://github.com/caltechlibrary/dibs/blob/main/dibs.conf-example), but it should be possible to run DIBS in other WSGI-compliant servers.
3. An **authentication layer**. DIBS assumes that the web server takes care of user authentication in such a way that DIBS is behind the authentication layer and all users who can reach DIBS pages are allowed to view content. DIBS itself only implements checks to distinguish between regular users versus staff who are allowed to access restricted pages. For the authentication layer, at Caltech we use the [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) single sign-on system, but it is possible to use other schemes, including [Apache Basic Authentication](https://httpd.apache.org/docs/2.4/howto/auth.html). The installation and configuration of a single sign-on system depends on the specifics of a given institution, and are not described here.
4. The use of [FOLIO](https://www.folio.org) LSP or [TIND](https://tind.io) ILS for retrieving metadata based on barcodes or unique identifiers, _or_  a willingness to extend the existing metadata retrieval layer in DIBS.  The interface for adding items to DIBS requires looking up metadata based on an item's barcode, and lacking a universal scheme to do that, we had to write our own interface layer. The use of another LSP will require extending this interface layer. (Thankfully, the [code is short](https://github.com/caltechlibrary/dibs/blob/main/dibs/lsp.py) and the amount of metadata required is small.)
5. Modification to the HTML templates to change the branding. The template files in [`dibs/templates`](https://github.com/caltechlibrary/dibs/blob/main/dibs/templates) are specific to Caltech, and will need to be edited to suit another installation. (We are open to making the branding customization easier and would welcome a [pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) for suitable changes!)


## Installation and operation

Please refer to the [detailed installation instructions in the DIBS manual](https://caltechlibrary.github.io/dibs/installation.html).

**Backwards compatibility warning**: If you previously used a DIBS version before version 0.5, you will not be able to run 0.5 without migrating the database and doing other work.  Some migration help can be found in the [DIBS wiki on GitHub](https://github.com/caltechlibrary/dibs/wiki).  The version 0.5 release brings significant changes and new features, but it is also not fully backward compatible with previous versions. We apologize for breaking backward compatibility; we lack the resources to do it differently or create a proper migration engine.


## General information

Documentation for DIBS is available online at [https://caltechlibrary.github.io/dibs/](https://caltechlibrary.github.io/dibs/).


## Known issues and limitations

DIBS is in active development.  The current version was produced rapidly, and has a limited scope and streamlined design.  We continue to improve DIBS in various ways.

It is worth mentioning that DIBS does not (currently) implement a queue or wait list for loan requests.  This is a conscious design decision.  Queuing systems tend to lead to complexity quickly, and we want to delay implementing a queue until it becomes clear that it's really essential.  (After all, in a physical library, there are no queues for borrowing books: you go to see if it's available, and if it's not, you can't borrow it.)  Perhaps we can implement interfaces and behaviors in DIBS that avoid the need for a queue at all!

The DIBS server acts as an intermediary between the IIIF server and patrons viewing content in IIIF viewers &ndash; all content goes through DIBS. This is how DIBS can implement loan policies and secure content management: it's a choke point. However, it means the DIBS server is a potential performance bottleneck. At our institution, we have not found the speed impact to be objectionable for CDL in an academic setting, even using single server hardware. But other sites may have different experiences. If you experience performance issues, first try to increase the number of parallel threads that your Apache server will use for DIBS, and also increase `IIIF_CACHE_SIZE` in [`settings.ini`](https://github.com/caltechlibrary/dibs/blob/main/settings.ini-example). If that is not enough, let the developers know, and we can start thinking about architectural changes.


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

The [vector artwork](https://thenounproject.com/term/book-waiting/1531542/) of a book with a clock on it, used as the icon for this project, was created by [Royyan Wijaya](https://thenounproject.com/roywj/) from the Noun Project.  It is licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license.  DIBS also uses other icons created by [Scott Desmond](https://thenounproject.com/thezyna) and [SlideGenius](https://thenounproject.com/slidegenius).

We gratefully acknowledge bug reports and fixes submitted by the following users, who helped improve DIBS:

<table>
<tr>
<td><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;</td>

<td align="center"><a href="https://github.com/stanonik"><img src="https://avatars.githubusercontent.com/stanonik" title="stanonik" width="50" height="50"><br>@stanonik</a></td>
<td align="center"><a href="https://github.com/phette23"><img src="https://avatars.githubusercontent.com/phette23" title="phette23" width="50" height="50"><br>@phette23</a></td>

<td><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
        <span>&nbsp;&nbsp;</td>
</tr>
</table>

DIBS makes use of numerous open-source packages, without which it would have been effectively impossible to develop DIBS with the resources we had.  We want to acknowledge this debt.  In alphabetical order, the packages are:

* [Arrow](https://pypi.org/project/arrow/) &ndash; a library for creating & manipulating dates
* [Bootstrap](https://getbootstrap.com) &ndash; CSS framework for developing responsive websites
* [Bootstrap Table](https://bootstrap-table.com) &ndash; extended table framework for Bootstrap
* [Boltons](https://github.com/mahmoud/boltons/) &ndash; package of miscellaneous Python utilities
* [Bottle](https://bottlepy.org) &ndash; a lightweight WSGI micro web framework for Python
* [Bottle-fdsend](https://pypi.org/project/bottle-fdsend/) &ndash; Bottle plugin to enable sending content from in-memory files
* [Clipboard.js](https://clipboardjs.com) &ndash; JavaScript library for copying text to the clipboard
* [Coif](https://github.com/caltechlibrary/coif) &ndash; a Python package for finding book cover images
* [CommonPy](https://github.com/caltechlibrary/commonpy) &ndash; a collection of commonly-useful Python functions
* [expiringdict](https://pypi.org/project/expiringdict/) &ndash; an ordered dictionary class with auto-expiring values
* [Font Awesome](https://fontawesome.com) &ndash; scalable vector icons for web design
* [humanize](https://github.com/jmoiron/humanize) &ndash; make numbers more easily readable by humans
* [ipdb](https://github.com/gotcha/ipdb) &ndash; the IPython debugger
* [jQuery](https://jquery.com) &ndash; JavaScript library of common functions
* [LRU Dict](https://github.com/amitdev/lru-dict) &ndash; an implementation of Least Recently Used caching
* [mod_wsgi](http://www.modwsgi.org) &ndash; an Apache module for hosting Python WSGI web applications
* [Peewee](http://docs.peewee-orm.com/en/latest/) &ndash; a simple ORM for Python
* [Pillow](https://github.com/python-pillow/Pillow) &ndash; a fork of the Python Imaging Library
* [Plac](https://github.com/ialbert/plac) &ndash; a command line argument parser
* [Pokapi](https://github.com/caltechlibrary/pokapi) &ndash; a simple Python OKAPI interface
* [Popper.js](https://popper.js.org) &ndash; web page tooltip engine
* [Python Decouple](https://github.com/henriquebastos/python-decouple/) &ndash; a high-level configuration file interface
* [Rich](https://rich.readthedocs.io/en/latest/) &ndash; library for writing styled text to the terminal
* [Sidetrack](https://github.com/caltechlibrary/sidetrack) &ndash; simple debug logging/tracing package
* [str2bool](https://github.com/symonsoft/str2bool) &ndash; convert a string to a Boolean value
* [Trinomial](https://github.com/caltechlibrary/trinomial) &ndash; a simple name anonymization package
* [Topi](https://github.com/caltechlibrary/topi) &ndash; a simple package for getting data from a TIND.io ILS instance
* [Universal Viewer](https://github.com/UniversalViewer/universalviewer) &ndash; a browser-based viewer for content in [IIIF](https://iiif.io) format
* [Yurl](https://github.com/homm/yurl/) &ndash; URL manipulation library
* [Werkzeug](https://werkzeug.palletsprojects.com/en/2.0.x/) &ndash; WSGI application library

<div align="center">
  <br>
  <a href="https://www.caltech.edu">
    <img width="100" height="100" src="https://raw.githubusercontent.com/caltechlibrary/dibs/main/.graphics/caltech-round.png">
  </a>
</div>
