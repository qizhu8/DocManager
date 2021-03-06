# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import json
import tkinter as tk
import tkinter.scrolledtext as tkst
import tkinter.messagebox as tkmsg
import tkinter.filedialog as tkFileDialog
import bibtexparser

from DocManager import DocManager

VERSION = "1.0.0"

HELP_MESSAGE =\
""" Program Usage
1. Load bibfile
    Click the "Load "
"""

ABOUT_AUTHOR_MESSAGE=\
"""
This program is developed by Yu Wang 10/26/2019.
You are welcomed to contact the author via wangy52@rpi.edu.
"""

class DocManagerGUI(tk.Tk, object):
    """
    docstring for DocManagerGUI.

    This class focuses mainly on the GUI, rather than the detail implementation.
    """

    def __init__(self):
        super(DocManagerGUI, self).__init__()

        # default config
        self.windowsParam = {"GUI_WIDTH": 1000, "GUI_HEIGHT": 1000} # unused
        self.dbParams = {
            "username" : "root",
            "password" : "admin",
            "dbName" : "papers",
            "backupdir": ".",
            "exportWhenClose": True
        }
        self.themeParams = {
            "background": "grey",
            "topicColor": "green",
            "docColor": "blue",
            "default": "black",
            "fontAndSize": ("", 18)
        }
        self.__load_presetInfo()

        self.document_list_frame = None
        self.document_info_frame = None

        self.docManager = DocManager()
        try:
            self.docManager.initConn(self.dbParams["username"], self.dbParams["password"], self.dbParams["dbName"])
            self.docManager.createTbls() # create tables if doesn't exists
        except Exception as e:
            print("Fail to connect to the server")
            print(e)
        finally:
            return
        # docManager.executeScriptsFromFile(sqlDelTblsFilePath) # drop tables. DEBUG only
        # docManager.executeScriptsFromFile(sqlInitFilePath)


    """
    save/load GUI related parameters
    """
    def __load_presetInfo(self):
        """load parameters from config file"""
        configFilePath = os.path.join('config.json')
        if os.path.exists(configFilePath):
            with open(configFilePath, 'r') as f:
                configDic = json.load(f)

            # refresh window related parameters
            if "WINDOWS" in configDic:
                windowsParamDic = configDic["WINDOWS"]
                for key in self.windowsParam:
                    if key in windowsParamDic:
                        self.windowsParam[key] = windowsParamDic[key]

            # refresh database related parameters
            if "DBParams" in configDic:
                dbParamDic = configDic["DBParams"]
                for key in self.dbParams:
                    if key in dbParamDic:
                        self.dbParams[key] = dbParamDic[key]

            if "ThemeParams" in configDic:
                themeParamDic = configDic["ThemeParams"]
                for key in self.themeParams:
                    if key in themeParamDic:
                        self.themeParams[key] = themeParamDic[key]

        else:
            self.__refresh_presetInfo()

    def __refresh_presetInfo(self):
        """save parameters to config file"""
        configFilePath = os.path.join('config.json')

        # parameters to pack
        configDic = {"WINDOWS": self.windowsParam, "DBParams": self.dbParams, "ThemeParams": self.themeParams}

        # write to file
        with open(configFilePath, 'w+') as f:
            json.dump(configDic, f, indent=4, separators=(',', ': '))



    """
    create each control
    """

    """list for documents"""
    def __init_document_list_frame(self):
        if self.document_list_frame is not None:
            self.document_list_frame.pack_forget()
            self.document_list_frame.destroy()
        self.document_list_frame = tk.Frame(self)
        self.document_list_frame.config(bg=self.themeParams["background"])

        """
        | Documents:     |
        | keyword filter |
        | -------------- |
        | list of docs   |
        """

        def __list_select(evt):
            item_id = self.document_list_ctl_dict['list'].curselection()
            if item_id:
                docId = self.document_list_ctl_dict['itemKey'][item_id[0]]
                self.curDocId = docId
                print(docId, " is chosen")
                self.__show_doc_info(docId)
                self.__show_doc_hier(docId)

        def __load_from_files():
            loadFromFile_window = tk.Toplevel(self)
            self.__loadFromFile_window(loadFromFile_window)
            self.wait_window(loadFromFile_window)
            self.__show_doc_list()


        def keyword_search(evt):
            keyword = self.document_list_ctl_dict['filter'].get()
            if keyword != "filtered by keywords":
                self.__show_doc_list(keyword)


        # create each control and save them into a dict
        self.document_list_ctl_dict = {}

        self.document_list_ctl_dict['label'] = tk.Label(self.document_list_frame, text="Documents:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_list_ctl_dict['label'].pack(fill=tk.BOTH)

        self.document_list_ctl_dict['filter'] = tk.Entry(self.document_list_frame,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_list_ctl_dict['filter'].insert(tk.END, 'filtered by keywords')

        self.document_list_ctl_dict['filter'].pack(fill=tk.BOTH)
        self.document_list_ctl_dict['filter'].bind('<Return>', keyword_search)

        self.document_list_ctl_dict['list'] = tk.Listbox(self.document_list_frame,
            font=self.themeParams["fontAndSize"],
            bg=self.themeParams["background"])

        self.document_list_ctl_dict['list'].bind("<<ListboxSelect>>", __list_select)

        self.document_list_ctl_dict['scrollbar'] = tk.Scrollbar(self.document_list_frame, orient="vertical")
        self.document_list_ctl_dict['scrollbar'].config(command=self.document_list_ctl_dict['list'].yview)
        self.document_list_ctl_dict['scrollbar'].pack(side="right", fill="y")
        self.document_list_ctl_dict['list'].config(yscrollcommand=self.document_list_ctl_dict['scrollbar'].set)
        self.document_list_ctl_dict['list'].pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.document_list_ctl_dict['button'] = tk.Button(self.document_list_frame, text="Load from files", command=__load_from_files,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        self.document_list_ctl_dict['button'].pack(side=tk.TOP, fill=tk.BOTH)

        self.document_list_ctl_dict['itemKey'] = []


    def __show_doc_list(self, keyword=None):
        self.__clear_conn_info()
        self.document_list_ctl_dict['itemKey'] = []
        self.document_list_ctl_dict['list'].delete(0, tk.END)
        if keyword is None or len(keyword) == 0:
            docsToShow = self.docManager.getAllDocs()
        else:
            docsToShow = self.docManager.searchDocWithKeyword(keyword)

        for idx, record in enumerate(docsToShow):
            docId, title, type = record
            if type == "topic":
                descName = "topic - {title}".format(title=title)
                self.document_list_ctl_dict['list'].insert(idx, descName)
                self.document_list_ctl_dict['list'].itemconfig(idx, {'fg': self.themeParams["topicColor"]})
            else:
                descName = title
                self.document_list_ctl_dict['list'].insert(idx, descName)
                self.document_list_ctl_dict['list'].itemconfig(idx, {'fg': self.themeParams["docColor"]})

            self.document_list_ctl_dict['itemKey'].append(docId)


    """ frame of document detail """
    def __init_document_info_frame(self):

        if self.document_info_frame is not None:
            self.document_info_frame.pack_forget()
            self.document_info_frame.destroy()
        self.document_info_frame = tk.Frame(self)

        self.document_info_frame.config(bg=self.themeParams["background"])
        self.document_info_ctl_dict = {}



        def __ancList_select(evt):
            item_id = self.document_info_ctl_dict['ancList'].curselection()
            if item_id:
                docId = self.document_info_ctl_dict['ancList'].get(item_id)
                print(docId, " is chosen")
                if docId != "No Document":
                    print("show %s - %s" % (docId, self.curDocId))
                    self.__show_doc_info(docId)
                    self.__show_conn_info(docId, self.curDocId)

        def __deceList_select(evt):
            item_id = self.document_info_ctl_dict['deceList'].curselection()
            if item_id:
                # docId = self.document_info_ctl_dict['deceList'].get(item_id)
                docId = self.document_info_ctl_dict['deceList'].get(item_id)
                print(docId, " is chosen")
                if docId != "No Document":
                    print("show %s - %s" % (self.curDocId, docId))
                    self.__show_doc_info(docId)
                    self.__show_conn_info(self.curDocId, docId)

        def __ancList_double_click(evt):
            item_id = self.document_info_ctl_dict['ancList'].curselection()
            if item_id:
                docId = self.document_info_ctl_dict['ancList'].get(item_id)
                print(docId, " is chosen")
                if docId != "No Document":
                    self.curDocId = docId
                    self.__show_doc_info(docId)
                    self.__show_doc_hier(docId)
                    self.__clear_conn_info()
                else:
                    print("do nothing when select No Document")
                # if tkmsg.askokcancel("Confirm", "Delete the following ancester item?"):
                #     print("delete %s -> %s" % (docId, self.curDocId))

        def __deceList_double_click(evt):
            item_id = self.document_info_ctl_dict['deceList'].curselection()
            if item_id:
                docId = self.document_info_ctl_dict['deceList'].get(item_id)
                print(docId, " is chosen")
                if docId != "No Document":
                    self.curDocId = docId
                    self.__show_doc_info(docId)
                    self.__show_doc_hier(docId)
                    self.__clear_conn_info()
                else:
                    print("do nothing when select No Document")
                # if tkmsg.askokcancel("Confirm", "Delete the following follower item?"):
                #     print("delete %s -> %s" % (self.curDocId, docId))

        def __list_focusout(evt):
            self.__show_doc_info(self.curDocId)
            self.__clear_conn_info()


        def ancAdd_hit():
            self.docToConn = None
            search_window = tk.Toplevel(self)
            self.__show_search_window(search_window)
            self.wait_window(search_window)
            print("-"*10)
            print(self.docToConn)
            if self.docToConn is not None:
                print("adding ancestor doc %s" % self.docToConn)
                if self.document_info_ctl_dict['ancList'].get(0) == "No Document":
                    self.document_info_ctl_dict['ancList'].delete(0, tk.END)
                self.document_info_ctl_dict['ancList'].insert(tk.END, self.docToConn[0])
                # insert the connection to database
                self.docManager.addConnection(dstDocId=self.curDocId, srcDocId=self.docToConn[0], description="")

        def deceAdd_hit():
            self.docToConn = None
            search_window = tk.Toplevel(self)
            self.__show_search_window(search_window)
            self.wait_window(search_window)
            print("-"*10)
            print(self.docToConn)
            if self.docToConn is not None:
                print("adding descendant doc %s" % self.docToConn)
                if self.document_info_ctl_dict['deceList'].get(0) == "No Document":
                    self.document_info_ctl_dict['deceList'].delete(0, tk.END)
                self.document_info_ctl_dict['deceList'].insert(tk.END, self.docToConn[0])
                self.docManager.addConnection(srcDocId=self.curDocId, dstDocId=self.docToConn[0], description="")

        def ancDel_hit():
            item_id = self.document_info_ctl_dict['ancList'].curselection()
            if item_id is not None:
                tgtdocId = self.document_info_ctl_dict['ancList'].get(item_id)
                self.docManager.delConnection(srcDocId=tgtdocId, dstDocId=self.curDocId)
                self.document_info_ctl_dict['ancList'].delete(item_id)


        def deceDel_hit():
            item_id = self.document_info_ctl_dict['deceList'].curselection()
            if item_id is not None:
                tgtdocId = self.document_info_ctl_dict['deceList'].get(item_id)
                self.docManager.delConnection(dstDocId=tgtdocId, srcDocId=self.curDocId)
                self.document_info_ctl_dict['deceList'].delete(item_id)

        def updateDoc_hit():
            title = self.document_info_ctl_dict['titleEntry'].get()
            type = self.document_info_ctl_dict['typeEntry'].get()
            description = self.document_info_ctl_dict['descText'].get("1.0",tk.END)

            self.docManager.modifyDocument(self.curDocId, 'title', title)
            self.docManager.modifyDocument(self.curDocId, 'type', type)

            self.docManager.modifyDocument(self.curDocId, 'description', description)

        def updateConn_hit():
            description = self.document_info_ctl_dict['connText'].get("1.0",tk.END)
            self.docManager.modifyConnectionDescription(
                    srcDocId=self.curConnPair[0],
                    dstDocId=self.curConnPair[1],
                    description=description)
            print("update connection description %s-%s :\n %s" %(self.curConnPair[0], self.curConnPair[1], description))

        def exportToLocal_hit():
            backupdir = self.dbParams["backupdir"]
            self.docManager.exportDocs(os.path.join(backupdir, "mybib.bib"))
            self.docManager.exportTopics(os.path.join(backupdir, "topic.json"))
            self.docManager.exportConnections(os.path.join(backupdir, "connection.json"))


        row = 0 # next available row
        # type
        self.document_info_ctl_dict['typeLabel'] = tk.Label(self.document_info_frame, text="type:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['typeEntry'] = tk.Entry(self.document_info_frame, show=None,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])

        self.document_info_ctl_dict['typeLabel'].grid(row=row, column=0)
        self.document_info_ctl_dict['typeEntry'].grid(row=row, column=1, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        row += 1

        # title
        self.document_info_ctl_dict['titleLabel'] = tk.Label(self.document_info_frame, text="title:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['titleEntry'] = tk.Entry(self.document_info_frame, show=None,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])

        self.document_info_ctl_dict['titleLabel'].grid(row=row, column=0)
        self.document_info_ctl_dict['titleEntry'].grid(row=row, column=1, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        row += 1

        # docId
        self.document_info_ctl_dict['docIdLabel'] = tk.Label(self.document_info_frame, text="id:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['docIdEntry'] = tk.Entry(self.document_info_frame, show=None,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])

        self.document_info_ctl_dict['docIdLabel'].grid(row=row, column=0)
        self.document_info_ctl_dict['docIdEntry'].grid(row=row, column=1, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        row += 1

        # description
        height=15
        self.document_info_ctl_dict['descLabel'] = tk.Label(self.document_info_frame, text="description:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['descText'] = tkst.ScrolledText(self.document_info_frame, height=height,
            wrap = tk.WORD, font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])

        self.document_info_ctl_dict['descLabel'].grid(row=row, column=0)
        self.document_info_ctl_dict['descText'].grid(row=row, column=1, sticky='wesn')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=height)
        row += 1

        # update doc info
        self.document_info_ctl_dict['updateDocButton'] = tk.Button(self.document_info_frame, text="Update Doc Info", command=updateDoc_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        self.document_info_ctl_dict['updateDocButton'].grid(row=row, columnspan=2, sticky='we')
        row += 1
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)


        # ancester and decendants
        self.document_info_ctl_dict['ancLabel'] = tk.Label(self.document_info_frame, text="ancesters:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['ancList'] = tk.Listbox(self.document_info_frame, bg=self.themeParams["background"])
        self.document_info_ctl_dict['ancAddButton'] = tk.Button(self.document_info_frame, text="Add Ancesters", command=ancAdd_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        self.document_info_ctl_dict['ancDelButton'] = tk.Button(self.document_info_frame, text="Delete Ancesters", command=ancDel_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        self.document_info_ctl_dict['deceLabel'] = tk.Label(self.document_info_frame, text="followers:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['deceList'] = tk.Listbox(self.document_info_frame, bg=self.themeParams["background"])
        self.document_info_ctl_dict['deceAddButton'] = tk.Button(self.document_info_frame, text="Add Decendants", command=deceAdd_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        self.document_info_ctl_dict['deceDelButton'] = tk.Button(self.document_info_frame, text="Delete Decendants", command=deceDel_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        self.document_info_ctl_dict['ancLabel'].grid(row=row, column=0, sticky='we')
        self.document_info_ctl_dict['ancList'].grid(row=row, column=1, sticky='we')
        self.document_info_ctl_dict['ancAddButton'].grid(row=row+1, column=1, sticky='we')
        self.document_info_ctl_dict['ancDelButton'].grid(row=row+1, column=0, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        tk.Grid.rowconfigure(self.document_info_frame, row+1, weight=1)
        row += 2

        self.document_info_ctl_dict['deceLabel'].grid(row=row, column=0, sticky='we')
        self.document_info_ctl_dict['deceList'].grid(row=row, column=1, sticky='we')
        self.document_info_ctl_dict['deceDelButton'].grid(row=row+1, column=0, sticky='we')
        self.document_info_ctl_dict['deceAddButton'].grid(row=row+1, column=1, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        tk.Grid.rowconfigure(self.document_info_frame, row+1, weight=1)
        row += 2

        self.document_info_ctl_dict['ancList'].bind("<<ListboxSelect>>", __ancList_select)
        self.document_info_ctl_dict['ancList'].bind("<Double-Button-1>", __ancList_double_click)
        self.document_info_ctl_dict['ancList'].bind("<FocusOut>", __list_focusout)
        self.document_info_ctl_dict['deceList'].bind("<<ListboxSelect>>", __deceList_select)
        self.document_info_ctl_dict['deceList'].bind("<Double-Button-1>", __deceList_double_click)
        self.document_info_ctl_dict['deceList'].bind("<FocusOut>", __list_focusout)

        # connection description
        height=5
        self.document_info_ctl_dict['connLabel'] = tk.Label(self.document_info_frame, text="Connection Description:",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        self.document_info_ctl_dict['connText'] = tkst.ScrolledText(self.document_info_frame, height=height, wrap = tk.WORD,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])

        self.document_info_ctl_dict['connLabel'].grid(row=row, column=0)
        self.document_info_ctl_dict['connText'].grid(row=row, column=1, sticky='wesn')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=height)
        row += 1

        # update conn info
        self.document_info_ctl_dict['updateConnButton'] = tk.Button(self.document_info_frame, text="Update Conn Info", command=updateConn_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        self.document_info_ctl_dict['updateConnButton'].grid(row=row, columnspan=2, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        row += 1

        self.document_info_ctl_dict['exportButton'] = tk.Button(self.document_info_frame, text="Export to local", command=exportToLocal_hit,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        self.document_info_ctl_dict['exportButton'].grid(row=row, columnspan=3, sticky='we')
        tk.Grid.rowconfigure(self.document_info_frame, row, weight=1)
        row += 1

        tk.Grid.columnconfigure(self.document_info_frame, 0, weight=1)
        tk.Grid.columnconfigure(self.document_info_frame, 1, weight=4)



    """ control the sub-module layout """
    def __layout_frames(self):

        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)
        # self.document_list_frame.config(width=self.windowsParam['GUI_WIDTH']*0.5)
        # self.document_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # self.document_list_frame.pack_propagate(0)
        self.document_list_frame.grid(row=0, column=0, sticky="SWEN")
        # self.document_info_frame.config(width=self.windowsParam['GUI_WIDTH']*0.5)
        # self.document_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # self.document_info_frame.pack_propagate(0)
        self.document_info_frame.grid(row=0, column=1, sticky="SWEN")

    def __show_doc_info(self, docId):
        if docId == "No Document":
            return
        docInfo = self.docManager.getDocById(docId)
        # docId, title, type, year, source, description, bib
        if docInfo is None or len(docInfo) == 0:
            print("docInfo is empty", docInfo)
            return
        try:
            docId, title, type, year, source, description, bib = docInfo[0]

            self.document_info_ctl_dict['typeEntry'].delete(0, tk.END)
            self.document_info_ctl_dict['titleEntry'].delete(0, tk.END)
            self.document_info_ctl_dict['docIdEntry'].delete(0, tk.END)
            self.document_info_ctl_dict['descText'].delete('1.0', tk.END)

            self.document_info_ctl_dict['typeEntry'].insert(tk.END, type)
            self.document_info_ctl_dict['titleEntry'].insert(tk.END, title)
            self.document_info_ctl_dict['docIdEntry'].insert(tk.END, docId)
            self.document_info_ctl_dict['descText'].insert(tk.END, description)

        except Exception as e:
            print(e)


    def __show_doc_hier(self, docId):
        ancesDocsInfo = self.docManager.getAncestors(docId)
        decenDocsInfo = self.docManager.getDescendants(docId)

        self.document_info_ctl_dict['ancList'].delete(0, tk.END)
        self.document_info_ctl_dict['deceList'].delete(0, tk.END)

        if ancesDocsInfo is None or len(ancesDocsInfo) == 0:
            print("no ancester", ancesDocsInfo)
            self.document_info_ctl_dict['ancList'].insert(0, "No Document")
        else:
            try:
                for idx, ancesDocInfo in enumerate(ancesDocsInfo):
                    ancesDocId, ancesTitle, ancesType = ancesDocInfo
                    if ancesType == "topic":
                        self.document_info_ctl_dict['ancList'].insert(idx, ancesDocId)
                        self.document_info_ctl_dict['ancList'].itemconfig(idx, {'fg': self.themeParams["topicColor"]})
                    else:
                        self.document_info_ctl_dict['ancList'].insert(idx, ancesDocId)
                        self.document_info_ctl_dict['ancList'].itemconfig(idx, {'fg': self.themeParams["docColor"]})

            except Exception as e:
                print(e)

        if decenDocsInfo is None or len(decenDocsInfo) == 0:
            print("no decendants", decenDocsInfo)

            self.document_info_ctl_dict['deceList'].insert(0, "No Document")
        else:
            try:
                for idx, decenDocInfo in enumerate(decenDocsInfo):
                    decenDocId, decenTitle, decenType = decenDocInfo
                    if decenType == "topic":
                        self.document_info_ctl_dict['deceList'].insert(idx, decenDocId)
                        self.document_info_ctl_dict['deceList'].itemconfig(idx, {'fg': self.themeParams["topicColor"]})
                    else:
                        self.document_info_ctl_dict['deceList'].insert(idx, decenDocId)
                        self.document_info_ctl_dict['deceList'].itemconfig(idx, {'fg': self.themeParams["docColor"]})

            except Exception as e:
                print(e)

    def __show_conn_info(self, srcDocId, dstDocId):
        if srcDocId not in {"No Document", "NULL"} and dstDocId not in {"No Document", "NULL"}:
            self.curConnPair = [srcDocId, dstDocId]
            descriptionInfo = self.docManager.getConnectionInfo(srcDocId, dstDocId)
            if descriptionInfo is not None and len(descriptionInfo) > 0:
                description = descriptionInfo[0]
                self.document_info_ctl_dict['connText'].delete('1.0', tk.END)
                self.document_info_ctl_dict['connText'].insert(tk.END, description[0])

    def __clear_conn_info(self):
        self.document_info_ctl_dict['connText'].delete('1.0', tk.END)

    """search window"""
    def __show_search_window(self, search_window):
        search_window.config(bg=self.themeParams["background"])
        tk.Grid.rowconfigure(search_window, 0, weight=1)
        tk.Grid.columnconfigure(search_window, 0, weight=1)

        self.searchRst = None
        def filterRstList_double_click(evt):
            item_id = filterRstList.curselection()
            # docId = self.document_info_ctl_dict['deceList'].get(item_id)
            # title = filterRstList.get(item_id)
            self.docToConn = self.searchRst[item_id[0], :]
            print("add %s" % self.docToConn)
            search_window.destroy()

        def keyword_search(evt):
            keyword = keywordEntry.get()
            self.searchRst = self.docManager.searchDocWithKeyword(keyword)
            filterRstList.delete(0, tk.END)
            if len(self.searchRst) > 0:

                for idx, record in enumerate(self.searchRst):
                    docId, title, type = record
                    if type == "topic":
                        descName = "topic - {title}".format(title=title)
                        filterRstList.insert(idx, descName)
                        filterRstList.itemconfig(idx, {'fg': self.themeParams["topicColor"]})
                    else:
                        descName = title
                        filterRstList.insert(idx, descName)
                        filterRstList.itemconfig(idx, {'fg': self.themeParams["docColor"]})



        search_window.geometry("%dx%d+%d+%d" % (
                    self.windowsParam['GUI_WIDTH']//2,
                    self.windowsParam['GUI_HEIGHT']//2,
                    self.winfo_screenwidth()/2 - self.windowsParam['GUI_WIDTH']//4,
                    self.winfo_screenheight()/2 - self.windowsParam['GUI_HEIGHT'] // 4))



        # keyword
        keyword_frame = tk.Frame(search_window)
        keyword_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        keywordLabel = tk.Label(keyword_frame, text="Keywords:", fg=self.themeParams["default"], bg=self.themeParams["background"])
        keywordEntry = tk.Entry(keyword_frame, show=None, fg=self.themeParams["default"], bg=self.themeParams["background"])
        filterRstList = tk.Listbox(keyword_frame, bg=self.themeParams["background"])

        filterRstList.bind("<Double-Button-1>", filterRstList_double_click)
        keywordEntry.bind('<Return>', keyword_search)

        keywordLabel.grid(row=0, column=0, sticky=(tk.E, tk.W))
        keywordEntry.grid(row=0, column=1, sticky=(tk.E, tk.W))
        filterRstList.grid(row=1, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W))


        tk.Grid.rowconfigure(keyword_frame, 0, weight=1)
        tk.Grid.rowconfigure(keyword_frame, 1, weight=15)
        tk.Grid.columnconfigure(keyword_frame, 0, weight=1)
        tk.Grid.columnconfigure(keyword_frame, 1, weight=4)


    def __menu(self):
        def __show_help():
            tkmsg.showinfo("Help", HELP_MESSAGE)

        def __show_about_author():
            tkmsg.showinfo("About", ABOUT_AUTHOR_MESSAGE)

        def __reset_database():
            ans = tkmsg.askokcancel("Warning","Would you like to delete all data?")
            if ans:
                self.docManager.deleteTbls()
                self.docManager.createTbls()
                self.__show_doc_list()

        self.menubar = tk.Menu(self)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        aboutmenu = tk.Menu(self.menubar, tearoff=0)

        self.menubar.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='Reset Database', command=lambda: __reset_database())
        filemenu.add_command(label='Help', command=lambda: __show_help())
        #
        self.menubar.add_cascade(label='About', menu=aboutmenu)
        aboutmenu.add_command(label='About author', command=lambda: __show_about_author())


    def __loadFromFile_window(self, loadFromFile_window):
        loadFromFile_window.config(bg=self.themeParams["background"])
        rows = 0
        loadFromFile_window.geometry("%dx%d+%d+%d" % (
                    self.winfo_screenwidth()/2,
                    self.winfo_screenheight()/2,
                    self.winfo_screenwidth()/4,
                    self.winfo_screenheight()/4))

        def __btn_choose_docBib():
            newFilePath = tkFileDialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("bibtext files","*.bib"),("backup files","*.bk"),("all files","*.*")))
            if newFilePath:
                newFilePath = os.path.relpath(newFilePath)
                bibFilePath.delete(0, tk.END)
                bibFilePath.insert(tk.END, newFilePath)

        def __btn_load_docBib():
            filepath = bibFilePath.get()
            if len(filepath) > 0:
                self.docManager.insertDocFromBibFile(filepath, deleteAfterInsert=False)

        def __btn_choose_topic():
            newFilePath = tkFileDialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("json files","*.json"),("backup files","*.bk"),("all files","*.*")))
            if newFilePath:
                newFilePath = os.path.relpath(newFilePath)
                topicFilePath.delete(0, tk.END)
                topicFilePath.insert(tk.END, newFilePath)

        def __btn_load_topic():
            filepath = topicFilePath.get()
            if len(filepath) > 0:
                self.docManager.insertTopicFromFile(filepath, deleteAfterInsert=False)
        
        def __btn_load_topic_quick():
            topic = topicName.get()
            if len(topic) > 0:
                self.docManager.insertTopic(topicId=topic, name=topic)

        def __btn_choose_conn():
            newFilePath = tkFileDialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("json files","*.json"),("backup files","*.bk"),("all files","*.*")))
            if newFilePath:
                newFilePath = os.path.relpath(newFilePath)
                connectionFilePath.delete(0, tk.END)
                connectionFilePath.insert(tk.END, newFilePath)

        def __btn_load_conn():
            filepath = connectionFilePath.get()
            if len(filepath) > 0:
                self.docManager.addConnectionFromFile(filepath, deleteAfterInsert=False)

        def __btn_load_text():
            inputString = inputText.get("1.0",tk.END)

            try:
                obj = json.loads(inputString)
                if isinstance(obj, dict):
                    dicList = [obj]
                else:
                    dicList = obj
                for dic in dicList:
                    if "srcDocId" in dic:
                        self.docManager.addConnectionFromDic(dic)
                    elif "topicId" in dic:
                        self.docManager.insertTopicFromDic(dic)
                    else:
                        print("unknown input object ")
                        print(dic)


            except Exception as e:
                try:
                    print(inputString)
                    dicList = bibtexparser.loads(inputString).entries
                    print(dicList)
                    self.docManager.insertDocFromDictList(dicList)
                except Exception as e:
                    print("cannot interpret the input string")
                    print(e)
                    return



        # bib file
        bibFileLabel = tk.Label(loadFromFile_window, text="Documents (.bib)",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        bibFilePath = tk.Entry(loadFromFile_window, text="",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        bibFileChooser = tk.Button(loadFromFile_window, text="choose file", command=__btn_choose_docBib,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        bibFileLoad = tk.Button(loadFromFile_window, text="load", command=__btn_load_docBib,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        bibFileLabel.grid(row=rows, column=0, sticky="WE")
        bibFilePath.grid(row=rows, column=1, sticky="WE")
        bibFileChooser.grid(row=rows, column=2, sticky="WE")
        bibFileLoad.grid(row=rows, column=3, sticky="WE")
        rows += 1

        # topic json
        topicFileLabel = tk.Label(loadFromFile_window, text="Topics (.json)",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        topicFilePath = tk.Entry(loadFromFile_window, text="",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        topicFileChooser = tk.Button(loadFromFile_window, text="choose file", command=__btn_choose_topic,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        topicFileLoad = tk.Button(loadFromFile_window, text="Load", command=__btn_load_topic,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        topicFileLabel.grid(row=rows, column=0, sticky="WE")
        topicFilePath.grid(row=rows, column=1, sticky="WE")
        topicFileChooser.grid(row=rows, column=2, sticky="WE")
        topicFileLoad.grid(row=rows, column=3, sticky="WE")
        rows += 1

        # topic quick insert
        topicQuickLabel = tk.Label(loadFromFile_window, text="Topic Text",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        topicName = tk.Entry(loadFromFile_window, text="",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        topicAdd = tk.Button(loadFromFile_window, text="Load", command=__btn_load_topic_quick,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        topicQuickLabel.grid(row=rows, column=0, sticky="WE")
        topicName.grid(row=rows, column=1, sticky="WE")
        # topicFileChooser.grid(row=rows, column=2, sticky="WE")
        topicAdd.grid(row=rows, column=2, columnspan=2, sticky="WE")
        rows += 1

        # connection json
        connectionFileLabel = tk.Label(loadFromFile_window, text="Connections (.json)",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        connectionFilePath = tk.Entry(loadFromFile_window, text="",
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        connectionFileChooser = tk.Button(loadFromFile_window, text="choose file", command=__btn_choose_conn,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])
        connectionFileLoad = tk.Button(loadFromFile_window, text="Load", command=__btn_load_conn,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        connectionFileLabel.grid(row=rows, column=0, sticky="WE")
        connectionFilePath.grid(row=rows, column=1, sticky="WE")
        connectionFileChooser.grid(row=rows, column=2, sticky="WE")
        connectionFileLoad.grid(row=rows, column=3, sticky="WE")
        rows += 1

        # place for input
        inputText = tkst.ScrolledText(loadFromFile_window, height=4, wrap = tk.WORD,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"])
        inputTextLoad = tk.Button(loadFromFile_window, text="Load", command=__btn_load_text,
            font=self.themeParams["fontAndSize"],
            fg=self.themeParams["default"], bg=self.themeParams["background"], highlightbackground=self.themeParams["background"])

        inputText.grid(row=rows, column=0, columnspan=2, sticky="WESN")
        inputTextLoad.grid(row=rows, column=3, sticky="WE")
        rows += 1

        for row in range(rows-1):
            tk.Grid.rowconfigure(loadFromFile_window, row, weight=1)
        tk.Grid.rowconfigure(loadFromFile_window, rows-1, weight=15)

        tk.Grid.columnconfigure(loadFromFile_window, 0, weight=0.5)
        tk.Grid.columnconfigure(loadFromFile_window, 1, weight=3)
        tk.Grid.columnconfigure(loadFromFile_window, 2, weight=1)
        tk.Grid.columnconfigure(loadFromFile_window, 3, weight=1)

    def __build_GUI(self):
        def configure(event):
            if event.width > 700:
                self.windowsParam['GUI_WIDTH'] = event.width
            if event.height > 700:
                self.windowsParam['GUI_HEIGHT'] = event.height


        def on_closing():
            self.__refresh_presetInfo()
            self.destroy()


        self.title("Document Manager %s" % VERSION)
        self.windowsParam['GUI_WIDTH'] = self.winfo_screenwidth()
        self.windowsParam['GUI_HEIGHT'] = self.winfo_screenheight()
        self.geometry("%dx%d+%d+%d" % (
                    self.windowsParam['GUI_WIDTH'],
                    self.windowsParam['GUI_HEIGHT'],
                    self.winfo_screenwidth()/2 - self.windowsParam['GUI_WIDTH']//2,
                    self.winfo_screenheight()/2 - self.windowsParam['GUI_HEIGHT'] // 2))

        # bind resize event
        self.bind("<Configure>", configure)
        # bind close event
        self.protocol("WM_DELETE_WINDOW", on_closing)

        # initialize each frame
        self.__init_document_list_frame()
        self.__init_document_info_frame()

        # initialize menubar
        self.__menu()

        # layout frames
        self.__layout_frames()

        # show values
        self.__show_doc_list()



    def run(self):
        def on_closing():
            print(self.dbParams["exportWhenClose"])
            if self.dbParams["exportWhenClose"]:
                print("need export db")
                backupdir = self.dbParams["backupdir"]
                self.docManager.exportDocs(os.path.join(backupdir, "mybib.bib"))
                self.docManager.exportTopics(os.path.join(backupdir, "topic.json"))
                self.docManager.exportConnections(os.path.join(backupdir, "connection.json"))

            self.__refresh_presetInfo()
            self.destroy()

        self.__build_GUI()
        # add menu
        self.config(menu=self.menubar)
        self.protocol("WM_DELETE_WINDOW", on_closing)
        self.mainloop()


if __name__ == "__main__":
    docManagerGUI = DocManagerGUI()
    docManagerGUI.run()
