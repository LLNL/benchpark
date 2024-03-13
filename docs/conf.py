# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import subprocess

subprocess.call(
    [
        "make",
        "systemconfigs",
    ]
)

subprocess.call(
    [
        "make",
        "tags",
    ]
)

project = "Benchpark"
copyright = "2023, LLNS LLC"
author = "Olga Pearce, Alec Scott, Peter Scheibel, Greg Becker, Riyaz Haque, and Nathan Hanford"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
    "sphinxcontrib.programoutput",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".spack-env"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
