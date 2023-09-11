import requests
import urllib
import urllib2
import socket

global globalIp 
global globalPreSharedKey
global globalSimpleIPport
# You probably should configure the TV, or your router so that the TV always receives the same IP address).
# The port number should (apparently) always be 80.
# Initial IP address of the TV, before configuration:
ipAddress='192.168.0.69'
globalIp='192.168.0.69'

# The TV's pre-shared key: 
preSharedKey = '1111'
globalPreSharedKey = "1111"
# The TV's simple IP port:
simpleIPport = '20060'
globalSimpleIPport = '20060'

#Pre-shared key can be adjusted on your TV by going to:
#Settings
#  Network
#    Home network setup
#      IP Address Control
#       Authentication
#          Normal & Preshared Key
#          Preshared Key
#            1111 <- just choose one>
#          Simple ipAddress Control
#            On

eg.RegisterPlugin(
    name = "Sony TV Network Remote Plugin",
    author = "Toby Gerenger, paseant, blaher, MarkerB", 
    version = "0.1.0",
    kind = "external",
    createMacrosOnAdd = True,
    url = "https://web.archive.org/web/20210228003319/http://www.eventghost.net/forum/viewtopic.php?f=9&t=6067",
    descripAddresstion = "This plugin connects to the network control interface for certain Sony TVs.  The included codes are for a Sony Bravia 2015 model: KDL65W850C. Reworked by MarkerB, who added REST and Simple IP control."
)

class SonyTVNetworkPlugin(eg.PluginBase):
    def __init__(self):
        group1 = self.AddGroup("RemoteControl","Send commands as if pushing buttons on the remote control, plus Simple IP commands.")
        group1.AddActionsFromList(REMOTE_ACTIONS, TVRemoteAction)
        self.AddAction(SendCommand)
        self.AddAction(SendREST)
        self.AddAction(SendSimpleIP)
        globalIp = ipAddress
        globalPreSharedKey = preSharedKey
        globalSimpleIPport = simpleIPport

    def __start__(self, ipAddress, preSharedKey, simpleIPport):
        global globalIp
        global globalPreSharedKey
        global globalSimpleIPport
        self.ipAddress = ipAddress
        self.preSharedKey = preSharedKey
        self.simpleIPport = simpleIPport
        self.globalIp = globalIp
        self.globalPreSharedKey = globalPreSharedKey
        self.globalSimpleIPport = globalSimpleIPport
        
        globalIp = ipAddress
        globalPreSharedKey = preSharedKey
        globalSimpleIPport = simpleIPport
        print "Sony TV's IP set to:" , globalIp
        print "Sony TV's pre-shared key set to:", globalPreSharedKey
        print "Sony TV's Simple IP Control Port set to:", globalSimpleIPport

    def __stop__(self):
        pass

    def Configure(self, ipAddress="192.168.0.69", preSharedKey="1111", simpleIPport="20060"):
        global globalIp
        global globalPreSharedKey
        global globalSimpleIPport

        panel = eg.ConfigPanel()
        textControl = wx.TextCtrl(panel, -1, ipAddress)
        textControl2 = wx.TextCtrl(panel, -1, preSharedKey)
        textControl3 = wx.TextCtrl(panel, -1, simpleIPport)
        
        panel.sizer.Add(wx.StaticText(panel, -1, "TV's IP Address:"))
        panel.sizer.Add(textControl)
        panel.sizer.Add(wx.StaticText(panel, -1, "TV's Pre-shared Key:"))
        panel.sizer.Add(textControl2)
        panel.sizer.Add(wx.StaticText(panel, -1, "TV's Simple IP Port:"))
        panel.sizer.Add(textControl3)
        while panel.Affirmed():
            panel.SetResult(textControl.GetValue(), textControl2.GetValue(), textControl3.GetValue())
            globalIp = ipAddress
            globalPreSharedKey = preSharedKey
            globalSimpleIPport = simpleIPport

class TVRemoteAction(eg.ActionClass):
    def __call__(self):
        SendIRCC(self.value)

