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

import json
import textwrap
import tempfile
import unittest
from mock import mock_open, patch

from ndn import conf_parser

class TestConfParser(unittest.TestCase):
    def test_parse_hosts(self):
        json_config = textwrap.dedent(
            """minindn-conf:2.0
               {
                 "hosts": [
                   {
                     "name": "NodeA",
                     "app": "test_app",
                     "params": "params",
                     "cpu": 10,
                     "cores": 2,
                     "cache": 10
                   }
                 ]
               }
            """
        )

        with patch('ndn.conf_parser.open', mock_open(read_data=json_config), create=True):
            config = conf_parser.parse('test.conf')

        self.assertEqual(len(config.hosts), 1)

        host = config.hosts[0]
        self.assertEqual(host.name, 'NodeA')
        self.assertEqual(host.app, 'test_app')
        self.assertEqual(host.params, 'params')
        self.assertEqual(host.cpu, 10)
        self.assertEqual(host.cores, 2)
        self.assertEqual(host.cache, 10)

    def test_parse_switches(self):
        json_config = textwrap.dedent(
            """minindn-conf:2.0
               {
                 "switches": [
                   {
                     "name": "switchA"
                   }
                 ]
               }
            """
        )

        with patch('ndn.conf_parser.open', mock_open(read_data=json_config), create=True):
            config = conf_parser.parse('test.conf')

        self.assertEqual(len(config.switches), 1)

        switch = config.switches[0]
        self.assertEqual(switch.name, 'switchA')

    def test_parse_links(self):
        json_config = textwrap.dedent(
            """minindn-conf:2.0
               {
                 "links": [
                   {
                     "host1": "NodeA",
                     "host2": "NodeB",
                     "delay": 1000.0,
                     "bandwidth": 100,
                     "jitter": 10,
                     "max_queue_size": 128,
                     "loss_rate": 15.0
                   }
                 ]
               }
            """
        )

        with patch('ndn.conf_parser.open', mock_open(read_data=json_config), create=True):
            config = conf_parser.parse('test.conf')

        self.assertEqual(len(config.links), 1)

        link = config.links[0]
        self.assertEqual(link.h1, 'NodeA')
        self.assertEqual(link.h2, 'NodeB')
        self.assertEqual(link.linkDict['delay'], 1000)
        self.assertEqual(link.linkDict['bw'], 100)
        self.assertEqual(link.linkDict['jitter'], 10)
        self.assertEqual(link.linkDict['max_queue_size'], 128)
        self.assertEqual(link.linkDict['loss'], 15)

    def test_parse_v1_0(self):
        config = textwrap.dedent(
            """
               [nodes]
               a: cpu=100 cores=2 cache=10 app="test_app" radius=12.34 angle=1.234
               b: _
               c: _
               d: _
               [switches]
               a: _
               [links]
               a:b delay=1000ms bw=100 jitter=10 max_queue_size=128 loss=15
               a:c delay=100ms bw=100
               b:d delay=10ms bw=10
            """
        )

        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(config)
        temp_file.seek(0)

        config = conf_parser.parse(temp_file.name)

        # Hosts
        self.assertEqual(len(config.hosts), 4)

        host_names = [host.name for host in config.hosts]
        self.assertTrue('a' in host_names)
        self.assertTrue('b' in host_names)
        self.assertTrue('c' in host_names)
        self.assertTrue('d' in host_names)

        a = [host for host in config.hosts if host.name == 'a'][0]
        self.assertEqual(a.name, 'a')
        self.assertEqual(a.app, 'test_app')
        self.assertEqual(a.cpu, 100)
        self.assertEqual(a.cores, '2')
        self.assertEqual(a.cache, '10')
        self.assertEqual(a.nlsrParameters['radius'], '12.34')
        self.assertEqual(a.nlsrParameters['angle'], '1.234')

        # Switches
        self.assertEqual(len(config.switches), 1)
        self.assertEqual(config.switches[0].name, 'a')

        # Links
        self.assertEqual(len(config.links), 3)

        link_names = [(link.h1, link.h2) for link in config.links]
        self.assertTrue(('a', 'b') in link_names)
        self.assertTrue(('a', 'c') in link_names)
        self.assertTrue(('b', 'd') in link_names)

        link = [link for link in config.links if link.h1 == 'a' and link.h2 == 'b'][0]
        self.assertEqual(link.linkDict['delay'], '1000ms')
        self.assertEqual(link.linkDict['bw'], 100)
        self.assertEqual(link.linkDict['jitter'], 10)
        self.assertEqual(link.linkDict['max_queue_size'], 128)
        self.assertEqual(link.linkDict['loss'], 15)

