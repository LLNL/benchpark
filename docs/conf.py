# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Benchpark"
copyright = "2023, LLNS LLC"
author = "Olga Pearce, Alec Scott, Peter Scheibel, Greg Becker, Riyaz Haque, and Nathan Hanford"

import os
import sys

from sphinx.ext.apidoc import main as sphinx_apidoc

# -- Benchpark customizations ------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.append(os.path.abspath("../lib/benchpark/benchpark"))
print(sys.path)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autodoc",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".spack-env"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Run sphinx-apidoc -------------------------------------------------
# Remove any previous API docs
# ReadtheDocs doesn't clean up after previous builds
# Without this, the API Docs will never actually update
apidoc_args = [
    "--force",  # Overwrite existing files
    "--no-toc",  # Don't create a table of contents file
    "--output-dir=.",  # Directory to place all output
    "--module-first",  # emit module docs before submodule docs
]
sphinx_apidoc(
    apidoc_args
    + [
        "../lib/benchpark/benchpark",
    ]
)
