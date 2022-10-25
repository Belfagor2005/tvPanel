#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------#
#   coded by Lululla  #
#    skin by MMark    #
#      24/09/2022     #
# --------------------#
# Info http://t.me/tivustream
from __future__ import print_function
from .__init__ import _
from . import Utils
from . import Lcn
# from Components.HTMLComponent import HTMLComponent
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigYesNo
from Components.config import ConfigDirectory, ConfigSelection, getConfigListEntry
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import fileExists, resolveFilename
from Tools.Downloader import downloadWithProgress
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER
from enigma import loadPNG, gFont
from enigma import eTimer
from enigma import eListboxPythonMultiContent, eConsoleAppContainer
from os import chmod
from twisted.web.client import downloadPage, getPage
import base64
import gettext
import os
import re
import sys
import shutil
import ssl
import glob
import six
import subprocess
global skin_path, mmkpicon, set, regexC, category

PY3 = sys.version_info.major >= 3
if PY3:
    from urllib.error import URLError
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse
    unicode = str
    unichr = chr
    long = int
    PY3 = True
else:
    from urllib2 import urlopen, Request, URLError
    from urlparse import urlparse


if sys.version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None


def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context=sslContext)
    else:
        return urlopen(url)


def trace_error():
    import sys
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/errorpanel.log', 'a'))
    except:
        pass


try:
    from OpenSSL import SSL
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except:
    sslverify = False


if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx


def getDesktopSize():
    from enigma import getDesktop
    s = getDesktop(0).size()
    return (s.width(), s.height())


def isFHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] == 1920


def checkMyFile(url):
    return []
    try:
        # dest = "/tmp/download.zip"
        req = Request(url)
        # req.add_header('User-Agent', RequestAgent())
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        req.add_header('Referer', 'https://www.mediafire.com')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        page = urlopen(req)
        r = page.read()
        n1 = r.find('"download_link', 0)
        n2 = r.find('downloadButton', n1)
        r2 = r[n1:n2]
        print("r2 =", r2)
        regexcat = 'href="https://download(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(r2)
        print("match =", match[0])
        myfile = match[0]
        # logdata("Myfile ", myfile)
        return myfile
    except:
        e = URLError
        print('We failed to open "%s".' % url)
        if hasattr(e, 'code'):
            print('We failed with error code - %s.' % e.code)
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        return ''


def make_request(url):
    try:
        import requests
        link = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        return link
    except ImportError:
        req = Request(url)
        req.add_header('User-Agent', 'TVS')
        response = urlopen(req, None, 7)
        link = response.read().decode('utf-8')
        response.close()
        return link
    except:
        e = URLError
        print('We failed to open "%s".' % url)
        if hasattr(e, 'code'):
            print('We failed with error code - %s.' % e.code)
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        return
    return


def ReloadBouquets():
    # global set
    print('\n----Reloading bouquets----\n')
    try:
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
        print('bouquets reloaded...')
    except ImportError:
        eDVBDB = None
        os.system('wget -qO - http://127.0.0.1/web/servicelistreload?mode=2 > /dev/null 2>&1 &')
        print('bouquets reloaded...')


def ReloadBouquet():
    global set
    print('\n----Reloading bouquets----')
    if set == 1:
        set = 0
        terrestrial_rest()
    ReloadBouquets()


def mountipkpth():
    ipkpth = []
    if os.path.isfile('/proc/mounts'):
        for line in open('/proc/mounts'):
            if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
                drive = line.split()[1].replace('\\040', ' ') + '/'
                if drive not in ipkpth:
                    ipkpth.append(drive)
    ipkpth.append('/tmp')
    return ipkpth


# ================config

config.plugins.tvaddon = ConfigSubsection()
config.plugins.tvaddon.strtext = ConfigYesNo(default=True)
config.plugins.tvaddon.mmkpicon = ConfigDirectory(default='/media/hdd/picon/')
config.plugins.tvaddon.strtmain = ConfigYesNo(default=True)
config.plugins.tvaddon.ipkpth = ConfigSelection(default="/tmp", choices=mountipkpth())
config.plugins.tvaddon.autoupd = ConfigYesNo(default=False)
mmkpicon = config.plugins.tvaddon.mmkpicon.value.strip()
currversion = '2.0.8'
title_plug = '..:: TiVuStream Addons Panel V. %s ::..' % currversion
name_plug = 'TiVuStream Addon Panel'
category = 'lululla.xml'
set = 0
pblk = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT1vdnowNG1ycHpvOXB3JmNvbnRlbnRfdHlwZT1mb2xkZXJzJmNodW5rX3NpemU9MTAwMCZyZXNwb25zZV9mb3JtYXQ9anNvbg== '
ptrs = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT10dmJkczU5eTlocjE5JmNvbnRlbnRfdHlwZT1mb2xkZXJzJmNodW5rX3NpemU9MTAwMCZyZXNwb25zZV9mb3JtYXQ9anNvbg== '
ptmov = 'aHR0cHM6Ly93d3cubWVkaWFmaXJlLmNvbS9hcGkvMS41L2ZvbGRlci9nZXRfY29udGVudC5waHA/Zm9sZGVyX2tleT1uazh0NTIyYnY0OTA5JmNvbnRlbnRfdHlwZT1maWxlcyZjaHVua19zaXplPTEwMDAmcmVzcG9uc2VfZm9ybWF0PWpzb24= '
data_upd = 'aHR0cDovL2NvcnZvbmUuYWx0ZXJ2aXN0YS5vcmcvdHZQYW5lbC8= '
data_xml = 'aHR0cDovL3BhdGJ1d2ViLmNvbS94bWwv'
regexC = '<plugins cont="(.*?)"'
regexL = 'href="(.+?)">.+?alt=.+?">(.+?)</a>.+?data.+?">(.+?)</td>'
# regexL = 'href="(.*?)">.*?">(.*?)</a>.*?">(.*?)-(.*?)-(.*?) '
host_trs = Utils.b64decoder(ptrs)
host_blk = Utils.b64decoder(pblk)
host_mov = Utils.b64decoder(ptmov)
upd_path = Utils.b64decoder(data_upd)
xml_path = Utils.b64decoder(data_xml)
plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tvaddon'))
ico_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/logo.png".format('tvaddon'))
no_cover = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/no_coverArt.png".format('tvaddon'))
res_plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/".format('tvaddon'))
skin_path = res_plugin_path + 'skins/hd/'


if isFHD():
    skin_path = res_plugin_path + 'skins/fhd/'
if Utils.DreamOS():
    skin_path = skin_path + 'dreamOs/'
os.system('rm -fr ' + plugin_path + '/temp/*')
if mmkpicon.endswith('/'):
    mmkpicon = mmkpicon[:-1]
if not os.path.exists(mmkpicon):
    try:
        os.makedirs(mmkpicon)
    except OSError as e:
        print(('Error creating directory %s:\n%s') % (mmkpicon, str(e)))
print('****************************************path Picons: ', mmkpicon)

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
 _('PLUGIN GAME'),
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
 ('SETTINGS MANUTEK'),
 ('SETTINGS MILENKA61'),
 ('SETTINGS MORPHEUS'),
 ('SETTINGS PREDRAG'),
 ('SETTINGS VHANNIBAL'),
 ('SETTINGS VHANNIBAL 2'),
 ('UPDATE SATELLITES.XML'),
 ('UPDATE TERRESTRIAL.XML')]

Panel_list3 = [
 _('MMARK PICONS BLACK'),
 _('MMARK PICONS TRANSPARENT'),
 _('MMARK PICONS MOVIE')]


class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if isFHD():
            self.l.setItemHeight(50)
            textfont = int(32)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(24)
            self.l.setFont(0, gFont('Regular', textfont))


