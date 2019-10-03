# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import MySQLdb
import os
import numpy as np
import matplotlib.pyplot as plt
from functionSet import *

username = "root"
password = "admin"

dbName = "papers"

f_initConn(username, password, dbName)
f_executeScriptsFromFile("class/createTbls.sql")
