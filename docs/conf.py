import sys
import os

sys.path.append(os.path.abspath(".."))
project = "REST API contacts"
copyright = "2024, Paweł Szumański"
author = "Paweł Szumański"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.viewcode"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pyramid"
html_theme_options = {"sidebarwidth": 320}
html_static_path = ["_static"]
