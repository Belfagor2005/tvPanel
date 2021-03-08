#!/usr/bin/python
# -*- coding: utf-8 -*-
#--------------------#
#  coded by Lululla  #
#   skin by MMark    #
#     07/03/2021     #
#--------------------#
#Info http://t.me/tivustream
# from __future__ import print_function
from . import _
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
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_PLUGINS
from Tools.Directories import pathExists, fileExists, copyfile
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, getDesktop, loadPNG
from enigma import eListbox, eTimer, eListboxPythonMultiContent, eConsoleAppContainer, gFont
from os import path, listdir, remove, mkdir, access, X_OK, chmod
from os.path import splitext
from twisted.web.client import downloadPage, getPage
from xml.dom import Node, minidom
import base64
import os
import re
import sys
import shutil
import ssl
import socket
import glob
import subprocess
from sys import version_info
from Lcn import *
# try:
    # import commands
# except ImportError:
    # import subprocess
global skin_path, mmkpicon, isDreamOS, set, regexC, regexL
headers        = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
                 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }

currversion      = '2.0.0'
title_plug       = '..:: TiVuStream Addons Panel V. %s ::..' % currversion
name_plug        = 'TiVuStream Addon Panel'



PY3 = version_info[0] == 3
if PY3:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError

    from urllib.parse import urlencode, quote                                             
    from urllib.request import urlretrieve
    from urllib.parse import urlparse
else:
    from urllib2 import urlopen, Request
    from urllib2 import URLError, HTTPError                                           
    from urllib import urlencode, quote                                       
    from urllib import urlretrieve
    from urlparse import urlparse


if sys.version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None

def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context= sslContext)
    else:
        return urlopen(url)

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


# try:
    # _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
    # pass
# else:
    # ssl._create_default_https_context = _create_unverified_https_context


#--------------------#
# Small test program #
#--------------------#
def checkStr(txt):
    if PY3:
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')
    return txt

def checkInternet():
    try:
        response = checkStr(urlopen("http://google.com", None, 5))
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True

def checkMyFile(url):
    try:
        # dest = "/tmp/download.zip"
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        req.add_header('Referer', 'https://www.mediafire.com/')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        page = urlopen(req)
        r = page.read()
        n1 = r.find('"Download file"', 0)
        n2 = r.find('Repair your download', n1)
        r2 = r[n1:n2]
        myfile = re.findall('href="http://download(.*?)">', r2)

        return myfile
    except:
        return ''

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

#================config
config.plugins.tvaddon = ConfigSubsection()
config.plugins.tvaddon.strtext = ConfigYesNo(default=True)
config.plugins.tvaddon.mmkpicon = ConfigDirectory(default='/media/hdd/picon/')
config.plugins.tvaddon.strtmain = ConfigYesNo(default=True)
config.plugins.tvaddon.ipkpth = ConfigSelection(default = "/tmp",choices = mountipkpth())
config.plugins.tvaddon.autoupd = ConfigYesNo(default=False)

pblk = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT1vdnowNG1ycHpvOXB3JmNvbnRlbnRfdHlwZT1mb2xkZXJzJmNodW5rX3NpemU9MTAwMCZyZXNwb25zZV9mb3JtYXQ9anNvbg=='
ptrs = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT10dmJkczU5eTlocjE5JmNvbnRlbnRfdHlwZT1mb2xkZXJzJmNodW5rX3NpemU9MTAwMCZyZXNwb25zZV9mb3JtYXQ9anNvbg=='
ptmov = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT1uazh0NTIyYnY0OTA5JmNvbnRlbnRfdHlwZT1maWxlcyZjaHVua19zaXplPTEwMDAmcmVzcG9uc2VfZm9ybWF0PWpzb24='
host_trs        = base64.b64decode(ptrs)
host_blk        = base64.b64decode(pblk)
host_mov        = base64.b64decode(ptmov)

HD               = getDesktop(0).size()
# plugin_path      = os.path.dirname(sys.modules[__name__].__file__)
plugin_path      = '/usr/lib/enigma2/python/Plugins/Extensions/tvaddon'
skin_path        = plugin_path
ico_path         = plugin_path + '/logo.png'
pngx             = plugin_path + '/res/pics/plugins.png'
pngl             = plugin_path + '/res/pics/plugin.png'
pngs             = plugin_path + '/res/pics/setting.png'
no_cover         = plugin_path + '/no_coverArt.png'
mmkpicon         = config.plugins.tvaddon.mmkpicon.value.strip()
regexC           = '<plugins cont="(.*?)"'
regexL           = '<a href="(.*?)">(.*?)</a>.*?(.*?)-(.*?)-(.*?) '

#<img src="/_autoindex/icons/unknown.png" alt="unknown"> <a href="/panel-addons/EnigmaOE2.0/kodilite/enigma2-plugin-extensions-kodilite_6.0_r0_all.ipk">enigma2-plugin-extensions-kodilite_6.0_r0_all.ipk</a> 
#======================================================config

os.system('rm -fr ' + plugin_path + '/temp/*')

if mmkpicon.endswith('/'):
    mmkpicon = mmkpicon[:-1]
if not os.path.exists(mmkpicon):
    try:
        os.makedirs(mmkpicon)
    except OSError as e:
        print(('Error creating directory %s:\n%s') % (mmkpicon, str(e)))
print('****************************************path Picons: ', mmkpicon)
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

Panel_list = [
 _('LULULLA CORNER'),
 _('DEBIAN DREAMOS'),
 _('DAILY PICONS'),
 _('DAILY SETTINGS'), 
 _('KODILITE BY PCD'),
 _('DEPENDENCIES'),
 _('DRIVERS'),
 _('PLUGIN BACKUP'),
 _('PLUGIN EPG'),
 _('PLUGIN EMULATORS CAMS'),
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
 ('SETTINGS BI58'),
 ('SETTINGS CIEFP'),
 ('SETTINGS CYRUS'), 
 ('SETTINGS COLOMBO'),
 ('SETTINGS MANUTEK'),
 ('SETTINGS MILENKA61'),
 ('SETTINGS MORPHEUS'),
 ('SETTINGS PREDRAG'),
 ('SETTINGS VHANNIBAL'),
 ('UPDATE SATELLITES.XML'),
 ('UPDATE TERRESTRIAL.XML')
 ]

Panel_list3 = [
 _('MMARK PICONS BLACK'),
 _('MMARK PICONS TRANSPARENT'),
 _('MMARK PICONS MOVIE'),
 _('COLOMBO PICONS')]

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
            self.l.setItemHeight(50)

def OnclearMem():
    try:
        os.system("sync")
        os.system("echo 1 > /proc/sys/vm/drop_caches")
        os.system("echo 2 > /proc/sys/vm/drop_caches")
        os.system("echo 3 > /proc/sys/vm/drop_caches")
    except:
        pass

def DailyListEntry(name, idx):
    res = [name]
    if HD.width() > 1280:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png =loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=7, text =name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))
    return res

def oneListEntry(name):
    res = [name]
    if HD.width() > 1280:
        res.append(MultiContentEntryPixmapAlphaTest(pos =(10, 12), size =(34, 25), png =loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size =(1900, 50), font =7, text =name, color = 0xa6d1fe, flags =RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos =(10, 6), size =(34, 25), png =loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size =(1000, 50), font=2, text =name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))
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
        self['text'] = tvList([])
        # self.working = False
        # self.selection = 'all'
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
            destr = plugin_path + '/update.txt'
            req = Request(upd_path + 'updatePanel.txt')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
            fp = checkStr(urlopen(req))
            fp = fp.read()
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
        self['title'] = Label(_(title_plug))
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
        try:
            import requests
            from PIL import Image
        except:
            dependencies = False
        if dependencies is False:
            chmod("/usr/lib/enigma2/python/Plugins/Extensions/tvaddon/dependencies.sh", 0o0755)
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/tvaddon/dependencies.sh"
            self.session.openWithCallback(self.starts, Console, title ="Checking Python Dependencies", cmdlist =[cmd1], closeOnSuccess =False)
        else:
            self.starts()

    def starts(self):
        OnclearMem()

    def closerm(self):
        # plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self.timer = eTimer()
        self.timer.start(1000, True)
        try:
            self.timer.callback.append(deletetmp)
        except:
            self.timer_conn = self.timer.timeout.connect(deletetmp)
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
            list.append(DailyListEntry(x, idx))
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
        if sel == _('DEBIAN DREAMOS'):
            self.session.open(debian)
        elif sel == _('DRIVERS'):
            self.session.open(Drivers)
        elif sel == _('DEPENDENCIES'):
            self.session.open(Dependencies)
        elif sel == _('DAILY PICONS'):
            self.session.open(SelectPicons)
        elif sel == _('DAILY SETTINGS'):
            self.session.open(tvDailySetting)
        elif sel == _('KODILITE BY PCD'):
            self.session.open(mainkodilite)
        elif sel == _('PLUGIN BACKUP'):
            self.session.open(PluginBackup)
        elif sel == _('PLUGIN EMULATORS CAMS'):
            self.session.open(PluginEmulators)
        elif sel == _('PLUGIN EPG'):
            self.session.open(PluginEpg)
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
        elif sel == _('PLUGIN SKINS'):
            self.session.open(PluginSkins)
        elif sel == _('PLUGIN SPORT'):
            self.session.open(PluginSport)
        elif sel == _('PLUGIN UTILITY'):
            self.session.open(PluginUtility)
        elif sel == _('PLUGIN WEATHER'):
            self.session.open(PluginWeather)
        elif sel == _('LULULLA CORNER'):
            self.session.open(PluginLululla)            

    def msgupdate1(self):
        if self.Update == False :
            return
        if config.plugins.tvaddon.autoupd.value == False :
            return
        else:
            self.session.openWithCallback(self.runupdate, tvMessageBox, (_('New update available!!\nDo you want update plugin ?\nPlease Reboot GUI after install!')), tvMessageBox.TYPE_YESNO)

    def runupdate(self, result):
        if result:
            if isDreamOS:
                com = dmlink
                dom = 'New version ' + self.version
                os.system('wget %s -O /tmp/tvaddon.tar > /dev/null' % com)
                os.system('sleep 3')
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['tar -xvf /tmp/tvaddon.tar -C /'], finishedCallback = self.msgipkrst1) #, closeOnSuccess =False)
            else:
                com = link
                dom = 'New Version ' + self.version
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['opkg install %s' % com], finishedCallback = self.msgipkrst1) #, closeOnSuccess =False)

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
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()


