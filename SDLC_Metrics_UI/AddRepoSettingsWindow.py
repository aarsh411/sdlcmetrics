import wx
import git
from GitHooks.copyVirtualEnvironment import copyVirtualEnvironment
from SDLC_Metrics_UI import TaskBarFunctionalities,AppSettingData
from GitHooks import main


list = [1, '', False, False, "", False, " ", "-1"]

class AddRepoSetting(wx.Dialog):
    def __init__(self, parent, MainWin):
        super(AddRepoSetting, self).__init__(parent,title="Add New Repository...",size=(800, 500))
        self.RefMainWin = MainWin
        self.CreatePanel()

        self.tbIcon = TaskBarFunctionalities.CustomTaskBarIcon(self)
        self.SetIcon(wx.Icon("images/icon.png"))
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.Centre()
        self.Show()
        self.Fit()

    # Frame Design
    def CreatePanel(self):
        self.panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = self.HBox1(self.panel)
        hbox2 = self.HBox2(self.panel)
        hbox3 = self.HBox3(self.panel)
        hbox4 =self.HBox4(self.panel)
        hbox5 = self.HBox5(self.panel)

        vbox.Add(hbox1)
        vbox.Add(hbox5)
        vbox.Add(hbox4)
        vbox.Add(hbox3)
        vbox.Add(hbox2, wx.ALIGN_BOTTOM)
        self.panel.SetSizer(vbox)


    def HBox1(self, parent):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        l1 = wx.StaticText(parent, -1, "Choose Local Repo Path")
        hbox1.Add(l1, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

        self.dp = wx.DirPickerCtrl(parent,size=(650, 25))
        hbox1.Add(self.dp, 1, wx.ALIGN_RIGHT, 10)

        return hbox1

    def HBox2(self, parent):
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.btnOK = wx.Button(parent, wx.ID_OK, "OK")
        hbox2.Add(self.btnOK, 0, wx.ALIGN_CENTER)
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnClickedOK)

        self.btnCancel = wx.Button(parent, wx.ID_CANCEL, "Cancel")
        hbox2.Add(self.btnCancel, 0, wx.ALIGN_CENTER)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnClickedCancel)

        return hbox2

    def HBox3(self,parent):
        hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.rbox1 = wx.RadioBox(parent,12,label='Do You Want To Collect Git Data ?',
                                 pos = (10,35), choices = ['Yes','No'],majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        self.rbox1.SetSelection(0)
        return hbox3

    def HBox4(self,parent):
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)

        self.rbox2 = wx.RadioBox(parent, 13, label='Message Commit Policy', pos=(10,110),
                                 choices=['Yes', 'No'], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rbox2.Bind(wx.EVT_RADIOBOX, self.OnCheckgroup2)
        self.rbox2.SetSelection(0)
        self.OnCheckgroup2(event=None)
        return hbox4

    def HBox5(self, parent):

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        self.rbox3 = wx.RadioBox(parent, 14, label='Prevent Branch Commit Policy', pos=(10, 175),
                                 choices=['Yes', 'No'], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rbox3.Bind(wx.EVT_RADIOBOX, self.OnCheckgroup3)
        self.rbox3.SetSelection(1)

        return hbox5



    # METHODS

    def onClose(self, event):
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

    def OnClickedOK(self, event):
            global path, list
            path = self.dp.GetPath()

            RepoSettings = AppSettingData.ReadSettingData()
            flag = 0
            for dict in RepoSettings:
                if dict['path'] == path:
                    flag = 1

            try:
                 if path == "":
                     wx.MessageBox("Empty path is not valid !", "INVALID REPOSITORY", wx.OK | wx.ICON_ERROR)
                 elif flag == 1 :
                     wx.MessageBox("Repository is already exists !", "INVALID REPOSITORY", wx.OK | wx.ICON_ERROR)
                 else:
                     list[1] = path
                     _= git.Repo(path).git_dir

                     copyVirtualEnvironment()
                     main.removeHooks(path)

                     if self.rbox1.GetSelection() == 0:
                         list[2] = True

                     elif self.rbox1.GetSelection() == 1:
                         list[2] = False

                     if self.rbox2.GetSelection() == 0:
                         list[3] = True
                         list[4] = self.t2.GetValue()
                         main.prepareCommitMessageHook(path, self.t2.GetValue())
                     elif self.rbox2.GetSelection() == 1:
                         list[3] = False
                         list[4] = ''

                     if self.rbox3.GetSelection() == 0:
                         list[5] = True
                         list[6] = self.t4.GetValue()
                         main.preCommitHook(path, self.t4.GetValue())
                     elif self.rbox3.GetSelection() == 1:
                         list[5] = False
                         list[6] = ''

                     AppSettingData.AddSetting(list)
                     Refresh(self.RefMainWin)
                     self.Close()
                     self.Destroy()

            except git.exc.InvalidGitRepositoryError:
                msg = wx.MessageBox("Not a valid git Directory !", "INVALID REPOSITORY", wx.OK | wx.ICON_ERROR)



    def OnClickedCancel(self, event):
        self.Close()
        self.Destroy()


    def OnCheckgroup2(self, event):
        if self.rbox2.GetSelection() == 0 :
            self.t1 = wx.StaticText(self.panel, 4, "Please write your error message for commit here", pos=(230, 100))
            self.t2 = wx.TextCtrl(self.panel, 5, pos=(230, 130), size=(300, 25), name='txt1',value="ERROR! The commit message must be passed")

        elif self.rbox2.GetSelection()==1:
                self.t1.Destroy()
                self.t2.Destroy()
                delattr(self, 't1')
                delattr(self, 't2')


    def OnCheckgroup3(self, e):
        if self.rbox3.GetSelection()==0:
            self.t3= wx.StaticText(self.panel, 2, "Please enter in comma separated format ", pos=(230, 180))
            self.t4 = wx.TextCtrl(self.panel, pos=(230, 200), size=(300, 25))

        elif self.rbox3.GetSelection()==1:
                self.t3.Destroy()
                self.t4.Destroy()
                delattr(self,'t3')
                delattr(self, 't4')


def Refresh(self):
    self.panel.Destroy()
    self.CreatePanel()
    self.panel.SetSize(800,500)
    for processGIF in self.PList:
        processGIF.Hide()
    self.Refresh()