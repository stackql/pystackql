extensions = ['myst_parser', 'sphinx.ext.autodoc']

source_suffix = ['.rst', '.md']

master_doc = 'index'
project = u'pystackql'

import os
import sys
sys.path.insert(0, os.path.abspath('../pystackql'))