class PluginLululla(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Lululla Corner')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = xml_path + 'lululla.xml'
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['info'].setText(_('Try again later ...'))
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()


class Dependencies(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Dependencies')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class Picons(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Picons')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))        
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginBackup(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Backup')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))        
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                # selection = str(self['text'].getCurrent())
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginEmulators(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Emulators')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))        
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginEpg(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Epg')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()


class PluginMultimedia(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Multimedia')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginMultiboot(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Multiboot')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginPpanel(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Ppanel')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginSettings(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Settings')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginSkins(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Skins')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginSport(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Sport')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()


class PluginUtility(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Utility')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class PluginWeather(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Plugin Weather')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class debian(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Debian')
        Screen.__init__(self, session)
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        if self.downloading == True:
            try:
                idx = self["text"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except:
                return
        else:
            self.close()

class tvDailySetting(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Daily Setting')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self['text'] = tvList([])
        # self.working = False
        # self.selection = 'all'
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['info'] = Label('')
        self['info'].setText(_('Getting the list, please wait ...'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_('Lcn'))
        if isDreamOS:
                self['key_yellow'].hide()
        self["key_blue"] = Button(_(''))
        self['key_blue'].hide()
        self['title'] = Label(_(title_plug))
        self['actions'] = NumberActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
         'green': self.okRun,
         'back': self.closerm,
         'red': self.closerm,
         'yellow': self.Lcn,
         'cancel': self.closerm}, -1)
        self.onLayoutFinish.append(self.updateMenuList)

    def Lcn(self):
        self.mbox = self.session.open(tvMessageBox, _('Reorder Terrestrial channels with Lcn rules'), tvMessageBox.TYPE_INFO, timeout=5)
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
        self['info'].setText(_('Please select ...'))

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
        elif sel == ('SETTINGS CYRUS'):
            self.session.open(SettingCyrus)            
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
        self.session.openWithCallback(self.okSatInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okSatInstall(self, result):
        if result:
            if checkInternet():
                try:
                    url_sat_oealliance              = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
                    link_sat = ssl_urlopen(url_sat_oealliance)
                    dirCopy = '/etc/tuxbox/satellites.xml'
                    # urlretrieve(url_sat_oealliance, dirCopy, context= ssl._create_unverified_context())
                    urlretrieve(link_sat, dirCopy)
                    self.mbox = self.session.open(tvMessageBox, _('Satellites.xml Updated!'), tvMessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation done !!!'))
                except:
                    return
            else:
                session.open(tvMessageBox, "No Internet", tvMessageBox.TYPE_INFO)

    def okTERRESTRIAL(self):
        self.session.openWithCallback(self.okTerrInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okTerrInstall(self, result):
        if result:
            if checkInternet():
                try:
                    url_sat_oealliance              = 'https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/terrestrial.xml'
                    link_ter = ssl_urlopen(url_sat_oealliance)
                    dirCopy                         = '/etc/tuxbox/terrestrial.xml'
                    # urlretrieve(url_sat_oealliance, dirCopy, context= ssl._create_unverified_context())
                    urlretrieve(link_ter, dirCopy) # , context= ssl._create_unverified_context())
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
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
                if 'zip' in url.lower():
                    if 'setting' in url.lower():
                        if '.php' in url.lower():
                            continue
                        name = url
                        url64b = base64.b64decode("aHR0cDovL2NvbG9tYm8uYWx0ZXJ2aXN0YS5vcmc=")
                        url = url64b + url
                        print('url: ', url)
                        name = name.replace("/colombo/colombo/", "")
                        name = name.replace(".zip", "")
                        name = name.replace("%20", " ")
                        name = name.replace("_", " ")
                        name = name.replace("-", " ")
                        self.urls.append(url)
                        self.names.append(name)
                        self.downloading = True
                        self['info'].setText(_('Please select ...'))
                    else:
                        self['info'].setText(_('no data ...'))
                        self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            print('downloading = ', self.downloading)
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()

                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.zip'):
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
                self.session.open(tvConsole, _(title), cmd)
                if not isDreamOS:
                    self.onShown.append(resettings)


class SettingVhan(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Vhannibal')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
                if 'zip' in url.lower():
                    if '.php' in url.lower():
                        continue
                    name = "Vhannibal" + url
                    name = name.replace(".zip", "")
                    name = name.replace("%20", " ")
                    url64b = base64.b64decode("aHR0cDovL3NhdC5hbGZhLXRlY2gubmV0L3VwbG9hZC9zZXR0aW5ncy92aGFubmliYWwvVmhhbm5pYmFs")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                self.name = self.names[idx]
                url = self.urls[idx]
                dest = "/tmp/settings.zip"

                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.zip'):
            os.system('rm -rf /etc/enigma2/lamedb')
            os.system('rm -rf /etc/enigma2/*.radio')
            os.system('rm -rf /etc/enigma2/*.tv')
            fdest1 = "/tmp"
            fdest2 = "/etc/enigma2"
            cmd1 = "unzip -o -q '/tmp/settings.zip' -d " + fdest1
            cmd2 = "cp -rf  '/tmp/" + self.name + "'/* " + fdest2
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
            self.session.open(tvConsole, _(title), cmd)
            if not isDreamOS:
                self.onShown.append(resettings)

class Milenka61(Screen):


    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Milenka61')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
            regex = '<a href="Satvenus(.*?)".*?align="right">(.*?)-(.*?)-(.*?) '
            match = re.compile(regex,re.DOTALL).findall(self.xml)
            for url, date1, date2, date3 in match:
                if url.find('.tar.gz') != -1 :
                    name = url.replace('Satvenus_EX-YU_Lista_za_milenka61_', '')
                    name = name + ' ' + date1 + '-' + date2 + '-' + date3
                    name = name.replace(".tar.gz", "")
                    name = name.replace("Satvenus", "").replace("milenka61 ", "")
                    name = name.replace("EX YU", "").replace("za", "")
                    name = name.replace("Lista", "").replace("%20", " ")
                    name = name.replace("-", " ").replace("_", " ")
                    url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvdGFyR3ovU2F0dmVudXM=")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.tar.gz'):
            os.system('rm -rf /etc/enigma2/lamedb')
            os.system('rm -rf /etc/enigma2/*.radio')
            os.system('rm -rf /etc/enigma2/*.tv')
            cmd1 = "tar -xvf /tmp/*.tar.gz -C /"

            cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
            cmd4 = "rm -rf /tmp/*.tar.gz"
            cmd = []
            cmd.append(cmd1)
            cmd.append(cmd3)
            cmd.append(cmd4)
            title = _("Installation Settings")
            self.session.open(tvConsole, _(title), cmd)
            if not isDreamOS:
                self.onShown.append(resettings)

class SettingManutek(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Manutek')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
                if 'zip' in url.lower():
                    name = url
                    name = name.replace(".zip", "")
                    name = name.replace("%20", " ")
                    name = name.replace("NemoxyzRLS_", "")
                    name = name.replace("_", " ")
                    url64b = base64.b64decode("aHR0cDovL3d3dy5tYW51dGVrLml0L2lzZXR0aW5nL2VuaWdtYTIv")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.zip'):
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
                self.session.open(tvConsole, _(title), cmd)
            if not isDreamOS:
                self.onShown.append(resettings)


class SettingMorpheus(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Morpheus')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
                    name = name.replace("E2", "")
                    url64b = base64.b64decode("aHR0cDovL21vcnBoZXVzODgzLmFsdGVydmlzdGEub3JnL3NldHRpbmdzLw==")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                url= str(url)
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.zip'):
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
            self.session.open(tvConsole, _(title), cmd)
        # deletetmp()
            if not isDreamOS:
                self.onShown.append(resettings)

class SettingCiefp(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Ciefp')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQ2llZnA=")
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
            regex = '<a href="ciefp(.*?)".*?align="right">(.*?)-(.*?)-(.*?) '
            match = re.compile(regex,re.DOTALL).findall(self.xml)
            for url,date1, date2, date3 in match:
                if 'tar.gz' in url:
                    name = url
                    name = name.replace('-e2-settings-', 'Ciefp ')
                    name = name + ' ' + date1 + '-' + date2 + '-' + date3
                    name = name.replace(".tar.gz", "")
                    name = name.replace("%20", " ")
                    url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQ2llZnAvY2llZnA=")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.tar.gz'):
            os.system('rm -rf /etc/enigma2/lamedb')
            os.system('rm -rf /etc/enigma2/*.radio')
            os.system('rm -rf /etc/enigma2/*.tv')
            cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
            cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
            cmd4 = "rm -rf /tmp/*.tar.gz"
            cmd = []
            cmd.append(cmd1)
            cmd.append(cmd3)
            cmd.append(cmd4)
            title = _("Installation Settings")
            self.session.open(tvConsole, _(title), cmd)
            if not isDreamOS:
                self.onShown.append(resettings)


class SettingBi58(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Bi58')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
            regex = '<a href="bi58-e2(.*?)".*?align="right">(.*?)-(.*?)-(.*?) '
            match = re.compile(regex,re.DOTALL).findall(self.xml)
            for url, date1, date2, date3 in match:
                if url.find('.tar.gz') != -1 :
                    name = url.replace('-settings-','bi58 ')
                    name = name + ' ' + date1 + '-' + date2 + '-' + date3
                    name = name.replace(".tar.gz", "")
                    name = name.replace("%20", " ")
                    url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvQmk1OC9iaTU4LWUy")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.tar.gz'):
            os.system('rm -rf /etc/enigma2/lamedb')
            os.system('rm -rf /etc/enigma2/*.radio')
            os.system('rm -rf /etc/enigma2/*.tv')
            cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
            cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
            cmd4 = "rm -rf /tmp/*.tar.gz"
            cmd = []
            cmd.append(cmd1)
            cmd.append(cmd3)
            cmd.append(cmd4)
            title = _("Installation Settings")
            self.session.open(tvConsole, _(title), cmd)
            if not isDreamOS:
                self.onShown.append(resettings)


class SettingPredrag(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Predrag')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
            regex = '<a href="predrag(.*?)".*?align="right">(.*?)-(.*?)-(.*?) '
            match = re.compile(regex,re.DOTALL).findall(self.xml)
            for url, date1, date2,date3 in match:
                if url.find('.tar.gz') != -1 :
                    name = url
                    name = name.replace('-settings-e2-','Predrag ')
                    name = name + date1 + '-' + date2 + '-' + date3
                    name = name.replace(".tar.gz", "")
                    url64b = base64.b64decode("aHR0cDovLzE3OC42My4xNTYuNzUvcGFuZWxhZGRvbnMvUHJlZHJAZy9wcmVkcmFn")
                    url = url64b + url
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.tar.gz'):
            os.system('rm -rf /etc/enigma2/lamedb')
            os.system('rm -rf /etc/enigma2/*.radio')
            os.system('rm -rf /etc/enigma2/*.tv')
            cmd1 = "tar -xvf /tmp/*.tar.gz -C /"
            cmd3 = "wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"
            cmd4 = "rm -rf /tmp/*.tar.gz"
            cmd = []
            cmd.append(cmd1)
            cmd.append(cmd3)
            cmd.append(cmd4)
            title = _("Installation Settings")
            self.session.open(tvConsole, _(title), cmd)
            if not isDreamOS:
                self.onShown.append(resettings)

class SettingCyrus(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Cyrus')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['pth'] = Label('')
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = base64.b64decode("aHR0cDovL3d3dy5jeXJ1c3NldHRpbmdzLmNvbS9TZXRfMjlfMTFfMjAxMS9EcmVhbWJveC1JcEJveC9Db25maWcueG1s")
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
            n1 = data.find('name="Sat">', 0)
            n2 = data.find("/ruleset>", n1)
            data1 = data[n1:n2]
        
            regex = 'Name="(.*?)".*?Link="(.*?)".*?Date="(.*?)"><'
            match = re.compile(regex,re.DOTALL).findall(data1)
            for name, url, date in match:
                if url.find('.zip') != -1 :
                    if 'ddt' in name.lower():
                        continue
                    if 'Sat' in name.lower():
                        continue
                    name = name + ' ' + date
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                if 'dtt' not in url.lower():
                    if not isDreamOS:
                        set = 1
                        terrestrial()
                downloadPage(url, dest).addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def showError(self, error):
        print("download error =", error)
        self.close()

    def install(self, fplug):
        if os.path.exists('/tmp/settings.zip'):
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
            self.session.open(tvConsole, _(title), cmd)
        # deletetmp()
            if not isDreamOS:
                self.onShown.append(resettings)
                
class tvInstall(Screen):
    def __init__(self, session, data, name, selection = None):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
                self.skin = f.read()
        self.setup_title = ('Install')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.selection = selection
        self['info'] = Label()
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        list = []
        list.sort()
        self['info'].setText(_('... please wait'))
        n1 = data.find(name, 0)
        n2 = data.find("</plugins>", n1)
        data1 = data[n1:n2]
        self.names = []
        self.urls = []
        # regex = '<plugin name="(.*?)".*?url>"(.*?)"'                                              
        regex = '<plugin name="(.*?)".*?url>"(.*?)"</url'
        match = re.compile(regex,re.DOTALL).findall(data1)
        for name, url in match:
            self.names.append(name)
            self.urls.append(url)
        self['text'] = tvList([])
        self['info'].setText(_('Please install ...'))
        self['title'] = Label(_(title_plug))
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_('Download'))
        self["key_blue"] = Button(_(''))
        # self['key_yellow'].hide()
        self['key_blue'].hide()
        self['actions'] = ActionMap(['SetupActions',  'ColorActions'], {'ok': self.message,
         'green': self.message,
         'red': self.close,
         'yellow': self.okDown,
         'cancel': self.close}, -2)
        self.onLayoutFinish.append(self.start)

    def start(self):
        showlist(self.names, self['text'])

    def message(self):
        self.session.openWithCallback(self.selclicked, tvMessageBox,(_("Do you want to install?")), tvMessageBox.TYPE_YESNO)

    def selclicked(self, result):
        if result:
            idx = self["text"].getSelectionIndex()
            dom = self.names[idx]
            com = self.urls[idx]
            self.prombt(com, dom)

    def prombt(self, com, dom):
        useragent = {'User-Agent': 'Enigma2 - tvaddon Plugin'}
        # useragent = "--header='User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
        self.com = com
        n2 = self.com.rfind("/",0)
        dom = self.com[:n2]
        downplug = self.com.replace(dom,'').replace('/','').lower()
        print('commmm : ', com)
        print('n2 : ', n2)
        print('dommmm : ', dom)

        print('downplug : ', downplug)
        self['info'].setText(_('Installing ') + dom + _('... please wait'))
        if self.com != None:
                extensionlist = self.com.split('.')
                extension = extensionlist[-1].lower()
                if len(extensionlist) > 1:
                    tar = extensionlist[-2].lower()
                if extension in ["gz","bz2"] and tar == "tar":
                    self.command = ['']
                    if extension == "gz":
                        dest = '/tmp/' + downplug #+ '.gz'
                        self.command = [ "tar -xzvf " + dest + " -C /" ]
                    elif extension == "bz2":
                        self.command = [ "tar -xjvf " + dest + " -C /" ]
                        dest = '/tmp/' + downplug #+ '.bz2'
                    self.timer = eTimer()
                    self.timer.start(2000, True)
                    cmd = 'wget -q -O %s %s;' +  self.command[0] % (dest, str(self.com))
                    self.session.open(tvConsole, _('Downloading-installing: %s') % dom, [cmd] )
                    self['info'].setText(_('Installation done !!!'))
                elif extension == "deb":
                    if not isDreamOS:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation canceled!'))
                    else:
                        self.timer = eTimer()
                        self.timer.start(2000, True)
                        dest = '/tmp/' + downplug #+ '.deb'
                        cmd = 'wget -q -O %s %s;dpkg --install --force-overwrite %s' % (dest, str(self.com), dest)
                        self.session.open(tvConsole, _('Downloading-installing: %s') % dom, [cmd] )
                        self['info'].setText(_('Installation done !!!'))
                elif self.com.endswith(".ipk"):
                    if isDreamOS:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Installation canceled!'))
                    else:
                        dest = '/tmp/' + downplug #+ '.ipk'
                        self.timer = eTimer()
                        self.timer.start(2000, True)
                        cmd = 'wget -q -O %s %s;opkg install %s' % (dest, str(self.com), dest)
                        self.session.open(tvConsole, _('Downloading-installing: %s') % dom, [cmd] )
                        self['info'].setText(_('Installation done !!!'))

                elif self.com.endswith('.zip'):
                    if 'setting' in dom.lower():
                        if not isDreamOS:
                            set = 1
                            terrestrial()
                        if os.path.exists("/tmp/unzipped"):
                            os.system('rm -rf /tmp/unzipped')
                        os.makedirs('/tmp/unzipped')
                        cmd = []
                        cmd1 = 'unzip -o -q /tmp/settings.zip -d /tmp/unzipped'
                        cmd.append(cmd1)
                        cmd2 = 'rm -rf /etc/enigma2/lamedb'
                        cmd.append(cmd2)
                        cmd3 = 'rm -rf /etc/enigma2/*.radio'
                        cmd.append(cmd3)
                        cmd4 = 'rm -rf /etc/enigma2/*.tv'
                        cmd.append(cmd4)
                        cmd5 = 'cp -rf /tmp/unzipped/*.tv /etc/enigma2'
                        cmd.append(cmd5)
                        cmd6 = 'cp -rf /tmp/unzipped/*.radio /etc/enigma2'
                        cmd.append(cmd6)
                        cmd7 = 'cp -rf /tmp/unzipped/lamedb /etc/enigma2'
                        cmd.append(cmd7)
                        if not os.path.exists("/etc/enigma2/blacklist"):
                            cmd8 = 'cp -rf /tmp/unzipped/blacklist /etc/tuxbox/'
                            cmd.append(cmd8)
                        if not os.path.exists("/etc/enigma2/whitelist"):
                            cmd9 ='cp -rf /tmp/unzipped/whitelist /etc/tuxbox/'
                            cmd.append(cmd9)
                        cmd10 = 'cp -rf /tmp/unzipped/satellites.xml /etc/tuxbox/'
                        cmd.append(cmd10)
                        cmd11 = 'cp -rf /tmp/unzipped/terrestrial.xml /etc/tuxbox/'
                        cmd.append(cmd11)
                        if not isDreamOS:
                            terrestrial_rest()
                        self.reloadSettings2()
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        self.session.open(tvConsole, _('SETTING - install: %s') % dom, [cmd] )
                        self['info'].setText(_('Installation done !!!'))
                    elif 'picon' in dom.lower():
                        dest = '/tmp/picon.zip'
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        cmd = ['wget -q -O /tmp/picon.zip %s; unzip -o -q /tmp/picon.zip -d %s' %(str(self.com), mmkpicon)]
                        self.session.open(tvConsole, _('Downloading-installing: %s') % dom, [cmd] )
                        self['info'].setText(_('Installation done !!!'))
                    else:
                        self['info'].setText(_('Downloading the selected file in /tmp') + dom + _('... please wait'))
                        dest = '/tmp/' + downplug #+ '.zip'
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        cmd = ["wget %s -c '%s' -O '%s' > /dev/null" % (useragent, self.com, dest)]
                        self.session.open(tvConsole, _('Downloading-installing: %s') % dom, [cmd] )
                        self['info'].setText(_('Installation done !!!'))
                        self.mbox = self.session.open(tvMessageBox, _('Download file in /tmp successful!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Download file in /tmp successful!!'))
                else:
                    self['info'].setText(_('Download failed!') + dom + _('... Not supported'))
                return

    def cancel(self, result = None):
        self.close(None)

    def reloadSettings2(self):
        ReloadBouquet()
        self.mbox = self.session.open(tvMessageBox, _('Setting Installed!'), tvMessageBox.TYPE_INFO, timeout=5)
        self['info'].setText(_('Installation done !!!'))

    def startTimer(self):
        os.system('sleep 5')
        pass

    def okDown(self):
        self.session.openWithCallback(self.okDownload, tvMessageBox,(_("Do you want to Download?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okDownload(self, result):
        self['info'].setText(_('... please wait'))
        
        if result:
            idx = self["text"].getSelectionIndex()
            dom = self.names[idx]
            self.com = self.urls[idx]
            n2 = self.com.rfind("/",0)
            dom = self.com[:n2]
            print('dommmm : ', dom)
            downplug = self.com.replace('/','').lower()# .replace(dom,'')
            print('downplug : ', downplug)
            if self.com != None:
                global dest          
                dest = '/tmp/' + downplug
                extensionlist = self.com.split('.')
                print('extensionlist: ', extensionlist)
                extension = extensionlist[-1].lower()
                if len(extensionlist) > 1:
                    tar = extensionlist[-2].lower()
                print('extension: ', extension)
                if extension in ["gz","bz2"] and tar == "tar":
                    if extension == "gz":
                        dest = '/tmp/' + downplug #+ '.gz'
                    elif extension == "bz2":
                        dest = '/tmp/' + downplug #+ '.bz2'
                elif extension == "deb":
                    if not isDreamOS:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Download canceled!'))
                        return
                    else:
                        dest = '/tmp/' + downplug #+ '.deb'
                elif self.com.endswith(".ipk"):
                    if isDreamOS:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Download canceled!'))
                        return
                    else:
                        dest = '/tmp/' + downplug #+ '.ipk'
                elif self.com.endswith('.zip'):
                        dest = '/tmp/' + downplug #+ '.zip'
                dest = dest.replace('..','.')
                print('dest = :', dest)
                self.download = downloadWithProgress(self.com, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.finish).addErrback(self.showError)
            else:
                self['info'].setText(_('Download failed!') + dom + _('... Not supported'))
            # return

    def downloadProgress(self, recvbytes, totalbytes):
        self['info'].setText(_('Download...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))
        print('progress = ok')

    def finish(self, fplug):
        if os.path.exists(dest):
            self['info'].setText(_('File Downloaded ...'))
            self.ipkinst(dest)            
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)


    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)

    def finished(self,result):
         return

    def ipkinst(self, dest):
        self.sel = dest
        if self.sel:
            self.session.openWithCallback(self.ipkinst2, tvMessageBox, (_('Do you really want to install the selected Addon?') + '\n' + self.sel), tvMessageBox.TYPE_YESNO)

    def ipkinst2(self, answer ):
        self.sel = dest
        if answer is True:
            try:
                if self.sel.find('.ipk') != -1:
                    if not isDreamOS:
                        self.sel = self.sel[0]
                        print('self.sel ipk: ', self.sel)
                        # cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";opkg update > /dev/null; echo ":Install ' + dest + '";opkg install --force-overwrite ' + dest + ' > /dev/null'
                        #--force-overwrite install
                        cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + dest + '";opkg install ' + dest + ' > /dev/null'
                        self.session.open(tvConsole, title ='IPK Local Installation', cmdlist =[cmd0, 'sleep 5'] )
                    else:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)                    
                elif self.sel.find('.tar.gz') != -1:
                    self.sel = self.sel[0]
                    print('self.sel tar: ', self.sel)
                    cmd0 = 'tar -xzvf ' + dest + ' -C /'
                    self.session.open(tvConsole, title ='TAR GZ Local Installation', cmdlist =[cmd0, 'sleep 5'] )
                                 
                elif self.sel.find('.deb') != -1:
                    if isDreamOS:
                        self.sel = self.sel[0]
                        print('self.sel deb: ', self.sel)
                        cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + dest + '";dpkg --force-all -i ' + dest + ' > /dev/null 2>&1' #+ dest + ' > /dev/null' #; apt-get -f --force-yes --assume-yes install'
                        self.session.open(tvConsole, title ='DEB Local Installation', cmdlist =[cmd0, 'sleep 3'] )
                    else:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                elif self.sel.find('.zip') != -1:
                    if 'picon' in self.sel.lower():
                        # dest = '/tmp/picon.zip'
                        self.sel = self.sel[0]
                        print('self.sel zip: ', self.sel)
                        
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        cmd = ['unzip -o -q /tmp/%s -d %s' %(dest, mmkpicon)]
                        self.session.open(tvConsole, _('Installing: %s') % dest, [cmd] )
                        self['info'].setText(_('Installation done !!!'))
                    elif 'setting' in self.sel.lower():
                        self.sel = self.sel[0]
                        print('self.sel setting: ', self.sel)
                        
                        if not isDreamOS:
                            set = 1
                            terrestrial()
                        if os.path.exists("/tmp/unzipped"):
                            os.system('rm -rf /tmp/unzipped')
                        os.makedirs('/tmp/unzipped')
                        cmd = []
                        cmd1 = 'unzip -o -q /tmp/%s -d /tmp/unzipped' % dest
                        cmd.append(cmd1)
                        cmd2 = 'rm -rf /etc/enigma2/lamedb'
                        cmd.append(cmd2)
                        cmd3 = 'rm -rf /etc/enigma2/*.radio'
                        cmd.append(cmd3)
                        cmd4 = 'rm -rf /etc/enigma2/*.tv'
                        cmd.append(cmd4)
                        cmd5 = 'cp -rf /tmp/unzipped/*.tv /etc/enigma2'
                        cmd.append(cmd5)
                        cmd6 = 'cp -rf /tmp/unzipped/*.radio /etc/enigma2'
                        cmd.append(cmd6)
                        cmd7 = 'cp -rf /tmp/unzipped/lamedb /etc/enigma2'
                        cmd.append(cmd7)
                        if not os.path.exists("/etc/enigma2/blacklist"):
                            cmd8 = 'cp -rf /tmp/unzipped/blacklist /etc/tuxbox/'
                            cmd.append(cmd8)
                        if not os.path.exists("/etc/enigma2/whitelist"):
                            cmd9 ='cp -rf /tmp/unzipped/whitelist /etc/tuxbox/'
                            cmd.append(cmd9)
                        cmd10 = 'cp -rf /tmp/unzipped/satellites.xml /etc/tuxbox/'
                        cmd.append(cmd10)
                        cmd11 = 'cp -rf /tmp/unzipped/terrestrial.xml /etc/tuxbox/'
                        cmd.append(cmd11)
                        if not isDreamOS:
                            terrestrial_rest()
                        self.reloadSettings2()
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        self.session.open(tvConsole, _('SETTING - install: %s') % dest, [cmd] )
                        self['info'].setText(_('Installation done !!!'))
                    else:
                        self.mbox = self.session.open(tvMessageBox, _('Download file in /tmp successful!'), tvMessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Download file in /tmp successful!!'))
                else:
                    self.session.open(tvMessageBox, _('Unknow Error!'), tvMessageBox.TYPE_ERROR, timeout=10)
            except:
                # self.delFile(dest)
                self['info'].text = _('File: Installation failed!')

    def delFile(self, dest):
        if fileExists(dest):
            os.system('rm -rf ' + dest)

    def msgipkinst(self):
        self.session.openWithCallback(self.ipkrestart, MessageBox, (_('Restart Enigma to load the installed plugin?')), MessageBox.TYPE_YESNO)

    def ipkrestart(self, result):
        if result:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

class tvConsole(Screen):

    def __init__(self, session, title ="Console", cmdlist =None, finishedCallback =None, closeOnSuccess =False, endstr =''):
        self.session = session
        skin = skin_path + 'tvConsole.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Console')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.endstr = endstr
        self.errorOcurred = False
        self['text'] = ScrollLabel('')
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions' 'ColorActions',], {'ok': self.cancel,
         'back': self.cancel,
         'red': self.cancel,
         "blue": self.restartenigma,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.newtitle = _(title_plug)
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run=0
        try:
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
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
            str= self["text"].getText()
            if not retval and self.endstr.startswith("Swapping"):
               str += _("\n\n" + self.endstr)
            else:
               str += _("Execution finished!!\n")
            self["text"].setText(str)
            self["text"].lastPage()
            # if self.finishedCallback is not None:
                    # self.finishedCallback(retval)
            # if not retval and self.closeOnSuccess:
            self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            try:
                self.appClosed_conn = None
                self.dataAvail_conn = None
            except:
                self.container.appClosed.remove(self.runFinished)
                self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, data):
        if PY3:
            data = data.decode("utf-8")
        try:
            self["text"].setText(self["text"].getText() + data)
        except:
            trace_error()
        return
        if self["text"].getText().endswith("Do you want to continue? [Y/n] "):
            msg= self.session.openWithCallback(self.processAnswer, MessageBox, _("Additional packages must be installed. Do you want to continue?"), MessageBox.TYPE_YESNO)

    def processAnswer(self, retval):
        if retval:
            self.container.write("Y",1)
        else:
            self.container.write("n",1)
        self.dataSent_conn = self.container.dataSent.connect(self.processInput)

    def processInput(self, retval):
        self.container.sendEOF()

    def restartenigma(self):
        self.session.open(TryQuitMainloop, 3)
        
class tvIPK(Screen):

    def __init__(self, session, title = None, cmdlist = None, finishedCallback = None, closeOnSuccess = False):

        self.session = session
        skin = skin_path + 'tvIPK.xml'
        with open(skin, 'r') as f:
                self.skin = f.read()
        self.setup_title = ('IPK')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.flist = []
        idx = 0
        ipkpth = str(config.plugins.tvaddon.ipkpth.value)
        pkgs = listdir(ipkpth)
        for fil in pkgs:
            if fil.find('.ipk') != -1 or fil.find('.tar.gz') != -1 or fil.find('.deb') != -1 or fil.find('.zip') != -1  :
                res = (fil, idx)
                print('lista : ', res)
                self.flist.append(res)
                idx = idx + 1
        self['ipkglisttmp'] = List(self.flist)
        self['info1'] = Label(_('Put .ipk .tar.gz .deb .zip and install (Set folder from config path) ') + ' ' + str(ipkpth) )
        self['info'] = Label('')
        self['key_green'] = Button(_('Install'))
        self['key_yellow'] = Button(_('Restart'))
        self['key_blue'] = Button(_('Remove'))
        self['key_red'] = Button(_('Back'))
        self['title'] = Label(_(title_plug))        
        self['actions'] = ActionMap(['OkCancelActions', 'WizardActions', 'ColorActions', "MenuActions"], {'ok': self.ipkinst,
         'green': self.ipkinst,
         'yellow': self.msgipkinst,
         'blue': self.msgipkrmv,
         'red': self.close,
         'menu': self.goConfig,
         'cancel': self.close}, -1)
        self.onLayoutFinish.append(self.getfreespace)

    def refreshlist(self):
        self.flist = []
        self['ipkglisttmp'] = List(self.flist)
        idx = 0
        ipkpth = config.plugins.tvaddon.ipkpth.value
        pkgs = listdir(ipkpth)
        for fil in pkgs:
            if fil.find('.ipk') != -1 or fil.find('.tar.gz') != -1 or fil.find('.deb') != -1 or fil.find('.zip') != -1  :
                res = (fil, idx)
                self.flist.append(res)
                idx = idx + 1

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
            ipkpth = config.plugins.tvaddon.ipkpth.value
            dest = ipkpth + '/' + self.sel
            try:
                if self.sel.find('.ipk') != -1:
                    self.sel = self.sel[0]
                    # cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";opkg update > /dev/null; echo ":Install ' + dest + '";opkg install --force-overwrite ' + dest + ' > /dev/null'
                    cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + dest + '";opkg install ' + dest  + ' > /dev/null'
                    self.session.open(tvConsole, title ='IPK Local Installation', cmdlist =[cmd0, 'sleep 5'] )

                elif self.sel.find('.tar.gz') != -1:
                    self.sel = self.sel[0]
                    cmd0 = 'tar -xzvf ' + dest + ' -C /'
                    self.session.open(tvConsole, title ='TAR GZ Local Installation', cmdlist =[cmd0, 'sleep 5'] )

                elif self.sel.find('.deb') != -1:
                    if isDreamOS:
                        self.sel = self.sel[0]
                        cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + dest + '";dpkg --force-all -i ' + dest #+ ' > /dev/null 2>&1' #+ dest + ' > /dev/null' #; apt-get -f --force-yes --assume-yes install'
                        self.session.open(tvConsole, title ='DEB Local Installation', cmdlist =[cmd0, 'sleep 3'] )
                    else:
                        self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)

                elif self.sel.find('.zip') != -1:
                    if 'picon' in self.sel.lower():
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        cmd = ['unzip -o -q /tmp/%s -d %s' %(dest, mmkpicon)]
                        self.session.open(tvConsole, _('Installing: %s') % dest, cmdlist =[cmd, 'sleep 3'])
                    elif 'setting' in self.sel.lower():
                        if not isDreamOS:
                            set = 1
                            terrestrial()
                        if os.path.exists("/tmp/unzipped"):
                            os.system('rm -rf /tmp/unzipped')
                        os.makedirs('/tmp/unzipped')
                        cmd = []
                        cmd1 = 'unzip -o -q /tmp/%s -d /tmp/unzipped' % dest
                        cmd.append(cmd1)
                        cmd2 = 'rm -rf /etc/enigma2/lamedb'
                        cmd.append(cmd2)
                        cmd3 = 'rm -rf /etc/enigma2/*.radio'
                        cmd.append(cmd3)
                        cmd4 = 'rm -rf /etc/enigma2/*.tv'
                        cmd.append(cmd4)
                        cmd5 = 'cp -rf /tmp/unzipped/*.tv /etc/enigma2'
                        cmd.append(cmd5)
                        cmd6 = 'cp -rf /tmp/unzipped/*.radio /etc/enigma2'
                        cmd.append(cmd6)
                        cmd7 = 'cp -rf /tmp/unzipped/lamedb /etc/enigma2'
                        cmd.append(cmd7)
                        if not os.path.exists("/etc/enigma2/blacklist"):
                            cmd8 = 'cp -rf /tmp/unzipped/blacklist /etc/tuxbox/'
                            cmd.append(cmd8)
                        if not os.path.exists("/etc/enigma2/whitelist"):
                            cmd9 ='cp -rf /tmp/unzipped/whitelist /etc/tuxbox/'
                            cmd.append(cmd9)
                        cmd10 = 'cp -rf /tmp/unzipped/satellites.xml /etc/tuxbox/'
                        cmd.append(cmd10)
                        cmd11 = 'cp -rf /tmp/unzipped/terrestrial.xml /etc/tuxbox/'
                        cmd.append(cmd11)
                        if not isDreamOS:
                            terrestrial_rest()
                        self.reloadSettings2()
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        self.session.open(tvConsole, _('SETTING - install: %s') % dest, cmdlist =[cmd, 'sleep 3'])
                else:
                    self.session.open(tvMessageBox, _('Unknow Error!'), tvMessageBox.TYPE_ERROR, timeout=10)
            except:
                self.delFile(dest)
                self['info1'].text = _('File: %s\nInstallation failed!') % dest

    def delFile(self, dest):
        if fileExists(dest):
            os.system('rm -rf ' + dest)

    def msgipkrmv(self):
        self.sel = self['ipkglisttmp'].getCurrent()
        if self.sel:
            self.sel = self.sel[0]
            self.session.openWithCallback(self.msgipkrmv2, tvMessageBox, (_('Do you really want to remove selected?')+ '\n' + self.sel), tvMessageBox.TYPE_YESNO)

    def finished(self, result):
        return

    def msgipkinst(self):
        self.session.openWithCallback(self.ipkrestart, MessageBox, (_('Restart Enigma to load the installed plugin?')), MessageBox.TYPE_YESNO)

    def ipkrestart(self, result):
        if result:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def msgipkrmv2(self, result):
        if result:
            self.flist = []
            ipkpth = str(config.plugins.tvaddon.ipkpth.value)
            idx = self['ipkglisttmp'].getCurrent()
            if idx:
                idx = idx[0]
            dom = ipkpth + '/' + idx
            if fileExists(dom):
                os.remove(dom)
                self.session.open(MessageBox, dom +"   has been successfully deleted\nwait time to refresh the list...", MessageBox.TYPE_INFO, timeout=5)
            else:
                self.session.open(MessageBox, dom +"   not exist!\nwait time to refresh the list...", MessageBox.TYPE_INFO, timeout=5)
        self.close()

class tvUpdate(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
                self.skin = f.read()
        self.setup_title = ('Update')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
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
        self.Update = False
        global link, dmlink
        dmlink=''
        link=''
        try:
            fp = ''
            destr = plugin_path + '/update.txt'
            req = Request(upd_path + 'updatePanel.txt')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
            fp = checkStr(urlopen(req))
            fp = fp.read()
            # print("fp3 =", fp)
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
                    self['info'].setText(title_plug)
                    self['pth'].setText('No updates available!')
                    self.Update = False
                else:
                    updatestr = title_plug
                    cvrs = 'New update ' + s1 + ' is available!! '
                    cvrt = 'Updates: ' + self.info + '\nPress yellow button to start updating'
                    self.Update = True
                    self['info'].setText(updatestr)
                    self['pth'].setText(cvrs)
                    self['pform'].setText(cvrt)
        except:
            self.Update = False
            self['info'].setText(title_plug)
            self['pth'].setText('No updates available!')

        self.timer = eTimer()
        self.timer.start(2000, 1)
        if isDreamOS:
            self.timer_conn = self.timer.timeout.connect(self.msgupdate1)
        else:
            self.timer.callback.append(self.msgupdate1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
         'cancel': self.close,
         'green': self.msgipkrst1,
         'red': self.close,
         'yellow': self.msgupdate}, -1)

    def msgupdate1(self):
        if self.Update == False :
            return
        if config.plugins.tvaddon.autoupd.value == False :
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
                os.system('wget %s -O /tmp/tvaddon.tar > /dev/null' % com)
                os.system('sleep 3')
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['tar -xvf /tmp/tvaddon.tar -C /'], finishedCallback = self.msgipkrst1) #, closeOnSuccess =True)
            else:
                com = link
                dom = 'New Version ' + self.version
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['opkg install %s' % com], finishedCallback = self.msgipkrst1) #, closeOnSuccess =True)

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


class tvRemove(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Remove')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
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
        self['title'] = Label(_(title_plug))
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
                    if name.endswith('.postinst') or name.endswith('.preinst') or name.endswith('.prerm') or name.endswith('.postrm'):
                        continue
                    if name.endswith('.md5sums') or name.endswith('.conffiles') or name.endswith('~') :
                        continue
                    if isDreamOS:
                        if name.endswith('.list'):
                            name= name.replace('.list', '')
                    else:
                        if name.endswith('.control'):
                            name= name.replace('.control', '')
                        if name.endswith('.list'):
                            continue

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
                self.session.open(tvConsole, _('Removing: %s') % dom, ['dpkg -r %s' % com], self.openList, False)
            else:
                self.session.open(tvConsole, _('Removing: %s') % dom, ['opkg remove --force-removal-of-dependent-packages %s' % com], self.openList, False)

    def getfreespace(self):
        fspace = freespace()
        self['info'].setText(fspace)
        self.openList()

    def message1(self):
        self.session.openWithCallback(self.callMyMsg1, tvMessageBox,_("Do you want to remove?"), tvMessageBox.TYPE_YESNO)

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
        self.setTitle(_(title_plug))
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
        self.setTitle(_(title_plug))
        self['description'] = Label('')
        info = ''
        self['info'] = Label(_('Config Panel Addon'))
        self['key_yellow'] = Button(_('Update'))
        self['key_green'] = Button(_('Save'))
        self['key_red'] = Button(_('Back'))
        self["key_blue"] = Button(_(''))
        self['key_blue'].hide()
        self['title'] = Label(_(title_plug))
        self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'], {'cancel': self.extnok,
         'red': self.extnok,
         'back': self.close,
         'left': self.keyLeft,
         'right': self.keyRight,
         'yellow': self.tvUpdate,
         "showVirtualKeyboard": self.KeyText,
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
        self.list.append(getConfigListEntry(_('Auto Update Plugin'), config.plugins.tvaddon.autoupd, _("If Active: Automatic Update Plugin")))
        self.list.append(getConfigListEntry(_("Set the path to the Picons folder"), config.plugins.tvaddon.mmkpicon, _("Configure folder containing picons files")))
        self.list.append(getConfigListEntry(_('Path Manual IPK'), config.plugins.tvaddon.ipkpth, _("Path to the addon installation folder")))
        self.list.append(getConfigListEntry(_('Link in Extensions Menu'), config.plugins.tvaddon.strtext, _("Link in Extensions button")))
        self.list.append(getConfigListEntry(_('Link in Main Menu'), config.plugins.tvaddon.strtmain, _("Link in Main Menu")))
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
        if os.path.exists(config.plugins.tvaddon.ipkpth.value) is False:
            self.mbox = self.session.open(MessageBox, _('Device not detected!'), MessageBox.TYPE_INFO, timeout=4)
        for x in self["config"].list:
            x[1].save()
        self.mbox = self.session.open(MessageBox, _('Successfully saved configuration'), MessageBox.TYPE_INFO, timeout=4)
        self.close(True)

    def Ok_edit(self):
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        if sel and sel == config.plugins.tvaddon.mmkpicon:
            self.setting = 'mmkpicon'
            print("current selection:", self["config"].l.getCurrentSelection())
            mmkpth = config.plugins.tvaddon.mmkpicon.value
            self.openDirectoryBrowser(mmkpth)
        else:
            pass

    def openDirectoryBrowser(self, path):
        try:
            self.session.openWithCallback(
             self.openDirectoryBrowserCB,
             LocationBox,
             windowtitle =_('Choose Directory:'),
             text=_('Choose directory'),
             currDir= str(path),
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
                config.plugins.tvaddon.mmkpicon.setValue(path)
            if self.setting == 'ipkpth':
                config.plugins.tvaddon.ipkpth.setValue(path)
        return

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title = self['config'].getCurrent()[0], text= self['config'].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback = None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())
        return

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

class SelectPicons(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Select Picons')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self['text'] = tvList([])
        # self.working = False
        # self.selection = 'all'
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
        self['info'] = Label('')
        self['info'].setText(_('Please select ...'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_('Remove'))
        self["key_blue"] = Button(_(''))
        # self['key_yellow'].hide()
        self['key_blue'].hide()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self['title'] = Label(_(title_plug))
        self['actions'] = NumberActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
         'green': self.okRun,
         'yellow': self.remove,
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
        elif sel == _('MMARK PICONS MOVIE'):
            self.session.open(MMarkMov)
        elif sel == _('COLOMBO PICONS'):
            self.session.open(ColomboTrasp)

    def remove(self):
        self.session.openWithCallback(self.okRemove,tvMessageBox,(_("Do you want to remove all picons in folder?\n%s\nIt could take a few minutes, wait .." % mmkpicon)), tvMessageBox.TYPE_YESNO)

    def okRemove(self, result):
        if result:
            self['info'].setText(_('Erase %s... please wait' % mmkpicon))
            # print("Folder picons : ", mmkpicon)
            piconsx = glob.glob(str(mmkpicon) + '/*.png')
            for f in piconsx:
                try:
                    print("processing file: " + f)
                    os.remove(f)
                except OSError as e:
                    print("Error: %s : %s" % (f, e.strerror))
        self['info'].setText(_('Please select ...'))

class MMarkFolderBlk(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('MMark')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()        
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
                name = 'MMark Picons ' + name
                self.urls.append(url)
                self.names.append(name)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

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
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Load selected filter list, please wait ...'))  
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
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
        self.name = name
        self.timer = eTimer()
        self.timer.start(500, 1)
        if isDreamOS:
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def getfreespace(self):
        fspace = freespace()
        self['pform'].setText(fspace)

    def downxmlpage(self):
        url = self.url
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
            n1 = r.find('"quickkey":', 0)
            n2 = r.find('more_chunks', n1)
            data2 = r[n1:n2]
            regex = 'filename":"(.*?)".*?"created":"(.*?)".*?"downloads":"(.*?)".*?"normal_download":"(.*?)"'
            match = re.compile(regex,re.DOTALL).findall(data2)
            for name, data, download, url  in match:
                if 'zip' in url:
                    url = url.replace('\\','')
                    name = name.replace('_',' ').replace('mmk','MMark').replace('.zip','')
                    name = name + ' ' + data[0:10] + ' ' + 'Down:' + download
                    self.urls.append(url)
                    self.names.append(name)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
            self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        global dest
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                myfile = checkMyFile(url)
                for url in myfile:
                    img = no_cover
                    url = 'http://download' + url
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close(None)

    def downloadProgress(self, recvbytes, totalbytes):
        self['info'].setText(_('Download ...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(dest):
            self['info'].setText(_('Install ...'))
            myCmd = "unzip -o -q '%s' -d %s/" % (dest, str(mmkpicon))
            subprocess.Popen(myCmd, shell=True, executable='/bin/bash')
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self.downloading = False

    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)
        self.close()

    def cancel(self, result = None):
        self.close(None)
        return

    def finished(self,result):
         return


class MMarkFolderTrs(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('MMark')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Load selected filter list, please wait ...'))        
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Select'))
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
        self['title'] = Label(_(title_plug))
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
                name = 'MMark Picons ' + name
                self.urls.append(url)
                self.names.append(name)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

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
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def getfreespace(self):
        fspace = freespace()
        self['pform'].setText(fspace)

    def downxmlpage(self):
        url = self.url
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
            n1 = r.find('"quickkey":', 0)
            n2 = r.find('more_chunks', n1)
            data2 = r[n1:n2]
            regex = 'filename":"(.*?)".*?"created":"(.*?)".*?"downloads":"(.*?)".*?"normal_download":"(.*?)"'
            match = re.compile(regex,re.DOTALL).findall(data2)
            for name, data, download, url  in match:
                if 'zip' in url:
                    url = url.replace('\\','')
                    name = name.replace('_',' ').replace('mmk','MMark').replace('.zip','')
                    name = name + ' ' + data[0:10] + ' ' + 'Down: ' + download
                    self.urls.append(url)
                    self.names.append(name)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        global dest
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                myfile = checkMyFile(url)
                for url in myfile:
                    img = no_cover
                    url = 'http://download' + url
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close(None)

    def downloadProgress(self, recvbytes, totalbytes):
        self['info'].setText(_('Download ...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(dest):
            self['info'].setText(_('Install ...'))
            myCmd = "unzip -o -q '%s' -d %s/" % (dest, str(mmkpicon))
            subprocess.Popen(myCmd, shell=True, executable='/bin/bash')
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        # self.downloading = False

    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)
        self.close()

    def finished(self,result):
         return

class MMarkMov(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('MMark')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
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
        self.url = host_mov
        name = 'MMark-Picons'
        self.timer = eTimer()
        self.timer.start(500, 1)
        if isDreamOS:
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def getfreespace(self):
        fspace = freespace()
        self['pform'].setText(fspace)

    def downxmlpage(self):
        url = self.url
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
            n1 = r.find('"quickkey":', 0)
            n2 = r.find('more_chunks', n1)
            data2 = r[n1:n2]
            regex = 'filename":"(.*?)".*?"created":"(.*?)".*?"downloads":"(.*?)".*?"normal_download":"(.*?)"'
            match = re.compile(regex,re.DOTALL).findall(data2)
            for name, data, download, url  in match:
                if 'zip' in url:
                    url = url.replace('\\','')
                    name = name.replace('_',' ').replace('-',' ').replace('mmk','MMark').replace('.zip','')
                    name = name + ' ' + data[0:10] + ' ' + 'Down: ' + download
                    self.urls.append(url)
                    self.names.append(name)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        global dest
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                myfile = checkMyFile(url)
                for url in myfile:
                    img = no_cover
                    url = 'http://download' + url
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close(None)

    def downloadProgress(self, recvbytes, totalbytes):
        self['info'].setText(_('Download ...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(dest):
            self['info'].setText(_('Install ...'))
            myCmd = "unzip -o -q '/tmp/download.zip' -d %s/" % str(mmkpicon)
            subprocess.Popen(myCmd, shell=True, executable='/bin/bash')
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)

    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)
        self.close()

    def finished(self,result):
         return

class ColomboTrasp(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Colombo')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
        self.icount = 0
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
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
        self['title'] = Label(_(title_plug))
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
                    name = name.replace("/colombo/colombo/", "")
                    name = name.replace(".zip", "")
                    name = name.replace("%20", " ")
                    name = name.replace("-", " ")
                    name = name.replace("_", " ")
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self['info'].setText(_('Download...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))


    def install(self, fplug):
        if os.path.exists('/tmp/download.zip'):
            self['info'].setText(_('Install ...'))
            myCmd = "unzip -o -q '/tmp/download.zip' -d %s/" % str(mmkpicon)
            subprocess.Popen(myCmd, shell=True, executable='/bin/bash')
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self.close()

    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)
        self.close()

    # def finished(self,result):
         # return

Panel_list4 = [
 # _('KODILITE'),
 _('VIDEO ADDONS'),
 _('ADULT ADDON'),
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
        self.setTitle(_(title_plug))
        self['text'] = tvList([])
        # self.working = False
        # self.selection = 'all'
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
        self['title'] = Label(_(title_plug))
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
        # if sel == _('KODILITE') or sel == 0:
            # self.session.open(kodilite)
        if sel == _('VIDEO ADDONS') or sel == 0:
            self.session.open(plugins)
        elif sel == _('ADULT ADDON') or sel == 1:
            self.session.open(plugins_adult)
        elif sel == _('SCRIPT') or sel == 2:
            self.session.open(script)
        elif sel == _('REPOSITORY') or sel == 3:
            self.session.open(repository)

# class kodilite(Screen):

    # def __init__(self, session):
        # self.session = session
        # skin = skin_path + 'tvall.xml'
        # with open(skin, 'r') as f:
            # self.skin = f.read()
        # self.setup_title = ('Kodilite by pcd')
        # Screen.__init__(self, session)
        # self.setTitle(_(title_plug))
        # self.list = []
        # self['text'] = tvList([])
        # # self.addon = 'emu'
        # self.icount = 0
        # self['info'] = Label(_('Load selected filter list, please wait ...'))
        # self['pth'] = Label('')
        # self['pth'].setText(_('Support on'))
        # self['pform'] = Label('')
        # self['pform'].setText(_('linuxsat-support.com '))
        # self['progress'] = ProgressBar()
        # self['progresstext'] = StaticText()
        # self['key_green'] = Button(_('Install'))
        # self['key_red'] = Button(_('Back'))
        # self['key_yellow'] = Button(_(''))
        # self["key_blue"] = Button(_(''))
        # self['key_yellow'].hide()
        # self['key_blue'].hide()
        # self.downloading = False
        # self.timer = eTimer()
        # self.timer.start(500, 1)
        # if isDreamOS:
            # self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        # else:
            # self.timer.callback.append(self.downxmlpage)
        # self['title'] = Label(_(title_plug))
        # self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         # 'green': self.okRun,
         # 'red': self.close,
         # 'cancel': self.close}, -2)

    # def downxmlpage(self):
        # url = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbS9wYW5lbC1hZGRvbnMvRW5pZ21hT0UyLjAva29kaWxpdGU=")
        # getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    # def errorLoad(self, error):
        # print(str(error))
        # self['info'].setText(_('Try again later ...'))
        # self.downloading = False

    # def _gotPageLoad(self, data):
        # # global downn
        # self.xml = data
        # self.names = []
        # self.urls = []
        # self.downx = []
        # try:
            # match = re.compile(regexL,re.DOTALL).findall(self.xml)
            # for url, name, date1, date2, date3 in match:
                # if 'ipk' in url or 'deb' in url:
                    # url64b = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbQ==")
                    # url = url64b + url
                    # downn= name
                    # name = name.replace("enigma2-", "").replace("plugin-", "").replace("extensions-", "")
                    # name = name.replace("%20", " ")
                    # name = name.replace("-", " ")
                    # name = name.replace("_", " ")
                    # date = date1 + '-' + date2 + '-' + date3
                    # date = date.replace(' ','')
                    # name = name +' - '+ date
                    # self.urls.append(url)
                    # self.names.append(name)
                    # self.downx.append(downn)
                # else:
                    # self['info'].setText(_('No File!!'))
                    # self.downloading = False

            # showlist(self.names, self['text'])
            # self.downloading = True
        # except:
            # pass

    # def okRun(self):
        # self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    # def okInstall(self, result):
        # self['info'].setText(_('... please wait'))
        # if result:
            # if self.downloading == True:
                # global down
                # idx = self["text"].getSelectionIndex()
                # self.name = self.names[idx]
                # url = self.urls[idx]
                # down = self.downx[idx]
                # # dest = "/tmp/download.ipk"
                # dest = "/tmp/" + down
                
                # self.download = downloadWithProgress(url, dest)
                # self.download.addProgress(self.downloadProgress)
                # self.download.start().addCallback(self.install).addErrback(self.showError)
            # else:
                # self.close()

    # def downloadProgress(self, recvbytes, totalbytes):
        # self['progress'].value = int(100 * recvbytes / float(totalbytes))
        # self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))


    # # def install(self, fplug):
        # # if os.path.exists('/tmp/download.ipk'):
            # # cmd1 = "opkg install /tmp/download.ipk"
            # # cmd = []
            # # cmd.append(cmd1)
            # # title = _("Installation")
            # # self.session.open(tvConsole, _(title), cmd )
        # # self['info'].setText(_('Please select ...'))
        # # self['progresstext'].text = ''
        # # self.progclear = 0
        # # self['progress'].setValue(self.progclear)


    # def install(self, fplug):
        # dest = "/tmp/" + down
        # print('dest: ', dest)
        # if os.path.exists(dest):
            # if dest.endswith('.ipk'):
                # cmd1 = "opkg install /tmp/download.ipk"
                # cmd = []
                # cmd.append(cmd1)
                # title = _("Installation")
                # print('---------ok ipk')
                # self.session.open(Console, _(title), cmd )
                

            # if dest.endswith('.deb'):
                # if not isDreamOS:            
                    # self.mbox = self.session.open(tvMessageBox, _('Unknow Image!'), tvMessageBox.TYPE_INFO, timeout=5)
                    # self['info'].setText(_('Installation canceled!'))            
            
                # cmd1 = "dpkg --install --force-overwrite %s" % dest
                # cmd = []
                # cmd.append(cmd1)
                # title = _("Installation")
                # print('---------ok deb')
                # self.session.open(Console, _(title), cmd )
                
                
                       
                
        # self['info'].setText(_('Please select ...'))
        # self['progresstext'].text = ''
        # self.progclear = 0
        # self['progress'].setValue(self.progclear)

    # def showError(self, error):
        # print("download error =", error)
        # self.close()

    # def cancel(self, result = None):
        # self.close(None)
        # return

    # def finished(self,result):
         # return

class plugins(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Kodilite by pcd')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbS9wYW5lbC1hZGRvbnMvRW5pZ21hT0UyLjAva29kaWxpdGUvcGx1Z2lucw==")
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
            match = re.compile(regexL,re.DOTALL).findall(self.xml)
            for url, name, date1, date2, date3 in match:
                if 'zip' in url:
                    url64b = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbQ==")
                    url = url64b + url
                    name = name.replace("%20", " ")
                    name = name.replace("-", " ")
                    name = name.replace("_", " ")
                    date = date1 + '-' + date2 + '-' + date3
                    date = date.replace(' ','')
                    name = name +' - '+ date
                    self.urls.append(url)
                    self.names.append(name)
                else:
                    self['info'].setText(_('No File!!'))
                    self.downloading = False
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        fdest = KodilitePcd + "/plugins"
        if os.path.exists('/tmp/download.zip'):
            cmd1 = "unzip -o -q '/tmp/download.zip' -d '" + fdest + "'"
            cmd = []
            cmd.append(cmd1)
            title = _("Installation")
            self.session.open(tvConsole, _(title), cmd )
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

    def finished(self,result):
         return

class plugins_adult(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Kodilite by pcd')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun1,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbS9wYW5lbC1hZGRvbnMvRW5pZ21hT0UyLjAva29kaWxpdGUvcGx1Z2luYWR1bHQ=")
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
            match = re.compile(regexL,re.DOTALL).findall(self.xml)
            for url, name, date1, date2, date3 in match:
                if 'zip' in url:
                    url64b = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbQ==")
                    url = url64b + url
                    name = name.replace("%20", " ")
                    name = name.replace("-", " ")
                    name = name.replace("_", " ")
                    date = date1 + '-' + date2 + '-' + date3
                    date = date.replace(' ','')
                    name = name +' - '+ date
                    self.urls.append(url)
                    self.names.append(name)
                else:
                    self['info'].setText(_('No File!!'))
                    self.downloading = False
            showlist(self.names, self['text'])
            self.downloading = True
        except:
            pass

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
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        fdest = KodilitePcd + "/plugins"
        if os.path.exists('/tmp/download.zip'):
            cmd1 = "unzip -o -q '/tmp/download.zip' -d '" + fdest + "'"
            cmd = []
            cmd.append(cmd1)
            title = _("Installation")
            self.session.open(tvConsole, _(title), cmd )
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

    def finished(self,result):
         return

class script(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Kodilite by pcd')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbS9wYW5lbC1hZGRvbnMvRW5pZ21hT0UyLjAva29kaWxpdGUvc2NyaXB0")
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
            match = re.compile(regexL,re.DOTALL).findall(self.xml)
            for url, name, date1, date2, date3 in match:
                if 'zip' in url:
                    url64b = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbQ==")
                    url = url64b + url
                    name = name.replace("%20", " ")
                    name = name.replace("-", " ")
                    name = name.replace("_", " ")
                    date = date1 + '-' + date2 + '-' + date3
                    date = date.replace(' ','')
                    name = name +' - '+ date
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        fdest = KodilitePcd + "/scripts"
        if os.path.exists('/tmp/download.zip'):
            cmd1 = "unzip -o -q '/tmp/download.zip' -d '" + fdest + "'"
            cmd = []
            cmd.append(cmd1)
            title = _("Installation")
            self.session.open(tvConsole, _(title), cmd )
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

    def finished(self,result):
         return

class repository(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Kodilite by pcd')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['text'] = tvList([])
        # self.addon = 'emu'
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
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def downxmlpage(self):
        url = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbS9wYW5lbC1hZGRvbnMvRW5pZ21hT0UyLjAva29kaWxpdGUvcmVwb3NpdG9yeQ==")
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
            match = re.compile(regexL,re.DOTALL).findall(self.xml)
            for url, name, date1, date2, date3 in match:
                if 'zip' in url:
                    url64b = base64.b64decode("aHR0cDovL3BhdGJ1d2ViLmNvbQ==")
                    url = url64b + url
                    name = name.replace("%20", " ")
                    name = name.replace("-", " ")
                    name = name.replace("_", " ")
                    date = date1 + '-' + date2 + '-' + date3
                    date = date.replace(' ','')
                    name = name +' - '+ date
                    self.urls.append(url)
                    self.names.append(name)
                    self.downloading = True
                    self['info'].setText(_('Please select ...'))
                else:
                    self['info'].setText(_('no data ...'))
                    self.downloading = False
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        self.session.openWithCallback(self.okInstall, tvMessageBox,(_("Do you want to install?\nIt could take a few minutes, wait ..")), tvMessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading == True:
                idx = self["text"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                self.download = downloadWithProgress(url, dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        fdest = KodilitePcd + "/repos"
        if os.path.exists('/tmp/download.zip'):
            cmd1 = "unzip -o -q '/tmp/download.zip' -d '" + fdest + "'"
            cmd = []
            cmd.append(cmd1)
            title = _("Installation")
            self.session.open(tvConsole, _(title), cmd )
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

    def finished(self,result):
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
          'TiVuStream Addons',
          44)]
    else:
        return []

def mainmenu(session, **kwargs):
        main(session, **kwargs)

# def StartSetup(menuid):
    # if menuid == 'setup':
        # return [('TiVuStream Addons',
          # main,
          # 'TiVuStream Addons',
          # 44)]
    # else:
        # return []

def Plugins(**kwargs):
    ico_path = 'logo.png'
    if not isDreamOS:
        ico_path = plugin_path + '/res/pics/logo.png'
    extDescriptor = PluginDescriptor(name =name_plug, description =_(title_plug), where =PluginDescriptor.WHERE_EXTENSIONSMENU, icon =ico_path, fnc =main)
    mainDescriptor = PluginDescriptor(name =name_plug, description =_(title_plug), where =PluginDescriptor.WHERE_MENU, icon =ico_path, fnc =cfgmain)
    result = [PluginDescriptor(name =name_plug, description =_(title_plug), where =[PluginDescriptor.WHERE_PLUGINMENU], icon =ico_path, fnc =main)]
    if config.plugins.tvaddon.strtext.value:
        result.append(extDescriptor)
    if config.plugins.tvaddon.strtmain.value:
        result.append(mainDescriptor)
    return result

def terrestrial():
    SavingProcessTerrestrialChannels = StartSavingTerrestrialChannels()
    # run a rescue reload
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
    # if os.path.exists('/var/etc/enigma2/lamedb') :   
        lcn = LCN()
        lcn.read()
        if len(lcn.lcnlist) > 0:
            lcn.writeBouquet()
            # lcn.reloadBouquets()
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
            os.system('rm -fr ' + plugin_path + '/temp/TrasponderListOldLamedb')
            os.system('rm -fr ' + plugin_path + '/temp/ServiceListOldLamedb')
        except:
            pass
        return Trasponder
        
       
    def CreateBouquetForce():
        WritingBouquetTemporary = open(plugin_path +'/temp/TerrestrialChannelListArchive','w')
        WritingBouquetTemporary.write('#NAME Terrestre\n')
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
          # return

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
#======================================================
