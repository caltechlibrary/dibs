# DIBS history

_"If you have an apple and I have an apple and we exchange these apples then you and I will still each have one apple. But if you have an idea and I have an idea and we exchange these ideas, then each of us will have two ideas."_ &mdash; [Charles F. Brennan](https://quoteinvestigator.com/2011/12/13/swap-ideas/).


## Origin story

[Controlled digital lending](https://en.wikipedia.org/wiki/Controlled_digital_lending) (CDL) is an approach for making print books available to digital patrons in a "lend like print" fashion. Although the concept of CDL predates the start of the [COVID-19 pandemic](https://www.who.int/emergencies/diseases/novel-coronavirus-2019) in 2020, the need for educational institutions to support remote access to their collections during 2020–2021 resulted in renewed interest in CDL systems. Like many institutions, the [Caltech Library sought to satisfy requests for electronic access](https://www.library.caltech.edu/DIBS-overview) from quarantined course instructors and patrons in late 2020, but we found no suitable off-the-shelf system that could provide access to digitized publications in a manner that mimics the loaning of legally-purchased materials.  We implemented [DIBS](https://github.com/caltechlibrary/dibs) ("_**Di**gital **B**orrowing **S**ystem_") in response.

The DIBS software system is the work of <a href="https://github.com/mhucka">Michael Hucka</a>, <a href="https://github.com/rsdoiel">Robert Doiel</a>, <a href="https://github.com/t4k">Tommy Keswick</a> and <a href="https://github.com/nosivads">Stephen Davison</a> from the Caltech Library's <a href="https://www.library.caltech.edu/staff?&field_directory_department%5B0%5D=754">Digital Library Development team</a>. The software is written primarily in Python and uses the JavaScript-based <a href="http://universalviewer.io">Universal Viewer</a> for displaying scanned books and other items that comply with the [International Image Interoperability Framework](https://iiif.io) (IIIF).  The icons used on DIBS pages are from <a href="https://fontawesome.com">Font Awesome</a>, with additional special icons created by <a href="https://thenounproject.com/roywj/">Royyan Wijaya</a>, <a href="https://thenounproject.com/thezyna/">Scott Desmond</a> and <a href="https://thenounproject.com/slidegenius">SlideGenius</a> for the <a href="https://thenounproject.com">Noun Project</a>. A photo of books in Caltech's Sherman Fairchild Library is included by permission of the author, Rebecca Minarez, and distributed under a [CC BY-NC-SA 4.0](http://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1) license.

DIBS is <a href="https://en.wikipedia.org/wiki/Open-source_software">open-source software</a>. The source code is freely available <a href="https://github.com/caltechlibrary/dibs">from GitHub</a> under the terms of a <a href="https://github.com/caltechlibrary/dibs/blob/main/LICENSE">BSD 3-clause license</a>.


## Version history

The following subsections summarize the major released versions of DIBS.

### Version 0.5.0 (October 1, 2021)

[Release 0.5.0](https://github.com/caltechlibrary/dibs/releases/tag/v0.5.0) brings significant new features and some backwards-incompatible changes. The new features include **support for FOLIO** as an alternative to TIND.io; support for triggering IIIF conversion workflows after adding a new item to DIBS; the ability to download the item database and history as CSV files; the ability to replace book cover thumbnail images with your own preferred images; and the ability to show a site banner for announcements. The breaking changes include changes to the database object models, changes to the format of the settings file, and some changes to the HTML page templates. Finally, this release fixes a number of bugs and adds some other enhancements.


### Version 0.4.0 (May 28, 2021)

[Release 0.4.0](https://github.com/caltechlibrary/dibs/releases/tag/v0.4.0) adds an interface to the `/list` page for starting an external workflow for scan/image conversion. More documentation is needed on this facility, but the basic idea is to write a file to a designation location that will then trigger some external action. In addition, the new release anonymizes user identities in log messages printed when verbose mode is turned on; this uses the Python module [Trinomial](https://github.com/caltechlibrary/trinomial) to replace user email addresses with a pseudorandom hex string. Finally, this release addresses some additional issues, removes some small bugs, and refactors some code to simplify internal logic.


### Version 0.3.0 (April 30, 2021)

[Release 0.3.0](https://github.com/caltechlibrary/dibs/releases/tag/v0.3.0) of DIBS polishes the user interface, uses the latest official release of the Universal Viewer (version 3.1.1), and fixes some user interface glitches. DIBS has been running at Caltech for a month; with this release, we believe the software to be stable enough for others to try to use it. (However, there remain hard-coded references to Caltech in the HTML files and these would need to be edited manually to modify the system for use in other institutions.)


### Version 0.2.0 (April 13, 2021)

[Release 0.2.0](https://github.com/caltechlibrary/dibs/releases/tag/v0.2.0) enhanced a number of pages, added functionality to the `/stats` page, fixed internal issues, and generally improved DIBS overall.


### Version 0.1.0 (March 29, 2021)

[Release 0.1.0](https://github.com/caltechlibrary/dibs/releases/tag/v0.1.0) corresponds to the version that has been made live to the Caltech community on 2021-03-29. It features the use of Shibboleth for authentication, the removal of the use of sessions, the addition of a `/stats` page, plus numerous other changes large and small.
