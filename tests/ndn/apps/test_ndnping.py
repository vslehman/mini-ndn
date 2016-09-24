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

import unittest

import ndn.apps.ndnping as ndnping

class MockHost(object):
    def __init__(self):
        self.cmds = []

    def cmd(self, cmd_input):
        self.cmds.append(cmd_input)

class TestNdnPing(unittest.TestCase):
    def setUp(self):
        self.host = MockHost()
        self.name_prefix = '/ndn/edu/memphis/ping'

    def test_default(self):
        ndnping.ping(self.host, self.name_prefix)

        expected_cmd = "ndnping {} &".format(self.name_prefix)
        self.assertTrue(self.host.cmds[0] == expected_cmd)

    def test_args(self):
        args = {
            'interval': 100,
            'timeout': 1000,
            'count': 10,
            'starting_seq_no': 1234,
            'identifier': 'test',
            'allow_cached_data': True,
            'print_timestamp': True,
            'log_file': 'ping-log.txt'
        }

        ndnping.ping(self.host, self.name_prefix, **args)

        expected_cmd = "ndnping -i 100 -o 1000 -c 10 -n 1234 -p test -a -t {} >> ping-log.txt &".format(self.name_prefix)
        self.assertTrue(self.host.cmds[0] == expected_cmd)

