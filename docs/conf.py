# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'DIBS'
copyright = '2021, Caltech Library'
author = 'Caltech Library'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',
    "sphinx.ext.autodoc",
    'sphinx.ext.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README.md']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_material'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_short_title = "Home"


# -- Options for the Material theme ---------------------------------------------
# C.f. https://github.com/bashtage/sphinx-material/blob/master/docs/conf.py

# Set link name generated in the top bar.
html_title = 'Caltech DIBS'

# Material theme options (see theme.conf for more information)
html_theme_options = {

    # Set the name of the project to appear in the navigation.
    'nav_title': 'Caltech DIBS',

    # Set you GA account ID to enable tracking
    'google_analytics_account': '',

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://caltechlibrary.github.io/dibs',

    # Set the colors. I found a list here:
    # https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/
    "theme_color": 'grey',
    'color_primary': 'orange',
    'color_accent': 'brown',

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/caltechlibrary/dibs/',
    'repo_name': 'Caltech DIBS',

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 3,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,

    "html_minify": False,
    "html_prettify": True,

    # "version_dropdown": True,
    # "version_json": "_static/versions.json",
    # "version_info": {
    #     "Release": "https://bashtage.github.io/sphinx-material/",
    #     "Development": "https://bashtage.github.io/sphinx-material/devel/",
    #     "Release (rel)": "/sphinx-material/",
    #     "Development (rel)": "/sphinx-material/devel/",
    # },
}


# -- Options for the MyST parser ---------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "html_image",
    "linkify",
    "smartquotes",
    "substitution"
]
