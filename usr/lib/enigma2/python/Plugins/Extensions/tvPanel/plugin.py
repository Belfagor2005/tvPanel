#"****************************************"
#"*        coded by Lululla              *"
#"*             skin by MMark            *"
#"*             19/10/2020               *"
#"****************************************"
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.HTMLComponent import *
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ProgressBar import ProgressBar
from Components.SelectionList import SelectionList
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from Components.Sources.Source import Source
from Components.config import *
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import *
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_SKIN_IMAGE, resolveFilename, SCOPE_PLUGINS, fileExists, copyfile, SCOPE_LANGUAGE, pathExists
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG, loadPic
from enigma import eListbox, eTimer, eListboxPythonMultiContent, eConsoleAppContainer, addFont, gFont
from os import path, listdir, remove, mkdir, access, X_OK, chmod
from twisted.web.client import downloadPage, getPage
from xml.dom import Node, minidom
import base64
import os, re, sys
import shutil
import ssl
import socket
import glob
from Lcn import *

currversion      = '1.9.1'

global skin_path, mmkpicon, isDreamOS, set
headers        = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }

PY3 = sys.version_info.major >= 3

if PY3:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    from urllib.request import urlretrieve
else:
    from urllib2 import urlopen, Request, URLError
    from urllib import urlretrieve

set = 0
isDreamOS = False
try:
        from enigma import eMediaDatabase
        isDreamOS = True
except:
        isDreamOS = False

try:
        from enigma import eDVBDB
except ImportError:
        eDVBDB = None

try:
        import zipfile
except:
        pass
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    
def checkStr(txt):
    # convert variable to type str both in Python 2 and 3
    if PY3:
        # Python 3
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        #Python 2
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')
    return txt

def checkInternet():
        try:
            response = checkStr(urlopen("http://google.com", None, 5))
            # response = urlopen("http://google.com", None, 5)
            response.close()
        except HTTPError:
                return False
        except URLError:
                return False
        except socket.timeout:
                return False
        else:
                return True

def freespace():
    try:
        diskSpace = os.statvfs('/')
        capacity = float(diskSpace.f_bsize * diskSpace.f_blocks)
        available = float(diskSpace.f_bsize * diskSpace.f_bavail)
        fspace = round(float(available / 1048576.0), 2)
        tspace = round(float(capacity / 1048576.0), 1)
        spacestr = 'Free space(' + str(fspace) + 'MB) Total space(' + str(tspace) + 'MB)'
        return spacestr
    except:
        return ''

def FreeDev(dev):
        statdev = os.statvfs(dev)
        space = statdev.f_bavail * statdev.f_frsize / 1024
        print('[Flash] Free space on %s = %i kilobytes' % (dev, space))
        return space

def ReloadBouquet():
        print('\n----Reloading bouquets----')
        if eDVBDB:
                eDVBDB.getInstance().reloadBouquets()
                print('bouquets reloaded...')
        else:
                os.system('wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &')
                print('bouquets reloaded...')

def resettings():
        if set == 1:
                terrestrial_rest()
                os.system("wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &")

def deletetmp():
        os.system('rm -rf /tmp/unzipped;rm -f /tmp/*.ipk;rm -f /tmp/*.tar;rm -f /tmp/*.zip;rm -f /tmp/*.tar.gz;rm -f /tmp/*.tar.bz2;rm -f /tmp/*.tar.tbz2;rm -f /tmp/*.tar.tbz')
        return

def mountipkpth():
    ipkpth = []
    if os.path.isfile('/proc/mounts'):
            for line in open('/proc/mounts'):
                    if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                            drive = line.split()[1].replace('\\040', ' ') + '/'
                            if not drive in ipkpth:
                                      ipkpth.append(drive)
    ipkpth.append('/tmp')
    return ipkpth

#======================================================config
config.plugins.tvPanel = ConfigSubsection()
config.plugins.tvPanel.strtext = ConfigYesNo(default=True)
config.plugins.tvPanel.mmkpicon = ConfigDirectory(default='/media/hdd/picon/')
# config.plugins.tvPanel.mmkpiconform = ConfigSelection(default = "220x132",choices = [("all", _("All Picons")),("oth", _("Other")),("500x300", _("500x300")), ("417x250", _("417x250")), ("330x198", _("330x198")), ("300x130", _("300x130")), ("220x132", _("220x132")), ("130x80", _("130x80")), ("100x60", _("100x60")), ("50x30", _("50x30"))])
config.plugins.tvPanel.strtmain = ConfigYesNo(default=True)
config.plugins.tvPanel.strtst = ConfigYesNo(default=False)
config.plugins.tvPanel.ipkpth = ConfigSelection(default = "/tmp",choices = mountipkpth())
config.plugins.tvPanel.autoupd = ConfigYesNo(default=False)

pblk             = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT11Yzd1eHBiMGQzaTg4JmNvbnRlbnRfdHlwZT1mb2xkZXJzJmNodW5rX3NpemU9MTAwMCZyZXNwb25zZV9mb3JtYXQ9anNvbg=='
ptrs             = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT15Mms1Nmd4ZmRyb2FtJmNvbnRlbnRfdHlwZT1mb2xkZXJzJmNodW5rX3NpemU9MTAwMCZyZXNwb25zZV9mb3JtYXQ9anNvbg=='
host_trs         = base64.b64decode(ptrs)
host_blk         = base64.b64decode(pblk)
HD               = getDesktop(0).size()
plugin_path      = os.path.dirname(sys.modules[__name__].__file__)
skin_path        = plugin_path
ico_path         = plugin_path + '/logo.png'
ico1_path        = plugin_path + '/res/pics/plugins.png'
ico2_path        = plugin_path + '/res/pics/plugin.png'
ico3_path        = plugin_path + '/res/pics/setting.png'
pngx             = ico1_path
pngl             = ico2_path
pngs             = ico3_path
no_cover         = plugin_path + '/no_coverArt.png'
mmkpicon         = config.plugins.tvPanel.mmkpicon.value.strip()
os.system('rm -fr ' + plugin_path + '/temp/*')

if mmkpicon.endswith('/'):
        mmkpicon = mmkpicon[:-1]
if not os.path.exists(mmkpicon):
    try:
            os.makedirs(mmkpicon)
    except OSError as e:
            print(('Error creating directory %s:\n%s') % (mmkpicon, str(e)))
print('************************************************************path Picons: ', mmkpicon)

data_upd        = 'aHR0cDovL2NvcnZvbmUuYWx0ZXJ2aXN0YS5vcmcvdHZQYW5lbC8='
upd_path        = base64.b64decode(data_upd)
data_xml        = 'aHR0cDovL3BhdGJ1d2ViLmNvbS94bWwv'
xml_path        = base64.b64decode(data_xml)

if HD.width() > 1280:
    if isDreamOS:
            skin_path = plugin_path + '/res/skins/fhd/dreamOs/'
    else:
            skin_path = plugin_path + '/res/skins/fhd/'
else:
    if isDreamOS:
            skin_path = plugin_path + '/res/skins/hd/dreamOs/'
    else:
            skin_path = plugin_path + '/res/skins/hd/'

# class logoStrt(Screen):
        # skin = """
        # <screen name = "logoStrt" position = "center,center" size = "600,571" flags = "wfNoBorder">
        # <ePixmap position = "0,0" size = "600,571" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvPanel/res/pics/tv_hd.png" />
        # <eLabel position = "0,496" size = "600,35" text="by Lululla" foregroundColor="yellow" font = "Regular;36" halign = "center" transparent = "1" zPosition = "10" />
        # </screen> """
        # def __init__(self, session):
                # self.session = session
                # Screen.__init__(self, session)
                # self['actions'] = ActionMap(['SetupActions'], {'ok': self.disappear,
                # 'cancel': self.disappear}, -1)
                # self.timer = eTimer()
                # self.timer.start(100, 1)
                # if isDreamOS:
                        # self.timer_conn = self.timer.timeout.connect(self.disappear)
                # else:
                        # self.timer.callback.append(self.disappear)

        # def disappear(self):
                # self.session.openWithCallback(self.close, Hometv)

Panel_list = [
 _('DEBIAN'),
 _('SETTINGS DAILY'),
 _('PICONS'),
 _('KODILITE BY PCD'),
 _('DEPENDENCIES'),
 _('DRIVERS'),
 _('PLUGIN BACKUP'),
 _('PLUGIN EPG'),
 _('PLUGIN EMULATORS CAMS'),
 _('PLUGIN KODI'),
 _('PLUGIN MULTIBOOT'),
 _('PLUGIN MULTIMEDIA'),
 _('PLUGIN PICONS'),
 _('PLUGIN PPANEL'),
 _('PLUGIN SETTINGS PANEL'),
 _('PLUGIN SKINS'),
 _('PLUGIN SPORT'),
 _('PLUGIN UTILITY'),
 _('PLUGIN WEATHER')]


Panel_list2 = [
 ('UPDATE SATELLITES.XML'),
 ('UPDATE TERRESTRIAL.XML'),
 ('SETTINGS CIEFP'),
 ('SETTINGS COLOMBO'),
 ('SETTINGS BI58'),
 ('SETTINGS MANUTEK'),
 ('SETTINGS MILENKA61'),
 ('SETTINGS MORPHEUS'),
 ('SETTINGS PREDRAG'),
 ('SETTINGS VHANNIBAL')
 ]

class tvList(MenuList):
        def __init__(self, list):
                MenuList.__init__(self, list, False, eListboxPythonMultiContent)
                self.l.setFont(0, gFont('Regular', 20))
                self.l.setFont(1, gFont('Regular', 22))
                self.l.setFont(2, gFont('Regular', 24))
                self.l.setFont(3, gFont('Regular', 26))
                self.l.setFont(4, gFont('Regular', 28))
                self.l.setFont(5, gFont('Regular', 30))
                self.l.setFont(6, gFont('Regular', 32))
                self.l.setFont(7, gFont('Regular', 34))
                self.l.setFont(8, gFont('Regular', 36))
                self.l.setFont(9, gFont('Regular', 40))
                if HD.width() > 1280:
                        self.l.setItemHeight(50)
                else:
                        self.l.setItemHeight(40)

def OnclearMem():
        try:
                os.system("sync")
                os.system("echo 1 > /proc/sys/vm/drop_caches")
                os.system("echo 2 > /proc/sys/vm/drop_caches")
                os.system("echo 3 > /proc/sys/vm/drop_caches")
        except:
                pass

def menuListEntry(name, idx):
        res = [name]
        if HD.width() > 1280:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngl)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))#
        else:

                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(pngl)))
                res.append(MultiContentEntryText(pos=(60, 5), size=(1000, 50), font=1, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))# | RT_VALIGN_CENTER
        return res

def DailyListEntry(name, idx):
        res = [name]
        if HD.width() > 1280:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngs)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))#
        else:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(pngs)))
                res.append(MultiContentEntryText(pos=(60, 5), size=(1000, 50), font=1, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))# | RT_VALIGN_CENTER
        return res

def oneListEntry(name):
        res = [name]
        if HD.width() > 1280:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
                res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))#
        else:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(pngx)))
                res.append(MultiContentEntryText(pos=(60, 5), size=(1000, 50), font=1, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))# | RT_VALIGN_CENTER
        return res

def showlist(data, list):
        icount = 0
        plist = []
        for line in data:
                name = data[icount]
                plist.append(oneListEntry(name))
                icount = icount+1
                list.setList(plist)

