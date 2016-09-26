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

import os
import re
import shutil
import subprocess
import time

from minindn.common import MINI_NDN_INSTALL_DIR
from ndn.ndn_application import NdnApplication

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

VERSION = _get_version()

_CONF_TEMPLATE_STRING = None
def _create_conf_template_string():
    if _CONF_TEMPLATE_STRING is None:
        # Use nfd.conf as default configuration for NFD, otherwise use the sample configuration
        if os.path.isfile(NFD_CONF_FILE):
            with open(NFD_CONF_FILE, 'r') as conf_file:
                _CONF_TEMPLATE_STRING = conf_file.read()
        elif os.path.isfile(NFD_SAMPLE_CONF_FILE):
            with open(NFD_SAMPLE_CONF_FILE, 'r') as conf_file:
                _CONF_TEMPLATE_STRING = conf_file.read()
        else:
            raise IOError("Neither nfd.conf or nfd.conf.sample can be found in {}!".format(NFD_CONF_DIR))

    return _CONF_TEMPLATE_STRING


def setup():
    _create_conf_template_string()

class Nfd(NdnApplication):
    def __init__(self, node):
        NdnApplication.__init__(self, node)

        self.logLevel = node.params["params"].get("nfd-log-level", "NONE")

        self.confFile   = os.path.join(node.homeFolder, '{}.conf'.format(node.name))
        self.logFile    = os.path.join(node.homeFolder, '{}.log'.format(node.name))
        self.sockFile   = os.path.abspath("/var/run/{}.sock".format(node.name))
        self.ndnFolder  = os.path.join(node.homeFolder, '.ndn')
        self.clientConf = os.path.join(node.ndnFolder, 'client.conf')

        # Create conf file
        conf_str = _CONF_TEMPLATE_STRING
        conf_str = re.sub('default_level [A-Z]*$', 'default_level {}'.format(self.logLevel), conf_str)
        conf_str = conf_str.replace('nfd.sock', '{}.sock'.format(node.name))

        with open(self.confFile, 'w') as conf_file:
            conf_file.write(conf_str)

        # Make NDN folder
        try:
            os.mkdir(self.ndnFolder)
        except OSError as e:
            pass

        # Create client.conf file
        with open('/usr/local/etc/mini-ndn/client.conf.sample', 'r') as client_conf_file:
            client_conf_str = client_conf_file.read()
            client_conf_str = client_conf_str.replace('nfd.sock', '{}.sock'.format(node.name))

        with open(self.clientConf, 'w') as client_conf_file:
            client_conf_file.write(client_conf_str)

        # Change home folder
        node.cmd("export HOME=%s" % node.homeFolder)

    def start(self):
        NdnApplication.start(self, "nfd --config %s 2>> %s &" % (self.confFile, self.logFile))
        time.sleep(2)

    def setStrategy(self, name, strategy):
        self.node.cmd("nfdc set-strategy %s ndn:/localhost/nfd/strategy/%s" % (name, strategy))
        time.sleep(0.5)
