# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

import os

sample_bib_file = os.path.join('data', 'mybib.bib')
with open(sample_bib_file) as bibfile:
    bibDicList = bibtexparser.load(bibfile).entries

# loads() is for string, load() is for file
print(bibDicList)

# instance for writing...
db = BibDatabase()
writer = BibTexWriter()
writer.indent = ' '*4     # indent entries with 4 spaces instead of one
writer.comma_first = True  # place the comma at the beginning of the line

for bibDic in bibDicList:
    for key in bibDic:
        print("{key}: {val}".format(key=key, val=bibDic[key]))

    type = bibDic['ENTRYTYPE']
    id = bibDic['ID']
    year = bibDic['year']
    title = bibDic['title']
    # source = bibDic['journal']
    author = bibDic['author'].split('and')

    print("="*20)
    print(type)
    print(id)
    print(title)
    print(year)
    # print(source)
    print(author)
    db.entries = [bibDic]
    print(writer.write(db))