def DailyListEntry(name, idx):
    res = [name]
    pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting.png".format('tvaddon'))  # ico1_path
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def oneListEntry(name):
    res = [name]
    pngx = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/plugins.png".format('tvaddon'))  # ico1_path
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
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
        self['list'] = tvList([])
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Extensions Installer'))
        self['key_yellow'] = Button(_('Uninstall'))
        self["key_blue"] = Button(_("tvManager"))
        self['key_blue'].hide()
        self.Update = False
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/tvManager'):
            self["key_blue"].show()
            self['key_blue'] = Label(_('tvManager'))
        elif os.path.exists('/usr/lib/enigma2/python/Plugins/PLi/tvManager'):
            self["key_blue"].show()
            self['key_blue'] = Label(_('tvManager'))
        self.dmlink = ''
        self.tlink = ''
        try:
            fp = ''
            destr = plugin_path + '/update.txt'
            req = Request(upd_path + 'updatePanel.txt')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
            fp = Utils.checkStr(urlopen(req))
            fp = fp.read()
            with open(destr, 'w') as f:
                f.write(fp)
                f.seek(0)
                f.close()
            with open(destr, 'r') as fp:
                # count = 0
                self.labeltext = ''
                s1 = fp.readline()
                s2 = fp.readline()
                s3 = fp.readline()
                s4 = fp.readline()
                self.version = s1.strip()
                self.tlink = s2.strip()
                self.info = s3.strip()
                self.dmlink = s4.strip()
                fp.close()
                if s1 <= currversion:
                    self.Update = False
                else:
                    self.Update = True
        except Exception as e:
            print('error: ', str(e))
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.msgupdate1)
        else:
            self.timer.callback.append(self.msgupdate1)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions', "MenuActions"], {'ok': self.okRun,
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
        except:
            dependencies = False
        if dependencies is False:
            chmod("/usr/lib/enigma2/python/Plugins/Extensions/tvaddon/dependencies.sh", 0o0755)
            cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/tvaddon/dependencies.sh"
            self.session.openWithCallback(self.starts, Console, title="Checking Python Dependencies", cmdlist=[cmd1], closeOnSuccess=False)
        else:
            self.starts()

    def starts(self):
        Utils.OnclearMem()

    def closerm(self):
        ReloadBouquet()
        Utils.deletetmp()
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
        self['list'].setList(list)

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def ipkDs(self):
        self.session.open(tvRemove)

    def tvManager(self):
        tvman = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tvManager'))
        if os.path.exists(tvman):
            from Plugins.Extensions.tvManager.plugin import tvManager
            self.session.openWithCallback(self.close, tvManager)
        else:
            self.session.open(MessageBox, ("tvManager Not Installed!!\nInstall First"), type=MessageBox.TYPE_INFO, timeout=3)

    def tvIPK(self):
        self.session.open(tvIPK)

    def keyNumberGlobalCB(self, idx):
        global category
        sel = self.menu_list[idx]

        if sel == _('DAILY PICONS'):
            self.session.open(SelectPicons)
        elif sel == _('DAILY SETTINGS'):
            self.session.open(tvDailySetting)
        elif sel == _('KODILITE BY PCD'):
            self.session.open(mainkodilite)
        else:
            if sel == _('LULULLA CORNER'):
                category = 'lululla.xml'
                self.session.open(Categories, category)
            if sel == _('DEBIAN DREAMOS'):
                category = 'debian.xml'
                self.session.open(Categories, category)
            if sel == _('DRIVERS'):
                category = 'Drivers.xml'
                self.session.open(Categories, category)
            if sel == _('DEPENDENCIES'):
                category = 'Dependencies.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN BACKUP'):
                category = 'PluginBackup.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN EMULATORS CAMS'):
                category = 'PluginEmulators.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN EPG'):
                category = 'PluginEpg.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN GAME'):
                category = 'PluginGame.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN MULTIBOOT'):
                category = 'PluginMultiboot.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN MULTIMEDIA'):
                category = 'PluginMultimedia.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN PICONS'):
                category = 'Picons.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN PPANEL'):
                category = 'PluginPpanel.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN SETTINGS PANEL'):
                category = 'PluginSettings.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN SKINS'):
                category = 'PluginSkins.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN SPORT'):
                category = 'PluginSport.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN UTILITY'):
                category = 'PluginUtility.xml'
                self.session.open(Categories, category)
            if sel == _('PLUGIN WEATHER'):
                category = 'PluginWeather.xml'
                self.session.open(Categories, category)
            return
            # self.session.open(Categories, category)

    def msgupdate1(self):
        if self.Update is False:
            return
        if config.plugins.tvaddon.autoupd.value is False:
            return
        else:
            self.session.openWithCallback(self.runupdate, MessageBox, (_('New update available!!\nDo you want update plugin ?\nPlease Reboot GUI after install!')), MessageBox.TYPE_YESNO)

    def runupdate(self, result):
        if result:
            if Utils.DreamOS():
                com = self.dmlink
                dom = 'New version ' + self.version
                tvtemp = '/tmp/tvaddon.tar'
                import requests
                r = requests.get(com)
                with open(tvtemp, 'wb') as f:
                    f.write(r.content)
                # os.system('wget %s -O /tmp/tvaddon.tar > /dev/null' % com)
                os.system('sleep 3')
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['tar -xvf /tmp/tvaddon.tar -C /'], closeOnSuccess=False)
            else:
                com = self.tlink
                dom = 'New Version ' + self.version
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['opkg install %s' % com], closeOnSuccess=False)

    def msgipkrst1(self):
        self.session.openWithCallback(self.ipkrestrt, MessageBox, (_('Do you want restart enigma2 ?')), MessageBox.TYPE_YESNO)

    def ipkrestrt(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if os.path.exists(epgbakpath):
                os.remove(epgbakpath)
            if os.path.exists(epgpath):
                shutil.copyfile(epgpath, epgbakpath)
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()


class Categories(Screen):
    def __init__(self, session, category):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = (category)
        Screen.__init__(self, session)
        self.list = []
        self['list'] = tvList([])
        self.icount = 0
        category = category
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        # PY2
        url = str(xml_path) + category
        print('py2------>')
        try:
            if six.PY3:
                # url = str(xml_path) + six.binary_type(category, encoding="utf-8") #no work on wix image
                url = url.encode()
                print('py3------>')
            getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)
            # error : url must be bytes, not unicode
        except Exception as e:
            print('error: ', str(e))

    def errorLoad(self, error):
        print(error)
        self['info'].setText(_('Try again later ...'))
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        if six.PY3:
            self.xml = six.ensure_str(data)
        try:
            match = re.compile(regexC, re.DOTALL).findall(self.xml)
            for name in match:
                self.list.append(name)
                self['info'].setText(_('Please select ...'))
            showlist(self.list, self['list'])
            self['key_green'].show()
            self.downloading = True
        except Exception as e:
            print('error: ', str(e))

    def okRun(self):
        if self.downloading is True:
            try:
                idx = self["list"].getSelectionIndex()
                name = self.list[idx]
                self.session.open(tvInstall, self.xml, name)
            except Exception as e:
                print('error: ', str(e))
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
        self['list'] = tvList([])
        self['title'] = Label(_(title_plug))
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self['key_yellow'].hide()
        self['key_green'].hide()
        self.LcnOn = False
        if os.path.exists('/etc/enigma2/lcndb'):
            self['key_yellow'].show()
            self['key_yellow'] = Button('Lcn')
            self.LcnOn = True
        self["key_blue"] = Button('')
        self['key_blue'].hide()
        self['actions'] = ActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
                                                                         'green': self.okRun,
                                                                         'back': self.closerm,
                                                                         'red': self.closerm,
                                                                         'yellow': self.Lcn,
                                                                         'cancel': self.closerm}, -1)
        self.onLayoutFinish.append(self.updateMenuList)

    def Lcn(self):
        self.session.open(MessageBox, _('Reorder Terrestrial channels with Lcn rules'), MessageBox.TYPE_INFO, timeout=5)
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
        self['list'].setList(list)
        self['key_green'].show()
        self['info'].setText(_('Please select ...'))

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        if sel == ('SETTINGS CIEFP'):
            self.session.open(SettingCiefp)
        elif sel == ('SETTINGS CYRUS'):
            self.session.open(SettingCyrus)
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
        elif sel == ('SETTINGS VHANNIBAL 2'):
            self.session.open(SettingVhan2)
        elif sel == _('UPDATE SATELLITES.XML'):
            self.okSATELLITE()
        elif sel == _('UPDATE TERRESTRIAL.XML'):
            self.okTERRESTRIAL()

    def okSATELLITE(self):
        self.session.openWithCallback(self.okSatInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okSatInstall(self, result):
        if result:
            if Utils.checkInternet():
                try:
                    url_sat_oealliance = 'http://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml'
                    link_sat = ssl_urlopen(url_sat_oealliance)
                    dirCopy = '/etc/tuxbox/satellites.xml'
                    import requests
                    r = requests.get(link_sat)
                    with open(dirCopy, 'wb') as f:
                        f.write(r.content)
                    self.session.open(MessageBox, _('Satellites.xml Updated!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation done !!!'))
                except Exception as e:
                    print('error: ', str(e))
            else:
                self.session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

    def okTERRESTRIAL(self):
        self.session.openWithCallback(self.okTerrInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okTerrInstall(self, result):
        if result:
            if Utils.checkInternet():
                try:
                    url_sat_oealliance = 'https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/terrestrial.xml'
                    link_ter = ssl_urlopen(url_sat_oealliance)
                    dirCopy = '/etc/tuxbox/terrestrial.xml'
                    import requests
                    r = requests.get(link_ter)
                    with open(dirCopy, 'wb') as f:
                        f.write(r.content)
                    self.session.open(MessageBox, _('Terrestrial.xml Updated!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation done !!!'))
                except Exception as e:
                    print('error: ', str(e))
            else:
                self.session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        self.names = []
        self.urls = []
        try:
            urlsat = 'https://www.vhannibal.net/asd.php'
            r = make_request(urlsat)
            print('rrrrrrrr ', r)
            if PY3:
                r = six.ensure_str(r)
            match = re.compile('<td><a href="(.+?)">(.+?)</a></td>.*?<td>(.+?)</td>', re.DOTALL).findall(r)
            for url, name, date in match:
                name = name + ' ' + date
                url = "https://www.vhannibal.net/" + url
                print('url : ', url)
                print('name : ', name)
                self.urls.append(Utils.checkStr(url.strip()))
                self.names.append(Utils.checkStr(name.strip()))

            # urldtt = 'https://www.vhannibal.net/enigma2dtt.php'
            # r2=make_request(urldtt)
            # print('rrrrrrrr ', r2)
            # if PY3:
                # r2  = six.ensure_str(r2)
            # match2   = re.compile('<td><a href="(.+?)" target="_blank">(.+?)</a></td>.*?<td>(.+?)</td>', re.DOTALL).findall(r2)
            # for url, name, date in match2:
                # name = name + ' ' + date
                # url = "https://www.vhannibal.net/" + url
                # print('url : ', url)
                # print('name : ', name)
                # self.urls.append(Utils.checkStr(url.strip()))
                # self.names.append(Utils.checkStr(name.strip()))

            self.downloading = True
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
        except Exception as e:
            print(('downxmlpage get failed: ', str(e)))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.name = self.names[idx]
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                print("url =", url)
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if 'dtt' not in self.name.lower():
                    set = 1
                    terrestrial()
                if os.path.exists(dest):
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
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &; sleep 3"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
                else:
                    self['info'].setText(_('Settings Not Installed ...'))
            else:
                self['info'].setText(_('No Downloading ...'))

    def yes(self):
        ReloadBouquet()


class SettingVhan2(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Setting Vhannibal')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://sat.alfa-tech.net/upload/settings/vhannibal/'
        r = make_request(url)
        print('rrrrrrrr ', r)
        if six.PY3:
            r = six.ensure_str(r)
        self.names = []
        self.urls = []
        try:
            regex = '<a href="Vhannibal(.*?).zip"'
            match = re.compile(regex).findall(r)
            for url in match:
                if '.php' in url.lower():
                    continue
                name = "Vhannibal" + url
                name = name.replace(".zip", "").replace("%20", " ")
                url = "http://sat.alfa-tech.net/upload/settings/vhannibal/Vhannibal" + url + '.zip'
                self.urls.append(Utils.checkStr(url.strip()))
                self.names.append(Utils.checkStr(name.strip()))
                self.downloading = True
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                try:
                    idx = self["list"].getSelectionIndex()
                    self.name = self.names[idx]
                    url = self.urls[idx]
                    self.dest = "/tmp/settings.zip"
                    print("url =", url)
                    if six.PY3:
                        url = six.ensure_binary(url)
                    if url.startswith(b"https") and sslverify:
                        parsed_uri = urlparse(url)
                        domain = parsed_uri.hostname
                        sniFactory = SNIFactory(domain)
                        # if six.PY3:
                            # url = url.encode()
                        print('uurrll: ', url)
                        downloadPage(url, self.dest, sniFactory, timeout=5).addCallback(self.download, self.dest).addErrback(self.downloadError)
                    else:
                        downloadPage(url, self.dest).addCallback(self.download, self.dest).addErrback(self.downloadError)
                except Exception as e:
                    print('error: ', str(e))
                    print("Error: can't find file or read data")

    def download(self, data, dest):
        try:
            if 'dtt' not in self.name.lower():
                set = 1
                terrestrial()
            if os.path.exists(dest):
                self.namel = ''
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
                        self.namel = name
                os.system('rm -rf /etc/enigma2/lamedb')
                os.system('rm -rf /etc/enigma2/*.radio')
                os.system('rm -rf /etc/enigma2/*.tv')
                os.system('rm -rf /etc/enigma2/*.del')
                os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                title = _("Installation Settings")
                self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &; sleep 3"], closeOnSuccess=False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

        except Exception as e:
            print('error: ', str(e))
            self['info'].setText(_('Not Installed ...'))

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as e:
            print('error: ', str(e))
            print('downloadError')

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://178.63.156.75/tarGz/'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            regex = '<a href="Satvenus(.+?)".*?align="right">(.*?) </td>'
            # regex = '<a href="Satvenus(.+?)".+?align="right">(.*?)-(.*?)-(.*?) .+?</td'
            match = re.compile(regex).findall(r)
            for url, txt in match:
                if url.find('.tar.gz') != -1:
                    name = url.replace('_EX-YU_Lista_za_milenka61_', '')
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' ' + date
                    name = name.replace("_", " ").replace(".tar.gz", "")
                    url = "http://178.63.156.75/tarGz/Satvenus" + url
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                    self.downloading = True
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists('/tmp/settings.tar.gz'):
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["tar -xvf /tmp/settings.tar.gz -C /; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess=False)
                self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://www.manutek.it/isetting/index.php'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            regex = 'href="/isetting/.*?file=(.+?).zip">'
            match = re.compile(regex).findall(r)
            for url in match:
                name = url
                url = 'http://www.manutek.it/isetting/enigma2/' + url + '.zip'
                name = name.replace("NemoxyzRLS_Manutek_", "").replace("_", " ").replace("%20", " ")
                self.urls.append(Utils.checkStr(url.strip()))
                self.names.append(Utils.checkStr(name.strip()))
                self.downloading = True
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists(dest):
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
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &; sleep 3"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = r'http://morpheus883.altervista.org/download/index.php'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            regex = 'href="/download/.*?file=(.*?)">'
            match = re.compile(regex).findall(r)
            for url in match:
                if 'zip' in url.lower():
                    self.downloading = True
                    if 'settings' in url.lower():
                        continue
                    name = url
                    name = name.replace(".zip", "").replace("%20", " ").replace("_", " ").replace("E2_Morph883", "")
                    url = "http://morpheus883.altervista.org/settings/" + url
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                    print("url =", url)
                    print("name =", name)
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        print("self.downloading is =", self.downloading)
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists(dest):
                    # fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        os.system('rm -rf /tmp/unzipped')
                    os.makedirs('/tmp/unzipped')
                    os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                    path = '/tmp/unzipped'
                    # pth = ''
                    for root, dirs, files in os.walk(path):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'https://github.com/ciefp/ciefpsettings-enigma2-zipped'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            n1 = r.find('title="README.txt', 0)
            n2 = r.find('href="#readme">', n1)
            r = r[n1:n2]
            regex = 'title="ciefp-E2-(.*?).zip".*?href="(.*?)"'
            match = re.compile(regex).findall(r)
            for name, url in match:
                if url.find('.zip') != -1:
                    # if 'ddt' in name.lower():
                        # continue
                    # if 'sat' in name.lower():
                        # continue
                    url = url.replace('blob', 'raw')
                    # https://github.com/ciefp/ciefpsettings-enigma2-zipped/blob/master/
                    url = 'https://github.com' + url
                    print('name ', name)
                    print('url ', url)
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                    self.downloading = True
            self['key_green'].show()
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists(dest):
                    # fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        os.system('rm -rf /tmp/unzipped')
                    os.makedirs('/tmp/unzipped')
                    os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                    path = '/tmp/unzipped'
                    for root, dirs, files in os.walk(path):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://178.63.156.75/paneladdons/Bi58/'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            regex = '<a href="bi58-e2(.*?)".*?align="right">(.*?) </td>'
            match = re.compile(regex).findall(r)
            for url, txt in match:
                if url.find('.tar.gz') != -1:
                    name = url.replace('-settings-', 'bi58 ')
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' ' + date
                    name = name.replace(".tar.gz", "").replace("%20", " ")
                    url = "http://178.63.156.75/paneladdons/Bi58/bi58-e2" + url
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                    self.downloading = True
            self['key_green'].show()
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists('/tmp/settings.tar.gz'):
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["tar -xvf /tmp/settings.tar.gz -C /; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://178.63.156.75/paneladdons/Predr@g/'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            regex = '<a href="predrag(.*?)".*?align="right">(.*?) </td>'
            match = re.compile(regex).findall(r)
            for url, txt in match:
                if url.find('.tar.gz') != -1:
                    name = url.replace('-settings-e2-', 'Predrag ')
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' ' + date
                    name = name.replace(".tar.gz", "").replace("%20", " ")
                    url = "http://178.63.156.75/paneladdons/Predr@g/predrag" + url
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                    self.downloading = True
            self['key_green'].show()
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.name = self.names[idx]
                url = self.urls[idx]
                dest = "/tmp/settings.tar.gz"
                print("url =", url)
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists('/tmp/settings.tar.gz'):
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["tar -xvf /tmp/settings.tar.gz -C /; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():

            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        url = 'http://www.cyrussettings.com/Set_29_11_2011/Dreambox-IpBox/Config.xml'
        data = make_request(url)
        r = data
        print('rrrrrrrr ', r)
        self.names = []
        self.urls = []
        try:
            n1 = r.find('name="Sat">', 0)
            n2 = r.find("/ruleset>", n1)
            r = r[n1:n2]
            regex = 'Name="(.*?)".*?Link="(.*?)".*?Date="(.*?)"><'
            match = re.compile(regex).findall(r)
            for name, url, date in match:
                if url.find('.zip') != -1:
                    if 'ddt' in name.lower():
                        continue
                    if 'Sat' in name.lower():
                        continue
                    name = name + ' ' + date
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                    self.downloading = True
            self['key_green'].show()
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['list'])
        except Exception as e:
            print('downxmlpage get failed: ', str(e))
            self['info'].setText(_('Download page get failed ...'))

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        global set
        set = 0
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                url = self.urls[idx]
                dest = "/tmp/settings.zip"
                self.namel = ''
                if 'dtt' not in url.lower():
                    # if not os.path.exists('/var/lib/dpkg/status'):
                    set = 1
                    terrestrial()
                # urlretrieve(url, dest)
                import requests
                r = requests.get(url)
                with open(dest, 'wb') as f:
                    f.write(r.content)
                if os.path.exists(dest):
                    # fdest1 = "/tmp/unzipped"
                    fdest2 = "/etc/enigma2"
                    if os.path.exists("/tmp/unzipped"):
                        os.system('rm -rf /tmp/unzipped')
                    os.makedirs('/tmp/unzipped')
                    os.system('unzip -o -q /tmp/settings.zip -d /tmp/unzipped')
                    path = '/tmp/unzipped'
                    for root, dirs, files in os.walk(path):
                        for name in dirs:
                            self.namel = name
                    os.system('rm -rf /etc/enigma2/lamedb')
                    os.system('rm -rf /etc/enigma2/*.radio')
                    os.system('rm -rf /etc/enigma2/*.tv')
                    os.system('rm -rf /etc/enigma2/*.del')
                    os.system("cp -rf  '/tmp/unzipped/" + str(self.namel) + "/'* " + fdest2)
                    title = _("Installation Settings")
                    self.session.openWithCallback(self.yes, tvConsole, title=_(title), cmdlist=["wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 > /tmp/inst.txt 2>&1 &"], closeOnSuccess=False)
                    self['info'].setText(_('Settings Installed ...'))
            else:
                self['info'].setText(_('Settings Not Installed ...'))

    def yes(self):
        ReloadBouquet()


class tvInstall(Screen):
    def __init__(self, session, data, name, selection=None):
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
        self['key_green'] = Button(_('Install'))
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        list = []
        list.sort()
        self['info'].setText(_('... please wait'))

        n1 = data.find(name, 0)
        n2 = data.find("</plugins>", n1)
        data1 = data[n1:n2]
        self.names = []
        self.urls = []
        regex = '<plugin name="(.*?)".*?url>"(.*?)"</url'
        match = re.compile(regex, re.DOTALL).findall(data1)
        for name, url in match:
            self.names.append(name)
            self.urls.append(url)
        self['list'] = tvList([])
        self['info'].setText(_('Please install ...'))
        self['title'] = Label(_(title_plug))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_('Download'))
        self["key_blue"] = Button('')
        self['key_blue'].hide()
        self['key_green'].hide()
        self['actions'] = ActionMap(['SetupActions',  'ColorActions'], {'ok': self.message,
                                                                        'green': self.message,
                                                                        'red': self.close,
                                                                        'yellow': self.okDown,
                                                                        'cancel': self.close}, -2)
        self.onLayoutFinish.append(self.start)

    def start(self):
        showlist(self.names, self['list'])
        self['key_green'].show()

    def message(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.selclicked, MessageBox, (_("Do you want to install?")), MessageBox.TYPE_YESNO)

    def selclicked(self, result):
        if result:
            idx = self["list"].getSelectionIndex()
            dom = self.names[idx]
            com = self.urls[idx]
            self.prombt(com, dom)

    def prombt(self, com, dom):
        useragent = {'User-Agent': 'Enigma2 - tvaddon Plugin'}
        # useragent = "--header= 'User-Agent: QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)'"
        self.com = com
        self.dom = dom
        n2 = self.com.rfind("/", 0)
        dom = self.com[:n2]
        print('dommmm : ', dom)
        self.downplug = self.com.replace(dom, '').replace('/', '').lower()
        print('self.downplug : ', self.downplug)
        self.dest = '/tmp/' + self.downplug
        self['info'].setText(_('Installing ') + self.dom + _('... please wait'))
        if self.com is not None:
            extensionlist = self.com.split('.')
            extension = extensionlist[-1].lower()
            if len(extensionlist) > 1:
                tar = extensionlist[-2].lower()
            if extension in ["gz", "bz2"] and tar == "tar":
                self.command = ['']
                if extension == "gz":
                    self.command = ["tar -xzvf " + self.dest + " -C /"]
                elif extension == "bz2":
                    self.command = ["tar -xjvf " + self.dest + " -C /"]
                self.timer = eTimer()
                self.timer.start(1000, True)
                cmd = 'wget -q -O %s %s;' + self.command[0] % (self.dest, str(self.com))
                self.session.open(tvConsole, _('Downloading-installing: %s') % self.dom, [cmd], closeOnSuccess=False)
                self['info'].setText(_('Installation done !!!'))
            elif extension == "deb":
                if not os.path.exists('/var/lib/dpkg/status'):
                    self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation canceled!'))
                else:
                    self.timer = eTimer()
                    self.timer.start(1000, True)
                    # cmd = 'wget -q -O %s %s;dpkg --install --force-overwrite %s' % (self.dest, str(self.com), self.dest)
                    cmd = 'wget -q -O %s %s;apt-get install --reinstall %s -y' % (self.dest, str(self.com), self.dest)

                    self.session.open(tvConsole, _('Downloading-installing: %s') % self.dom, [cmd], closeOnSuccess=False)
                    self['info'].setText(_('Installation done !!!'))
            elif extension == "ipk":
                if Utils.DreamOS():
                    self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Installation canceled!'))
                else:
                    self.timer = eTimer()
                    self.timer.start(1000, True)
                    cmd = 'wget -q -O %s %s;opkg install --force-reinstall %s' % (self.dest, str(self.com), self.dest)
                    # cmd = 'wget -q -O %s %s;opkg install %s' % (self.dest, str(self.com), self.dest)

                    self.session.open(tvConsole, _('Downloading-installing: %s') % self.dom, [cmd], closeOnSuccess=False)
                    self['info'].setText(_('Installation done !!!'))
            elif self.com.endswith('.zip'):
                if 'setting' in self.dom.lower():
                    if not os.path.exists('/var/lib/dpkg/status'):
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
                        cmd9 = 'cp -rf /tmp/unzipped/whitelist /etc/tuxbox/'
                        cmd.append(cmd9)
                    cmd10 = 'cp -rf /tmp/unzipped/satellites.xml /etc/tuxbox/'
                    cmd.append(cmd10)
                    cmd11 = 'cp -rf /tmp/unzipped/terrestrial.xml /etc/tuxbox/'
                    cmd.append(cmd11)
                    terrestrial_rest()
                    self.timer = eTimer()
                    self.timer.start(500, True)
                    self.session.open(tvConsole, _('SETTING - install: %s') % self.dom, [cmd], closeOnSuccess=False)
                    self['info'].setText(_('Installation done !!!'))
                elif 'picon' in self.dom.lower():
                    self.timer = eTimer()
                    self.timer.start(500, True)
                    cmd = ['wget -q -O %s %s; unzip -o -q %s -d %s' % (str(self.dest), str(self.com), str(self.dest), mmkpicon)]
                    self.session.open(tvConsole, _('Downloading-installing: %s') % self.dom, [cmd], closeOnSuccess=False)
                    self['info'].setText(_('Installation done !!!'))
                else:
                    self['info'].setText(_('Downloading the selected file in /tmp') + self.dom + _('... please wait'))
                    self.timer = eTimer()
                    self.timer.start(500, True)
                    cmd = ["wget %s -c '%s' -O '%s' > /dev/null" % (useragent, self.com, self.dest)]
                    self.session.open(tvConsole, _('Downloading-installing: %s') % self.dom, [cmd], closeOnSuccess=False)
                    self['info'].setText(_('Installation done !!!'))
                    self.session.open(MessageBox, _('Download file in /tmp successful!'), MessageBox.TYPE_INFO, timeout=5)
                    self['info'].setText(_('Download file in /tmp successful!!'))
            else:
                self['info'].setText(_('Download failed!') + self.dom + _('... Not supported'))
            return

    def cancel(self, result=None):
        self.close(None)

    def okDown(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okDownload, MessageBox, (_("Do you want to Download?\nIt could take a few minutes, wait ..")), MessageBox.TYPE_YESNO)

    def okDownload(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            idx = self["list"].getSelectionIndex()
            self.dom = self.names[idx]
            self.com = self.urls[idx]
            n2 = self.com.rfind("/", 0)
            dom = self.com[:n2]
            self.downplug = self.com.replace(dom, '').replace('/', '').lower()
            self.dest = '/tmp/' + self.downplug
            if self.com is not None:
                extensionlist = self.com.split('.')
                print('extensionlist: ', extensionlist)
                extension = extensionlist[-1].lower()
                if len(extensionlist) > 1:
                    tar = extensionlist[-2].lower()
                print('extension: ', extension)
                if extension == "deb":
                    if not os.path.exists('/var/lib/dpkg/status'):
                        self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Download canceled!'))
                        return
                elif self.com.endswith(".ipk"):
                    if Utils.DreamOS():
                        self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
                        self['info'].setText(_('Download canceled!'))
                        return
                self.dest = self.dest.replace('..', '.')
                print('dest = :', self.dest)
                self.download = downloadWithProgress(self.com, self.dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.finish).addErrback(self.showError)
            else:
                self['info'].setText(_('Download failed!') + self.dom + _('... Not supported'))

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['info'].setText(_('Download...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))
        print('progress = ok')

    def finish(self, fplug):
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()
        if os.path.exists(self.dest):
            self['info'].setText(_('File Downloaded ...'))
            self.tvIPK()

    def tvIPK(self):
        self.session.openWithCallback(self.close, tvIPK)

    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)


class tvConsole(Screen):
    def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False, endstr=''):
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
        self['title'] = Label(_(title_plug))
        self['list'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.cancel,
                                                                                            'back': self.cancel,
                                                                                            'red': self.cancel,
                                                                                            "blue": self.restartenigma,
                                                                                            'up': self['list'].pageUp,
                                                                                            'down': self['list'].pageDown}, -1)
        self.cmdlist = cmdlist
        self.newtitle = _(title_plug)
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run = 0
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
        self['list'].setText(_('Execution Progress:') + '\n\n')
        print('Console: executing in run', self.run, ' the command:', self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
        else:
            self.show()
            self.finished = True
            str = self["list"].getText()
            if not retval and self.endstr.startswith("Swapping"):
                str += _("\n\n" + self.endstr)
            else:
                str += _("Execution finished!!\n")
            self["list"].setText(str)
            self["list"].lastPage()
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

    def cancelCallback(self, ret=None):
        self.cancel_msg = None
        if ret:
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)
            self.container.kill()
            self.close()
        return

    def dataAvail(self, data):
        if six.PY3:
            data = data.decode("utf-8")
        try:
            self["list"].setText(self["list"].getText() + data)
        except:
            trace_error()
        return
        if self["list"].getText().endswith("Do you want to continue? [Y/n] "):
            self.session.openWithCallback(self.processAnswer, MessageBox, _("Additional packages must be installed. Do you want to continue?"), MessageBox.TYPE_YESNO)

    def processAnswer(self, retval):
        if retval:
            self.container.write("Y", 1)
        else:
            self.container.write("n", 1)
        self.dataSent_conn = self.container.dataSent.connect(self.processInput)

    def processInput(self, retval):
        self.container.sendEOF()

    def restartenigma(self):
        self.session.open(TryQuitMainloop, 3)

    def closeConsole(self):
        if self.finished:
            try:
                self.container.appClosed.append(self.runFinished)
                self.container.dataAvail.append(self.dataAvail)
            except:
                self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
                self.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
                self.close()
            else:
                self.show()


class tvIPK(Screen):
    def __init__(self, session, title=None, cmdlist=None, finishedCallback=None, closeOnSuccess=False):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('IPK')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.ipkpth = str(config.plugins.tvaddon.ipkpth.value)
        # count = 0
        self.list = []
        self.names = []
        self['list'] = tvList([])
        self['key_green'] = Button(_('Install'))
        self['key_yellow'] = Button(_('Restart'))
        self['key_red'] = Button(_('Back'))
        self["key_blue"] = Button('Remove')
        self['key_green'].hide()
        self['pth'] = Label('')
        self['pform'] = Label(_('Path %s (Set folder from config path)\nPut .ipk .tar.gz .deb .zip and install') % self.ipkpth)
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['info'] = Label()
        self['info'].setText(_('Please install ...'))
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['OkCancelActions', 'WizardActions', 'ColorActions', "MenuActions"], {'ok': self.ipkinst,
                                                                                                          'green': self.ipkinst,
                                                                                                          'yellow': self.msgipkinst,
                                                                                                          'blue': self.msgipkrmv,
                                                                                                          'red': self.close,
                                                                                                          'menu': self.goConfig,
                                                                                                          'cancel': self.close}, -1)
        self.onLayoutFinish.append(self.refreshlist)

    def refreshlist(self):
        self.list = []
        del self.names[:]
        del self.list[:]

        path = self.ipkpth
        for root, dirs, files in os.walk(path):
            if files is not None:
                files.sort()
                for name in files:
                    if name.endswith('.ipk') or name.endswith('.deb') or name.endswith('.zip') or name.endswith('.tar.gz') or name.endswith('.tar'):
                        self.names.append(name)

        print(self.list)
        self.getfreespace()
        self['key_green'].show()
        self["list"].l.setList(self.list)
        showlist(self.names, self['list'])

    def msgipkrmv(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self['list'].getSelectionIndex()
        self.sel = self.names[idx]
        self.com = self.ipkpth + '/' + self.sel
        self.session.openWithCallback(self.msgipkrmv2, MessageBox, (_('Do you really want to remove selected?') + '\n' + self.sel), MessageBox.TYPE_YESNO)

    def msgipkrmv2(self, result):
        if result:
            if fileExists(self.com):
                os.remove(self.com)
                self.session.open(MessageBox, (_("%s has been successfully deleted\nwait time to refresh the list...") % self.sel), MessageBox.TYPE_INFO, timeout=5)
                i = len(self.list)
                del self.list[0:i]
            else:
                self.session.open(MessageBox, (_("%s not exist!\nwait time to refresh the list...") % self.sel), MessageBox.TYPE_INFO, timeout=5)
            self.refreshlist()

    def getfreespace(self):
        fspace = Utils.freespace()
        self['pth'].setText(fspace)

    def goConfig(self):
        self.session.open(tvConfig)

    def ipkinst(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self['list'].getSelectionIndex()
        self.sel = self.names[idx]
        self.session.openWithCallback(self.ipkinst2, MessageBox, (_('Do you really want to install the selected Addon?') + '\n' + self.sel), MessageBox.TYPE_YESNO)

    def ipkinst2(self, answer):
        if answer is True:
            self.dest = self.ipkpth + '/' + self.sel
            try:
                if self.sel.endswith('.ipk'):
                    # cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";opkg update > /dev/null; echo ":Install ' + self.dest + '";opkg install --force-overwrite ' + self.dest + ' > /dev/null'
                    cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + self.dest + '";opkg install --force-reinstall ' + self.dest + ' > /dev/null'
                    self.session.open(tvConsole, title='IPK Local Installation', cmdlist=[cmd0, 'sleep 5'], closeOnSuccess=False)
                elif self.sel.endswith('.tar.gz'):
                    # self.sel = self.sel[0]
                    cmd0 = 'tar -xzvf ' + self.dest + ' -C /'
                    self.session.open(tvConsole, title='TAR GZ Local Installation', cmdlist=[cmd0, 'sleep 5'], closeOnSuccess=False)
                elif self.sel.endswith('.deb'):
                    if Utils.DreamOS():
                        # self.sel = self.sel[0]
                        cmd0 = 'echo "Sistem Update .... PLEASE WAIT ::.....";echo ":Install ' + self.dest + '";apt-get install --reinstall %s -y' % self.dest  # + ' > /dev/null 2>&1' #+ self.dest + ' > /dev/null' #; apt-get -f --force-yes --assume-yes install'
                        self.session.open(tvConsole, title='DEB Local Installation', cmdlist=[cmd0], closeOnSuccess=False)
                    else:
                        self.session.open(MessageBox, _('Unknow Image!'), MessageBox.TYPE_INFO, timeout=5)
                elif self.sel.endswith('.zip'):
                    if 'picon' in self.sel.lower():
                        self.timer = eTimer()
                        self.timer.start(500, True)
                        cmd = ['unzip -o -q %s -d %s' % (self.dest, mmkpicon)]
                        # self.session.open(tvConsole, _('Installing: %s') % self.dest, cmdlist=[cmd])
                        self.session.open(tvConsole, _('Installing: %s') % self.dest, cmdlist=[cmd], closeOnSuccess=False)
                    elif 'setting' in self.sel.lower():
                        if not os.path.exists('/var/lib/dpkg/status'):
                            set = 1
                            terrestrial()
                        if os.path.exists("/tmp/unzipped"):
                            os.system('rm -rf /tmp/unzipped')
                        os.makedirs('/tmp/unzipped')
                        cmd = []
                        cmd1 = 'unzip -o -q %s -d /tmp/unzipped' % self.dest
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
                            cmd9 = 'cp -rf /tmp/unzipped/whitelist /etc/tuxbox/'
                            cmd.append(cmd9)
                        cmd10 = 'cp -rf /tmp/unzipped/satellites.xml /etc/tuxbox/'
                        cmd.append(cmd10)
                        cmd11 = 'cp -rf /tmp/unzipped/terrestrial.xml /etc/tuxbox/'
                        cmd.append(cmd11)
                        # if not os.path.exists('/var/lib/dpkg/status'):
                        self.timer = eTimer()
                        terrestrial_rest()
                        self.timer.start(500, True)
                        self.session.open(tvConsole, _('SETTING - install: %s') % self.dest, cmdlist=[cmd], closeOnSuccess=False)
                else:
                    self.session.open(MessageBox, _('Unknow Error!'), MessageBox.TYPE_ERROR, timeout=10)
            except Exception as e:
                print('error: ', str(e))
                self.delFile(self.dest)
                self['info1'].text = _('File: %s\nInstallation failed!') % self.dest

    def delFile(self, dest):
        if fileExists(self.dest):
            os.system('rm -rf ' + self.dest)
        self.refreshlist()

    def finished(self, result):
        return

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
        self.setTitle(_(title_plug))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_('Update'))
        self['key_green'] = Button(_('Restart'))
        self["key_blue"] = Button('')
        self['key_blue'].hide()
        self['key_green'].hide()
        self['info'] = Label('')
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['list'] = tvList([])
        self.Update = False
        self.dmlink = ''
        self.tlink = ''
        try:
            fp = ''
            destr = plugin_path + '/update.txt'
            req = Request(upd_path + 'updatePanel.txt')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0')
            fp = Utils.checkStr(urlopen(req))
            fp = fp.read()
            with open(destr, 'w') as f:
                f.write(fp)
                f.seek(0)
                f.close()
            with open(destr, 'r') as fp:
                # count = 0
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
                self.tlink = s2
                self.info = s3
                self.dmlink = s4
                fp.close()
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
                    self['key_green'].show()
        except:
            self.Update = False
            self['info'].setText(title_plug)
            self['pth'].setText('No updates available!')

        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.msgupdate1)
        else:
            self.timer.callback.append(self.msgupdate1)
        self.timer.start(1000, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
                                                                                           'cancel': self.close,
                                                                                           'green': self.msgipkrst1,
                                                                                           'red': self.close,
                                                                                           'yellow': self.msgupdate}, -1)

    def msgupdate1(self):
        if self.Update is False:
            return
        if config.plugins.tvaddon.autoupd.value is False:
            return
        else:
            self.session.openWithCallback(self.runupdate, MessageBox, (_('New update available!!\nDo you want update plugin ?\nPlease Reboot GUI after install!')), MessageBox.TYPE_YESNO)

    def msgupdate(self):
        if self.Update is False:
            return
        else:
            self.session.openWithCallback(self.runupdate, MessageBox, (_('Do you want update plugin ?\nPlease Reboot GUI after install!')), MessageBox.TYPE_YESNO)

    def runupdate(self, result):
        if result:
            if Utils.DreamOS():
                com = self.dmlink
                dom = 'New version ' + self.version
                tvtemp = '/tmp/tvaddon.tar'
                import requests
                r = requests.get(com)
                with open(tvtemp, 'wb') as f:
                    f.write(r.content)
                # os.system('wget %s -O /tmp/tvaddon.tar > /dev/null' % com)
                os.system('sleep 3')
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['tar -xvf /tmp/tvaddon.tar -C /'], finishedCallback=self.msgipkrst1, closeOnSuccess=False)
            else:
                com = self.tlink
                dom = 'New Version ' + self.version
                self.session.open(tvConsole, _('Install Update: %s') % dom, ['opkg install --force-reinstall %s' % com], finishedCallback=self.msgipkrst1, closeOnSuccess=False)

    def msgipkrst1(self):
        self.session.openWithCallback(self.ipkrestrt, MessageBox, (_('Do you want restart enigma2 ?')), MessageBox.TYPE_YESNO)

    def ipkrestrt(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if os.path.exists(epgbakpath):
                os.remove(epgbakpath)
            if os.path.exists(epgpath):
                shutil.copyfile(epgpath, epgbakpath)
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
        self.names = []
        self.container = eConsoleAppContainer()
        # self.container.appClosed.append(self.runFinished)
        try:
            self.container.appClosed.append(self.runFinished)
        except:
            self.appClosed_conn = self.container.appClosed.connect(self.runFinished)
        self['list'] = tvList([])
        self['key_green'] = Button(_('Uninstall'))
        self['key_yellow'] = Button(_('Restart'))
        self['key_red'] = Button(_('Back'))
        self["key_blue"] = Button('')
        self['key_blue'].hide()
        self['key_green'].hide()
        self['pth'] = Label('')
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
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

    def PluginDownloadBrowserClosed(self):
        self.openList()

    def runFinished(self, retval):
        # plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self['pth'].setText(_('Addons Packege removed successfully.'))
        self.getfreespace()

    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['pth'].setText(_('Process Killed by user.Addon not removed completly!'))

    def openList(self):
        # self.names = [:]
        self.lists = []
        del self.names[:]
        del self.list[:]
        self["list"].l.setList(self.list)
        path = ('/var/lib/opkg/info')
        if Utils.DreamOS():
            path = ('/var/lib/dpkg/info')
        for root, dirs, files in os.walk(path):
            if files is not None:
                files.sort()
                for name in files:
                    if name.endswith('.postinst') or name.endswith('.preinst') or name.endswith('.prerm') or name.endswith('.postrm'):
                        continue
                    if name.endswith('.md5sums') or name.endswith('.conffiles') or name.endswith('~'):
                        continue
                    if Utils.DreamOS():
                        if name.endswith('.list'):
                            name = name.replace('.list', '')
                    else:
                        if name.endswith('.control'):
                            name = name.replace('.control', '')
                        if name.endswith('.list'):
                            continue
                    if name.startswith('enigma2-plugin-'):
                        self.names.append(name)
        self['key_green'].show()
        showlist(self.names, self['list'])

    def message1(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.callMyMsg1, MessageBox, _("Do you want to remove?"), MessageBox.TYPE_YESNO)

    def callMyMsg1(self, result):
        if result:
            idx = self['list'].getSelectionIndex()
            dom = self.names[idx]
            com = dom
            if Utils.DreamOS():
                self.session.open(tvConsole, _('Removing: %s') % dom, ['dpkg -r %s' % com], closeOnSuccess=False)
            else:
                self.session.open(tvConsole, _('Removing: %s') % dom, ['opkg remove --force-removal-of-dependent-packages %s' % com], closeOnSuccess=False)
            self.getfreespace()

    def getfreespace(self):
        from Components.PluginComponent import plugins
        plugins.clearPluginList()
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        fspace = Utils.freespace()
        self['info'].setText(fspace)
        self.openList()

    def msgipkrst(self):
        self.session.openWithCallback(self.ipkrestrt, MessageBox, _('Do you want restart enigma2 ?'), MessageBox.TYPE_YESNO)

    def ipkrestrt(self, result):
        if result:
            epgpath = '/media/hdd/epg.dat'
            epgbakpath = '/media/hdd/epg.dat.bak'
            if os.path.exists(epgbakpath):
                os.remove(epgbakpath)
            if os.path.exists(epgpath):
                shutil.copyfile(epgpath, epgbakpath)
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()


class tvConfig(Screen, ConfigListScreen):
    def __init__(self, session):
        skin = skin_path + 'tvConfig.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.setup_title = _("Config")
        self.onChangedEntry = []
        self.session = session
        self.setTitle(_(title_plug))
        self['description'] = Label('')
        self["paypal"] = Label()
        self['info'] = Label(_('Config Panel Addon'))
        self['key_yellow'] = Button(_('Update'))
        self['key_green'] = Button(_('Save'))
        self['key_red'] = Button(_('Back'))
        self["key_blue"] = Button('')
        self['key_blue'].hide()
        self['title'] = Label(_(title_plug))
        self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'], {'cancel': self.extnok,
                                                                                                                                                  'red': self.extnok,
                                                                                                                                                  'back': self.close,
                                                                                                                                                  # 'left': self.keyLeft,
                                                                                                                                                  # 'right': self.keyRight,
                                                                                                                                                  'yellow': self.tvUpdate,
                                                                                                                                                  "showVirtualKeyboard": self.KeyText,
                                                                                                                                                  'ok': self.Ok_edit,
                                                                                                                                                  'green': self.msgok}, -1)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        paypal = self.paypal2()
        self["paypal"].setText(paypal)
        if not os.path.exists('/tmp/currentip'):
            os.system('wget -qO- http://ipecho.net/plain > /tmp/currentip')
        currentip1 = open('/tmp/currentip', 'r')
        currentip = currentip1.read()
        self['info'].setText(_('Config Panel Addon\nYour current IP is %s') % currentip)

    def paypal2(self):
        conthelp = "If you like what I do you\n"
        conthelp += " can contribute with a coffee\n\n"
        conthelp += "scan the qr code and donate € 1.00"
        return conthelp

    def setInfo(self):
        entry = str(self.getCurrentEntry())
        if entry == _('Auto Update Plugin'):
            self['description'].setText(_("If Active: Automatic Update Plugin"))
            return
        if entry == _('Set the path to the Picons folder'):
            self['description'].setText(_("Configure folder containing picons files"))
            return
        if entry == _('Path Manual IPK'):
            self['description'].setText(_("Path to the addon installation folder"))
            return
        if entry == _('Link in Extensions Menu'):
            self['description'].setText(_("Link in Extensions button"))
        if entry == _('Link in Main Menu'):
            self['description'].setText(_("Link in Main Menu"))
        return

    def tvUpdate(self):
        self.session.open(tvUpdate)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_('Auto Update Plugin'), config.plugins.tvaddon.autoupd))
        self.list.append(getConfigListEntry(_("Set the path to the Picons folder"), config.plugins.tvaddon.mmkpicon))
        self.list.append(getConfigListEntry(_('Path Manual IPK'), config.plugins.tvaddon.ipkpth))
        self.list.append(getConfigListEntry(_('Link in Extensions Menu'), config.plugins.tvaddon.strtext))
        self.list.append(getConfigListEntry(_('Link in Main Menu'), config.plugins.tvaddon.strtmain))
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

    def msgok(self):
        if os.path.exists(config.plugins.tvaddon.ipkpth.value) is False:
            self.session.open(MessageBox, _('Device not detected!'), MessageBox.TYPE_INFO, timeout=4)
        for x in self["config"].list:
            x[1].save()
        self.session.open(MessageBox, _('Successfully saved configuration'), MessageBox.TYPE_INFO, timeout=4)
        self.close(True)

    def Ok_edit(self):
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        print("current selection:", sel)
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
                windowTitle=_("Choose Directory:"),
                text=_("Choose directory"),
                currDir=str(path),
                bookmarks=config.movielist.videodirs,
                autoAdd=False,
                editDir=True,
                inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/var"],
                minFree=15)
        except Exception as e:
            print('error: ', str(e))

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
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback=None):
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
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving the settings?'))
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
        self['list'] = tvList([])
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
        self['info'] = Label('')
        self['info'].setText(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_('Remove'))
        self["key_blue"] = Button('')
        # self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
                                                                         'green': self.okRun,
                                                                         'yellow': self.remove,
                                                                         'back': self.closerm,
                                                                         'red': self.closerm,
                                                                         'cancel': self.closerm}, -1)
        self.onLayoutFinish.append(self.updateMenuList)

    def getfreespace(self):
        fspace = Utils.freespace()
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
        self['list'].setList(list)
        self['key_green'].show()
        self['info'].setText(_('Please select'))
        self.getfreespace()

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        if sel == ('MMARK PICONS BLACK'):
            self.session.open(MMarkFolder, host_blk)
        elif sel == 'MMARK PICONS TRANSPARENT':
            self.session.open(MMarkFolder, host_trs)
        elif sel == ('MMARK PICONS MOVIE'):
            self.session.open(MMarkPicons, 'MMark-Picons', host_mov, True)
        else:
            return

    def remove(self):
        self.session.openWithCallback(self.okRemove, MessageBox, (_("Do you want to remove all picons in folder?\n%s\nIt could take a few minutes, wait .." % mmkpicon)), MessageBox.TYPE_YESNO)

    def okRemove(self, result):
        if result:
            self['info'].setText(_('Erase %s... please wait' % mmkpicon))
            piconsx = glob.glob(str(mmkpicon) + '/*.png')
            for f in piconsx:
                try:
                    print("processing file: " + f)
                    os.remove(f)
                except OSError as e:
                    print("Error: %s : %s" % (f, e.strerror))
        self.session.open(MessageBox, _('%s it has been cleaned' % mmkpicon), MessageBox.TYPE_INFO, timeout=4)
        self['info'].setText(_('Please select ...'))


