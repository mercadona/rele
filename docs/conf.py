# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


sys.path.insert(0, os.path.abspath(".."))

import rele  # noqa

# -- Project information -----------------------------------------------------

project = "Relé"
copyright = "2019-2020, Mercadona S.A."
author = "Mercadona"
version = rele.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.doctest"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"
html_theme_options = {
    "font_family": "Heebo",
    "logo_name": False,
    "code_font_family": ('"SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,'
                         ' monospace'),
    "code_font_size": "0.8em",
    "show_related": False,
    "fixed_sidebar": False,
    "github_banner": False,
    "github_button": True,
    "github_type": "star",
    "github_user": "Mercadona",
    "github_repo": "rele",
}
master_doc = "index"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_sidebars = {"**": ["sidebar.html", "navigation.html", "searchbox.html"]}


# Setup function
def setup(app):
    app.add_stylesheet("style.css")


# -- Extension configuration -------------------------------------------------
