# About this directory

`htdocs` is used to redirect the browser to the subfolder containing the DIBS application in Apache, so that Shibboleth can protect the application. For example, in Caltech's case, it redirects https://ourserver.caltech.edu to https://ourserver.caltech.edu/dibs, where Shib works to protect the dibs app.