class Hometv(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'Hometv.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Main')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['text'] = tvList([])
                self.working = False
                self.selection = 'all'
                self['key_red'] = Button(_('Exit'))
                self['key_green'] = Button(_('Extensions Installer'))
                self['key_yellow'] = Button(_('Uninstall'))
                self["key_blue"] = Button(_("tvManager"))
                self['key_blue'].hide()
                if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/tvManager/plugin.pyo'):
                        self["key_blue"].show()
                        self['key_blue'] = Label(_('tvManager'))
                elif fileExists('/usr/lib/enigma2/python/Plugins/PLi/tvManager/plugin.pyo'):
                        self["key_blue"].show()
                        self['key_blue'] = Label(_('tvManager'))
                global dmlink, link
                dmlink = ''
                link =''
                try:
                        fp = ''
                        destr = plugin_path + 'update.txt'
                        req = Request(upd_path + 'updatePanel.txt')
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
                        # fp = urlopen(req)
                        fp = checkStr(urlopen(req))
                        fp = fp.read()
                        print("fp3 =", fp)

                        with open(destr, 'w') as f:
                            f.write(fp)
                            f.close()
                        with open(destr, 'r') as fp:
                            count = 0
                            self.labeltext = ''
                            s1 = fp.readline()
                            s2 = fp.readline()
                            s3 = fp.readline()
                            s4 = fp.readline()
                            s1 = s1.strip()
                            s2 = s2.strip()
                            s3 = s3.strip()
                            s4 = s4.strip()
                            self.version = s1
                            link = s2
                            self.info = s3
                            dmlink = s4
                            fp.close()
                            cstr = s1 + ' ' + s2
                            if s1 <= currversion:
                                self.Update = False
                            else:
                                self.Update = True
                except:
                        self.Update = False

                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.msgupdate1)
                else:
                        self.timer.callback.append(self.msgupdate1)
                self['actions'] = NumberActionMap(['SetupActions', 'ColorActions', "MenuActions"], {'ok': self.okRun,
                 'green': self.tvIPK,
                 'menu': self.goConfig,
                 'blue': self.tvManager,
                 'yellow': self.ipkDs,
                 'red': self.closerm,
                 'back': self.closerm,
                 'cancel': self.closerm}, -1)
                self.onLayoutFinish.append(self.updateMenuList)

        def check_dependencies(self):
                dependencies = True
                # if PY3:
                try:
                    import requests
                    from PIL import Image
                except:
                    dependencies = False
                if dependencies is False:
                    chmod("/usr/lib/enigma2/python/Plugins/Extensions/tvPanel/dependencies.sh", 0o0755)
                    cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/tvPanel/dependencies.sh"
                    self.session.openWithCallback(self.starts, Console, title="Checking Python Dependencies", cmdlist=[cmd1], closeOnSuccess=False)
                else:
                    self.starts()

        def starts(self):
                OnclearMem()

        def closerm(self):
                # plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
                ReloadBouquet()
                self.close()

        def goConfig(self):
                self.session.open(tvConfig)

        def updateMenuList(self):
                self.menu_list = []
                for x in self.menu_list:
                        del self.menu_list[0]
                list = []
                idx = 0
                for x in Panel_list:
                        list.append(menuListEntry(x, idx))
                        self.menu_list.append(x)
                        idx += 1
                self['text'].setList(list)

        def okRun(self):
                self.keyNumberGlobalCB(self['text'].getSelectedIndex())

        def ipkDs(self):
                self.session.open(tvRemove)

        def tvManager(self):
                if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/tvManager/plugin.pyo'):
                        from Plugins.Extensions.tvManager.plugin import tvManager
                        self.session.openWithCallback(self.close, tvManager)
                elif fileExists('/usr/lib/enigma2/python/Plugins/PLi/tvManager/plugin.pyo'):
                        from Plugins.PLi.tvManager.plugin import tvManager
                        self.session.openWithCallback(self.close, tvManager)
                else:
                        self.session.open(tvMessageBox,("tvManager Not Installed!!"), type=tvMessageBox.TYPE_INFO, timeout=3)

        def tvIPK(self):
                self.session.open(tvIPK)

        def keyNumberGlobalCB(self, idx):
                sel = self.menu_list[idx]
                if sel == _('DEBIAN'):
                        self.session.open(debian)
                elif sel == _('DRIVERS'):
                        self.session.open(Drivers)
                elif sel == _('DEPENDENCIES'):
                        self.session.open(Dependencies)
                elif sel == _('PICONS'):
                        self.session.open(SelectPicons)
                elif sel == _('KODILITE BY PCD'):
                        self.session.open(mainkodilite)
                elif sel == _('PLUGIN BACKUP'):
                        self.session.open(PluginBackup)
                elif sel == _('PLUGIN EMULATORS CAMS'):
                        self.session.open(PluginEmulators)
                elif sel == _('PLUGIN EPG'):
                        self.session.open(PluginEpg)
                elif sel == _('PLUGIN KODI'):
                        self.session.open(Kodi)
                elif sel == _('PLUGIN MULTIBOOT'):
                        self.session.open(PluginMultiboot)
                elif sel == _('PLUGIN MULTIMEDIA'):
                        self.session.open(PluginMultimedia)
                elif sel == _('PLUGIN PICONS'):
                        self.session.open(Picons)
                elif sel == _('PLUGIN PPANEL'):
                        self.session.open(PluginPpanel)
                elif sel == _('PLUGIN SETTINGS PANEL'):
                        self.session.open(PluginSettings)
                elif sel == _('SETTINGS DAILY'):
                        self.session.open(tvDailySetting)
                elif sel == _('PLUGIN SKINS'):
                        self.session.open(PluginSkins)
                elif sel == _('PLUGIN SPORT'):
                        self.session.open(PluginSport)
                elif sel == _('PLUGIN UTILITY'):
                        self.session.open(PluginUtility)
                elif sel == _('PLUGIN WEATHER'):
                        self.session.open(PluginWeather)

        def msgupdate1(self):
                if self.Update == False :
                        return
                if config.plugins.tvPanel.autoupd.value == False :
                        return
                else:
                        self.session.openWithCallback(self.runupdate, tvMessageBox, (_('New update available!!\nDo you want update plugin ?\nPlease Reboot GUI after install!')), tvMessageBox.TYPE_YESNO)

        def runupdate(self, result):
                if result:
                        if isDreamOS:
                                com = dmlink
                                dom = 'New version ' + self.version
                                os.system('wget %s -O /tmp/tvpanel.tar > /dev/null' % com)
                                os.system('sleep 3')
                                self.session.open(tvConsole, _('Install Update: %s') % dom, ['tar -xvf /tmp/tvpanel.tar -C /'], finishedCallback=self.msgipkrst1, closeOnSuccess=False)
                        else:
                                com = link
                                dom = 'New Version ' + self.version
                                self.session.open(tvConsole, _('Install Update: %s') % dom, ['opkg install %s' % com], finishedCallback=self.msgipkrst1, closeOnSuccess=False)

        def msgipkrst1(self):
                self.session.openWithCallback(self.ipkrestrt, tvMessageBox, (_('Do you want restart enigma2 ?')), tvMessageBox.TYPE_YESNO)

        def ipkrestrt(self, result):
                if result:
                        epgpath = '/media/hdd/epg.dat'
                        epgbakpath = '/media/hdd/epg.dat.bak'
                        if os.path.exists(epgbakpath):
                                os.remove(epgbakpath)
                        if os.path.exists(epgpath):
                                copyfile(epgpath, epgbakpath)
                        self.session.open(TryQuitMainloop, 3)
                else:
                        self.close()

