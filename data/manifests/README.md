Demo of using IIIF manifests
============================

In its current implementation, the DIBS server responds to the endpoint at `/manifests/NNNNNN` and returns a manifest for an item based on the barcode `NNNNNN`. The manifest is found by looking for a file with a name having the pattern `NNNNNN-manifest.json` in this directory.

The demo manifest file found here, `350470000363458-manifest.json`, is a copy of the IIIF manifest provided by Wellcome Library for [its copy of The biocrats](https://wellcomelibrary.org/item/b18035978#?c=0&m=0&s=0&cv=0&z=-1.099%2C-0.0809%2C3.1979%2C1.6181).  The metadata for this demo manifest is loaded into the demo DIBS database by the script [`../load-mock-data.py`](../load-mock-data.py).