class MMarkFolder(Screen):
    def __init__(self, session, url):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('MMark')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.url = url
        # self.getfreespace()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)
        self.onLayoutFinish.append(self.getfreespace)

    def getfreespace(self):
        fspace = Utils.freespace()
        self['pform'].setText(fspace)

    def downxmlpage(self):
        url = six.ensure_binary(self.url)
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['info'].setText(_('Try again later ...'))
        # logdata("errorLoad ", error)
        self.downloading = False

    def _gotPageLoad(self, data):
        r = data
        if six.PY3:
            r = six.ensure_str(data)
        self.names = []
        self.urls = []
        try:
            n1 = r.find('"folderkey"', 0)
            n2 = r.find('more_chunks', n1)
            data2 = r[n1:n2]
            regex = '{"folderkey":"(.*?)".*?"name":"(.*?)".*?"created":"(.*?)"'
            match = re.compile(regex, re.DOTALL).findall(data2)
            for url, name, data in match:
                url = 'https://www.mediafire.com/api/1.5/folder/get_content.php?folder_key=' + url + '&content_type=files&chunk_size=1000&response_format=json'
                url = url.replace('\\', '')
                name = 'Picons-' + name
                self.urls.append(url)
                self.names.append(name)
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
            self.downloading = True
        except:
            self.downloading = False
        self.load_poster()

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self['list'].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        self.session.open(MMarkPicons, name, url)

    def cancel(self, result=None):
        self.downloading = False
        self.close(None)
        return


