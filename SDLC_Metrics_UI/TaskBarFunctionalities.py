import wx
import wx.adv


class CustomTaskBarIcon(wx.adv.TaskBarIcon):

    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame

        img = wx.Image("images/icon.png", wx.BITMAP_TYPE_ANY)
        bmp = wx.Bitmap(img)
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(bmp)

        self.SetIcon(self.icon, "SDLC-Metrics")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN,self.OnTaskBarLeftClick)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN,self.OnTaskBarRightClick)
        
    def OnTaskBarActivate(self, event):
        pass

    def OnTaskBarClose(self, event):
        self.frame.Close()

    def OnTaskBarLeftClick(self, event):
        self.frame.Show()
        self.frame.Restore()

    def OnTaskBarRightClick(self,event):
        wx.adv.TaskBarIcon.CreatePopupMenu(self)

    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        i1=self.menu.Append(wx.NewId(), "Restore")
        self.Bind(wx.EVT_MENU, self.OnTaskBarLeftClick, i1)
        i2=self.menu.Append(wx.NewId(), "Exit")
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, i2)
        return self.menu

