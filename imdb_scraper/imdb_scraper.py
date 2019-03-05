# -*- coding: utf-8 -*-
import sys
import os
import requests
from lxml import html

# Dir paths
WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(WORKING_DIR, 'files')

# File paths


START_AT = 1
MAIN_URL = f'https://www.imdb.com/search/title?count=250&start={START_AT}&title_type=feature&ref_=nv_wl_img_2'
