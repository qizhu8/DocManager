# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from src.DocManager import DocManager

username = "root"
password = "admin"

dbName = "papers"
sqlInitFilePath = "src/createTbls.sql"
bibfile = "data/mybib.bib"

docManager = DocManager()
docManager.initConn(username, password, dbName)
docManager.executeScriptsFromFile(sqlInitFilePath)

docManager.insertDocFromBibFile(bibfile)

docManager.insertTopic(topicId='Index Coding', name='Index Coding')
print(docManager.getAllDoc().shape)
docManager.deleteDoc('yu2018characterizing')
print(docManager.getAllDoc().shape)


docManager.closeConn()