class SendCommand(eg.ActionBase):
    name = "Send IRCCCommand"
    descripAddresstion = "Sends an IRCC code to the TV."

    def __call__(self, commandString):
        SendIRCC(commandString)

    def Configure(self, commandString=""):
        panel = eg.ConfigPanel()
        textControl3 = wx.TextCtrl(panel, -1, commandString)
        panel.sizer.Add(textControl3, 1, wx.EXPAND)
        while panel.Affirmed():
            panel.SetResult(textControl3.GetValue())

class SendREST(eg.ActionBase):
    name = "Send REST Command"
    descripAddresstion = "Sends an REST command to the TV."

    def __call__(self, commandString):
        self.SendREST_low(commandString)

    def Configure(self, commandString="audio {}"):
        panel = eg.ConfigPanel()
        textControl3 = wx.TextCtrl(panel, -1, commandString)
        panel.sizer.Add(wx.StaticText(panel, -1, "REST service string (system,audio,etc) + a space + full JSON REST Command on a single line\nSee https://pro-bravia.sony.net/develop/integrate/rest-api/spec/index.html"))
        panel.sizer.Add(textControl3, 1, wx.EXPAND)
        while panel.Affirmed():
            # panel.SetResult(textControl2.GetValue())
            panel.SetResult(textControl3.GetValue())

    def SendREST_low(self, commandString):  # command is a JSON string
        global globalIp
        global globalPreSharedKey
        
        commandString = commandString.strip().split(' ',1)  # split command string into service string and JSON command, only on first space
        # print("commandString.split() length = ", len(commandString))
        # print("commandString.split() = ", commandString)
        service = commandString[0]                          # get service string
        commandString = commandString[1]                    # get JSON command

        headers = {
      'X-Auth-psk': globalPreSharedKey,
      'User-Agent': 'TVSideView/2.0.1 CFNetwork/672.0.8 Darwin/14.0.0',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': '*/*',
            'Accept-Encoding': 'gzipAddress, deflate',
            'Host': globalIp,
            'Connection': 'close',}

        url = 'http://' + globalIp + '/sony/' + service
        # print("url = "+url)
        # print("Open REST with strings = "+commandString)
        # print("Headers=", headers)
        # print("globalPreSharedKey=",globalPreSharedKey)
        try:
            req = requests.post(url, data=commandString, headers=headers)  # data=urllib.quote_plus(commandString) doesn't work for some reason (too escaped?), so make sure commandString is already escaped
            print("REST result", req)
        except Exception as e:
            print("Generic exception in SendREST.  Is the TV on?")

def SendIRCC(commandString):
    global globalIp
    global globalPreSharedKey
    ConnectionStrings = SOAPStrings
    headers = {
  'X-Auth-psk': globalPreSharedKey,
  'User-Agent': 'TVSideView/2.0.1 CFNetwork/672.0.8 Darwin/14.0.0',
        'Content-Type': 'text/xml; charset=UTF-8',
        'SOAPACTION': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzipAddress, deflate',
        'Host': globalIp,
        'Connection': 'close',}

    try:
        conn=urllib2.Request('http://' + globalIp + '/sony/IRCC', ConnectionStrings.contentStart + commandString + ConnectionStrings.contentEnd, headers)
        # print("Open to open with strings = "+ConnectionStrings.contentStart+commandString+ConnectionStrings.contentEnd)
        # print("Headers=", headers)
        # print("globalPreSharedKey=",globalPreSharedKey)
        urllib2.urlopen(conn, timeout=0.5)
    except Exception as e:
        print("Generic exception in SendIRCC.  Is the TV on?")

# https://pro-bravia.sony.net/develop/integrate/rest-api/spec/service/audio/v1_1/setSoundSettings/index.html
#{
#    "method": "setSoundSettings",
#    "id": 5,
#    "params": [{"settings": [{
#        "value": "audioSystem",
#        "target": "outputTerminal"
#    }]}],
#    "version": "1.1"
# }

# {"method": "setSoundSettings", "id": 5, "params": [{"settings": [{ "value": "audioSystem", "target": "outputTerminal" }]}], "version": "1.1"}


class SendSimpleIP(eg.ActionBase):
    name = "Send Simple IP Command"
    descripAddresstion = "Sends a Simple IP code to the TV."

    def __call__(self, commandString):
        self.SendSimpleIP_low(commandString)
#         global globalIp
#         global globalSimpleIPport
# 
#         s = socket.socket()
#         s.settimeout(2)
#         s.connect((globalIp, globalSimpleIPport))
#         # str = "*SCPMUT0000000000000000\n"
#         str = commandString+"\n"
#         s.send(str.encode());
#         s.close()

    def Configure(self, commandString=""):
        panel = eg.ConfigPanel()
        textControl3 = wx.TextCtrl(panel, -1, commandString)
        panel.sizer.Add(textControl3, 1, wx.EXPAND)
        while panel.Affirmed():
            panel.SetResult(textControl3.GetValue())
        
    def SendSimpleIP_low(self, commandString):
        global globalIp
        global globalSimpleIPport

        s = socket.socket()
        s.settimeout(2)
        s.connect((globalIp, int(globalSimpleIPport)))
        # str = "*SCPMUT0000000000000000\n"
        str = commandString+"\n"
        s.send(str.encode());
        s.close()
        print("Sent Simple IP command")

class SOAPStrings:
    contentStart = """<?xml version="1.0"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
        <u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">
        <IRCCCode>"""

    contentEnd = """</IRCCCode>
        </u:X_SendIRCC>
        </s:Body>
        </s:Envelope>"""
    
# The action list below consists of the following structure:
# ("class", "Command Name", "Command DescripAddresstion", "parameter"),
REMOTE_ACTIONS = (   
    ("Num1","Num1","Num1","AAAAAQAAAAEAAAAAAw=="),
    ("Num2","Num2","Num2","AAAAAQAAAAEAAAABAw=="),
    ("Num3","Num3","Num3","AAAAAQAAAAEAAAACAw=="),
    ("Num4","Num4","Num4","AAAAAQAAAAEAAAADAw=="),
    ("Num5","Num5","Num5","AAAAAQAAAAEAAAAEAw=="),
    ("Num6","Num6","Num6","AAAAAQAAAAEAAAAFAw=="),
    ("Num7","Num7","Num7","AAAAAQAAAAEAAAAGAw=="),
    ("Num8","Num8","Num8","AAAAAQAAAAEAAAAHAw=="),
    ("Num9","Num9","Num9","AAAAAQAAAAEAAAAIAw=="),
    ("Num0","Num0","Num0","AAAAAQAAAAEAAAAJAw=="),
    ("Num11","Num11","Num11","AAAAAQAAAAEAAAAKAw=="),
    ("Num12","Num12","Num12","AAAAAQAAAAEAAAALAw=="),
    ("Enter","Enter","Enter","AAAAAQAAAAEAAAALAw=="),
    ("GGuide","GGuide","GGuide","AAAAAQAAAAEAAAAOAw=="),
    ("ChannelUp","ChannelUp","ChannelUp","AAAAAQAAAAEAAAAQAw=="),
    ("ChannelDown","ChannelDown","ChannelDown","AAAAAQAAAAEAAAARAw=="),
    ("VolumeUp","VolumeUp","VolumeUp","AAAAAQAAAAEAAAASAw=="),
    ("VolumeDown","VolumeDown","VolumeDown","AAAAAQAAAAEAAAATAw=="),
    ("Mute","Mute","Mute","AAAAAQAAAAEAAAAUAw=="),
    ("TvPower","TvPower","TvPower","AAAAAQAAAAEAAAAVAw=="),
    ("Audio","Audio","Audio","AAAAAQAAAAEAAAAXAw=="),
    ("MediaAudioTrack","MediaAudioTrack","MediaAudioTrack","AAAAAQAAAAEAAAAXAw=="),
    ("Tv","Tv","Tv","AAAAAQAAAAEAAAAkAw=="),
    ("Input","Input","Input","AAAAAQAAAAEAAAAlAw=="),
    ("TvInput","TvInput","TvInput","AAAAAQAAAAEAAAAlAw=="),
    ("TvAntennaCable","TvAntennaCable","TvAntennaCable","AAAAAQAAAAEAAAAqAw=="),
    ("WakeUp","WakeUp","WakeUp","AAAAAQAAAAEAAAAuAw=="),
    ("PowerOff","PowerOff","PowerOff","AAAAAQAAAAEAAAAvAw=="),
    ("Sleep","Sleep","Sleep","AAAAAQAAAAEAAAAvAw=="),
    ("Right","Right","Right","AAAAAQAAAAEAAAAzAw=="),
    ("Left","Left","Left","AAAAAQAAAAEAAAA0Aw=="),
    ("SleepTimer","SleepTimer","SleepTimer","AAAAAQAAAAEAAAA2Aw=="),
    ("Analog2","Analog2","Analog2","AAAAAQAAAAEAAAA4Aw=="),
    ("TvAnalog","TvAnalog","TvAnalog","AAAAAQAAAAEAAAA4Aw=="),
    ("Display","Display","Display","AAAAAQAAAAEAAAA6Aw=="),
    ("Jump","Jump","Jump","AAAAAQAAAAEAAAA7Aw=="),
    ("PicOff","PicOff","PicOff","AAAAAQAAAAEAAAA+Aw=="),
    ("PictureOff","PictureOff","PictureOff","AAAAAQAAAAEAAAA+Aw=="),
    ("Teletext","Teletext","Teletext","AAAAAQAAAAEAAAA\/Aw=="),
    ("Video1","Video1","Video1","AAAAAQAAAAEAAABAAw=="),
    ("Video2","Video2","Video2","AAAAAQAAAAEAAABBAw=="),
    ("AnalogRgb1","AnalogRgb1","AnalogRgb1","AAAAAQAAAAEAAABDAw=="),
    ("Home","Home","Home","AAAAAQAAAAEAAABgAw=="),
    ("Exit","Exit","Exit","AAAAAQAAAAEAAABjAw=="),
    ("PictureMode","PictureMode","PictureMode","AAAAAQAAAAEAAABkAw=="),
    ("Confirm","Confirm","Confirm","AAAAAQAAAAEAAABlAw=="),
    ("Up","Up","Up","AAAAAQAAAAEAAAB0Aw=="),
    ("Down","Down","Down","AAAAAQAAAAEAAAB1Aw=="),
    ("ClosedCaption","ClosedCaption","ClosedCaption","AAAAAgAAAKQAAAAQAw=="),
    ("Component1","Component1","Component1","AAAAAgAAAKQAAAA2Aw=="),
    ("Component2","Component2","Component2","AAAAAgAAAKQAAAA3Aw=="),
    ("Wide","Wide","Wide","AAAAAgAAAKQAAAA9Aw=="),
    ("EPG","EPG","EPG","AAAAAgAAAKQAAABbAw=="),
    ("PAP","PAP","PAP","AAAAAgAAAKQAAAB3Aw=="),
    ("TenKey","TenKey","TenKey","AAAAAgAAAJcAAAAMAw=="),
    ("BSCS","BSCS","BSCS","AAAAAgAAAJcAAAAQAw=="),
    ("Ddata","Ddata","Ddata","AAAAAgAAAJcAAAAVAw=="),
    ("Stop","Stop","Stop","AAAAAgAAAJcAAAAYAw=="),
    ("Pause","Pause","Pause","AAAAAgAAAJcAAAAZAw=="),
    ("Play","Play","Play","AAAAAgAAAJcAAAAaAw=="),
    ("Rewind","Rewind","Rewind","AAAAAgAAAJcAAAAbAw=="),
    ("Forward","Forward","Forward","AAAAAgAAAJcAAAAcAw=="),
    ("DOT","DOT","DOT","AAAAAgAAAJcAAAAdAw=="),
    ("Rec","Rec","Rec","AAAAAgAAAJcAAAAgAw=="),
    ("Return","Return","Return","AAAAAgAAAJcAAAAjAw=="),
    ("Blue","Blue","Blue","AAAAAgAAAJcAAAAkAw=="),
    ("Red","Red","Red","AAAAAgAAAJcAAAAlAw=="),
    ("Green","Green","Green","AAAAAgAAAJcAAAAmAw=="),
    ("Yellow","Yellow","Yellow","AAAAAgAAAJcAAAAnAw=="),
    ("SubTitle","SubTitle","SubTitle","AAAAAgAAAJcAAAAoAw=="),
    ("CS","CS","CS","AAAAAgAAAJcAAAArAw=="),
    ("BS","BS","BS","AAAAAgAAAJcAAAAsAw=="),
    ("Digital","Digital","Digital","AAAAAgAAAJcAAAAyAw=="),
    ("Options","Options","Options","AAAAAgAAAJcAAAA2Aw=="),
    ("Media","Media","Media","AAAAAgAAAJcAAAA4Aw=="),
    ("Prev","Prev","Prev","AAAAAgAAAJcAAAA8Aw=="),
    ("Next","Next","Next","AAAAAgAAAJcAAAA9Aw=="),
    ("DpadCenter","DpadCenter","DpadCenter","AAAAAgAAAJcAAABKAw=="),
    ("CursorUp","CursorUp","CursorUp","AAAAAgAAAJcAAABPAw=="),
    ("CursorDown","CursorDown","CursorDown","AAAAAgAAAJcAAABQAw=="),
    ("CursorLeft","CursorLeft","CursorLeft","AAAAAgAAAJcAAABNAw=="),
    ("CursorRight","CursorRight","CursorRight","AAAAAgAAAJcAAABOAw=="),
    ("ShopRemoteControlForcedDynamic","ShopRemoteControlForcedDynamic","ShopRemoteControlForcedDynamic","AAAAAgAAAJcAAABqAw=="),
    ("FlashPlus","FlashPlus","FlashPlus","AAAAAgAAAJcAAAB4Aw=="),
    ("FlashMinus","FlashMinus","FlashMinus","AAAAAgAAAJcAAAB5Aw=="),
    ("AudioQualityMode","AudioQualityMode","AudioQualityMode","AAAAAgAAAJcAAAB7Aw=="),
    ("DemoMode","DemoMode","DemoMode","AAAAAgAAAJcAAAB8Aw=="),
    ("Analog","Analog","Analog","AAAAAgAAAHcAAAANAw=="),
    ("Mode3D","Mode3D","Mode3D","AAAAAgAAAHcAAABNAw=="),
    ("DigitalToggle","DigitalToggle","DigitalToggle","AAAAAgAAAHcAAABSAw=="),
    ("DemoSurround","DemoSurround","DemoSurround","AAAAAgAAAHcAAAB7Aw=="),
    ("*AD","*AD","*AD","AAAAAgAAABoAAAA7Aw=="),
    ("AudioMixUp","AudioMixUp","AudioMixUp","AAAAAgAAABoAAAA8Aw=="),
    ("AudioMixDown","AudioMixDown","AudioMixDown","AAAAAgAAABoAAAA9Aw=="),
    ("Tv_Radio","Tv_Radio","Tv_Radio","AAAAAgAAABoAAABXAw=="),
    ("SyncMenu","SyncMenu","SyncMenu","AAAAAgAAABoAAABYAw=="),
    ("Hdmi1","Hdmi1","Hdmi1","AAAAAgAAABoAAABaAw=="),
    ("Hdmi2","Hdmi2","Hdmi2","AAAAAgAAABoAAABbAw=="),
    ("Hdmi3","Hdmi3","Hdmi3","AAAAAgAAABoAAABcAw=="),
    ("Hdmi4","Hdmi4","Hdmi4","AAAAAgAAABoAAABdAw=="),
    ("TopMenu","TopMenu","TopMenu","AAAAAgAAABoAAABgAw=="),
    ("PopUpMenu","PopUpMenu","PopUpMenu","AAAAAgAAABoAAABhAw=="),
    ("OneTouchTimeRec","OneTouchTimeRec","OneTouchTimeRec","AAAAAgAAABoAAABkAw=="),
    ("OneTouchView","OneTouchView","OneTouchView","AAAAAgAAABoAAABlAw=="),
    ("DUX","DUX","DUX","AAAAAgAAABoAAABzAw=="),
    ("FootballMode","FootballMode","FootballMode","AAAAAgAAABoAAAB2Aw=="),
    ("iManual","iManual","iManual","AAAAAgAAABoAAAB7Aw=="),
    ("Netflix","Netflix","Netflix","AAAAAgAAABoAAAB8Aw=="),
    ("Assists","Assists","Assists","AAAAAgAAAMQAAAA7Aw=="),
    ("ActionMenu","ActionMenu","ActionMenu","AAAAAgAAAMQAAABLAw=="),
    ("Help","Help","Help","AAAAAgAAAMQAAABNAw=="),
    ("TvSatellite","TvSatellite","TvSatellite","AAAAAgAAAMQAAABOAw=="),
    ("WirelessSubwoofer","WirelessSubwoofer","WirelessSubwoofer","AAAAAgAAAMQAAAB+Aw=="),
)