class MMarkPicons(Screen):
    def __init__(self, session, name, url, movie=False):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('MMark')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pth'].setText(_('Folder picons ') + mmkpicon)
        self['pform'] = Label('')
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.getfreespace()
        self.downloading = False
        self.movie = movie
        self.url = url
        self.name = name
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)
        self.onLayoutFinish.append(self.getfreespace)

    def getfreespace(self):
        fspace = Utils.freespace()
        self['pform'].setText(fspace)

    def downxmlpage(self):
        url = six.ensure_binary(self.url)
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['info'].setText(_('Try again later ...'))
        # logdata("errorLoad ", error)
        self.downloading = False

    def _gotPageLoad(self, data):
        r = data
        if six.PY3:
            r = six.ensure_str(data)
        self.names = []
        self.urls = []
        try:
            n1 = r.find('"quickkey":', 0)
            n2 = r.find('more_chunks', n1)
            data2 = r[n1:n2]
            regex = 'filename":"(.*?)".*?"created":"(.*?)".*?"downloads":"(.*?)".*?"normal_download":"(.*?)"'
            match = re.compile(regex, re.DOTALL).findall(data2)
            for name, data, download, url in match:
                if 'zip' in url:
                    url = url.replace('\\', '')
                    if self.movie:
                        name = name.replace('_', ' ').replace('-', ' ').replace('mmk', '').replace('.zip', '')
                        name = name + ' ' + data[0:10] + ' ' + 'Down: ' + download
                    else:
                        name = name.replace('_', ' ').replace('mmk', 'MMark').replace('.zip', '')
                        name = name + ' ' + data[0:10] + ' ' + 'Down:' + download
                    self.urls.append(url)
                    self.names.append(name)
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['list'])
            self.downloading = True
        except:
            self.downloading = False

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?\nIt could take a few minutes, wait ..")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.name = self.names[idx]
                url = self.urls[idx]
                dest = "/tmp/download.zip"
                print('url333: ', url)
                if os.path.exists(dest):
                    os.remove(dest)
                try:
                    myfile = Utils.ReadUrl2(url)
                    print('response: ', myfile)
                    regexcat = 'href="https://download(.*?)"'
                    match = re.compile(regexcat, re.DOTALL).findall(myfile)
                    print("match =", match[0])
                    # myfile = checkMyFile(url)
                    # print('myfile222:  ', myfile)
                    url = 'https://download' + str(match[0])
                    print("url final =", url)

                    # myfile = checkMyFile(url)
                    # print('myfile222:  ', myfile)
                    # # url =  'https://download' + str(myfile)

                    self.download = downloadWithProgress(url, dest)
                    self.download.addProgress(self.downloadProgress)
                    self.download.start().addCallback(self.install).addErrback(self.showError)
                except Exception as e:
                    print('error: ', str(e))
                    print("Error: can't find file or read data")

            else:
                self['info'].setText(_('Picons Not Installed ...'))

    def install(self, fplug):
        if os.path.exists('/tmp/download.zip'):
            self['info'].setText(_('Install ...'))
            myCmd = "unzip -o -q '/tmp/download.zip' -d %s/" % str(mmkpicon)
            # logdata("install2 ", myCmd)
            subprocess.Popen(myCmd, shell=True, executable='/bin/bash')
            self.mbox = self.session.open(MessageBox, _('Successfully Picons Installed'), MessageBox.TYPE_INFO, timeout=5)
        self['info'].setText(_('Please select ...'))
        self['progresstext'].text = ''
        self.progclear = 0
        self['progress'].setValue(self.progclear)
        self["progress"].hide()
        # self.downloading = False

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['info'].setText(_('Download ...'))
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def showError(self, error):
        self['info'].setText(_('Download Error ...'))
        print("download error =", error)
        self.downloading = False
        self.close()

    def finished(self, result):
        return


