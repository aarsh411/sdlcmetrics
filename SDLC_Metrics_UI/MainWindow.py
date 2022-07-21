import wx
import wx.grid
import threading
import datetime
import json
import os
from base64 import b64encode
from pip._vendor import requests
from SDLC_Metrics_UI.DeleteDialog import DeleteDialogBox
from VersionControlMetrics import CommitDataCollection
from SDLC_Metrics_UI import TaskBarFunctionalities, AppSettingData
from SDLC_Metrics_UI.AddRepoSettingsWindow import AddRepoSetting
from SDLC_Metrics_UI.EditRepoSettingsWindow import EditSetting
from wx.adv import Animation, AnimationCtrl

class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(800, 500))

        self.CreatePanel()
        self.tbIcon = TaskBarFunctionalities.CustomTaskBarIcon(self)
        self.SetIcon(wx.Icon("images/icon.png"))
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.Centre()
        self.Show()
        for processGIF in self.PList:
            processGIF.Hide()
        self.Fit()


# Frame Design
    def CreatePanel(self):

        self.panel = wx.Panel(self, wx.EXPAND)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = self.HBox1(self.panel)
        self.Grid1(self.panel)
        hbox3 = self.HBox3(self.panel)

        vbox.Add(hbox1)
        vbox.Add(self.grid, wx.EXPAND)
        # vbox.Add(hbox3)
        self.panel.SetSizer(vbox)

    def HBox1(self, parent):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.btnAddRepo = wx.Button(parent, -1, "Add New Repository(+)")
        hbox1.Add(self.btnAddRepo, 0, wx.ALIGN_RIGHT)
        self.btnAddRepo.Bind(wx.EVT_BUTTON, self.OnClickAddRepo)

        return hbox1

    def Grid1(self,parent):

        self.grid = wx.FlexGridSizer(cols=6, vgap=0, hgap=15)
        self.grid.SetFlexibleDirection(wx.HORIZONTAL)
        self.PList = []

        self.RepoSettings = ReadSettings()
        no_repo = len(self.RepoSettings)
       
        if no_repo > 0:
            self.grid.SetRows(no_repo)
            for setting in self.RepoSettings:

                    self.stRepo = wx.StaticText(parent, setting['id'], label="")
                    self.stRepo.SetLabel(setting['path'])
                    self.grid.Add(self.stRepo)

                    self.btnEdit = wx.Button(parent, setting['id'], "EDIT")
                    self.btnDelete = wx.Button(parent, setting['id'], "DELETE")

                    if setting['enableGitData'] == True :
                        self.btnSync = wx.Button(self.panel, setting['id'], "SYNC")
                        self.btnCollectData = wx.Button(parent, setting['id'], "COLLECT DATA")

                        self.btnSync.Bind(wx.EVT_BUTTON, self.OnClickedSync)
                        self.btnCollectData.Bind(wx.EVT_BUTTON, self.OnClickedCollectData)

                        self.grid.Add(self.btnCollectData)
                        self.grid.Add(self.btnSync)
                    else:
                        self.stEmpty1 = wx.StaticText(parent, setting['id'], label="")
                        self.grid.Add(self.stEmpty1)
                        self.stEmpty2 = wx.StaticText(parent, setting['id'], label="")
                        self.grid.Add(self.stEmpty2)

                    self.btnEdit.Bind(wx.EVT_BUTTON, self.OnClickedEdit)
                    self.grid.Add(self.btnEdit)
                    self.btnDelete.Bind(wx.EVT_BUTTON, self.OnClickedDelete)
                    self.grid.Add(self.btnDelete)

                    if setting['enableGitData'] == True:
                        self.gif = Animation('images/loading.gif')
                        self.loading = AnimationCtrl(parent, setting['id'] + 500, anim=self.gif)
                        self.loading.Play()
                        self.grid.Add(self.loading)
                        self.PList.append(self.loading)
                    else:
                        self.stEmpty3 = wx.StaticText(parent, setting['id'], label="")
                        self.grid.Add(self.stEmpty3)


    def HBox3(self, parent):
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.btnOK = wx.Button(parent, -1, "OK", pos=(306,350))
        hbox3.Add(self.btnOK)
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnClickedOK)

        self.btnCancel = wx.Button(parent, -1, "Cancel", pos=(406,350))
        hbox3.Add(self.btnCancel)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnClickedCancel)

        return hbox3


