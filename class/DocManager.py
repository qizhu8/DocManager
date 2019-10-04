# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import MySQLdb
import numpy as np
import re


class DocManager(object):
    """docstring for DocManager."""

    def __init__(self):
        super(DocManager, self).__init__()

        self.dbUser     = ""
        self.dbPwd      = ""
        self.dbName     = ""
        self.conn       = -1
        self.cursor     = -1

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
        print("initial connection finished")

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
                    print("[WARN] MySQLError during execute statement")
                    print(e)

    def _isConnect(self):
        if self.conn == -1:
            raise Exception("please connect the database using initConn(...) first")
            return False

        return True

    # custom search interface
    def search(self.sql):
        self._isConnect()

        self.cursor.execute(sql)
        searchResult = np.array(self.cursor.fetchall())
        return searchResult
