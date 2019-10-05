# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from src.DocManager import DocManager

username = "root"
password = "admin"

dbName = "papers"
sqlDelTblsFilePath = "src/dropTables.sql"
sqlInitFilePath = "src/createTbls.sql"
bibfile = "data/mybib.bib"

docManager = DocManager()
docManager.initConn(username, password, dbName)
# docManager.executeScriptsFromFile(sqlDelTblsFilePath) # drop tables. DEBUG only
docManager.executeScriptsFromFile(sqlInitFilePath)

"""insert document test"""
docManager.insertDocFromBibFile(bibfile)
docManager.insertTopic(topicId='Index Coding', name='Index Coding')
docManager.insertTopic(topicId='Coded Caching', name='Coded Caching')
print(docManager.getAllDocs().shape)
docManager.deleteDoc('yu2018characterizing')
print(docManager.getAllDocs().shape)

print(docManager.getAllTopics())

"""conenct document test"""
# docManager
description = """This is the first known paper that proposes the Index Coding"""
docManager.addConnection(srcDocId='Index Coding', dstDocId='birk1998informed', description=description)

description = """This is a paper largely contributes to the Index Coding"""
docManager.addConnection(srcDocId='birk1998informed', dstDocId='bar2011index', description=description)


print("="*20)
print(docManager.getAncestors(tgtDocId="birk1998informed"))
print("="*20)
print(docManager.getDescendants(tgtDocId="birk1998informed"))

docManager.closeConn()
