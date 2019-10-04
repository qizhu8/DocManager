# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import bibtexparser

""" some test bib """
paper1 = """@article{bar2011index,
  title={Index coding with side information},
  author={Bar-Yossef, Ziv and Birk, Yitzhak and Jayram, TS and Kol, Tomer},
  journal={IEEE Transactions on Information Theory},
  volume={57},
  number={3},
  pages={1479--1494},
  year={2011},
  publisher={IEEE}
}"""

paper2 = """@inproceedings{birk1998informed,
  title={Informed-source coding-on-demand (ISCOD) over broadcast channels},
  author={Birk, Yitzhak and Kol, Tomer},
  booktitle={Proceedings. IEEE INFOCOM'98, the Conference on Computer Communications. Seventeenth Annual Joint Conference of the IEEE Computer and Communications Societies. Gateway to the 21st Century (Cat. No. 98},
  volume={3},
  pages={1257--1264},
  year={1998},
  organization={IEEE}
}"""

bibDicList = bibtexparser.loads(paper2).entries
print(bibtexparser.loads(paper2).strings)

for bibDic in bibDicList:
    for key in bibDic:
        print("{key}: {val}".format(key=key, val=bibDic[key]))

    id = bibDic['ID']
    year = bibDic['year']
    source = bibDic['journal']
    author = bibDic['author'].split('and')

    print("="*20)
    print(id)
    print(year)
    print(source)
    print(author)
