# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import json

import os

inputString="""@article{sun2017capacity,
  title={The capacity of robust private information retrieval with colluding databases},
  author={Sun, Hua and Jafar, Syed Ali},
  journal={IEEE Transactions on Information Theory},
  volume={64},
  number={4},
  pages={2361--2370},
  year={2017},
  publisher={IEEE}
}"""

obj = bibtexparser.loads(inputString).entries

print(obj)
