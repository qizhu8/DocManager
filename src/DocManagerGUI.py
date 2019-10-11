# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import json
import tkinter as tk
import tkinter.scrolledtext as tkst
from DocManager import DocManager

VERSION = "1.0.0"

class DocManagerGUI(tk.Tk, object):
    """
    docstring for DocManagerGUI.

    This class focuses mainly on the GUI, rather than the detail implementation.
    """

    def __init__(self):
        super(DocManagerGUI, self).__init__()

        # default config
        self.windowsParam = {"GUI_WIDTH": 1000, "GUI_HEIGHT": 1000}
        self.dbParams = {
            "username" : "root",
            "password" : "admin",
            "dbName" : "papers",
            "sqlDelTblsFilePath" : "src/dropTables.sql",
            "sqlInitFilePath" : "src/createTbls.sql",
            "bibfile" : "data/mybib.bib",
            "connfile" : "data/connections.json",
            "topicfile" : "data/topics.json"
        }
        self.__load_presetInfo()

        self.document_list_frame = None
        self.document_info_frame = None

        self.docManager = DocManager()
        try:
            self.docManager.initConn(self.dbParams["username"], self.dbParams["password"], self.dbParams["dbName"])
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

        else:
            self.__refresh_presetInfo()

    def __refresh_presetInfo(self):
        """save parameters to config file"""
        configFilePath = os.path.join('config.json')

        # parameters to pack
        configDic = {"WINDOWS": self.windowsParam, "DBParams": self.dbParams}

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


        """
        | Documents:  |
        | ----------- |
        | list of doc |
        """

        def __list_select(evt):
            item_id = self.document_list_ctl_dict['list'].curselection()
            if item_id:
                docId = self.document_list_ctl_dict['itemKey'][item_id[0]]
                print(docId, " is chosen")
                self.__show_doc_info(docId)
                self.__show_doc_hier(docId)

        # create each control and save them into a dict
        self.document_list_ctl_dict = {}

        self.document_list_ctl_dict['label'] = tk.Label(self.document_list_frame, text="Documents:")
        self.document_list_ctl_dict['label'].pack(fill=tk.BOTH)

        self.document_list_ctl_dict['list'] = tk.Listbox(self.document_list_frame)

        self.document_list_ctl_dict['list'].bind("<<ListboxSelect>>", __list_select)
        self.document_list_ctl_dict['list'].pack(fill=tk.BOTH, expand=1)

        self.document_list_ctl_dict['scrollbar'] = tk.Scrollbar(self.document_list_frame, orient="vertical")
        self.document_list_ctl_dict['scrollbar'].config(command=self.document_list_ctl_dict['list'].yview)
        self.document_list_ctl_dict['scrollbar'].pack(side="right", fill="y")
        self.document_list_ctl_dict['list'].config(yscrollcommand=self.document_list_ctl_dict['scrollbar'].set)

        self.document_list_ctl_dict['button'] = tk.Label(self.document_list_frame, text="Load from files")
        self.document_list_ctl_dict['button'].pack(fill=tk.BOTH)

        self.document_list_ctl_dict['itemKey'] = []


    def __show_doc_list(self):
        self.document_list_ctl_dict['itemKey'] = []
        self.document_list_ctl_dict['list'].delete(0, tk.END)
        for idx, record in enumerate(self.docManager.getAllDocs()):
            docId, title, type = record
            if type is "topic":
                descName = "topic - {title}".format(title=title)
            else:
                descName = title
            self.document_list_ctl_dict['list'].insert(idx, descName)
            self.document_list_ctl_dict['itemKey'].append(docId)


    """ frame of document detail """
    def __init_document_info_frame(self):
        if self.document_info_frame is not None:
            self.document_info_frame.pack_forget()
            self.document_info_frame.destroy()
        self.document_info_frame = tk.Frame(self)

        self.document_info_ctl_dict = {}

        def __ancList_select(evt):
            item_id = self.document_info_ctl_dict['ancList'].curselection()
            if item_id:
                docId = self.document_info_ctl_dict['ancList'].get(item_id)
                print(docId, " is chosen")
                self.__show_doc_info(docId)

        def __deceList_select(evt):
            item_id = self.document_info_ctl_dict['deceList'].curselection()
            if item_id:
                # docId = self.document_info_ctl_dict['deceList'].get(item_id)
                docId = self.document_info_ctl_dict['deceList'].get(item_id)
                print(docId, " is chosen")
                self.__show_doc_info(docId)

        def ancAdd_hit():
            pass

        def deceAdd_hit():
            pass

        # type
        self.document_info_ctl_dict['typeLabel'] = tk.Label(self.document_info_frame, text="type:")
        self.document_info_ctl_dict['typeEntry'] = tk.Entry(self.document_info_frame, show=None)

        self.document_info_ctl_dict['typeLabel'].grid(row=0, column=0)
        self.document_info_ctl_dict['typeEntry'].grid(row=0, column=1, sticky='w')

        # title
        self.document_info_ctl_dict['titleLabel'] = tk.Label(self.document_info_frame, text="title:")
        self.document_info_ctl_dict['titleEntry'] = tk.Entry(self.document_info_frame, show=None)

        self.document_info_ctl_dict['titleLabel'].grid(row=1, column=0)
        self.document_info_ctl_dict['titleEntry'].grid(row=1, column=1, sticky='w')

        # docId
        self.document_info_ctl_dict['docIdLabel'] = tk.Label(self.document_info_frame, text="id:")
        self.document_info_ctl_dict['docIdEntry'] = tk.Entry(self.document_info_frame, show=None)

        self.document_info_ctl_dict['docIdLabel'].grid(row=2, column=0)
        self.document_info_ctl_dict['docIdEntry'].grid(row=2, column=1, sticky='w')

        # description
        self.document_info_ctl_dict['descLabel'] = tk.Label(self.document_info_frame, text="description:")
        self.document_info_ctl_dict['descText'] = tkst.ScrolledText(self.document_info_frame, height=4, wrap = tk.WORD)

        self.document_info_ctl_dict['descLabel'].grid(row=3, column=0)
        self.document_info_ctl_dict['descText'].grid(row=3, column=1, sticky='w')

        # ancester
        self.document_info_ctl_dict['ancLabel'] = tk.Label(self.document_info_frame, text="ancesters:")
        self.document_info_ctl_dict['ancList'] = tk.Listbox(self.document_info_frame)
        self.document_info_ctl_dict['deceLabel'] = tk.Label(self.document_info_frame, text="followers:")
        self.document_info_ctl_dict['deceList'] = tk.Listbox(self.document_info_frame)
        self.document_info_ctl_dict['ancAddButton'] = tk.Button(self.document_info_frame, text="add", command=ancAdd_hit)
        self.document_info_ctl_dict['deceAddButton'] = tk.Button(self.document_info_frame, text="add", command=deceAdd_hit)

        self.document_info_ctl_dict['ancLabel'].grid(row=4, column=0, sticky='we')
        self.document_info_ctl_dict['deceLabel'].grid(row=4, column=1, sticky='we')
        self.document_info_ctl_dict['ancList'].grid(row=5, column=0, sticky='we')
        self.document_info_ctl_dict['deceList'].grid(row=5, column=1, sticky='we')
        self.document_info_ctl_dict['ancAddButton'].grid(row=6, column=0, sticky='we')
        self.document_info_ctl_dict['deceAddButton'].grid(row=6, column=1, sticky='we')

        self.document_info_ctl_dict['ancList'].bind("<<ListboxSelect>>", __ancList_select)
        self.document_info_ctl_dict['deceList'].bind("<<ListboxSelect>>", __deceList_select)


        # connection description
        self.document_info_ctl_dict['connLabel'] = tk.Label(self.document_info_frame, text="Connection Description:")
        self.document_info_ctl_dict['connText'] = tkst.ScrolledText(self.document_info_frame, height=4, wrap = tk.WORD)

        self.document_info_ctl_dict['connLabel'].grid(row=7, column=0)
        self.document_info_ctl_dict['connText'].grid(row=7, column=1, sticky='w')

        # save info
        self.document_info_ctl_dict['updateButton'] = tk.Button(self.document_info_frame, text="Update Doc Info", command=ancAdd_hit)
        self.document_info_ctl_dict['updateButton'].grid(row=8, column=0, sticky='w')



    """ control the sub-module layout """
    def __layout_frames(self):
        self.document_list_frame.config(width=self.windowsParam['GUI_WIDTH']*0.5)
        self.document_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.document_list_frame.pack_propagate(0)

        self.document_info_frame.config(width=self.windowsParam['GUI_WIDTH']*0.5)
        self.document_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.document_info_frame.pack_propagate(0)


    def __show_doc_info(self, docId):
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
                for idx, docInfo in enumerate(ancesDocsInfo):
                    docId, title, type = docInfo
                    self.document_info_ctl_dict['ancList'].insert(idx, docId)

            except Exception as e:
                print(e)

        if decenDocsInfo is None or len(decenDocsInfo) == 0:
            print("no decendants", decenDocsInfo)

            self.document_info_ctl_dict['deceList'].insert(0, "No Document")
        else:
            try:
                for idx, docInfo in enumerate(decenDocsInfo):
                    docId, title, type = docInfo
                    self.document_info_ctl_dict['deceList'].insert(idx, docId)

            except Exception as e:
                print(e)





    def __build_GUI(self):
        def configure(event):
            if event.width > 200 and event.height > 300:
                self.windowsParam['GUI_WIDTH'] = event.width
                self.windowsParam['GUI_HEIGHT'] = event.height


        def on_closing():
            self.__refresh_presetInfo()
            self.destroy()


        self.title("Document Manager %s" % VERSION)
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

        # layout frames
        self.__layout_frames()

        # show values
        self.__show_doc_list()



    def run(self):
        self.__build_GUI()
        self.mainloop()


if __name__ == "__main__":
    docManagerGUI = DocManagerGUI()
    docManagerGUI.run()
