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
html_theme = "groundwork"
html_logo = "assets/icons/flapkine_icon.ico"  # logo in the top left corner
html_favicon = "assets/icons/flapkine_icon.ico"  # browser tab icon

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Enable the dark theme feature
html_theme_options = {
    'dark_css_variables': {
        'body-background': '#2e2e2e',  # Dark background color
        'text-color': '#e0e0e0',        # Light text color
        'link-color': '#5390d9',        # Link color (adjust as needed)
        'visited-link-color': '#d5859d', # Visited link color
    },
    'light_css_variables': {
        'body-background': '#ffffff',  # Light background color
        'text-color': '#000000',       # Text color for light theme
        'link-color': '#2c7be5',       # Link color
        'visited-link-color': '#6c4b9f', # Visited link color
    },
}


html_theme_options = {
    'navigation_depth': 4,  # Adjust navigation depth if needed
    'dark_css_variables': {
        'body-background': '#2e2e2e',
        'text-color': '#e0e0e0',
        'link-color': '#5390d9',
    },
    'light_css_variables': {
        'body-background': '#ffffff',
        'text-color': '#000000',
        'link-color': '#2c7be5',
    },
}