Panel_list4 = [
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
        self['list'] = tvList([])
        self['pth'] = Label('')
        self['pth'].setText(_('Support on'))
        self['pform'] = Label('')
        self['pform'].setText(_('linuxsat-support.com '))
        self['info'] = Label('')
        self['info'].setText(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions', ], {'ok': self.okRun,
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
        self['key_green'].show()
        self['list'].setList(list)
        self['info'].setText(_('Please select'))

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        sel = self.menu_list[idx]
        if sel == _('VIDEO ADDONS') or sel == 0:
            self.session.open(pluginx)
        elif sel == _('ADULT ADDON') or sel == 1:
            self.session.open(plugins_adult)
        elif sel == _('SCRIPT') or sel == 2:
            self.session.open(script)
        elif sel == _('REPOSITORY') or sel == 3:
            self.session.open(repository)


class pluginx(Screen):
    def __init__(self, session):
        self.session = session
        skin = skin_path + 'tvall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Kodilite by pcd')
        Screen.__init__(self, session)
        self.setTitle(_(title_plug))
        self.list = []
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pth'].setText(_('Support on'))
        self['pform'] = Label('')
        self['pform'].setText(_('linuxsat-support.com '))
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        self.url = "http://patbuweb.com/panel-addons/EnigmaOE2.0/kodilite/plugins"
        data = make_request(self.url)
        if six.PY3:
            data = six.ensure_str(data)
        print('data request', data)
        self.names = []
        self.urls = []
        try:
            match = re.compile(regexL, re.DOTALL).findall(data)
            print('match regex', match)
            for url, name, txt in match:
                if 'zip' in url:
                    url = 'http://patbuweb.com' + str(url)
                    name = name.replace("%20", " ").replace("-", " ").replace("_", " ").replace(".zip", "")
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' - ' + date
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                else:
                    self['info'].setText(_('No File!!'))
                    self.downloading = False
            showlist(self.names, self['list'])
            self['info'].setText(_('Please select'))
            self['key_green'].show()
            self.downloading = True
        except Exception as e:
            print('error: ', str(e))
            pass

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?\nIt could take a few minutes, wait ..")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.dom = self.names[idx]
                self.com = self.urls[idx]
                self.source = self.com.replace(str(self.url), '')
                print('source ', self.source)
                self.dest = "/tmp" + self.source
                print('dest ', self.dest)
                self.download = downloadWithProgress(self.com, self.dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(KodilitePcd):
            self.fdest = KodilitePcd + "/plugins"
            if fileExists(self.dest):
                title = _("Installation")
                cmd = "unzip -o -q '%s' -d '%s'" % (self.dest, self.fdest)
                self.session.open(tvConsole, _(title), cmdlist=[str(cmd)], closeOnSuccess=False)
            self['info'].setText(_('Please select ...'))
            self['progresstext'].text = ''
            self.progclear = 0
            self["progress"].hide()
            self['progress'].setValue(self.progclear)

    def showError(self, error):
        print("download error =", error)
        self.close()

    def cancel(self, result=None):
        self.close(None)
        return

    def finished(self, result):
        return

    def rst1(self):
        pass


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pth'].setText(_('Support on'))
        self['pform'] = Label('')
        self['pform'].setText(_('linuxsat-support.com '))
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun1,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        self.url = "http://patbuweb.com/panel-addons/EnigmaOE2.0/kodilite/pluginadult"
        data = make_request(self.url)
        if six.PY3:
            data = six.ensure_str(data)
        self.names = []
        self.urls = []
        try:
            match = re.compile(regexL, re.DOTALL).findall(data)
            for url, name, txt in match:
                if 'zip' in url:
                    url = "http://patbuweb.com" + url
                    name = name.replace("%20", " ").replace("-", " ").replace("_", " ").replace(".zip", "")
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' - ' + date
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                else:
                    self['info'].setText(_('No File!!'))
                    self.downloading = False
            showlist(self.names, self['list'])
            self['key_green'].show()
            self['info'].setText(_('Please select'))
            self.downloading = True
        except Exception as e:
            print('error: ', str(e))
            pass

    def okRun1(self):
        # adult = 'Adult'
        # if adult.lower() in name:
            # # self.catname = name
            self.allow()
        # else:
            # self.okRun()
            # self.close()

    def allow(self):
        if config.ParentalControl.configured.value:
            from Screens.InputBox import PinInput
            self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowTitle=_("Enter pin code"))
        else:
            self.pinEntered(True)

    def pinEntered(self, result):
        if result:
            self.okRun()
        else:
            self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
            self.close()

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?\nIt could take a few minutes, wait ..")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.dom = self.names[idx]
                self.com = self.urls[idx]
                self.source = self.com.replace(str(self.url), '')
                print('source ', self.source)
                self.dest = "/tmp" + self.source
                print('dest ', self.dest)
                self.download = downloadWithProgress(self.com, self.dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(KodilitePcd):
            self.fdest = KodilitePcd + "/plugins"
            if fileExists(self.dest):
                title = _("Installation")
                cmd = "unzip -o -q '%s' -d '%s'" % (self.dest, self.fdest)
                # print("debug: cmd:",type(cmd))
                self.session.open(tvConsole, _(title), cmdlist=[str(cmd)], closeOnSuccess=False)
            self['info'].setText(_('Please select ...'))
            self['progresstext'].text = ''
            self.progclear = 0
            self["progress"].hide()
            self['progress'].setValue(self.progclear)

    def showError(self, error):
        print("download error =", error)
        self.close()

    def cancel(self, result=None):
        self.close(None)
        return

    def finished(self, result):
        return

    def rst1(self):
        pass


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pth'].setText(_('Support on'))
        self['pform'] = Label('')
        self['pform'].setText(_('linuxsat-support.com '))
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        self.url = "http://patbuweb.com/panel-addons/EnigmaOE2.0/kodilite/script"
        data = make_request(self.url)
        if six.PY3:
            data = six.ensure_str(data)
        self.names = []
        self.urls = []
        try:
            match = re.compile(regexL, re.DOTALL).findall(data)
            for url, name, txt in match:
                if 'zip' in url:
                    url = "http://patbuweb.com" + url
                    name = name.replace("%20", " ").replace("-", " ").replace("_", " ").replace(".zip", "")
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' - ' + date
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                else:
                    self['info'].setText(_('No File!!'))
                    self.downloading = False
            showlist(self.names, self['list'])
            self['key_green'].show()
            self['info'].setText(_('Please select'))
        except Exception as e:
            print('error: ', str(e))
            pass

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?\nIt could take a few minutes, wait ..")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.dom = self.names[idx]
                self.com = self.urls[idx]
                self.source = self.com.replace(str(self.url), '')
                print('source ', self.source)
                self.dest = "/tmp" + self.source
                print('dest ', self.dest)
                self.download = downloadWithProgress(self.com, self.dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(KodilitePcd):
            self.fdest = KodilitePcd + "/scripts"
            if fileExists(self.dest):
                title = _("Installation")
                cmd = "unzip -o -q '%s' -d '%s'" % (self.dest, self.fdest)
                self.session.open(tvConsole, _(title), cmdlist=[str(cmd)], closeOnSuccess=False)
            self['info'].setText(_('Please select ...'))
            self['progresstext'].text = ''
            self.progclear = 0
            self["progress"].hide()
            self['progress'].setValue(self.progclear)

    def showError(self, error):
        print("download error =", error)
        self.close()

    def cancel(self, result=None):
        self.close(None)
        return

    def finished(self, result):
        return

    def rst1(self):
        pass


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
        self['list'] = tvList([])
        self.icount = 0
        self['info'] = Label(_('Loading data... Please wait'))
        self['pth'] = Label('')
        self['pth'].setText(_('Support on'))
        self['pform'] = Label('')
        self['pform'].setText(_('linuxsat-support.com '))
        self['progress'] = ProgressBar()
        self["progress"].hide()
        self['progresstext'] = StaticText()
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button('')
        self["key_blue"] = Button('')
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.downloading = False
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.downxmlpage)
        else:
            self.timer.callback.append(self.downxmlpage)
        self.timer.start(500, 1)
        self['title'] = Label(_(title_plug))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
                                                                       'green': self.okRun,
                                                                       'red': self.close,
                                                                       'cancel': self.close}, -2)

    def downxmlpage(self):
        self.url = "http://patbuweb.com/panel-addons/EnigmaOE2.0/Kodilite/repository"
        data = make_request(self.url)
        if six.PY3:
            data = six.ensure_str(data)
        self.names = []
        self.urls = []
        try:
            match = re.compile(regexL, re.DOTALL).findall(data)
            for url, name, txt in match:
                if 'zip' in url:
                    url = "http://patbuweb.com" + url
                    name = name.replace("%20", " ").replace("-", " ").replace("_", " ").replace(".zip", "")
                    date = re.search("(.+?)-(.+?)-(.+?) ", txt).group()
                    name = name + ' - ' + date
                    self.urls.append(Utils.checkStr(url.strip()))
                    self.names.append(Utils.checkStr(name.strip()))
                else:
                    self['info'].setText(_('No File!!'))
                    self.downloading = False
            showlist(self.names, self['list'])
            self['key_green'].show()
            self['info'].setText(_('Please select'))
        except Exception as e:
            print('error: ', str(e))
            pass

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        self.session.openWithCallback(self.okInstall, MessageBox, (_("Do you want to install?\nIt could take a few minutes, wait ..")), MessageBox.TYPE_YESNO)

    def okInstall(self, result):
        self['info'].setText(_('... please wait'))
        if result:
            if self.downloading is True:
                idx = self["list"].getSelectionIndex()
                self.dom = self.names[idx]
                self.com = self.urls[idx]
                self.source = self.com.replace(str(self.url), '')
                print('source ', self.source)
                self.dest = "/tmp" + self.source
                print('dest ', self.dest)
                self.download = downloadWithProgress(self.com, self.dest)
                self.download.addProgress(self.downloadProgress)
                self.download.start().addCallback(self.install).addErrback(self.showError)
            else:
                self.close()

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))

    def install(self, fplug):
        if os.path.exists(KodilitePcd):
            self.fdest = KodilitePcd + "/repos"
            if fileExists(self.dest):
                title = _("Installation")
                cmd = "unzip -o -q '%s' -d '%s'" % (self.dest, self.fdest)
                self.session.open(tvConsole, _(title), cmdlist=[str(cmd)], closeOnSuccess=False)
            self['info'].setText(_('Please select ...'))
            self['progresstext'].text = ''
            self.progclear = 0
            self["progress"].hide()
            self['progress'].setValue(self.progclear)

    def showError(self, error):
        print("download error =", error)
        self.close()

    def cancel(self, result=None):
        self.close(None)
        return

    def finished(self, result):
        return

    def rst1(self):
        pass


