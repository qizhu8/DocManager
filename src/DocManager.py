# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import MySQLdb
import numpy as np
import re
import os
import json
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

class DocManager(object):
    """docstring for DocManager."""

    def __init__(self):
        super(DocManager, self).__init__()

        self.dbUser     = ""
        self.dbPwd      = ""
        self.dbName     = ""
        self.conn       = -1
        self.cursor     = -1

        # instance for writing...
        self.db = BibDatabase()
        self.writer = BibTexWriter()
        self.writer.indent = ' '*4     # indent entries with 4 spaces instead of one
        self.writer.comma_first = False  # place the comma at the beginning of the line

    # initial connection and the cursor
    def initConn(self, user, passwd, db):
        self.conn   = MySQLdb.connect(user=user, passwd=passwd, charset='utf8mb4')
        self.cursor = self.conn.cursor()
        sql = 'CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' %db
        self.cursor.execute(sql)
        self.conn.commit()
        self.conn.close()
        self.conn  = MySQLdb.connect(user=user, passwd=passwd, charset='utf8mb4', db=db)
        self.cursor = self.conn.cursor()
        self.dbUser = user
        self.dbPwd  = passwd
        self.dbName = db
        print("[+] initial connection finished")

    def closeConn(self):
        if self.conn:
            self.conn.close()

    # execute .sql file
    def executeScriptsFromFile(self, filename):
        self._isConnect()

        statement = ""
        for line in open(filename):
            if re.match(r'--', line):  # ignore sql comment lines
                continue
            if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
                statement = statement + line
            else:  # when you get a line ending in ';' then exec statement and reset for next statement
                # print("reach the end of a complete line!!!!!!")
                statement = statement + line
                try:
                    self.cursor.execute(statement)
                    self.conn.commit()
                    statement = ""
                except Exception as e:
                    print("[-] MySQLError during execute statement")
                    print(e)

    def _isConnect(self):
        if self.conn == -1:
            raise Exception("[-] please connect the database using initConn(...) first")
            return False

        return True

    # custom search interface
    def _search(self, sql):
        self._isConnect()
        try:
            self.cursor.execute(sql)
            searchResult = np.array(self.cursor.fetchall())
        except Exception as e:
            print("[-] Cannot execute the query of:\n %s" % sql)
            print(e)
            return
        return searchResult

    def _execSql(self, sql):
        self._isConnect()
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print("[-] Cannot execute the sql:\n %s" % sql)
            print(e)
            return

    """insert into the DB system"""

    def _insertDoc(self, docId, title, type, year="NULL", source="NULL", description="NULL", bib="NULL"):
        SQL = """INSERT INTO Document(docID, title, type, year, source, description, bib) VALUES ("{docId}", "{title}", "{type}", {year}, "{source}", "{description}", "{bib}")""".format(
            docId=docId.replace('"', '""'),
            title=title.replace('"', '""'),
            type=type.replace('"', '""'),
            year=year,
            source=source.replace('"', '""'),
            description=description.replace('"', '""'),
            bib=bib.replace('"', '""')
        )
        try:
            self.cursor.execute(SQL)
            self.conn.commit()
            print("[+] Insert %s %s" % (type, docId))
        except Exception as e:
            print("[-] Cannot insert %s %s" % (type, docId))
            print(e)
            # print("SQL: %s" % SQL)


    def insertDocFromDict(self, docDic):
        requiredKeys = {'title', 'type', 'docId'}
        addupKeys = {'year', 'source', 'description', 'bib'}
        for checkKey in requiredKeys:
            if checkKey not in docDic:
                print("[-] input docDic instance must have %s" % checkKey)
                return
        for checkKey in addupKeys:
            if checkKey not in docDic:
                docDic[checkKey] = "NULL"

        print("%s description is %s" % (docDic["docId"], docDic["description"]))
        self._insertDoc(docId=docDic["docId"],
                        title=docDic["title"],
                        type=docDic["type"],
                        year=docDic["year"],
                        source=docDic["source"],
                        description=docDic["description"],
                        bib=docDic["bib"])



    def insertDocFromDictList(self, docDicList):
        if isinstance(docDicList, list):
            pass
        elif isinstance(docDicList, dict):
            docDicList = [docDicList]

        for docDic in docDicList:
            self.insertDocFromBibDic(docDic)



    # insert a bibDic object
    def insertDocFromBibDic(self, bibDic, description=""):
        try:

            type = bibDic['ENTRYTYPE']
            docId = bibDic['ID']
            year = bibDic['year']
            title = bibDic['title']

            if "description" in bibDic:
                description = bibDic["description"]

            source = ""
            for possbleSource in ['journal', 'booktitle', 'publisher']:
                if possbleSource in bibDic:
                    source = bibDic[possbleSource]
            # source = bibDic['journal']
            author = bibDic['author'].split('and')
            self.db.entries = [bibDic]
            bib = self.writer.write(self.db)


            self._insertDoc(docId=docId,
                            title=title,
                            type=type,
                            year=year,
                            source=source,
                            description=description,
                            bib=bib)

        except Exception as e:
            print("[-] Cannot insert current bib item")
            print(e)
        # finally:
        #     self.closeConn()

    def insertDocFromBibFile(self, bibFileName, deleteAfterInsert=False):
        if not os.path.getsize(bibFileName):
            return

        with open(bibFileName) as bibfile:
            bibDicList = bibtexparser.load(bibfile).entries
        self.insertDocFromDictList(bibDicList)

        if deleteAfterInsert:
            with open(bibFileName, 'w') as bibfile:
                bibfile.write("")

    def insertTopic(self, topicId, name, year="NULL", description="NULL"):
        self._insertDoc(docId=topicId,
                        title=name,
                        type='topic',
                        year='NULL',
                        source='NULL',
                        description=description,
                        bib='NULL')

    def insertTopicFromFile(self, jsonFilename, deleteAfterInsert=False):
        if not os.path.getsize(jsonFilename):
            return

        with open(jsonFilename) as topicFp:
            dicList = json.load(topicFp)
        self.insertTopicFromDicList(dicList=dicList)

        if deleteAfterInsert:
            with open(jsonFilename, 'w') as topicFp:
                topicFp.write("")

    def insertTopicFromDicList(self, dicList):
        for dic in dicList:
            self.insertTopicFromDic(dic)

    def insertTopicFromDic(self, dic):
        # check keys
        requiredKeys = {"topicId", "name"}
        addupKeys = {"description", "year"}
        for checkKey in requiredKeys:
            if checkKey not in dic:
                print("[-] topic dictionary must contain %s" % checkKey)
                return
        for checkKey in addupKeys:
            if checkKey not in dic:
                dic[checkKey] = "NULL"

        self.insertTopic(
            topicId=dic["topicId"],
            name=dic["name"],
            year=dic["year"],
            description=dic["description"]
            )


    """ delete a document """
    def deleteDoc(self, docId):
        SQL = """DELETE FROM Document WHERE docID="{docId}"; """.format(docId=docId)
        self._execSql(SQL)

    """ get documents """
    def getAllDocs(self):
        SQL = """SELECT docId, title, type FROM Document;"""
        return self._search(SQL)

    def getDocById(self, docId):
        SQL = """SELECT docId, title, type, year, source, description, bib FROM Document WHERE docID="{docId}";""".format(docId=docId)
        return self._search(SQL)

    def getAllTopics(self):
        SQL = """SELECT docId, title FROM Document WHERE type="topic";"""
        return self._search(SQL)


    """add connection"""
    def addConnection(self, srcDocId, dstDocId, description=""):
        if dstDocId == srcDocId:
            print("srcDocId shouldn't equal dstDocId")
            return
        SQL = """INSERT INTO Connection(srcDocId, dstDocId, description) VALUE("{srcDocId}", "{dstDocId}", "{description}");""".format(
            srcDocId=srcDocId,
            dstDocId=dstDocId,
            description=description.replace('"', '""')
        )
        try:
            self.cursor.execute(SQL)
            self.conn.commit()
            print("[+] Insert connection pair %s - %s" % (srcDocId, dstDocId))
        except Exception as e:
            print("[-] Cannot insert connection %s - %s" % (srcDocId, dstDocId))
            print(e)


    def addConnectionFromFile(self, jsonFilename, deleteAfterInsert=False):
        if not os.path.getsize(jsonFilename):
            return

        with open(jsonFilename) as connectionFp:
            dicList = json.load(connectionFp)
        self.addConnectionFromDicList(dicList=dicList)

        if deleteAfterInsert:
            with open(jsonFilename, 'w') as connectionFp:
                connectionFp.write("")

    def addConnectionFromDicList(self, dicList):
        for dic in dicList:
            self.addConnectionFromDic(dic)

    def addConnectionFromDic(self, dic):
        # check key
        requiredKeys = {"srcDocId", "dstDocId"}
        addupKeys = {"description"}
        for checkKey in requiredKeys:
            if checkKey not in dic:
                print("[-] connection dictionary must contain %s" % checkKey)
                return
        for checkKey in addupKeys:
            if checkKey not in dic:
                dic[checkKey] = "NULL"
        self.addConnection(
                            srcDocId=dic["srcDocId"],
                            dstDocId=dic["dstDocId"],
                            description=dic["description"]
                            )


    """delete connection"""
    def delConnection(self, srcDocId, dstDocId):
        SQL = """DELETE FROM Connection WHERE srcDocId="{srcDocId}" and dstDocId="{dstDocId}"; """.format(srcDocId=srcDocId, dstDocId=dstDocId)
        self._execSql(SQL)

    """get connections"""
    def getAncestors(self, tgtDocId):
        SQL = """SELECT docId, title, type FROM Document WHERE docId in (SELECT srcDocId FROM Connection WHERE dstDocId="{tgtDocId}");""".format(tgtDocId=tgtDocId)
        return self._search(SQL)

    def getDescendants(self, tgtDocId):
        SQL = """SELECT docId, title, type FROM Document WHERE docId in (SELECT dstDocId FROM Connection WHERE srcDocId="{tgtDocId}");""".format(tgtDocId=tgtDocId)
        return self._search(SQL)

    def getConnectionInfo(self, srcDocId, dstDocId):
        SQL = """SELECT description FROM Connection WHERE srcDocId="{srcDocId}" AND dstDocId="{dstDocId}";""".format(srcDocId=srcDocId, dstDocId=dstDocId)
        return self._search(SQL)

    """modify Document"""
    def modifyDocument(self, docId, category, newVal):
        if isinstance(newVal, str): # manually add double quotation marks
            SQL = """UPDATE Document SET {category}="{newVal}" WHERE docId="{docId}"; """.format(
            category=category,
            newVal=newVal.replace('"', '""'),
            docId=docId
        )
        else:
            SQL = """UPDATE Document SET {category}={newVal} WHERE docId="{docId}"; """.format(
            category=category,
            newVal=newVal,
            docId=docId
        )
        self._execSql(SQL)

    """modify Connection"""
    def modifyConnectionDescription(self, srcDocId, dstDocId, description):
        if isinstance(description, str): # manually add double quotation marks
            description = '"%s"' % description
        SQL = """UPDATE Connection SET description={description} WHERE srcDocId="{srcDocId}" and dstDocId="{dstDocId}"; """.format(
            description=description,
            srcDocId=srcDocId,
            dstDocId=dstDocId
        )
        self._execSql(SQL)

    """export docs to bib, export topics and connections to json files """
    def exportDocs(self, filename="mybib.bib.bk"):
        SQL = "SELECT description, bib FROM Document WHERE type != 'topic';"
        docsInfo = self._search(SQL)
        bibDicList = []
        for description, bib in docsInfo:
            bibDicList += bibtexparser.loads(bib).entries
            bibDicList[-1]['description'] = description
        self.db.entries = bibDicList
        with open(filename, 'w') as bibtexFp:
            bibtexparser.dump(self.db, bibtexFp)

    def exportTopics(self, filename="topics.json.bk"):
        SQL = "SELECT docID, title, description FROM Document WHERE type = 'topic';"
        topicInfo = self._search(SQL)
        listForJson = []
        for docId, title, description in topicInfo:
            listForJson.append({"topicId":docId, "name":title, "description":description})

        with open(filename, 'w') as jsonFp:
            json.dump(listForJson, jsonFp, indent=4, separators=(',', ': '))

    def exportConnections(self, filename="connections.json.bk"):
        SQL = "SELECT srcDocId, dstDocId, description FROM Connection;"
        connectionInfo = self._search(SQL)
        listForJson = []
        for srcDocId, dstDocId, description in connectionInfo:
            listForJson.append({"srcDocId":srcDocId, "dstDocId":dstDocId, "description":description})

        with open(filename, 'w') as jsonFp:
            json.dump(listForJson, jsonFp, indent=4, separators=(',', ': '))


    """search"""
    def searchDocWithKeyword(self, keyword):
        SQL = """SELECT docId, title, type FROM Document WHERE docId LIKE "%{keyword}%" OR title LIKE "%{keyword}%" OR description LIKE "%{keyword}%";""".format(keyword=keyword)

        return self._search(SQL)
