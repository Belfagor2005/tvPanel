#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
PY3 = sys.version_info.major >= 3
print("Update.py")


def upd_done():
    from os import popen, system
    installUrl = 'https://raw.githubusercontent.com/Belfagor2005/tvPanel/main/installer.sh'
    cmd00 = 'wget -q "--no-check-certificate" ' + installUrl + ' -O - | /bin/sh'
    popen(cmd00)
    # cmd01 = "wget --no-cache --no-dns-cache http://patbuweb.com/tvPanelxxx/tvaddon.tar -O /tmp/tvaddon.tar --post-data='action=purge';tar -xvf /tmp/tvaddon.tar -C /"
    # cmd02 = "wget --no-check-certificate --no-cache --no-dns-cache -U 'Enigma2 - TvAddon Plugin' -c 'https://patbuweb.com/tvPanelxxx/tvaddon.tar' -O '/tmp/tvaddon.tar' --post-data='action=purge';tar -xvf /tmp/tvaddon.tar -C /; rm -rf /tmp/tvaddon.tar"
    # cmd22 = 'find /usr/bin -name "wget"'
    # res = popen(cmd22).read()
    # if 'wget' not in res.lower():
        # if os.path.exists('/etc/opkg'):
            # cmd23 = 'opkg update && opkg install wget'
        # else:
            # cmd23 = 'apt-get update && apt-get install wget'
        # popen(cmd23)
    # try:
        # popen(cmd02)
    # except:
        # popen(cmd01)
    # system('rm -rf /tmp/tvaddon.tar')
    return
