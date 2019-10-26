# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from src.DocManager import DocManager
import os

username = "root"
password = "admin"

dbName = "papers"
bibfile = "mybib.bib"
connfile = "connection.json"
topicfile = "topic.json"


docManager = DocManager()
docManager.initConn(username, password, dbName)
docManager.deleteTbls() # drop tables. DEBUG only
docManager.createTbls()

"""insert document test"""
docManager.insertDocFromBibFile(bibfile, deleteAfterInsert=False)
print("="*20)
docManager.insertTopicFromFile(topicfile, deleteAfterInsert=False)
"""conenct document test"""
print("="*20)
docManager.addConnectionFromFile(connfile, deleteAfterInsert=False)

print(docManager.getAllDocs())
# docManager.exportDocs()
# docManager.exportTopics()
# docManager.exportConnections()

docManager.closeConn()
