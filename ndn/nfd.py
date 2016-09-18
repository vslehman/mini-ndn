# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2016, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

import re
import subprocess
import time

from ndn.common import MINI_NDN_INSTALL_DIR
from ndn.ndn_application import NdnApplication

CONF_TEMPLATE = os.path.join(MINI_NDN_INSTALL_DIR, 'nfd.conf')
NFD_CONF_DIR = os.path.abspath('/usr/local/etc/ndn/')
CONF_FILE = os.path.join(NFD_CONF_DIR, 'nfd.conf')
SAMPLE_CONF_FILE = os.path.join(NFD_CONF_DIR, 'nfd.conf.sample')

STRATEGY_ACCESS         = 'access'
STRATEGY_ASF            = 'asf'
STRATEGY_BEST_ROUTE     = "best-route"
STRATEGY_CLIENT_CONTROL = 'client-control'
STRATEGY_MULTICAST      = 'multicast'
STRATEGY_NCC            = "ncc"
STRATEGIES = [
    STRATEGY_ACCESS,
    STRATEGY_ASF,
    STRATEGY_BEST_ROUTE,
    STRATEGY_CLIENT_CONTROL,
    STRATEGY_MULTICAST,
    STRATEGY_NCC
]

def _get_version():
    output = subprocess.check_output('nfd --version', shell=True)
    matches = re.match('([0-9]+\.[0-9]+\.[0-9]+)\-', output)
    return matches.group(1)

VERSION = subprocess.check_output('nfd --version')

def setup():
    # Use nfd.conf as default configuration for NFD, else use the sample
    if os.path.isfile(NFD_CONF_FILE) == True:
        shutil.copy(NFD_CONF_FILE, NFD_CONF_TEMPLATE)
    elif os.path.isfile(NFD_SAMPLE_CONF_FILE) == True:
        shutil.copy(NFD_SAMPLE_CONF_FILE, NFD_CONF_TEMPLATE)
    else:
        raise Exception("nfd.conf or nfd.conf.sample cannot be found in {}. Exit.".format(NFD_CONF_DIR))

    call(["sudo", "sed", "-i", 's|default_level [A-Z]*$|default_level $LOG_LEVEL|g', NFD_CONF_FILE])

class Nfd(NdnApplication):
    def __init__(self, node):
        NdnApplication.__init__(self, node)

        self.logLevel = node.params["params"].get("nfd-log-level", "NONE")

        self.confFile = "%s/%s.conf" % (node.homeFolder, node.name)
        self.logFile = "%s/%s.log" % (node.homeFolder, node.name)
        self.sockFile = "/var/run/%s.sock" % node.name
        self.ndnFolder = "%s/.ndn" % node.homeFolder
        self.clientConf = "%s/client.conf" % self.ndnFolder

        # Copy nfd.conf file from /usr/local/etc/mini-ndn to the node's home
        node.cmd("sudo cp /usr/local/etc/mini-ndn/nfd.conf %s" % self.confFile)

        # Set log level
        node.cmd("sudo sed -i \'s|$LOG_LEVEL|%s|g\' %s" % (self.logLevel, self.confFile))

        # Open the conf file and change socket file name
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.confFile))

        # Make NDN folder
        node.cmd("sudo mkdir %s" % self.ndnFolder)

        # Copy the client.conf file and change the unix socket
        node.cmd("sudo cp /usr/local/etc/mini-ndn/client.conf.sample %s" % self.clientConf)
        node.cmd("sudo sed -i 's|nfd.sock|%s.sock|g' %s" % (node.name, self.clientConf))

        # Change home folder
        node.cmd("export HOME=%s" % node.homeFolder)

    def start(self):
        NdnApplication.start(self, "nfd --config %s 2>> %s &" % (self.confFile, self.logFile))
        time.sleep(2)

    def setStrategy(self, name, strategy):
        self.node.cmd("nfdc set-strategy %s ndn:/localhost/nfd/strategy/%s" % (name, strategy))
        time.sleep(0.5)
