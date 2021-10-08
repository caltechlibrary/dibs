# FAQs about DIBS

Here are answers to some common questions about DIBS.

## What ILS or LSP systems does DIBS support?

As of version 0.5, the DIBS software architecture features an abstraction layer for interfacing to LSP/ILS systems. Out of the box, it includes two concrete interfaces, for [FOLIO](https://www.folio.org) and [TIND](https://tind.io). The use of one or the other is selectable in the DIBS site settings file.

DIBS only needs to retrieve about 8 metadata fields for an item in a catalog system. These are fields such as a barcode, a title, author, year &ndash; that sort of thing.  Given the abstraction layer, and the scheme for configuring LSP parameters using the site settings file, the developers of DIBS believe it would not require significant effort to add interfaces to other LSPs. We would welcome code contributions from other institutions to enhance DIBS in this way.


## Are documents in DIBS stored as PDFs?

No. The IIIF format is image-based, and document pages are stored in a pyramidal image scheme in which each document page is represented by multiple fragments at different resolutions. The scheme minimizes the data sent to a user's browser while still enabling the ability to zoom in and out (similar to how you can zoom in and out in Google Maps).


## Is OCR applied to document pages? Can it be?

In principle, one could apply optical character recognition (OCR) to document pages and make the text available _somehow_. We (the Caltech developers of DIBS) did not pursue this, in part because we feared it would put DIBS on shakier legal grounds than the strict CDL approach we followed. Instead, we focused on producing a library book-lending experience in electronic form.


## Is the viewer compatible with screen readers?

The [Universal Viewer](http://universalviewer.io) used in DIBS for presenting documents is (to our knowledge) unfortunately not compatible with screen readers at this time. We are not aware of any IIIF viewers that are compatible. The IIIF community has made some efforts in this direction but there does not seem to be a solution at this time.


## Can patrons schedule loans?

There is currently no scheduling system in DIBS. Users need to visit the information page for a given book when they are interested in borrowing it.


## Do items have waiting lists associated with them?

There is currently no queuing or wait list system in DIBS. It is a first-come, first-served system.


## Isn't the lack of a queuing system in DIBS a problem?

At the Caltech Library, our policy has been that if a book is in particularly high demand, we purchase more copies and then make more copies available in DIBS. We have not yet had to do this, nor have we encountered pressure situations on any given book.

That said, we do realize that not all institutions may have the resources to take this approach; moreover, perhaps this approach works at Caltech because Caltech is particularly small and we don't have enough students to cause problems. 

Finally, while we don't have the resources to implement a queuing system at this time, we would welcome outside code contributions to implement such a feature in DIBS.


## How does DIBS prevent users from saving copies of the materials?

DIBS uses multiple techniques to prevent users from saving the books they borrow through the system:

* Each book is stored on the IIIF server as thousands of images, not as single PDFs files.

* The IIIF format is structured in such a way that individual pages are not stored as complete page images, but rather as multiple fragments of each page. The data received by the user's browser consists of (many) fragments for any given page. Clever users may think of opening a browser's web developer interface and inspecting the image content, but they will not find complete pages stored anywhere.

* Downloading is disabled in the Universal Viewer (the system used for rendering documents in user's web browsers). There is no "download" button, and UV does not provide a way to "open the image" of a document page that users see in their browsers.

* The DIBS server acts as a traffic cop between the IIIF server and the user. All URLs to document images retrieved by the viewer go through the DIBS server, and the server checks a user's loan status for every image retrieval. If the user's loan period has ended (or they have not borrowed the requested item), the server refuses all network requests for image retrievals. Users can save the URLs to loaned books, but those URLs are useless outside of the limited periods of time when the user has an active loan in progress.

* Caltech has an [Honor Code](https://deans.caltech.edu/HonorCode), a code of ethics that guides the entire campus of students, staff, and faculty. At Caltech, we point out to users that attempting to circumvent the intellectual property protections built into DIBS is a violation of trust and therefore the honor code. Honor code violations are punishable.

These measures represent a best-faith effort in DIBS to prevent copyright violations through DIBS itself. Ultimately, though, there is only so much we can do. DIBS cannot prevent users from (say) taking photos of screen images using their cell phones, just as physical libraries cannot prevent users from taking photos of physical books. Not even Amazon can prevent users of Kindle from doing the same &ndash; and if an entity with the resources of Amazon cannot prevent all methods of saving content, then we certainly cannot.


## Does DIBS use IIIF authentication?

IIIF has an authentication protocol. We did not investigate its use in DIBS because the approach used to implement timed loans ended up encompassing all network communications and thereby obviated the need for separate authentication at the IIIF level. Not using the IIIF authentication component also has the benefit of simplifying what DIBS needs from IIIF, which in turn simplifies IIIF server configuration and management.
