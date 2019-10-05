# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
from class.DocManager import DocManager


dbInitFile = os.join('class', 'createTbls.sql')

docManager = DocManager()
docManager.initConn()