def main(session, **kwargs):
    try:
        if Utils.zCheckInternet(1):
            # if config.plugins.tvaddon.autoupd.value is True:
            try:
                from . import Update
                Update.upd_done()
            except Exception as e:
                print(str(e))
            session.open(Hometv)
        else:
            from Screens.MessageBox import MessageBox
            from Tools.Notifications import AddPopup
            AddPopup(_("Sorry but No Internet :("), MessageBox.TYPE_INFO, 10, 'Sorry')
    except:
        pass


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('TiVuStream Addons'), main, 'TiVuStream Addons Panel', 44)]
    else:
        return []


def cfgmain(menuid):
    if menuid == 'mainmenu':
        return [('TiVuStream Addons', main, 'TiVuStream Addons Panel', 44)]
    else:
        return []


def mainmenu(session, **kwargs):
    main(session, **kwargs)


def Plugins(**kwargs):
    ico_path = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        ico_path = plugin_path + '/res/pics/logo.png'
    extDescriptor = PluginDescriptor(name=name_plug, description=title_plug, where=PluginDescriptor.WHERE_EXTENSIONSMENU, icon=ico_path, fnc=main)
    mainDescriptor = PluginDescriptor(name=name_plug, description=title_plug, where=PluginDescriptor.WHERE_MENU, icon=ico_path, fnc=cfgmain)
    result = [PluginDescriptor(name=name_plug, description=title_plug, where=[PluginDescriptor.WHERE_PLUGINMENU], icon=ico_path, fnc=main)]
    if config.plugins.tvaddon.strtext.value:
        result.append(extDescriptor)
    if config.plugins.tvaddon.strtmain.value:
        result.append(mainDescriptor)
    return result


