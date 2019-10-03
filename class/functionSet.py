#!/usr/python/env env
import MySQLdb
import os
import matplotlib.pyplot as plt
import numpy as np
import re


dbUser     = ""
dbPwd      = ""
dbName     = ""
conn       = -1
cursor     = -1

# initial connection and the cursor
def f_initConn(user, passwd, db):
    global conn
    global cursor
    global dbUser
    global dbPwd
    global dbName
    conn   = MySQLdb.connect(user = user, passwd = passwd, charset='utf8mb4')
    cursor = conn.cursor()
    sql = 'CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;' %db
    cursor.execute(sql)
    conn.commit()
    conn.close()
    conn  = MySQLdb.connect(user = user, passwd = passwd, charset='utf8mb4', db=db)
    cursor = conn.cursor()
    dbUser = user
    dbPwd  = passwd
    dbName = db
    print("initial connection finished")

# execute .sql file
def f_executeScriptsFromFile(filename):
    statement = ""
    for line in open(filename):
        if re.match(r'--', line):  # ignore sql comment lines
            continue
        if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            print("reach the end of a complete line!!!!!!")
            statement = statement + line
            try:
                cursor.execute(statement)
                conn.commit()
                statement = ""
            except Exception as e:
                print("[WARN] MySQLError during execute statement")
                print(e)


# insert
def f_insert(sql):
    cursor.execute(sql)
    conn.commit()

# custom search interface
def f_search(sql):
    cursor.execute(sql)
    searchResult = np.array(cursor.fetchall())
    return searchResult
