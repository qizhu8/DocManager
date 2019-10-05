# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from src.DocManager import DocManager
import os

username = "root"
password = "admin"

dbName = "papers"
sqlDelTblsFilePath = "src/dropTables.sql"
sqlInitFilePath = "src/createTbls.sql"
bibfile = "data/mybib.bib"
connfile = "data/connections.json"
topicfile = "data/topics.json"


docManager = DocManager()
docManager.initConn(username, password, dbName)
# docManager.executeScriptsFromFile(sqlDelTblsFilePath) # drop tables. DEBUG only
# docManager.executeScriptsFromFile(sqlInitFilePath)

"""insert document test"""
docManager.insertDocFromBibFile(bibfile, deleteAfterInsert=True)
print("="*20)
docManager.insertTopicFromFile(topicfile, deleteAfterInsert=True)
"""conenct document test"""
print("="*20)
docManager.addConnectionFromFile(connfile, deleteAfterInsert=True)

docManager.closeConn()
