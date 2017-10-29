import wx
import time

import analyse as m 
# Define the tab content as classes:
class tabGather(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.text = wx.StaticText(self, -1, "Please enter a #hashtag to search on Twitter", (45,20))
        
        self.hashtagTextBox=wx.TextCtrl(self, -1, pos=(40,50),size= (300,-1)) 
        
        self.button = wx.Button(self, id=wx.ID_ANY, label="Get Tweets", pos=(150,100))
        self.button.Bind(wx.EVT_BUTTON, self.onClick)
        
        self.workingText=wx.StaticText(self,-1,'Working on it...',((150,140)))
        self.workingText.SetForegroundColour((69,139,0))
        self.workingText.SetFont(wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL))

        self.doneText=wx.StaticText(self,-1,"Done!",((150,140)))
        self.doneText.SetForegroundColour((69,139,0))
        self.doneText.SetFont(wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL))


        self.errText=wx.StaticText(self,-1,'Please enter a valid hashtag',((100,140)))
        self.errText.SetForegroundColour((255,0,0))
        self.errText.SetFont(wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL))

        self.workingText.Hide()
        self.errText.Hide()
        self.doneText.Hide()

    def onClick(self, event):
        """
        This method is fired when its corresponding button is pressed
        """

        hashtag =  str(self.hashtagTextBox.GetValue())
        self.doneText.Hide()
        if hashtag is '':
        	self.errText.Show()

        else:
            self.doneText.Hide()
            self.errText.Hide()
            self.button.Disable()
            self.workingText.Show()
            wx.Yield()
            m.fillTweets(hashtag)
            self.hashtagTextBox.ChangeValue('')
            self.button.Enable()
            self.workingText.Hide()
            self.doneText.Show()
 
class tabCompare(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "Select a search key to compare", (45,20))
        
        search_keys = m.getSearchKeys()
        
        self.combo = wx.ComboBox(self,-1, "All",choices = search_keys,pos=(40,50),size= (300,-1),style=wx.CB_READONLY)
        self.button = wx.Button(self, id=wx.ID_ANY, label="Compare", pos=(150,100))
        self.button.Bind(wx.EVT_BUTTON, self.onClick)

        self.workingText=wx.StaticText(self,-1,'Working on it...',((150,140)))
        self.workingText.SetForegroundColour((69,139,0))
        self.workingText.SetFont(wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL))
        self.workingText.Hide()

        self.doneText=wx.StaticText(self,-1,"Done!",((150,140)))
        self.doneText.SetForegroundColour((69,139,0))
        self.doneText.SetFont(wx.Font(10, wx.DEFAULT, wx.ITALIC, wx.NORMAL))

    def onClick(self, event):
        self.searchkey =  str(self.combo.GetValue())
        self.doneText.Hide()
        self.workingText.Show()
        wx.Yield()
        m.compare(self.searchkey)
        self.workingText.Hide()
        self.doneText.Show()
 
 
class tabAbout(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This software has been developed by Semra Yildirim", (20,20))
 
 
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="TweetSentimental",size=(400,250), style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
 
        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)
 
        # Create the tab windows
        tab1 = tabGather(nb)
        tab2 = tabCompare(nb)
        tab3 = tabAbout(nb)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Get Tweets")
        nb.AddPage(tab2, "Compare")
        nb.AddPage(tab3, "About")

 
        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        
 
 
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Center()
    frame.Show()
    app.MainLoop()