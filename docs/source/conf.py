# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FlapKine'
copyright = '2025, Kalbhavi Vadhi Raj'
author = 'Kalbhavi Vadhi Raj'
release = 'v0.1.0'

html_logo = "D:\Research\Kinematics_App\TempFlapkine\FlapKine\\app\\assets\\flapkine_icon.png"
html_favicon = "D:\Research\Kinematics_App\TempFlapkine\FlapKine\\flapkine_icon.ico"
html_static_path = ['_static']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
