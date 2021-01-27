Caltech Library Digital Borrowing System<img width="50em" align="right" style="display: block; margin: auto auto 2em 2em"  src="_static/media/dibs-icon.svg">
========================================

Caltech DIBS ("<span style="font-weight: bold; margin-right: -0.2778em">Di</span>gital <span style="font-weight: bold; margin-right: -0.2778em">B</span>orrowing <span style="font-weight: bold; margin-right: -0.2778em">S</span>ystem") is the [Caltech Library](https://www.library.caltech.edu)'s basic implementation of a [controlled digital lending](https://en.wikipedia.org/wiki/Controlled_digital_lending) system.  It enables members of Caltech to borrow materials (e.g., older books) that are not otherwise available in e-book or other electronic formats.  The system was implemented in the year 2021 to help Caltech students and faculty continue their studies and work during the global [COVID-19 pandemic](https://www.who.int/emergencies/diseases/novel-coronavirus-2019).

The concept of [controlled digital lending](https://en.wikipedia.org/wiki/Controlled_digital_lending) (CDL) is to allow libraries to loan items to digital patrons in a "lend like print" fashion.  The number of digital copies of an item allowed to be loaned at any given time is strictly controlled to match the number of physical print copies taken off the shelves, to ensure an exact "owned-to-loaned" ratio.  DIBS implements two main components of a CDL system: a patron loan tracking system, and an integrated digital content viewing interface.  DIBS makes use of the [Universal Viewer](http://universalviewer.io) to implement the viewer.

Access to materials in Caltech DIBS is limited to current Caltech faculty, students and staff, but the software for DIBS itself is open-sourced under a BSD type license and [available on GitHub](https://github.com/caltechlibrary/dibs).


## Sections

```{toctree}
---
maxdepth: 2
---
usage.md
architecture.md
```
