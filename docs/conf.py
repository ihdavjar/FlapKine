# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FlapKine'
copyright = '2025, Kalbhavi Vadhi Raj'
author = 'Kalbhavi Vadhi Raj'
release = 'v0.1.1'

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


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "furo"
html_favicon = "assets/icons/flapkine_icon.ico"  # browser tab icon

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Furo theme options
html_theme_options = {
    "navigation_with_keys": True,   # arrow-key nav
    "light_logo": "flapkine_icon.png",
    "dark_logo": "flapkine_icon.png",
    # control sidebar depth, collapse:
    "sidebar_hide_name": False,
    "sidebar_hideable": True,
    "sidebar_collapse": True,

    # control navigation bar depth:
    "navigation_depth": 2,
    "navigation_collapse": True,

    # Change the sidebar width:
    "sidebar_width": "300px",
}
