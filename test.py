# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import json

import os

with open('data/connections.json') as connectionFp:
    connectionDicList = json.load(connectionFp)