class Drivers(Screen):
        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Drivers')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self['pth'] = Label('')
                self['pform'] = Label('')
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'Drivers.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class Dependencies(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Dependencies')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'Dependencies.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class Picons(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Picons')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'Picons.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginBackup(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Backup')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginBackup.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginEmulators(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Emulators')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginEmulators.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginEpg(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Epg')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginEpg.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginMultimedia(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Multimedia')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginMultimedia.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class Kodi(Screen):

        def __init__(self, session):

                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodi')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'Kodi.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginMultiboot(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Multiboot')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginMultiboot.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginPpanel(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Ppanel')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginPpanel.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginSettings(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Settings')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginSettings.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginSkins(Screen):


        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Skins')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginSkins.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginSport(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Sport')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginSport.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class PluginUtility(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Utility')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginUtility.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close


class PluginWeather(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Plugin Weather')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'PluginWeather.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close


class debian(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Debian')
                Screen.__init__(self, session)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = xml_path + 'debian.xml'
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                try:
                        regex = '<plugins cont="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for name in match:
                                   self.list.append(name)
                                   self['info'].setText(_('Please select ...'))
                        showlist(self.list, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                if self.downloading == True:
                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                name = self.list[idx]
                                self.session.open(tvInstall, self.xml, name)
                        except:
                                return
                else:
                        self.close

class tvDailySetting(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Daily Setting')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['text'] = tvList([])
                self.working = False
                self.selection = 'all'
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label('')
                self['info'].setText(_('Please select ...'))
                self['key_green'] = Button(_('Select'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_('Lcn'))
                self["key_blue"] = Button(_(''))
                self['key_blue'].hide()
                self['actions'] = NumberActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
                 'green': self.okRun,
                 'back': self.closerm,
                 'red': self.closerm,
                 'yellow': self.Lcn,
                 'cancel': self.closerm}, -1)
                self.onLayoutFinish.append(self.updateMenuList)

        def Lcn(self):
                self.mbox = self.session.open(tvMessageBox, _('Reorder terrestrial channels with Lcn rules'), tvMessageBox.TYPE_INFO, timeout=5)
                lcnstart()

        def closerm(self):
                self.close()

        def updateMenuList(self):
                self.menu_list = []
                for x in self.menu_list:
                        del self.menu_list[0]
                list = []
                idx = 0
                for x in Panel_list2:
                        list.append(DailyListEntry(x, idx))
                        self.menu_list.append(x)
                        idx += 1
                self['text'].setList(list)

        def okRun(self):
                self.keyNumberGlobalCB(self['text'].getSelectedIndex())

        def keyNumberGlobalCB(self, idx):
                sel = self.menu_list[idx]
                if sel == _('UPDATE SATELLITES.XML'):
                        self.okSATELLITE()
                elif sel == _('UPDATE TERRESTRIAL.XML'):
                        self.okTERRESTRIAL()
                elif sel == ('SETTINGS CIEFP'):
                        self.session.open(SettingCiefp)
                elif sel == ('SETTINGS COLOMBO'):
                        self.session.open(SettingColombo)
                elif sel == ('SETTINGS BI58'):
                        self.session.open(SettingBi58)
                elif sel == ('SETTINGS MANUTEK'):
                        self.session.open(SettingManutek)
                elif sel == ('SETTINGS MILENKA61'):
                        self.session.open(Milenka61)
                elif sel == ('SETTINGS MORPHEUS'):
                        self.session.open(SettingMorpheus)
                elif sel == ('SETTINGS PREDRAG'):
                        self.session.open(SettingPredrag)
                elif sel == ('SETTINGS VHANNIBAL'):
                        self.session.open(SettingVhan)

        def okSATELLITE(self):
                self.session.openWithCallback(self.okSatInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okSatInstall(self, result):
                if result:
                        if checkInternet():
                                try:
                                        url_sat_oealliance      = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
                                        dirCopy = '/etc/tuxbox/satellites.xml'
                                        urlretrieve(url_sat_oealliance, dirCopy, context=ssl._create_unverified_context())
                                        self.mbox = self.session.open(tvMessageBox, _('Satellites.xml Updated!'), tvMessageBox.TYPE_INFO, timeout=5)
                                        self['info'].setText(_('Installation done !!!'))
                                except:
                                        return
                        else:
                                session.open(tvMessageBox, "No Internet", tvMessageBox.TYPE_INFO)


        def okTERRESTRIAL(self):
                self.session.openWithCallback(self.okTerrInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okTerrInstall(self, result):
                if result:
                        if checkInternet():
                                try:
                                        url_sat_oealliance      = 'https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/terrestrial.xml'
                                        dirCopy           = '/etc/tuxbox/terrestrial.xml'
                                        urlretrieve(url_sat_oealliance, dirCopy, context=ssl._create_unverified_context())
                                        self.mbox = self.session.open(tvMessageBox, _('Terrestrial.xml Updated!'), tvMessageBox.TYPE_INFO, timeout=5)
                                        self['info'].setText(_('Installation done !!!'))
                                except:
                                        return
                        else:
                                self.mbox = self.session.open(tvMessageBox, "No Internet", tvMessageBox.TYPE_INFO)

class SettingColombo(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Colombo')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovL2NvbG9tYm8uYWx0ZXJ2aXN0YS5vcmcvY29sb21iby9jb2xvbWJvLw==")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url in match:
                                if 'setting' in url.lower():
                                        name = url
                                        url64b = base64.b64decode("aHR0cDovL2NvbG9tYm8uYWx0ZXJ2aXN0YS5vcmc=")
                                        url = url64b + url
                                        name = name.replace("/colombo/colombo/", "")
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("_", " ")
                                        name = name.replace("-", " ")
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self.downloading = True
                                else:
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False


        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.zip"
                                print("url =", url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.zip'
                if os.path.exists(checkfile):
                        fdest1 = "/tmp/unzipped"
                        fdest2 = "/etc/enigma2"
                        if os.path.exists(fdest1):
                                cmd = "rm -rf '/tmp/unzipped'"
                                os.system(cmd)
                        os.makedirs('/tmp/unzipped')
                        cmd2 = "unzip -o -q '/tmp/settings.zip' -d " + fdest1
                        os.system(cmd2)
                        if os.path.exists(fdest1):
                                cmd = []
                                cmd3 = "rm -rf /etc/enigma2/lamedb"
                                cmd4 = "rm -rf /etc/enigma2/*.radio"
                                cmd5 = "rm -rf /etc/enigma2/*.tv"
                                cmd6 = "cp -rf /tmp/unzipped/* /etc/enigma2"
                                cmd13 = "rm -rf /tmp/settings.zip"
                                cmd14 = "rm -rf /tmp/unzipped"
                                cmd.append(cmd3)
                                cmd.append(cmd4)
                                cmd.append(cmd5)
                                cmd.append(cmd6)
                                cmd.append(cmd13)
                                cmd.append(cmd14)
                                title = _("Installation Settings")
                                self.session.open(tvConsole,_(title),cmd)
                                self.onShown.append(resettings)
class SettingVhan(Screen):

        def __init__(self, session):

                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Vhannibal')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)


        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovL3NhdC5hbGZhLXRlY2gubmV0L3VwbG9hZC9zZXR0aW5ncy92aGFubmliYWwv")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                    regex = '<a href="Vhannibal(.*?)"'
                    match = re.compile(regex,re.DOTALL).findall(self.xml)
                    for url in match:
                                    name = "Vhannibal" + url
                                    name = name.replace(".zip", "")
                                    name = name.replace("%20", " ")
                                    url64b = base64.b64decode("aHR0cDovL3NhdC5hbGZhLXRlY2gubmV0L3VwbG9hZC9zZXR0aW5ncy92aGFubmliYWwvVmhhbm5pYmFs")
                                    url = url64b + url
                                    self.urls.append(url)
                                    self.names.append(name)
                                    self['info'].setText(_('Please select ...'))
                    showlist(self.names, self['text'])
                    self.downloading = True
                except:
                    self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.zip"
                                print("url =", url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.zip'
                if os.path.exists(checkfile):
                        os.system('rm -rf /etc/enigma2/lamedb')
                        os.system('rm -rf /etc/enigma2/*.radio')
                        os.system('rm -rf /etc/enigma2/*.tv')
                        fdest1 = "/tmp"
                        fdest2 = "/etc/enigma2"
                        cmd1 = "unzip -o -q '/tmp/settings.zip' -d " + fdest1
                        cmd2 = "cp -rf  '/tmp/" + self.name + "'/* " + fdest2
                        print("cmd2 =", cmd2)
                        cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                        cmd4 = "rm -rf /tmp/settings.zip"
                        cmd5 = "rm -rf /tmp/Vhannibal*"
                        cmd = []
                        cmd.append(cmd1)
                        cmd.append(cmd2)
                        cmd.append(cmd3)
                        cmd.append(cmd4)
                        cmd.append(cmd5)
                        title = _("Installation Settings")
                        self.session.open(tvConsole,_(title),cmd)
                        self.onShown.append(resettings)

class Milenka61(Screen):

        def __init__(self, session):

                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Milenka61')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvdGFyR3ov")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="Satvenus(.*?)".*?align="right">(.*?)20'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date in match:
                                if url.find('.tar.gz') != -1 :
                                        name = "Satvenus" + url + ' ' + date
                                        name = name.replace(".tar.gz", "")
                                        name = name.replace("-", " ")
                                        name = name.replace("_", " ")
                                        name = name.replace("Satvenus", "")
                                        name = name.replace("EX-YU", "")
                                        name = name.replace("Lista", "")
                                        name = name.replace("za", "")
                                        name = name.replace("%20", " ")
                                        url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvdGFyR3ovU2F0dmVudXM=")
                                        url = url64b + url
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.tar.gz"
                                print("url =", url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.tar.gz'
                if os.path.exists(checkfile):
                        os.system('rm -rf /etc/enigma2/lamedb')
                        os.system('rm -rf /etc/enigma2/*.radio')
                        os.system('rm -rf /etc/enigma2/*.tv')
                        cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
                        print("cmd1 =", cmd1)
                        cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                        cmd4 = "rm -rf /tmp/*.tar.gz"
                        cmd = []
                        cmd.append(cmd1)
                        cmd.append(cmd3)
                        cmd.append(cmd4)
                        title = _("Installation Settings")
                        self.session.open(tvConsole,_(title),cmd)
                        self.onShown.append(resettings)

class SettingManutek(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Manutek')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)


        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovL3d3dy5tYW51dGVrLml0L2lzZXR0aW5nLw==")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        match = re.compile('href=".*?file=(.+?)">', re.DOTALL).findall(self.xml)
                        for url in match:
                                        name = url
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("NemoxyzRLS_", "")
                                        name = name.replace("_", " ")
                                        url64b = base64.b64decode("aHR0cDovL3d3dy5tYW51dGVrLml0L2lzZXR0aW5nL2VuaWdtYTIv")
                                        url = url64b + url
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.zip"
                                print("url =", url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.zip'
                if os.path.exists(checkfile):
                        fdest1 = "/tmp/unzipped"
                        fdest2 = "/etc/enigma2"
                        if os.path.exists("/tmp/unzipped"):
                                cmd = "rm -rf '/tmp/unzipped'"
                                os.system(cmd)
                        os.makedirs('/tmp/unzipped')
                        cmd2 = "unzip -o -q '/tmp/settings.zip' -d " + fdest1
                        os.system(cmd2)
                        for root, dirs, files in os.walk(fdest1):
                                for name in dirs:
                                        os.system('rm -rf /etc/enigma2/lamedb')
                                        os.system('rm -rf /etc/enigma2/*.radio')
                                        os.system('rm -rf /etc/enigma2/*.tv')
                                        cmd3 = "cp -rf  '/tmp/unzipped/" + name + "'/* " + fdest2
                                        cmd4 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                                        cmd5 = "rm -rf /tmp/settings.zip"
                                        cmd6 = "rm -rf /tmp/unzipped"
                                        cmd = []
                                        cmd.append(cmd3)
                                        cmd.append(cmd4)
                                        cmd.append(cmd5)
                                        cmd.append(cmd6)
                                title = _("Installation Settings")
                                self.session.open(tvConsole,_(title),cmd)
                        self.onShown.append(resettings)

class SettingMorpheus(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Morpheus')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovL21vcnBoZXVzODgzLmFsdGVydmlzdGEub3JnL2Rvd25sb2FkL2luZGV4LnBocD9kaXI9")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        match = re.compile('href=".*?file=(.+?)">', re.DOTALL).findall(self.xml)
                        for url in match:
                                if 'zip' in url.lower():
                                        if 'settings' in url.lower():
                                                continue
                                        name = url
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("_", " ")
                                        name = name.replace("Morph883", "Morpheus883")
                                        url64b = base64.b64decode("aHR0cDovL21vcnBoZXVzODgzLmFsdGVydmlzdGEub3JnL3NldHRpbmdzLw==")
                                        url = url64b + url
                                        print('url 64b-url-', url)
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.zip"
                                print("url =", url)
                                url= str(url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.zip'
                if os.path.exists(checkfile):
                        if os.path.exists("/tmp/unzipped"):
                                os.system('rm -rf /tmp/unzipped')
                        os.makedirs('/tmp/unzipped')
                        os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                        path = '/tmp/unzipped'
                        for root, dirs, files in os.walk(path):
                                for pth in dirs:
                                        cmd = []
                                        os.system('rm -rf /etc/enigma2/lamedb')
                                        os.system('rm -rf /etc/enigma2/*.radio')
                                        os.system('rm -rf /etc/enigma2/*.tv')
                                        cmd1 = "cp -rf /tmp/unzipped/" + pth + "/* '/etc/enigma2'"
                                        cmd2 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                                        cmd.append(cmd1)
                                        cmd.append(cmd2)
                        title = _("Installation Settings")
                        self.session.open(tvConsole,_(title),cmd)
                deletetmp()
                self.onShown.append(resettings)

class SettingCiefp(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Ciefp')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQ2llZnAv")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="ciefp(.*?)".*?align="right">(.*?)20'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url,date in match:
                                if url.find('.tar.gz') != -1 :
                                        name = "ciefp" + url + ' '      + date
                                        name = name.replace(".tar.gz", "")
                                        name = name.replace("%20", " ")
                                        url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQ2llZnAvY2llZnA=")
                                        url = url64b + url
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
#                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.tar.gz"
                                print("url =", url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.tar.gz'
                if os.path.exists(checkfile):
                        os.system('rm -rf /etc/enigma2/lamedb')
                        os.system('rm -rf /etc/enigma2/*.radio')
                        os.system('rm -rf /etc/enigma2/*.tv')
                        cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
                        print("cmd1 =", cmd1)
                        cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                        cmd4 = "rm -rf /tmp/*.tar.gz"
                        cmd = []
                        cmd.append(cmd1)
                        cmd.append(cmd3)
                        cmd.append(cmd4)
                        title = _("Installation Settings")
                        self.session.open(tvConsole,_(title),cmd)
                        self.onShown.append(resettings)

class SettingBi58(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Bi58')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQmk1OC8=")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):

                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="bi58-e2(.*?)".*?align="right">(.*?)20'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date in match:
                                if url.find('.tar.gz') != -1 :
                                        name = "bi58-e2" + url + ' ' + date
                                        name = name.replace(".tar.gz", "")
                                        name = name.replace("%20", " ")
                                        url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQmk1OC9iaTU4LWUy")
                                        url = url64b + url
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                global set
                set = 0
                if result:
                        if self.downloading == True:
#                        try:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/settings.tar.gz"
                                print("url =", url)
                                if 'dtt' not in url.lower():
                                        set = 1
                                        terrestrial()
                                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.tar.gz'
                if os.path.exists(checkfile):
                        os.system('rm -rf /etc/enigma2/lamedb')
                        os.system('rm -rf /etc/enigma2/*.radio')
                        os.system('rm -rf /etc/enigma2/*.tv')
                        cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
                        print("cmd1 =", cmd1)
                        cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                        cmd4 = "rm -rf /tmp/*.tar.gz"
                        cmd = []
                        cmd.append(cmd1)
                        cmd.append(cmd3)
                        cmd.append(cmd4)
                        title = _("Installation Settings")
                        self.session.open(tvConsole,_(title),cmd)
                        self.onShown.append(resettings)

class SettingPredrag(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Setting Predrag')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['info'] = Label(_('Getting the list, please wait ...'))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvUHJlZHJAZy8=")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                    regex = '<a href="predrag(.*?)".*?align="right">(.*?)20'
                    match = re.compile(regex,re.DOTALL).findall(self.xml)

                    for url, date in match:
                            if url.find('.tar.gz') != -1 :
                                    name = url + ' ' + date
                                    name = name.replace(".tar.gz", "")
                                    name = name.replace("-settings", "settings")
                                    url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvUHJlZHJAZy9wcmVkcmFn")
                                    url = url64b + url
                                    self.urls.append(url)
                                    self.names.append(name)
                                    self['info'].setText(_('Please select ...'))
                    showlist(self.names, self['text'])
                    self.downloading = True
                except:
                    self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
            global set
            set = 0
            if result:
                if self.downloading == True:
                        selection = str(self['text'].getCurrent())
                        idx = self["text"].getSelectionIndex()
                        self.name = self.names[idx]
                        url = self.urls[idx]
                        dest = "/tmp/settings.tar.gz"
                        print("url =", url)
                        if 'dtt' not in url.lower():
                                set = 1
                                terrestrial()
                        downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
                else:
                        self.close

        def showError(self, error):
                    print("download error =", error)
                    self.close()

        def install(self, fplug):
                checkfile = '/tmp/settings.tar.gz'
                if os.path.exists(checkfile):
                        os.system('rm -rf /etc/enigma2/lamedb')
                        os.system('rm -rf /etc/enigma2/*.radio')
                        os.system('rm -rf /etc/enigma2/*.tv')
                        cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
                        print("cmd1 =", cmd1)
                        cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
                        cmd4 = "rm -rf /tmp/*.tar.gz"
                        cmd = []
                        cmd.append(cmd1)
                        cmd.append(cmd3)
                        cmd.append(cmd4)
                        title = _("Installation Settings")
                        self.session.open(tvConsole,_(title),cmd)
                        self.onShown.append(resettings)

class tvInstall(Screen):
        def __init__(self, session, data, name, selection = None):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Install')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.selection = selection
                self['info'] = Label()
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                list = []
                list.sort()
                n1 = data.find(name, 0)
                n2 = data.find("</plugins>", n1)
                data1 = data[n1:n2]
                self.names = []
                self.urls = []
                regex = '<plugin name="(.*?)".*?url>"(.*?)"'
                match = re.compile(regex,re.DOTALL).findall(data1)
                for name, url in match:
                                self.names.append(name)
                                self.urls.append(url)
                self['text'] = tvList([])
                self['info'].setText(_('Please install ...'))
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self['actions'] = ActionMap(['SetupActions'], {'ok': self.message,
                 'green': self.message,
                 'red': self.close,
                 'cancel': self.close}, -2)
                self.onLayoutFinish.append(self.start)

        def start(self):
                showlist(self.names, self['text'])

        def message(self):
                self.session.openWithCallback(self.selclicked,tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

        def selclicked(self, result):
            if result:
                    idx = self["text"].getSelectionIndex()
                    print('IDXXXXXXXXXXXXX: ', idx)
                    dom = self.names[idx]
                    com = self.urls[idx]
                    print('COOMMMMMMMM: ', com)
                    print('DOOOOOMMMMMMM: ', dom)
                    self.prombt(com, dom)


        def downloadProgress(self, recvbytes, totalbytes):
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

        def install(self, fplug):
                checkfile = '/tmp/ipkdownloaded.ipk'
                if os.path.exists(checkfile):
                        self.session.open(tvConsole, _('Installing: %s') % self.dom, ['opkg install %s' % checkfile])#self.com])
                        self['info'].setText(_('Installation done !!!'))
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)
                return

        def showError(self, error):
                print("download error =", error)
                self.close()

        def cancel(self, result = None):
                self.close(None)

        def prombt(self, com, dom):
                useragent = "--header='User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
                self.com = com
                self.dom = dom
                print('self.com', self.com)
                self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                if self.com.endswith('.ipk'):
                        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                        url = self.com
                        # self.session.open(tvConsole, _('Installing: %s') % self.dom, ['opkg install -force-overwrite -force-depends %s' % self.com])
                        self.session.open(tvConsole, _('Installing: %s') % self.dom, ['opkg install %s' % self.com])
                        self.timer = eTimer()
                        self.timer.start(500, 1)
                        if isDreamOS:
                                self.timer_conn = self.timer.timeout.connect(deletetmp)
                        else:
                                self.timer.callback.append(deletetmp)
                        self['info'].setText(_('Installation done !!!'))
                #### with progresss bar
                # if self.com.endswith('.ipk'):
                        # self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                        # url = self.com
                        # print 'urllll: ', url
                        # dest = '/tmp/ipkdownloaded.ipk'
                        # self.download = downloadWithProgress(url, dest)
                        # self.download.addProgress(self.downloadProgress)
                        # self.download.start().addCallback(self.install).addErrback(self.showError)
                elif self.com.endswith('.tar.gz'):
                        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                        self.timer = eTimer()
                        self.timer.start(500, 1)
                        if isDreamOS:
                                self.timer_conn = self.timer.timeout.connect(deletetmp)
                        else:
                                self.timer.callback.append(deletetmp)
                        os.system("wget %s -c '%s' -O '/tmp/download.tar.gz' > /dev/null" % (useragent,self.com) )
                        self.session.open(tvConsole, _('Installing: %s') % self.dom, ['tar -xzvf ' + '/tmp/download.tar.gz' + ' -C /'])
                        self.mbox = self.session.open(tvMessageBox, _('Installation done !!!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation done !!!'))
                elif self.com.endswith('.tar.bz2'):
                        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                        self.timer = eTimer()
                        self.timer.start(500, 1)
                        if isDreamOS:
                                self.timer_conn = self.timer.timeout.connect(deletetmp)
                        else:
                                self.timer.callback.append(deletetmp)
                        os.system("wget %s -c '%s' -O '/tmp/download.bz2' > /dev/null" % (useragent,self.com) )
                        self.session.open(tvConsole, _('Installing: %s') % self.dom, ['tar -xyvf ' + '/tmp/download.tar.bz2' + ' -C /'])
                        self.mbox = self.session.open(tvMessageBox, _('Installation done !!!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation done !!!'))
                elif self.com.endswith('.tbz2'):
                        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                        self.timer = eTimer()
                        self.timer.start(500, 1)
                        if isDreamOS:
                                self.timer_conn = self.timer.timeout.connect(deletetmp)
                        else:
                                self.timer.callback.append(deletetmp)
                        os.system("wget %s -c '%s' -O '/tmp/download.tbz2' > /dev/null" % (useragent,self.com) )
                        self.session.open(tvConsole, _('Installing: %s') % self.dom, ['tar -xyvf ' + '/tmp/download.tbz2' + ' -C /'])
                        self.mbox = self.session.open(tvMessageBox, _('Installation done !!!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation done !!!'))
                elif self.com.endswith('.tbz'):
                        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                        self.timer = eTimer()
                        self.timer.start(500, 1)
                        if isDreamOS:
                                self.timer_conn = self.timer.timeout.connect(deletetmp)
                        else:
                                self.timer.callback.append(deletetmp)
                        os.system("wget %s -c '%s' -O '/tmp/download.tbz' > /dev/null" % (useragent,self.com) )
                        self.session.open(tvConsole, _('Installing: %s') % self.dom, ['tar -xyvf ' + '/tmp/download.tbz' + ' -C /'])
                        self.mbox = self.session.open(tvMessageBox, _('Installation done !!!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation done !!!'))
                elif self.com.endswith('.deb'):
                        if not isDreamOS:
                                self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                                self['info'].setText(_('Installation canceled!'))
                        else:
                                self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                                self.timer = eTimer()
                                self.timer.start(500, 1)
                                if isDreamOS:
                                        self.timer_conn = self.timer.timeout.connect(deletetmp)
                                else:
                                        self.timer.callback.append(deletetmp)
                                os.system("wget %s -c '%s' -O '/tmp/download.deb' > /dev/null" % (useragent,self.com) )
                                self.session.open(tvConsole, _('Installing: %s') % self.dom, ['echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + self.dom + '";dpkg --force-all -i /tmp/download.deb > /dev/null 2>&1'])   # dpkg -i --force-overwrite /tmp/download.deb > /dev/null']) #; apt-get -f --force-yes --assume-yes install; sleep 3'])
                                self.mbox = self.session.open(tvMessageBox, _('Installation done !!!'), tvMessageBox.TYPE_INFO, timeout=5)
                                self['info'].setText(_('Installation done !!!'))
                elif self.com.endswith('.zip'):
                        if 'setting' in self.dom.lower():
                                self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                                self.timer = eTimer()
                                self.timer.start(500, 1)
                                if isDreamOS:
                                        self.timer_conn = self.timer.timeout.connect(deletetmp)
                                else:
                                        self.timer.callback.append(deletetmp)
                                os.system("wget %s -c '%s' -O '/tmp/settings.zip' > /dev/null" % (useragent,self.com) )
                                checkfile = '/tmp/settings.zip'
                                if os.path.exists(checkfile):
                                        terrestrial()
                                        if os.path.exists("/tmp/unzipped"):
                                                os.system('rm -rf /tmp/unzipped')
                                        os.makedirs('/tmp/unzipped')
                                        os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                                        os.system('rm -rf /etc/enigma2/lamedb')
                                        os.system('rm -rf /etc/enigma2/*.radio')
                                        os.system('rm -rf /etc/enigma2/*.tv')
                                        os.system("cp -rf /tmp/unzipped/*.tv /etc/enigma2")
                                        os.system("cp -rf /tmp/unzipped/*.radio /etc/enigma2")
                                        os.system("cp -rf /tmp/unzipped/lamedb /etc/enigma2")
                                        if not os.path.exists("/etc/enigma2/blacklist"):
                                                os.system("cp -rf /tmp/unzipped/blacklist /etc/tuxbox/")
                                        if not os.path.exists("/etc/enigma2/whitelist"):
                                                os.system("cp -rf /tmp/unzipped/whitelist /etc/tuxbox/")
                                        os.system("cp -rf /tmp/unzipped/satellites.xml /etc/tuxbox/")
                                        os.system("cp -rf /tmp/unzipped/terrestrial.xml /etc/tuxbox/")
                                        terrestrial_rest()
                                        self.reloadSettings2()
                                else:
                                        self.mbox = self.session.open(tvMessageBox, _('Download Failed!'), tvMessageBox.TYPE_INFO, timeout=5)
                        elif 'picon' in self.dom.lower():
                                os.system("wget %s -c '%s' -O '/tmp/download.zip' > /dev/null" % (useragent,self.com) )
                                checkfile = '/tmp/download.zip'
                                if os.path.exists(checkfile):
                                        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
                                        cmd1 = "unzip -o -q '/tmp/download.zip' -d " + mmkpicon
                                        cmd = []
                                        cmd.append(cmd1)
                                        title = _("Installation Picons")
                                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                                        self.mbox = self.session.open(tvMessageBox, _('Installation done !!!'), tvMessageBox.TYPE_INFO, timeout=5)
                                        self['info'].setText(_('Installation done !!!'))
                        else:
                                self['info'].setText(_('Downloading the selected file in /tmp') + self.dom + _('... please wait'))
                                downplug = self.dom.replace(' ', '') + '.zip'
                                os.system("wget %s -c '%s' -O '/tmp/%s' > /dev/null" % (useragent,self.com,downplug) )
                                self.mbox = self.session.open(tvMessageBox, _('Download file in /tmp successful!'), tvMessageBox.TYPE_INFO, timeout=5)
                                self['info'].setText(_('Download file in /tmp successful!!'))
                else:
                        self['info'].setText(_('Download failed!') + self.dom + _('... Not supported'))
                return

        def reloadSettings2(self):
                        ReloadBouquet()
                        self.mbox = self.session.open(tvMessageBox, _('Setting Installed!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation done !!!'))


class tvConsole(Screen):

        def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):
                self.session = session
                skin = skin_path + 'tvConsole.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Console')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                # self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.finishedCallback = finishedCallback
                self.closeOnSuccess = closeOnSuccess
                self.errorOcurred = False
                self['text'] = ScrollLabel('')
                self['actions'] = ActionMap(['WizardActions', 'DirectionActions' 'ColorActions',], {'ok': self.cancel,
                 'back': self.cancel,
                 'red': self.cancel,
                 'up': self['text'].pageUp,
                 'down': self['text'].pageDown}, -1)
                self.cmdlist = cmdlist
                self.newtitle = _('..:: TiVuStream Addons V. %s ::..' % currversion) #title
                self.onShown.append(self.updateTitle)
                self.container = eConsoleAppContainer()
                self.run = 0
                try:
                        self.container.appClosed.append(self.runFinished)
                except:
                        self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
                try:
                        self.container.dataAvail.append(self.dataAvail)
                except:
                        self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
                self.onLayoutFinish.append(self.startRun)

        def updateTitle(self):
                self.setTitle(self.newtitle)

        def startRun(self):
                self['text'].setText(_('Execution Progress:') + '\n\n')
                print('Console: executing in run', self.run, ' the command:', self.cmdlist[self.run])
                if self.container.execute(self.cmdlist[self.run]):
                        self.runFinished(-1)

        def runFinished(self, retval):
                self.run += 1
                if self.run != len(self.cmdlist):
                        if self.container.execute(self.cmdlist[self.run]):
                                self.runFinished(-1)
                else:
                        str = self['text'].getText()
                        str += _('Execution finished!!')
                        self['text'].setText(str)
                        self['text'].lastPage()
                        if self.finishedCallback is not None:
                                self.finishedCallback()
                        if not retval and self.closeOnSuccess:
                                self.cancel()

        def cancel(self):
            if self.run == len(self.cmdlist):
                self.close()
                self.appClosed_conn = None
                self.dataAvail_conn = None

        def dataAvail(self, str):
                self['text'].setText(self['text'].getText() + str)


class tvIPK(Screen):

        def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):

                self.session = session
                skin = skin_path + 'tvIPK.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('IPK')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.flist = []
                idx = 0
                ipkpth = config.plugins.tvPanel.ipkpth.value
                pkgs = listdir(ipkpth)
                for fil in pkgs:
                        if fil.find('.ipk') != -1 or fil.find('.tar.gz') != -1 or fil.find('.deb') != -1:
                                res = (fil, idx)
                                self.flist.append(res)
                                idx = idx + 1
                self['ipkglisttmp'] = List(self.flist)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['info1'] = Label(_('Put addon .ipk .tar.gz .deb and install from config path') + ' ' + str(ipkpth) )
                self['info'] = Label('')
                self['key_green'] = Button(_('Install'))
                self['key_yellow'] = Button(_('Restart'))
                self['key_blue'] = Button(_('Remove'))
                self['key_red'] = Button(_('Back'))
                self['actions'] = ActionMap(['OkCancelActions', 'WizardActions', 'ColorActions', "MenuActions"], {'ok': self.ipkinst,
                 'green': self.ipkinst,
                 'yellow': self.msgipkinst,
                 'blue': self.msgipkrmv,
                 'red': self.close,
                 'menu': self.goConfig,
                 'cancel': self.close}, -1)
                self.onLayoutFinish.append(self.getfreespace)

        def getfreespace(self):
                fspace = freespace()
                self['info'].setText(fspace)

        def goConfig(self):
                self.session.open(tvConfig)


        def ipkinst(self):
                self.sel = self['ipkglisttmp'].getCurrent()
                if self.sel:
                        self.sel = self.sel[0]
                        self.session.openWithCallback(self.ipkinst2, tvMessageBox, (_('Do you really want to install the selected Addon?')+ '\n' + self.sel), tvMessageBox.TYPE_YESNO)

        def ipkinst2(self, answer):
            if answer is True:
                    ipkpth = config.plugins.tvPanel.ipkpth.value
                    dest = ipkpth + '/' + self.sel
                    try:
                        if self.sel.find('.ipk') != -1:
                                self.sel = self.sel[0]
                                cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";opkg update > /dev/null; echo ":Install ' + dest + '";opkg install --force-overwrite ' + dest + ' > /dev/null'
                                self.session.open(tvConsole, title='IPK Local Installation', cmdlist=[cmd0, 'sleep 5'], finishedCallback=self.msgipkinst)

                        elif self.sel.find('.tar.gz') != -1:
                                self.sel = self.sel[0]
                                cmd0 = 'tar -xzvf ' + dest + ' -C /'
                                self.session.open(tvConsole, title='TAR GZ Local Installation', cmdlist=[cmd0, 'sleep 5'], finishedCallback=self.msgipkinst)

                        elif self.sel.find('.deb') != -1:
                                if isDreamOS:
                                        self.sel = self.sel[0]
                                        cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + dest + '";dpkg --force-all -i ' + dest + ' > /dev/null 2>&1' #+ dest + ' > /dev/null' #; apt-get -f --force-yes --assume-yes install'
                                        self.session.open(tvConsole, title='DEB Local Installation', cmdlist=[cmd0, 'sleep 3'], finishedCallback=self.msgipkinst)
                                else:
                                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                        else:
                                self.session.open(MessageBox, MessageBox.TYPE_ERROR, timeout=10)
                    except:
                            self.delFile(dest)
                            self['info1'].text = _('File: %s\nInstallation failed!') % dest

        def delFile(self,dest):
                if fileExists(dest):
                        os.system('rm -rf ' + dest)

        def msgipkrmv(self):
                self.sel = self['ipkglisttmp'].getCurrent()
                if self.sel:
                        self.sel = self.sel[0]
                        self.session.openWithCallback(self.msgipkrmv2, tvMessageBox, (_('Do you really want to remove selected?')+ '\n' + self.sel), tvMessageBox.TYPE_YESNO)

        def msgipkrmv2(self, answer):
                if answer is True:
                        ipkpth = config.plugins.tvPanel.ipkpth.value
                        dest = ipkpth + '/' + self.sel
                        cmd0 = 'rm -rf ' + dest
                        self.session.open(tvConsole, title='IPK Local Remove', cmdlist=[cmd0, 'sleep 3'], finishedCallback=self.close)

        def msgipkinst(self):
                self.session.openWithCallback(self.ipkrestart, MessageBox, (_('Restart Enigma to load the installed plugin?')), MessageBox.TYPE_YESNO)

        def ipkrestart(self, result):
                if result:
                        self.session.open(TryQuitMainloop, 3)
                else:
                        self.close()

class tvUpdate(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Update')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_('Update'))
                self['key_green'] = Button(_('Restart'))
                self["key_blue"] = Button(_(''))
                self['key_blue'].hide()
                self['info'] = Label('')
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['text'] = tvList([])
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.Update = False
                global link, dmlink
                dmlink=''
                link=''
                try:
                        fp = ''
                        destr = plugin_path + 'update.txt'
                        req = Request(upd_path + 'updatePanel.txt')
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
                        fp = checkStr(urlopen(req))
                        fp = fp.read()
                        print("fp3 =", fp)

                        with open(destr, 'w') as f:
                            f.write(fp)
                            f.close()
                        with open(destr, 'r') as fp:
                            count = 0
                            self.labeltext = ''
                            s1 = fp.readline()
                            s2 = fp.readline()
                            s3 = fp.readline()
                            s4 = fp.readline()
                            s1 = s1.strip()
                            s2 = s2.strip()
                            s3 = s3.strip()
                            s4 = s4.strip()
                            self.version = s1
                            link = s2
                            self.info = s3
                            dmlink = s4
                            fp.close()
                            cstr = s1 + ' ' + s2
                            if s1 <= currversion:
                                self['info'].setText('TiVuStream Panel version: ' + currversion )
                                self['pth'].setText('No updates available!')
                                self.Update = False
                            else:
                                updatestr = 'TiVuStream Panel version: ' + currversion
                                cvrs = 'New update ' + s1 + ' is available!! '
                                cvrt = 'Updates: ' + self.info + 'Press yellow button to start updating'
                                self.Update = True
                                self['info'].setText(updatestr)
                                self['pth'].setText(cvrs)
                                self['pform'].setText(cvrt)
                except:
                        self.Update = False
                        self['info'].setText('TiVuStream Panel version: ' + currversion )
                        self['pth'].setText('No updates available!')

                self.timer = eTimer()
                self.timer.start(2000, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.msgupdate1)
                else:
                        self.timer.callback.append(self.msgupdate1)
                self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
                 'cancel': self.close,
                 'green': self.msgipkrst1,
                 'red': self.close,
                 'yellow': self.msgupdate}, -1)

        def msgupdate1(self):
                if self.Update == False :
                        return
                if config.plugins.tvPanel.autoupd.value == False :
                        return
                else:
                        self.session.openWithCallback(self.runupdate, tvMessageBox, (_('New update available!!\nDo you want update plugin ?\nPlease Reboot GUI after install!')), tvMessageBox.TYPE_YESNO)

        def msgupdate(self):
                if self.Update == False:
                    return
                else:
                    self.session.openWithCallback(self.runupdate, tvMessageBox, (_('Do you want update plugin ?\nPlease Reboot GUI after install!')), tvMessageBox.TYPE_YESNO)

        def runupdate(self, result):
                if result:
                    if isDreamOS:
                            com = dmlink
                            dom = 'New version ' + self.version
                            os.system('wget %s -O /tmp/tvpanel.tar > /dev/null' % com)
                            os.system('sleep 3')
                            self.session.open(tvConsole, _('Install Update: %s') % dom, ['tar -xvf /tmp/tvpanel.tar -C /'], finishedCallback=self.msgipkrst1, closeOnSuccess=True)
                    else:
                            com = link
                            dom = 'New Version ' + self.version
                            self.session.open(tvConsole, _('Install Update: %s') % dom, ['opkg install %s' % com], finishedCallback=self.msgipkrst1, closeOnSuccess=True)

        def msgipkrst1(self):
                self.session.openWithCallback(self.ipkrestrt, MessageBox, (_('Do you want restart enigma2 ?')), MessageBox.TYPE_YESNO)

        def ipkrestrt(self, result):
            if result:
                    epgpath = '/media/hdd/epg.dat'
                    epgbakpath = '/media/hdd/epg.dat.bak'
                    if os.path.exists(epgbakpath):
                            os.remove(epgbakpath)
                    if os.path.exists(epgpath):
                            copyfile(epgpath, epgbakpath)
                    self.session.open(TryQuitMainloop, 3)
            else:
                    self.close()


class tvRemove(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Remove')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['key_green'] = Button(_('Uninstall'))
                self['key_yellow'] = Button(_('Restart'))
                self['key_red'] = Button(_('Back'))
                self["key_blue"] = Button(_(''))
                self['key_blue'].hide()
                self['pth'] = Label('')
                self['pform'] = Label('')
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['info'] = Label()
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.message1,
                 'ok': self.message1,
                 'yellow': self.msgipkrst,
                 'red': self.close,
                 'cancel': self.close}, -1)
                self.getfreespace()
                self.onLayoutFinish.append(self.openList)

        def openList(self):
                self.names = []
                patch= ''
                if isDreamOS:
                        path= ('/var/lib/dpkg/info')
                else:
                        path = ('/var/lib/opkg/info')
                for root, dirs, files in os.walk(path):
                        if files is not None:
                                files.sort()
                                for name in files:
                                        if name.endswith('md5sums') or name.endswith('postinst') or name.endswith('preinst') or name.endswith('prerm') or name.endswith('postrm'):
                                                continue
                                        if name.endswith('control') or name.endswith('list'):
                                                        name= name.replace('.control', '')
                                                        name= name.replace('.list', '')
                                        self.names.append(name)
                showlist(self.names, self['text'])

        def callMyMsg1(self, result):
            if result:
                idx = self['text'].getSelectionIndex()
                if idx == -1 or None:
                        return
                dom = self.names[idx]
                com = dom
                if isDreamOS:
                        self.session.open(tvConsole, _('Removing: %s') % dom, ['dpkg -r %s' % com], self.getfreespace, False)
                else:
                        self.session.open(tvConsole, _('Removing: %s') % dom, ['opkg remove --force-removal-of-dependent-packages %s' % com], self.getfreespace, False)

        def getfreespace(self):
                fspace = freespace()
                self['info'].setText(fspace)
                self.openList()

        def message1(self):
                self.session.openWithCallback(self.callMyMsg1,tvMessageBox,_("Do you want to remove?"), tvMessageBox.TYPE_YESNO)

        def msgipkrst(self):
                self.session.openWithCallback(self.ipkrestrt, MessageBox, _('Do you want restart enigma2 ?'), MessageBox.TYPE_YESNO)

        def ipkrestrt(self, result):
            if result:
                    epgpath = '/media/hdd/epg.dat'
                    epgbakpath = '/media/hdd/epg.dat.bak'
                    if os.path.exists(epgbakpath):
                            os.remove(epgbakpath)
                    if os.path.exists(epgpath):
                            copyfile(epgpath, epgbakpath)
                    self.session.open(TryQuitMainloop, 3)
            else:
                    self.close()

class tvMessageBox(Screen):
        TYPE_YESNO = 0
        TYPE_INFO = 1
        TYPE_WARNING = 2
        TYPE_ERROR = 3
        TYPE_MESSAGE = 4

        def __init__(self, session, text, type = TYPE_YESNO, timeout = -1, close_on_any_key = False, default = True, enable_input = True, msgBoxID = None, picon = None, simple = False, list = [], timeout_default = None):
                self.session = session
                skin = skin_path + 'tvMessageBox.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('MessageBox')
                self.type = type
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.msgBoxID = msgBoxID
                self['text'] = Label(text)
                self['Text'] = StaticText(text)
                self['selectedChoice'] = StaticText()
                self.text = text
                self.close_on_any_key = close_on_any_key
                self.timeout_default = timeout_default
                self['ErrorPixmap'] = Pixmap()
                self['QuestionPixmap'] = Pixmap()
                self['InfoPixmap'] = Pixmap()
                self['WarningPixmap'] = Pixmap()
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.timerRunning = False
                self.initTimeout(timeout)
                picon = picon or type
                if picon != self.TYPE_ERROR:
                        self['ErrorPixmap'].hide()
                if picon != self.TYPE_YESNO:
                        self['QuestionPixmap'].hide()
                if picon != self.TYPE_INFO:
                        self['InfoPixmap'].hide()
                if picon != self.TYPE_WARNING:
                        self['WarningPixmap'].hide()
                self.title = self.type < self.TYPE_MESSAGE and [_('Question'),
                 _('Information'),
                 _('Warning'),
                 _('Error')][self.type] or _('Message')
                if type == self.TYPE_YESNO:
                        if list:
                                self.list = list
                        elif default == True:
                                self.list = [(_('Yes'), True), (_('No'), False)]
                        else:
                                self.list = [(_('No'), False), (_('Yes'), True)]
                else:
                        self.list = []
                self['list'] = MenuList(self.list)
                if self.list:
                        self['selectedChoice'].setText(self.list[0][0])
                else:
                        self['list'].hide()
                if enable_input:
                        self['actions'] = ActionMap(['MsgBoxActions', 'DirectionActions'], {'cancel': self.cancel,
                         'ok': self.ok,
                         'alwaysOK': self.alwaysOK,
                         'up': self.up,
                         'down': self.down,
                         'left': self.left,
                         'right': self.right,
                         'upRepeated': self.up,
                         'downRepeated': self.down,
                         'leftRepeated': self.left,
                         'rightRepeated': self.right}, -1)
                self.onLayoutFinish.append(self.layoutFinished)

        def layoutFinished(self):
                self.setTitle(self.title)

        def initTimeout(self, timeout):
                self.timeout = timeout
                if timeout > 0:
                        self.timer = eTimer()

                        if isDreamOS:
                                self.timer_conn = self.timer.timeout.connect(self.timerTick)
                        else:
                                self.timer.callback.append(self.timerTick)
                        self.onExecBegin.append(self.startTimer)
                        self.origTitle = None
                        if self.execing:
                                self.timerTick()
                        else:
                                self.onShown.append(self.__onShown)
                        self.timerRunning = True
                else:
                        self.timerRunning = False
                return

        def __onShown(self):
                self.onShown.remove(self.__onShown)
                self.timerTick()

        def startTimer(self):
                self.timer.start(500)

        def stopTimer(self):
            if self.timerRunning:
                del self.timer
                self.onExecBegin.remove(self.startTimer)
                self.setTitle(self.origTitle)
                self.timerRunning = False

        def timerTick(self):
            if self.execing:
                self.timeout -= 1
                if self.origTitle is None:
                        self.origTitle = self.instance.getTitle()
                self.setTitle(self.origTitle + ' (' + str(self.timeout) + ')')
                if self.timeout == 0:
                        self.timer.stop()
                        self.timerRunning = False
                        self.timeoutCallback()
            return

        def timeoutCallback(self):
                print('Timeout!')
                if self.timeout_default is not None:
                        self.close(self.timeout_default)
                else:
                        self.ok()
                return

        def cancel(self):
                self.close(False)

        def ok(self):
                if self.list:
                        self.close(self['list'].getCurrent()[1])
                else:
                        self.close(True)

        def alwaysOK(self):
                self.close(True)

        def up(self):
                self.move(self['list'].instance.moveUp)

        def down(self):
                self.move(self['list'].instance.moveDown)

        def left(self):
                self.move(self['list'].instance.pageUp)

        def right(self):
                self.move(self['list'].instance.pageDown)

        def move(self, direction):
                if self.close_on_any_key:
                        self.close(True)
                self['list'].instance.moveSelection(direction)
                if self.list:
                        self['selectedChoice'].setText(self['list'].getCurrent()[0])
                self.stopTimer()

        def __repr__(self):
                return str(type(self)) + '(' + self.text + ')'


class tvConfig(Screen, ConfigListScreen):

        def __init__(self, session):
                skin = skin_path + 'tvConfig.xml'
                f = open(skin, 'r')
                self.skin = f.read()
                f.close()
                Screen.__init__(self, session)
                self.setup_title = _("Config")
                self.onChangedEntry = [ ]
                self.session = session
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['description'] = Label('')
                info = ''
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['info'] = Label(_('Config Panel Addon'))
                self['key_yellow'] = Button(_('Update'))
                self['key_green'] = Button(_('Save'))
                self['key_red'] = Button(_('Back'))
                self["key_blue"] = Button(_(''))
                self['key_blue'].hide()
                self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'], {'cancel': self.extnok,
                 'red': self.extnok,
                 'back': self.close,
                 'left': self.keyLeft,
                 'right': self.keyRight,
                 'yellow': self.tvUpdate,
                 'ok': self.Ok_edit,
                 'green': self.msgok}, -1)
                self.list = []
                ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
                self.createSetup()
                self.onLayoutFinish.append(self.layoutFinished)

        def layoutFinished(self):
                self.setTitle(self.setup_title)
                if not os.path.exists('/tmp/currentip'):
                        os.system('wget -qO- http://ipecho.net/plain > /tmp/currentip')
                currentip1 = open('/tmp/currentip', 'r')
                currentip = currentip1.read()
                self['info'].setText(_('Config Panel Addon\nYour current IP is %s') %currentip)

        def tvUpdate(self):
                self.session.open(tvUpdate)

        def createSetup(self):
            self.editListEntry = None
            self.list = []
            self.list.append(getConfigListEntry(_('Auto Update Plugin'), config.plugins.tvPanel.autoupd, _("If Active: Automatic Update Plugin")))
            self.list.append(getConfigListEntry(_("Set the path to the Picons folder"), config.plugins.tvPanel.mmkpicon, _("Configure folder containing picons files")))
            # self.list.append(getConfigListEntry(_("Format Size Picons"), config.plugins.tvPanel.mmkpiconform, _("Configure format size Picons filter")))
            self.list.append(getConfigListEntry(_('Path Manual IPK'), config.plugins.tvPanel.ipkpth, _("Path to the addon installation folder")))
            self.list.append(getConfigListEntry(_('Link in Extensions Menu'), config.plugins.tvPanel.strtext, _("Link in Extensions button")))
            self.list.append(getConfigListEntry(_('Link in Main Menu'), config.plugins.tvPanel.strtmain, _("Link in Main Menu")))
            self.list.append(getConfigListEntry(_('Link in Setup Menu'), config.plugins.tvPanel.strtst, _("Link in Setup Menu")))
            self["config"].list = self.list
            self["config"].setList(self.list)

        def changedEntry(self):
                for x in self.onChangedEntry:
                                x()

        def getCurrentEntry(self):
                return self["config"].getCurrent()[0]

        def getCurrentValue(self):
                return str(self["config"].getCurrent()[1].getText())

        def createSummary(self):
                from Screens.Setup import SetupSummary
                return SetupSummary

        def keyLeft(self):
                ConfigListScreen.keyLeft(self)
                print("current selection:", self["config"].l.getCurrentSelection())
                self.createSetup()

        def keyRight(self):
                ConfigListScreen.keyRight(self)
                print("current selection:", self["config"].l.getCurrentSelection())
                self.createSetup()

        def msgok(self):
                if os.path.exists(config.plugins.tvPanel.ipkpth.value) is False:
                        self.mbox = self.session.open(MessageBox, _('Device not detected!'), MessageBox.TYPE_INFO, timeout=4)
                for x in self["config"].list:
                          x[1].save()
                self.mbox = self.session.open(MessageBox, _('Successfully saved configuration'), MessageBox.TYPE_INFO, timeout=4)
                self.close(True)

        def Ok_edit(self):
                ConfigListScreen.keyOK(self)
                sel = self['config'].getCurrent()[1]
                if sel and sel == config.plugins.tvPanel.mmkpicon:
                        self.setting = 'mmkpicon'
                        print("current selection:", self["config"].l.getCurrentSelection())
                        mmkpth = config.plugins.tvPanel.mmkpicon.value
                        self.openDirectoryBrowser(mmkpth)
                else:
                        pass

        def openDirectoryBrowser(self, path):
            try:
                    self.session.openWithCallback(
                     self.openDirectoryBrowserCB,
                     LocationBox,
                     windowTitle=_('Choose Directory:'),
                     text=_('Choose directory'),
                     currDir=str(path),
                     bookmarks=config.movielist.videodirs,
                     autoAdd=False,
                     editDir=True,
                     inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                     minFree=15)
            except Exception as e:
                    print(('openDirectoryBrowser get failed: ', str(e)))

        def openDirectoryBrowserCB(self, path):
            if path is not None:
                    if self.setting == 'mmkpicon':
                            config.plugins.tvPanel.mmkpicon.setValue(path)
                    if self.setting == 'ipkpth':
                            config.plugins.tvPanel.ipkpth.setValue(path)
            return

        def KeyText(self):
            sel = self['config'].getCurrent()
            if sel:
                    self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

        def VirtualKeyBoardCallback(self, callback = None):
            if callback is not None and len(callback):
                    self['config'].getCurrent()[1].value = callback
                    self['config'].invalidate(self['config'].getCurrent())
            return

        #
        def cancelConfirm(self, result):
                if not result:
                        return
                for x in self['config'].list:
                        x[1].cancel()
                self.close()

        def extnok(self):
                if self['config'].isChanged():
                        self.session.openWithCallback(self.cancelConfirm, tvMessageBox, _('Really close without saving the settings?'))
                else:
                        self.close()

Panel_list3 = [
 _('MMARK PICONS TRANSPARENT'),
 _('MMARK PICONS BLACK'),
 _('COLOMBO PICONS')]


class SelectPicons(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Select Picons')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['text'] = tvList([])
                self.working = False
                self.selection = 'all'
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['pth'] = Label('')
                # mmkform          = config.plugins.tvPanel.mmkpiconform.value
                self['pth'].setText(_('Folder picons ') + mmkpicon)
                self['pform'] = Label('')
                # self['pform'].setText(_('Format size picons ') + mmkform)
                self['info'] = Label('')
                self['info'].setText(_('Please select ...'))
                self['key_green'] = Button(_('Select'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['actions'] = NumberActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
                 'green': self.okRun,
                 'back': self.closerm,
                 'red': self.closerm,
                 'cancel': self.closerm}, -1)
                self.onLayoutFinish.append(self.updateMenuList)

        def getfreespace(self):
                fspace = freespace()
                self['pform'].setText(fspace)

        def closerm(self):
                self.close()

        def updateMenuList(self):
                self.menu_list = []
                for x in self.menu_list:
                        del self.menu_list[0]
                list = []
                idx = 0
                for x in Panel_list3:
                        list.append(DailyListEntry(x, idx))
                        self.menu_list.append(x)
                        idx += 1
                self['text'].setList(list)
                self.getfreespace()

        def okRun(self):
                self.keyNumberGlobalCB(self['text'].getSelectedIndex())

        def keyNumberGlobalCB(self, idx):
                sel = self.menu_list[idx]
                if sel == _('MMARK PICONS BLACK'):
                        self.session.open(MMarkFolderBlk)
                elif sel == _('MMARK PICONS TRANSPARENT'):
                        self.session.open(MMarkFolderTrs)
                elif sel == _('COLOMBO PICONS'):
                        self.session.open(ColomboTrasp)


class MMarkFolderBlk(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('MMark')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                # mmkform          = config.plugins.tvPanel.mmkpiconform.value
                self['pth'].setText(_('Folder picons ') + mmkpicon)
                self['pform'] = Label('')
                # self['pform'].setText(_('Format size picons ') + mmkform)
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                # self['space'] = Label('')
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                self.getfreespace()
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def getfreespace(self):
                fspace = freespace()
                self['pform'].setText(fspace)

        def downxmlpage(self):
                url = host_blk
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                r = data
                self.names = []
                self.urls = []
                try:
                    n1 = r.find('"folderkey"', 0)
                    n2 = r.find('more_chunks', n1)
                    self.xml = r[n1:n2]
                    regex = '{"folderkey":"(.*?)".*?"name":"(.*?)".*?"created":"(.*?)"'
                    match = re.compile(regex,re.DOTALL).findall(self.xml)
                    for url, name, data in match:
                        url = 'https://www.mediafire.com/api/1.5/folder/get_content.php?folder_key=' + url + '&content_type=files&chunk_size=1000&response_format=json'
                        url = url.replace('\\','')
                        pic = no_cover
                        name = name + ' ' + data[0:10]
                        self.urls.append(url)
                        self.names.append(name)

                    self['info'].setText(_('Please select ...'))
                    showlist(self.names, self['text'])
                    self.downloading = True
                except:
                    self.downloading = False

        def okRun(self):
            idx = self['text'].getSelectionIndex()
            if idx == -1 or None:
                return
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(MMarkBlack,name, url)


        def cancel(self, result = None):
            self.close(None)
            return


class MMarkBlack(Screen):

        def __init__(self, session, name, url):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('MMark')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                # mmkform          = config.plugins.tvPanel.mmkpiconform.value
                self['pth'].setText(_('Folder picons ') + mmkpicon)
                self['pform'] = Label('')
                # self['pform'].setText(_('Format size picons ') + mmkform)
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.url = url
                name = name
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                self.getfreespace()
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def getfreespace(self):
                fspace = freespace()
                self['pform'].setText(fspace)

        def downxmlpage(self):
                url = self.url
                print('urlllll: ',url)
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                r = data
                print('data: ', r)
                self.names = []
                self.urls = []
                try:
                    n1 = r.find('"quickkey":', 0)
                    n2 = r.find('more_chunks', n1)
                    self.xml = r[n1:n2]
                    print("In rrrrrrrrrrrrrrrrrrrrrrrrrrrr =", self.xml)
                    regex = 'filename":"(.*?)".*?"created":"(.*?)".*?"normal_download":"(.*?)"'
                    match = re.compile(regex,re.DOTALL).findall(self.xml)
                    print("In rrrrrrrrrrrrrrrrrrrrrrrrrrrr =", match)
                    for name, data, url  in match:
                        if 'zip' in url:
                            url = url.replace('\\','')
                            print('url: ',url)
                            pic = no_cover
                            name = name.replace('_',' ').replace('mmk','MMark').replace('.zip','')
                            name = name + ' ' + data[0:10]
                            self.urls.append(url)
                            self.names.append(name)
                            self['info'].setText(_('Please select ...'))
                        else:
                            self['info'].setText(_('no data ...'))
                    showlist(self.names, self['text'])
                    self.downloading = True
                except:
                    self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
            self['info'].setText(_('... please wait'))
            if result:
                if self.downloading == True:
                        selection = str(self['text'].getCurrent())
                        idx = self["text"].getSelectionIndex()
                        self.name = self.names[idx]
                        url = self.urls[idx]
                        dest = "/tmp/download.zip"
                        print("url =", url)
                        url=url
                        print('read url: ',  url)
                        req = Request(url)
                        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                        req.add_header('Referer', 'https://www.mediafire.com/')
                        req.add_header('X-Requested-With', 'XMLHttpRequest')
                        page = urlopen(req)
                        r = page.read()
                        n1 = r.find('"Download file"', 0)
                        n2 = r.find('Repair your download', n1)
                        r2 = r[n1:n2]
                        print("In rrrrrrrrrrrrrrrrrrrrrrrrrrrr2 =", r2)
                        channels = re.findall('href="http://download(.*?)">', r2)
                        print("getChannel match =", channels)
                        for url in channels:
                            img = no_cover
                            url = 'http://download' + url

                        self.download = downloadWithProgress(url, dest)
                        self.download.addProgress(self.downloadProgress)
                        self.download.start().addCallback(self.install).addErrback(self.showError)
                else:
                        self['info'].setText(_('Please select ...'))
                        self.close


        def downloadProgress(self, recvbytes, totalbytes):
            self['info'].setText(_('Download ...'))
            self['progress'].value = int(100 * recvbytes / float(totalbytes))
            self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

        def install(self, fplug):
            checkfile = '/tmp/download.zip'
            if os.path.exists(checkfile):
                    cmd1 = "unzip -o -q '/tmp/download.zip' -d " + mmkpicon
                    cmd = []
                    cmd.append(cmd1)
                    title = _("Installation Picons")
                    self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
            self['info'].setText(_('Please select ...'))
            self['progresstext'].text = ''
            self.progclear = 0
            self['progress'].setValue(self.progclear)

        def showError(self, error):
            self['info'].setText(_('Download Error ...'))
            print("download error =", error)
            self.close()

        def cancel(self, result = None):
            self.close(None)
            return


class MMarkFolderTrs(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('MMark')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                # mmkform          = config.plugins.tvPanel.mmkpiconform.value
                self['pth'].setText(_('Folder picons ') + mmkpicon)
                self['pform'] = Label('')
                # self['pform'].setText(_('Format size picons ') + mmkform)
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.getfreespace()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def getfreespace(self):
                fspace = freespace()
                self['pform'].setText(fspace)

        def downxmlpage(self):
                url = host_trs
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                r = data
                self.names = []
                self.urls = []
                try:
                    n1 = r.find('"folderkey"', 0)
                    n2 = r.find('more_chunks', n1)
                    self.xml = r[n1:n2]
                    regex = '{"folderkey":"(.*?)".*?"name":"(.*?)".*?"created":"(.*?)"'
                    match = re.compile(regex,re.DOTALL).findall(self.xml)
                    for url, name, data in match:
                        url = 'https://www.mediafire.com/api/1.5/folder/get_content.php?folder_key=' + url + '&content_type=files&chunk_size=1000&response_format=json'
                        pic = no_cover
                        name = name + ' ' + data[0:10]
                        self.urls.append(url)
                        self.names.append(name)
                    self['info'].setText(_('Please select ...'))
                    showlist(self.names, self['text'])
                    self.downloading = True
                except:
                    self.downloading = False

        def okRun(self):
            idx = self['text'].getSelectionIndex()
            if idx == -1 or None:
                return
            name = self.names[idx]
            url = self.urls[idx]

            self.session.open(MMarkTrasp,name, url)


        def cancel(self, result = None):
            self.close(None)
            return



class MMarkTrasp(Screen):

        def __init__(self, session, name,url):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('MMark')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                # mmkform          = config.plugins.tvPanel.mmkpiconform.value
                self['pth'].setText(_('Folder picons ') + mmkpicon)
                self['pform'] = Label('')
                # self['pform'].setText(_('Format size picons ') + mmkform)
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.getfreespace()
                self.downloading = False
                self.url = url
                name = name
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def getfreespace(self):
                fspace = freespace()
                self['pform'].setText(fspace)

        def downxmlpage(self):
                url = self.url
                print('urlllll: ',url)

                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                r = data
                print('data: ', r)
                self.names = []
                self.urls = []
                try:
                        n1 = r.find('"quickkey":', 0)
                        n2 = r.find('more_chunks', n1)
                        self.xml = r[n1:n2]
                        print("In rrrrrrrrrrrrrrrrrrrrrrrrrrrr =", self.xml)
                        regex = 'filename":"(.*?)".*?"created":"(.*?)".*?"normal_download":"(.*?)"'
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        print("In rrrrrrrrrrrrrrrrrrrrrrrrrrrr =", match)
                        for name, data, url  in match:
                            if 'zip' in url:
                                url = url.replace('\\','')
                                print('url: ',url)
                                pic = no_cover
                                name = name.replace('_',' ').replace('mmk','MMark').replace('.zip','')
                                name = name + ' ' + data[0:10]
                                self.urls.append(url)
                                self.names.append(name)
                                self['info'].setText(_('Please select ...'))
                            else:
                                self['info'].setText(_('no data ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                    self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                self['info'].setText(_('... please wait'))
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/download.zip"
                                print("url =", url)
                                url=url
                                print('read url: ',  url)
                                req = Request(url)
                                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
                                req.add_header('Referer', 'https://www.mediafire.com/')
                                req.add_header('X-Requested-With', 'XMLHttpRequest')
                                page = urlopen(req)
                                r = page.read()
                                n1 = r.find('"Download file"', 0)
                                n2 = r.find('Repair your download', n1)
                                r2 = r[n1:n2]
                                print("In rrrrrrrrrrrrrrrrrrrrrrrrrrrr2 =", r2)
                                channels = re.findall('href="http://download(.*?)">', r2)
                                print("getChannel match =", channels)
                                for url in channels:
                                    img = no_cover
                                    url = 'http://download' + url
                                self.download = downloadWithProgress(url, dest)
                                self.download.addProgress(self.downloadProgress)
                                self.download.start().addCallback(self.install).addErrback(self.showError)
                        else:
                                self['info'].setText(_('Please select ...'))
                                self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['info'].setText(_('Download ...'))
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

        def install(self, fplug):
                checkfile = '/tmp/download.zip'
                if os.path.exists(checkfile):
                        cmd1 = "unzip -o -q '/tmp/download.zip' -d " + mmkpicon
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation Picons")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)

        def showError(self, error):
            self['info'].setText(_('Download Error ...'))
            print("download error =", error)
            self.close()

class ColomboTrasp(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Colombo')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                # mmkform          = config.plugins.tvPanel.mmkpiconform.value
                self['pth'].setText(_('Folder picons ') + mmkpicon)
                self['pform'] = Label('')
                # self['pform'].setText(_('Format size picons ') + mmkform)
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.getfreespace()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def getfreespace(self):
                fspace = freespace()
                self['pform'].setText(fspace)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cDovL2NvbG9tYm8uYWx0ZXJ2aXN0YS5vcmcvY29sb21iby9jb2xvbWJvLw==")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
            self.xml = data
            self.names = []
            self.urls = []
            try:
                regex = '<a href="(.*?)"'
                match = re.compile(regex,re.DOTALL).findall(self.xml)
                for url in match:
                    if 'picon' in url.lower():
                            url64b = base64.b64decode("aHR0cDovL2NvbG9tYm8uYWx0ZXJ2aXN0YS5vcmc=")
                            name = url
                            url = url64b + url
                            print('url: ', url)
                            print('name: ', name)
                    # if config.plugins.tvPanel.mmkpiconform.value == 'all':
                            # name = name.replace("/colombo/colombo/", "")
                            # name = name.replace(".zip", "")
                            # name = name.replace("%20", " ")
                            # name = name.replace("-", " ")
                            # name = name.replace("_", " ")
                            # print('name: ', name)
                            # self.urls.append(url)
                            # self.names.append(name)
                            # self['info'].setText(_('Please select ...'))
                    # if config.plugins.tvPanel.mmkpiconform.value in name:
                            name = name.replace("/colombo/colombo/", "")
                            name = name.replace(".zip", "")
                            name = name.replace("%20", " ")
                            name = name.replace("-", " ")
                            name = name.replace("_", " ")
                            print('name: ', name)
                            self.urls.append(url)
                            self.names.append(name)
                            self['info'].setText(_('Please select ...'))
                    # else:
                            # self['info'].setText(_('Please select ...'))
                            self.downloading = True
                    else:
                            self['info'].setText(_('Please select ...'))
                            self.downloading = False
                showlist(self.names, self['text'])
                self.downloading = True
            except:
                self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
            self['info'].setText(_('... please wait'))
            if result:
                if self.downloading == True:
                        selection = str(self['text'].getCurrent())
                        idx = self["text"].getSelectionIndex()
                        self.name = self.names[idx]
                        url = self.urls[idx]
                        dest = "/tmp/download.zip"
                        print("url =", url)
                        self.download = downloadWithProgress(url, dest)
                        self.download.addProgress(self.downloadProgress)
                        self.download.start().addCallback(self.install).addErrback(self.showError)
                else:
                        self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['info'].setText(_('Download...'))
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))


        def install(self, fplug):
                checkfile = '/tmp/download.zip'
                if os.path.exists(checkfile):
                        cmd1 = "unzip -o -q '/tmp/download.zip' -d " + mmkpicon
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation Picons")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)
                self.close

        def showError(self, error):
            self['info'].setText(_('Download Error ...'))
            print("download error =", error)
            self.close()

Panel_list4 = [
 _('KODILITE'),
 _('PLUGINS'),
 _('PLUGINS ADULT'),
 _('SCRIPT'),
 _('REPOSITORY')]

global KodilitePcd
KodilitePcd = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
class mainkodilite(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodilite by pcd')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['text'] = tvList([])
                self.working = False
                self.selection = 'all'
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['pth'] = Label('')
                self['pth'].setText(_('Support on'))
                self['pform'] = Label('')
                self['pform'].setText(_('linuxsat-support.com '))
                self['info'] = Label('')
                self['info'].setText(_('Please select ...'))
                self['key_green'] = Button(_('Select'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['actions'] = NumberActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
                 'green': self.okRun,
                 'back': self.closerm,
                 'red': self.closerm,
                 'cancel': self.closerm}, -1)
                self.onLayoutFinish.append(self.updateMenuList)

        def closerm(self):
                self.close()

        def updateMenuList(self):
                self.menu_list = []
                for x in self.menu_list:
                        del self.menu_list[0]
                list = []
                idx = 0
                for x in Panel_list4:
                        list.append(DailyListEntry(x, idx))
                        self.menu_list.append(x)
                        idx += 1
                self['text'].setList(list)

        def okRun(self):
                self.keyNumberGlobalCB(self['text'].getSelectedIndex())

        def keyNumberGlobalCB(self, idx):
                sel = self.menu_list[idx]
                if sel == _('KODILITE'):
                        self.session.open(kodilite)
                elif sel == _('PLUGINS'):
                        self.session.open(plugins)
                elif sel == _('PLUGINS ADULT'):
                        self.session.open(plugins_adult)
                elif sel == _('SCRIPT'):
                        self.session.open(script)
                elif sel == _('REPOSITORY'):
                        self.session.open(repository)

class kodilite(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodilite by pcd')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                self['pth'].setText(_('Support on'))
                self['pform'] = Label('')
                self['pform'].setText(_('linuxsat-support.com '))
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlLw==")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="(.*?)">.*?</a>(.*?)20(.*?) '
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date, date2 in match:
                                if 'ipk' in url:
                                        url64b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20=")
                                        url = url64b + url + '.ipk'
                                        url264b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlLw==")
                                        name = url.replace(url264b, '')
                                        name = name.replace(".ipk", "")
                                        name = name.replace("enigma2-plugin-extensions-", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("-", " ")
                                        name = name.replace("_", " ")
                                        print('name: ', name)
                                        name = name +'-'+ date.replace(' ','') + date2
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                                else:
                                        self['info'].setText(_('Please select ...'))

                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                self['info'].setText(_('... please wait'))
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/download.ipk"
                                print("url =", url)
                                self.download = downloadWithProgress(url, dest)
                                self.download.addProgress(self.downloadProgress)
                                self.download.start().addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

        def install(self, fplug):
                checkfile = '/tmp/download.ipk'
                if os.path.exists(checkfile):
                        cmd1 = "opkg install --force-overwrite " + checkfile
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def cancel(self, result = None):
                self.close(None)
                return



class plugins(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodilite by pcd')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                self['pth'].setText(_('Support on'))
                self['pform'] = Label('')
                self['pform'].setText(_('linuxsat-support.com '))
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3BsdWdpbnMv")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="(.*?)">.*?</a>(.*?)20(.*?) '
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date, date2 in match:
                                if 'zip' in url:
                                        url64b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20=")
                                        url = url64b + url
                                        url264b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3BsdWdpbnMv")
                                        name = url.replace(url264b, '')
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("-", " ")
                                        name = name.replace("_", " ")
                                        print('name: ', name)
                                        name = name +'-'+ date.replace(' ','') + date2
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                                else:
                                        self['info'].setText(_('Please select ...'))

                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                self['info'].setText(_('... please wait'))
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/download.zip"
                                print("url =", url)
                                self.download = downloadWithProgress(url, dest)
                                self.download.addProgress(self.downloadProgress)
                                self.download.start().addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))


        def install(self, fplug):
                checkfile = '/tmp/download.zip'
                fdest = KodilitePcd + "/plugins"
                if os.path.exists(checkfile):
                        cmd1 = "unzip -o -q '" + checkfile + "' -d '" + fdest + "'"
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def cancel(self, result = None):
                self.close(None)
                return

class plugins_adult(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodilite by pcd')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                self['pth'].setText(_('Support on'))
                self['pform'] = Label('')
                self['pform'].setText(_('linuxsat-support.com '))
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun1,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3BsdWdpbmFkdWx0Lw==")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="(.*?)">.*?</a>(.*?)20(.*?) '
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date, date2 in match:
                                if 'zip' in url:
                                        url64b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20=")
                                        url = url64b + url
                                        url264b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3BsdWdpbmFkdWx0Lw==")
                                        name = url.replace(url264b, '')
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("-", " ")
                                        name = name.replace("_", " ")
                                        print('name: ', name)
                                        name = name +'-'+ date.replace(' ','') + date2
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                                else:
                                        self['info'].setText(_('Please select ...'))

                        showlist(self.names, self['text'])
                        self.downloading = True

                except:
                        self.downloading = False

        def okRun1(self):
                adult = 'Adult'
                if adult.lower() in name:
                        self.catname = name
                        self.allow()
                else:
                        self.okRun()
                        self.close()

        def allow(self):
                if config.ParentalControl.configured.value :
                        from Screens.InputBox import InputBox, PinInput
                        self.session.openWithCallback(self.pinEntered, PinInput, pinList = [config.ParentalControl.setuppin.value], triesEntry = config.ParentalControl.retries.servicepin, title = _("Please enter the parental control pin code"), windowTitle = _("Enter pin code"))
                else:
                         self.pinEntered(True)

        def pinEntered(self, result):
                if result:
                        self.okRun()
                else:
                        self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
                        self.close()


        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                self['info'].setText(_('... please wait'))
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/download.zip"
                                print("url =", url)
                                self.download = downloadWithProgress(url, dest)
                                self.download.addProgress(self.downloadProgress)
                                self.download.start().addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

        def install(self, fplug):
                checkfile = '/tmp/download.zip'
                fdest = KodilitePcd + "/plugins"
                if os.path.exists(checkfile):
                        cmd1 = "unzip -o -q '" + checkfile + "' -d '" + fdest + "'"
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def cancel(self, result = None):
                self.close(None)
                return

class script(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodilite by pcd')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                self['pth'].setText(_('Support on'))
                self['pform'] = Label('')
                self['pform'].setText(_('linuxsat-support.com '))
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3NjcmlwdC8=")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="(.*?)">.*?</a>(.*?)20(.*?) '
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date, date2 in match:
                                if 'zip' in url:
                                        url64b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20=")
                                        url = url64b + url
                                        url264b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3NjcmlwdC8=")
                                        name = url.replace(url264b, '')
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("-", " ")
                                        name = name.replace("_", " ")
                                        print('name: ', name)
                                        name = name +'-'+ date.replace(' ','') + date2
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                                else:
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False

        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                self['info'].setText(_('... please wait'))
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/download.zip"
                                print("url =", url)
                                self.download = downloadWithProgress(url, dest)
                                self.download.addProgress(self.downloadProgress)
                                self.download.start().addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

        def install(self, fplug):
                checkfile = '/tmp/download.zip'
                fdest = KodilitePcd + "/scripts"
                if os.path.exists(checkfile):
                        cmd1 = "unzip -o -q '" + checkfile + "' -d '" + fdest + "'"
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def cancel(self, result = None):
                self.close(None)
                return


class repository(Screen):

        def __init__(self, session):
                self.session = session
                skin = skin_path + 'tvall.xml'
                with open(skin, 'r') as f:
                        self.skin = f.read()
                self.setup_title = ('Kodilite by pcd')
                Screen.__init__(self, session)
                self.setTitle(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self.list = []
                self['text'] = tvList([])
                self.addon = 'emu'
                self.icount = 0
                self['info'] = Label(_('Load selected filter list, please wait ...'))
                self['pth'] = Label('')
                self['pth'].setText(_('Support on'))
                self['pform'] = Label('')
                self['pform'].setText(_('linuxsat-support.com '))
                self['progress'] = ProgressBar()
                self['progresstext'] = StaticText()
                self['key_green'] = Button(_('Install'))
                self['key_red'] = Button(_('Back'))
                self['key_yellow'] = Button(_(''))
                self["key_blue"] = Button(_(''))
                self['key_yellow'].hide()
                self['key_blue'].hide()
                self.downloading = False
                self.timer = eTimer()
                self.timer.start(500, 1)
                if isDreamOS:
                        self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
                else:
                        self.timer.callback.append(self.downxmlpage)
                self['title'] = Label(_('..:: TiVuStream Addons V. %s ::..' % currversion))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                 'green': self.okRun,
                 'red': self.close,
                 'cancel': self.close}, -2)

        def downxmlpage(self):
                url = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3JlcG9zaXRvcnkv")
                getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

        def errorLoad(self, error):
                print(str(error))
                self['info'].setText(_('Try again later ...'))
                self.downloading = False

        def _gotPageLoad(self, data):
                self.xml = data
                self.names = []
                self.urls = []
                try:
                        regex = '<a href="(.*?)">.*?</a>(.*?)20(.*?) '
                        match = re.compile(regex,re.DOTALL).findall(self.xml)
                        for url, date, date2 in match:
                                if 'zip' in url:
                                        url64b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20=")
                                        url = url64b + url
                                        url264b = base64.b64decode("aHR0cHM6Ly9wYXRidXdlYi5jb20vcGFuZWwtYWRkb25zL0VuaWdtYU9FMi4wL2tvZGlsaXRlL3JlcG9zaXRvcnkv")
                                        name = url.replace(url264b, '')
                                        name = name.replace(".zip", "")
                                        name = name.replace("%20", " ")
                                        name = name.replace("-", " ")
                                        name = name.replace("_", " ")
                                        print('name: ', name)
                                        name = name +'-'+ date.replace(' ','') + date2
                                        self.urls.append(url)
                                        self.names.append(name)
                                        self['info'].setText(_('Please select ...'))
                                else:
                                        self['info'].setText(_('Please select ...'))
                        showlist(self.names, self['text'])
                        self.downloading = True
                except:
                        self.downloading = False


        def okRun(self):
                self.session.openWithCallback(self.okInstall,tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

        def okInstall(self, result):
                self['info'].setText(_('... please wait'))
                if result:
                        if self.downloading == True:
                                selection = str(self['text'].getCurrent())
                                idx = self["text"].getSelectionIndex()
                                self.name = self.names[idx]
                                url = self.urls[idx]
                                dest = "/tmp/download.zip"
                                print("url =", url)
                                self.download = downloadWithProgress(url, dest)
                                self.download.addProgress(self.downloadProgress)
                                self.download.start().addCallback(self.install).addErrback(self.showError)
                        else:
                                self.close

        def downloadProgress(self, recvbytes, totalbytes):
                self['progress'].value = int(100 * recvbytes / float(totalbytes))
                self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))


        def install(self, fplug):
                checkfile = '/tmp/download.zip'
                fdest = KodilitePcd + "/repos"
                if os.path.exists(checkfile):
                        cmd1 = "unzip -o -q '" + checkfile + "' -d '" + fdest + "'"
                        cmd = []
                        cmd.append(cmd1)
                        title = _("Installation")
                        self.session.open(tvConsole,_(title),cmd, finishedCallback=deletetmp)
                self['info'].setText(_('Please select ...'))
                self['progresstext'].text = ''
                self.progclear = 0
                self['progress'].setValue(self.progclear)

        def showError(self, error):
                                print("download error =", error)
                                self.close()

        def cancel(self, result = None):
                self.close(None)
                return

def main(session, **kwargs):
        if checkInternet():
                # if isDreamOS:
                        session.open(Hometv)
                # else:
                        # session.open(logoStrt)
        else:
                session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def menu(menuid, **kwargs):
        if menuid == 'mainmenu':
                return [(_('TiVuStream Addons'),
                  main,
                  'TiVuStream Panel',
                  44)]
        return []


def cfgmain(menuid):
        if menuid == 'mainmenu':
                return [('TiVuStream Addons',
                  main,
                  'TiVuStream Panel',
                  44)]
        else:
                return []

def mainmenu(session, **kwargs):
        main(session, **kwargs)

def StartSetup(menuid):
        if menuid == 'setup':
                return [('TiVuStream Addons',
                  main,
                  'TiVuStream Panel',
                  44)]
        else:
                return []

extDescriptor = PluginDescriptor(name='TiVuStream Panel', description=_('TiVuStream Addons'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=ico_path, fnc=main)
mainDescriptor = PluginDescriptor(name='TiVuStream Panel', description=_('TiVuStream Addons V.' + currversion), where=PluginDescriptor.WHERE_MENU, icon=ico_path, fnc=cfgmain)
strtstDescriptor = PluginDescriptor(name=_('TiVuStream Panel'), description=_('TiVuStream Addons'), where=PluginDescriptor.WHERE_MENU, icon=ico_path, fnc=StartSetup)

def Plugins(**kwargs):
        ico_path = 'logo.png'
        if not isDreamOS:
                ico_path = plugin_path + '/res/pics/logo.png'
        result = [PluginDescriptor(name='TiVuStream Panel', description=_('TiVuStream Addons V.' + currversion), where=[PluginDescriptor.WHERE_PLUGINMENU], icon=ico_path, fnc=main)]
        if config.plugins.tvPanel.strtext.value:
                result.append(extDescriptor)
        if config.plugins.tvPanel.strtmain.value:
                result.append(mainDescriptor)
        if config.plugins.tvPanel.strtst.value:
                result.append(strtstDescriptor)
        return result

def terrestrial():
        SavingProcessTerrestrialChannels = StartSavingTerrestrialChannels()
        # # run a rescue reload
        import time
        now = time.time()
        ttime = time.localtime(now)
        tt = str('{0:02d}'.format(ttime[2])) + str('{0:02d}'.format(ttime[1])) + str(ttime[0])[2:] + '_' + str('{0:02d}'.format(ttime[3])) + str('{0:02d}'.format(ttime[4])) + str('{0:02d}'.format(ttime[5]))
        os.system('tar -czvf /tmp/' + tt + '_enigma2settingsbackup.tar.gz' + ' -C / /etc/enigma2/*.tv /etc/enigma2/*.radio /etc/enigma2/lamedb')

        if SavingProcessTerrestrialChannels:
                        print('ok')
        return

def terrestrial_rest():
        if LamedbRestore():
                TransferBouquetTerrestrialFinal()
                icount = 0
                terrr = plugin_path + '/temp/TerrestrialChannelListArchive'
                if os.path.exists(terrr):
                        os.system("cp -rf " + plugin_path + "/temp/TerrestrialChannelListArchive /etc/enigma2/userbouquet.terrestrial.tv")
                os.system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                with open('/etc/enigma2/bouquets.tv', 'r+') as f:
                        bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.terrestrial.tv" ORDER BY bouquet\n'
                        if bouquetTvString not in f:
                                new_bouquet = open('/etc/enigma2/new_bouquets.tv', 'w')
                                new_bouquet.write('#NAME User - bouquets (TV)\n')
                                new_bouquet.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.terrestrial.tv" ORDER BY bouquet\n')
                                file_read = open('/etc/enigma2/bouquets.tv').readlines()
                                for line in file_read:
                                        if line.startswith("#NAME"):
                                                continue
                                        new_bouquet.write(line)
                                new_bouquet.close()
                                os.system('cp -rf /etc/enigma2/bouquets.tv /etc/enigma2/backup_bouquets.tv')
                                os.system('mv -f /etc/enigma2/new_bouquets.tv /etc/enigma2/bouquets.tv')
                lcnstart()

def lcnstart():
        print(' lcnstart ')
        if os.path.exists('/etc/enigma2/lcndb'):
                lcn = LCN()
                lcn.read()
                if len(lcn.lcnlist) > 0:
                        lcn.writeBouquet()
                        ReloadBouquet()
        return

def StartSavingTerrestrialChannels():

        def ForceSearchBouquetTerrestrial():
                for file in sorted(glob.glob("/etc/enigma2/*.tv")):
                  if 'tivustream' in file:
                          continue
                  f = open(file, "r").read()
                  x = f.strip().lower()


                  if x.find('http'):
                          continue


                  if x.find('eeee0000')!= -1:
                        if x.find('82000') == -1 and x.find('c0000') == -1:
                          return file
                          break
                return

        def ResearchBouquetTerrestrial(search):
                for file in sorted(glob.glob("/etc/enigma2/*.tv")):
                  if 'tivustream' in file:
                                  continue
                  f = open(file, "r").read()
                  x = f.strip().lower()
                  x1 = f.strip()
                  if x1.find("#NAME") != -1:
                        if x.lower().find((search.lower())) != -1:

                          if x.find('http'):
                                        continue

                          if x.find('eeee0000')!= -1:
                                        return file
                                        break
                return

        def SaveTrasponderService():
                TrasponderListOldLamedb = open(plugin_path +'/temp/TrasponderListOldLamedb', 'w')
                ServiceListOldLamedb = open(plugin_path +'/temp/ServiceListOldLamedb', 'w')
                Trasponder = False
                inTransponder = False
                inService = False
                try:
                  LamedbFile = open('/etc/enigma2/lamedb')
                  while 1:
                        line = LamedbFile.readline()
                        if not line: break
                        if not (inTransponder or inService):
                          if line.find('transponders') == 0:
                                        inTransponder = True
                          if line.find('services') == 0:
                                        inService = True
                        if line.find('end') == 0:
                          inTransponder = False
                          inService = False
                        line = line.lower()
                        if line.find('eeee0000') != -1:
                          Trasponder = True
                          if inTransponder:
                                        TrasponderListOldLamedb.write(line)
                                        line = LamedbFile.readline()
                                        TrasponderListOldLamedb.write(line)
                                        line = LamedbFile.readline()
                                        TrasponderListOldLamedb.write(line)
                          if inService:
                                        tmp = line.split(':')
                                        ServiceListOldLamedb.write(tmp[0] +":"+tmp[1]+":"+tmp[2]+":"+tmp[3]+":"+tmp[4]+":0\n")
                                        line = LamedbFile.readline()
                                        ServiceListOldLamedb.write(line)
                                        line = LamedbFile.readline()
                                        ServiceListOldLamedb.write(line)
                  TrasponderListOldLamedb.close()
                  ServiceListOldLamedb.close()
                  if not Trasponder:
                                os.system('rm -fr '+plugin_path +'/temp/TrasponderListOldLamedb')
                                os.system('rm -fr '+plugin_path +'/temp/ServiceListOldLamedb')
                except:
                                pass
                return Trasponder

        def CreateBouquetForce():
                WritingBouquetTemporary = open(plugin_path +'/temp/TerrestrialChannelListArchive','w')
                WritingBouquetTemporary.write('#NAME Digitale Terrestre\n')
                ReadingTempServicelist = open(plugin_path +'/temp/ServiceListOldLamedb').readlines()
                for jx in ReadingTempServicelist:
                  if jx.find('eeee') != -1:
                                 String = jx.split(':')
                                 WritingBouquetTemporary.write('#SERVICE 1:0:%s:%s:%s:%s:%s:0:0:0:\n'% (hex(int(String[4]))[2:],String[0],String[2],String[3],String[1]))
                WritingBouquetTemporary.close()

        def SaveBouquetTerrestrial():
                NameDirectory = ResearchBouquetTerrestrial('terr')
                if not NameDirectory:
                  NameDirectory = ForceSearchBouquetTerrestrial()
                try:
                  shutil.copyfile(NameDirectory,plugin_path +'/temp/TerrestrialChannelListArchive')
                  return True
                except :
                  pass
                return
        Service = SaveTrasponderService()
        if Service:
          if not SaveBouquetTerrestrial():
                        CreateBouquetForce()
          return True
        return

def LamedbRestore():
        try:
            TrasponderListNewLamedb = open(plugin_path +'/temp/TrasponderListNewLamedb', 'w')
            ServiceListNewLamedb = open(plugin_path +'/temp/ServiceListNewLamedb', 'w')
            inTransponder = False
            inService = False
            infile = open("/etc/enigma2/lamedb")
            while 1:
                line = infile.readline()
                if not line: break
                if not (inTransponder or inService):
                    if line.find('transponders') == 0:
                        inTransponder = True
                    if line.find('services') == 0:
                        inService = True
                    if line.find('end') == 0:
                        inTransponder = False
                        inService = False
                    if inTransponder:
                        TrasponderListNewLamedb.write(line)
                    if inService:
                        ServiceListNewLamedb.write(line)
            TrasponderListNewLamedb.close()
            ServiceListNewLamedb.close()
            WritingLamedbFinal=open("/etc/enigma2/lamedb", "w")
            WritingLamedbFinal.write("eDVB services /4/\n")
            TrasponderListNewLamedb = open(plugin_path +'/temp/TrasponderListNewLamedb').readlines()
            for x in TrasponderListNewLamedb:
                 WritingLamedbFinal.write(x)
            try:
                TrasponderListOldLamedb = open(plugin_path +'/temp/TrasponderListOldLamedb').readlines()
                for x in TrasponderListOldLamedb:
                    WritingLamedbFinal.write(x)
            except:
                pass
            WritingLamedbFinal.write("end\n")
            ServiceListNewLamedb = open(plugin_path +'/temp/ServiceListNewLamedb').readlines()
            for x in ServiceListNewLamedb:
                WritingLamedbFinal.write(x)
            try:
                ServiceListOldLamedb = open(plugin_path +'/temp/ServiceListOldLamedb').readlines()
                for x in ServiceListOldLamedb:
                    WritingLamedbFinal.write(x)
            except:
                pass
            WritingLamedbFinal.write("end\n")
            WritingLamedbFinal.close()
            return True
        except:
            return False

def TransferBouquetTerrestrialFinal():

        def RestoreTerrestrial():
                for file in os.listdir("/etc/enigma2/"):
                    if re.search('^userbouquet.*.tv', file):
                        f = open("/etc/enigma2/" + file, "r")
                        x = f.read()
                    if re.search("#NAME Digitale Terrestre",x, flags=re.IGNORECASE):
                        return "/etc/enigma2/"+file
                    else:
                        return  "/etc/enigma2/userbouquet.terrestrial.tv"
                return
        try:
                TerrestrialChannelListArchive = open(plugin_path +'/temp/TerrestrialChannelListArchive').readlines()
                DirectoryUserBouquetTerrestrial = RestoreTerrestrial()
                if DirectoryUserBouquetTerrestrial:
                    TrasfBouq = open(DirectoryUserBouquetTerrestrial,'w')
                    for Line in TerrestrialChannelListArchive:
                        if Line.lower().find('#name') != -1 :
                            TrasfBouq.write('#NAME Digitale Terrestre\n')
                        else:
                            TrasfBouq.write(Line)
                    TrasfBouq.close()
                return True
        except:
                return False
        return
#======================================================

