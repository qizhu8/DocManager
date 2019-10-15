# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from src.DocManager import DocManager
import os

username = "root"
password = "admin"

dbName = "papers"
sqlDelTblsFilePath = "src/dropTables.sql"
sqlInitFilePath = "src/createTbls.sql"
bibfile = "mybib.bib.bk"
connfile = "connections.json.bk"
topicfile = "topics.json.bk"


docManager = DocManager()
docManager.initConn(username, password, dbName)
docManager.executeScriptsFromFile(sqlDelTblsFilePath) # drop tables. DEBUG only
docManager.executeScriptsFromFile(sqlInitFilePath)

"""insert document test"""
docManager.insertDocFromBibFile(bibfile, deleteAfterInsert=False)
print("="*20)
docManager.insertTopicFromFile(topicfile, deleteAfterInsert=False)
"""conenct document test"""
print("="*20)
docManager.addConnectionFromFile(connfile, deleteAfterInsert=False)


# docManager.exportDocs()
# docManager.exportTopics()
# docManager.exportConnections()

docManager.closeConn()
