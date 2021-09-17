# Thumbnails directory example

DIBS displays cover image thumbnails on item pages. The present directory is the default location for the thumbnail images. The location of this directory is set by the variable `THUMBNAILS_DIR` in the [`settings.ini`](../settings.ini-example) file; you can use a different directory by changing the value of the variable. The DIBS LSP layer attempts to obtain cover images automatically for each new item added to DIBS, and will store the images in this directory. You can also deliberately put images here manually to override what DIBS uses.

DIBS assumes that thumbnail images are in [JPEG](https://en.wikipedia.org/wiki/JPEG) format and only recognizes files named according to the pattern `N.jpg`, where `N` is the barcode used to identify the item. (The barcode is typically a long integer.) Note that the file name _must_ end in `.jpg` and _not_ `.jpeg`.