def terrestrial():
    SavingProcessTerrestrialChannels = StartSavingTerrestrialChannels()
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
        # icount = 0
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
        if os.path.exists('/etc/enigma2/lcndb'):
            lcnstart()


def lcnstart():
    print(' lcnstart ')
    if os.path.exists('/etc/enigma2/lcndb'):
        lcn = Lcn.LCN()
        lcn.read()
        if len(lcn.lcnlist) > 0:
            lcn.writeBouquet()
            # lcn.reloadBouquet()
            ReloadBouquets()
    return


def StartSavingTerrestrialChannels():
    def ForceSearchBouquetTerrestrial():
        for file in sorted(glob.glob("/etc/enigma2/*.tv")):
            if 'tivustream' in file:
                continue
            f = open(file, "r").read()
            x = f.strip()
            x = x.lower()
            if x.find('http'):
                continue
            if x.find('eeee0000') != -1:
                if x.find('82000') == -1 and x.find('c0000') == -1:
                    return file
                    break

    def ResearchBouquetTerrestrial(search):
        for file in sorted(glob.glob("/etc/enigma2/*.tv")):
            if 'tivustream' in file:
                continue
            f = open(file, "r").read()
            x = f.strip()
            x = x.lower()
            x1 = f.strip()
            if x1.find("#NAME") != -1:
                if x.lower().find((search.lower())) != -1:
                    if x.find('http'):
                        continue
                    if x.find('eeee0000') != -1:
                        return file
                        break

    def SaveTrasponderService():
        TrasponderListOldLamedb = open(plugin_path + '/temp/TrasponderListOldLamedb', 'w')
        ServiceListOldLamedb = open(plugin_path + '/temp/ServiceListOldLamedb', 'w')
        Trasponder = False
        inTransponder = False
        inService = False
        try:
            LamedbFile = open('/etc/enigma2/lamedb')
            while 1:
                line = LamedbFile.readline()
                if not line:
                    break
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
                    ServiceListOldLamedb.write(tmp[0] + ":" + tmp[1] + ":" + tmp[2] + ":" + tmp[3] + ":" + tmp[4] + ":0\n")
                    line = LamedbFile.readline()
                    ServiceListOldLamedb.write(line)
                    line = LamedbFile.readline()
                    ServiceListOldLamedb.write(line)
                TrasponderListOldLamedb.close()
                ServiceListOldLamedb.close()
                if not Trasponder:
                    os.system('rm -fr ' + plugin_path + '/temp/TrasponderListOldLamedb')
                    os.system('rm -fr ' + plugin_path + '/temp/ServiceListOldLamedb')
        except Exception as e:
            print('error: ', str(e))
            pass
        return Trasponder

    def CreateBouquetForce():
        WritingBouquetTemporary = open(plugin_path + '/temp/TerrestrialChannelListArchive', 'w')
        WritingBouquetTemporary.write('#NAME Digitale Terrestre\n')
        ReadingTempServicelist = open(plugin_path + '/temp/ServiceListOldLamedb').readlines()
        for jx in ReadingTempServicelist:
            if jx.find('eeee') != -1:
                String = jx.split(':')
                WritingBouquetTemporary.write('#SERVICE 1:0:%s:%s:%s:%s:%s:0:0:0:\n' % (hex(int(String[4]))[2:], String[0], String[2], String[3], String[1]))
        WritingBouquetTemporary.close()

    def SaveBouquetTerrestrial():
        NameDirectory = ResearchBouquetTerrestrial('terr')
        if not NameDirectory:
            NameDirectory = ForceSearchBouquetTerrestrial()
        try:
            shutil.copyfile(NameDirectory, plugin_path + '/temp/TerrestrialChannelListArchive')
            return True
        except Exception as e:
            print('error: ', str(e))
            pass
        return
    Service = SaveTrasponderService()
    if Service:
        if not SaveBouquetTerrestrial():
            CreateBouquetForce()
        return True


