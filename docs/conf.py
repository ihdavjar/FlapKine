# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from src.version import __version__

project = 'FlapKine'
copyright = '2025, Kalbhavi Vadhi Raj'
author = 'Kalbhavi Vadhi Raj'
release = f'v{__version__}'

# -- Path setup --------------------------------------------------------
import os, sys
sys.path.insert(0, os.path.abspath('..'))  # so it can find app and src at root level
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("../app"))

# -- Extensions --------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]
autosummary_generate = True

# Add custom CSS

html_static_path = ['_static']
html_css_files = ['custom.css']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "pydata_sphinx_theme"
html_logo = "assets/icons/flapkine_icon.ico"  # logo in the top left corner
html_favicon = "assets/icons/flapkine_icon.ico"  # browser tab icon

html_show_sourcelink = False