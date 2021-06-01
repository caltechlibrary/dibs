# Copy of Universal Viewer version 3.1.1

This is a copy of the [Universal Viewer](http://universalviewer.io) version 3.1.1 distribution produced using the source code from the [GitHub repository](https://github.com/UniversalViewer/universalviewer/releases/tag/v3.1.1) as it existed on 2021-04-27.  The specific contents of this directory were produced using the following steps:

1. Install `npm` (we used version 7; installation instructions depend on your operating system)
2. `npm install -g grunt-cli`
3. Download the UV [source code ZIP archive](https://github.com/UniversalViewer/universalviewer/archive/refs/tags/v3.1.1.zip) to a local directory (call it `uv`)
4. `cd uv`
5. `unzip v3.1.1.zip`
6. `cd universalviewer-3.1.1`
7. `npm install grunt@1.0.3 --save-dev`
8. `grunt build --dist`

The outcome of this process will be a subdirectory named `dist`, and `dist` will contain the files that you see here before you (minus the `uv.zip` file that is also put in the `dist` directory by the build process, and which we removed because it simply contains all the same files and thus is redundant).

The Universal Viewer is released under the MIT license.