def LamedbRestore():
    try:
        TrasponderListNewLamedb = open(plugin_path + '/temp/TrasponderListNewLamedb', 'w')
        ServiceListNewLamedb = open(plugin_path + '/temp/ServiceListNewLamedb', 'w')
        inTransponder = False
        inService = False
        infile = open("/etc/enigma2/lamedb")
        while 1:
            line = infile.readline()
            if not line:
                break
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
        WritingLamedbFinal = open("/etc/enigma2/lamedb", "w")
        WritingLamedbFinal.write("eDVB services /4/\n")
        TrasponderListNewLamedb = open(plugin_path + '/temp/TrasponderListNewLamedb').readlines()
        for x in TrasponderListNewLamedb:
            WritingLamedbFinal.write(x)
        try:
            TrasponderListOldLamedb = open(plugin_path + '/temp/TrasponderListOldLamedb').readlines()
            for x in TrasponderListOldLamedb:
                WritingLamedbFinal.write(x)
        except:
            pass
        WritingLamedbFinal.write("end\n")
        ServiceListNewLamedb = open(plugin_path + '/temp/ServiceListNewLamedb').readlines()
        for x in ServiceListNewLamedb:
            WritingLamedbFinal.write(x)
        try:
            ServiceListOldLamedb = open(plugin_path + '/temp/ServiceListOldLamedb').readlines()
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
                if re.search("#NAME Digitale Terrestre", x, flags=re.IGNORECASE):
                    return "/etc/enigma2/"+file
    try:
        TerrestrialChannelListArchive = open(plugin_path + '/temp/TerrestrialChannelListArchive').readlines()
        DirectoryUserBouquetTerrestrial = RestoreTerrestrial()
        if DirectoryUserBouquetTerrestrial:
            TrasfBouq = open(DirectoryUserBouquetTerrestrial, 'w')
        for Line in TerrestrialChannelListArchive:
            if Line.lower().find('#name') != -1:
                TrasfBouq.write('#NAME Digitale Terrestre\n')
            else:
                TrasfBouq.write(Line)
        TrasfBouq.close()
        return True
    except:
        return False
# ======================================================