# METHODS
    def OnClickedCollectData(self, event):
        ID = event.GetEventObject().GetId()
        path =''
        for dict in self.RepoSettings:
            if dict['id'] == ID :
                path = dict['path']
                self.hexa = dict['LastCommitId']
        timestamp = str(datetime.datetime.now().timestamp())
        DataCollectionThread = threading.Thread(target=CommitDataCollection.collectData, args=(path, self, ID, self.hexa, timestamp), daemon=True)
        DataCollectionThread.start()


    def OnClickedSync(self, event):
        ID = event.GetEventObject().GetId()
        self.fd = wx.FileDialog(self, "Select Data File...",
                                        defaultDir = r"C:\Users\abhay.manvar\AppData\Roaming\SDLC_Metrics_UI",
                                        wildcard="Data files (*.json)|*.json",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) # | wx.FD_MULTIPLE
        self.fd.ShowModal()
        fileNames = self.fd.GetFilenames()
        files = self.fd.GetPaths()
        resp = requests.Response()
        for file in files:
            f = open(file, "r")
            dataFile = json.load(f)
            f.close()
            url = "http://10.12.41.119/api/gitdata"
            try:
                for commit in dataFile:
                    resp = requests.post(
                                url,
                                json = commit,
                                verify=False
                                )
            except requests.exceptions.SSLError:
                print('SSL Exception...')
                pass
            except requests.exceptions.ConnectionError:
                wx.MessageBox( "Failed to establish a connection." , "ERROR !", wx.OK | wx.ICON_ERROR)
                pass

            if resp.status_code == 201 :
                wx.MessageBox("Data successfuly uploaded. ", "Successfull", wx.OK)
                os.rename( file, os.path.splitext(file)[0]+ "_Processed.json")
            elif resp.status_code == 400 :
                wx.MessageBox( str(resp.status_code)+"  Bad Request... !" , "ERROR !", wx.OK | wx.ICON_ERROR)
                pass
            elif resp.status_code == 404 :
                wx.MessageBox( str(resp.status_code)+"  Not Found... !" , "ERROR !", wx.OK | wx.ICON_ERROR)
                pass
            elif resp.status_code == 500 :
                wx.MessageBox( str(resp.status_code)+"  Internal Server Error... !" , "ERROR !", wx.OK | wx.ICON_ERROR)
                pass

    def OnClickedEdit(self, event):
        ID = event.GetEventObject().GetId()
        editwindow = EditSetting(None,"Edit Settings", ID, self).ShowModal()

    def OnClickedDelete(self, event):
        Response = DeleteDialogBox(self, "WARNING !...").ShowModal()
        if Response == wx.ID_OK:
            ID = event.GetEventObject().GetId()
            Repo = {}
            for dict in self.RepoSettings:
                if dict['id'] == ID :
                    Repo = dict
            self.RepoSettings.remove(Repo)
            AppSettingData.WriteSettingData(self.RepoSettings)
            Refresh(self)


    def OnClickAddRepo(self, event):
        AddSettingWindow = AddRepoSetting(None, self).ShowModal()
        print(AddSettingWindow)

    def OnClickedOK(self, event):
        self.Hide()

    def OnClickedCancel(self, event):
        self.Hide()

# Title Bar operations
    def onClose(self, event):
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

    def onMinimize(self, event):
        if self.IsIconized():
            self.Hide()


#Threading
def CreateThread():
    print("Created")

    #Refresh
def Refresh(self):
    self.panel.Destroy()
    self.CreatePanel()
    self.panel.SetSize(800,500)
    for processGIF in self.PList:
        processGIF.Hide()
    self.Refresh()


# File i/o
def ReadSettings():
    return AppSettingData.ReadSettingData()

def WriteSettings(list):
    AppSettingData.AddSetting(list)


# Main Logic
app = wx.App(False)
obj = MainFrame(None, 'SDLC METRICS')

app.MainLoop()
