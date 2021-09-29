Caltech Library Digital Borrowing System<img width="50em" align="right" style="display: block; margin: auto auto 2em 2em"  src="_static/media/dibs-icon.svg">
========================================

Caltech DIBS ("_**Di**gital **B**orrowing **S**ystem_") is the [Caltech Library](https://www.library.caltech.edu)'s basic implementation of a web-based [controlled digital lending](https://en.wikipedia.org/wiki/Controlled_digital_lending) system.  The system was developed in the year 2021 to [help Caltech students and faculty continue their studies and work](https://www.library.caltech.edu/DIBS-overview) during the global [COVID-19 pandemic](https://www.who.int/emergencies/diseases/novel-coronavirus-2019).

The concept of [controlled digital lending](https://controlleddigitallending.org) (CDL) is to allow libraries to loan items to digital patrons in a "lend like print" fashion.  It is the digital equivalent of traditional library lending. Libraries digitize a physical item from their collection, then lend out a secured digital version to one user at a time while the original, printed copy is simultaneously marked as unavailable. The number of digital copies of an item allowed to be loaned at any given time is strictly controlled to match the number of physical print copies taken off the shelves, to ensure an exact "owned-to-loaned" ratio.

DIBS provides three main components of a CDL system: a loan tracking system, an integrated digital content viewing interface, and a basic administrative interface.  DIBS embeds the [Universal Viewer](http://universalviewer.io) to display materials that comply with the [International Image Interoperability Framework](https://iiif.io) (IIIF). DIBS also includes a basic mechanism for triggering external workflows that convert scans into IIIF format, and a software interface layer allowing DIBS to fetch book metadata automatically from (currently) [FOLIO](https://www.folio.org) or [TIND](https://tind.io).

## Sections

```{toctree}
---
maxdepth: 2
---
usage.md
architecture.md
installation.md
history.md
references.md
colophon.md
```
