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

import minindn

class TestConfParser(unittest.TestCase):
    def test_parse_hosts(self):
        json_config = textwrap.dedent(
            """minindn-conf:2.0
               {
                 "hosts": [
                   {
                     "name": "NodeA",
                     "params": "params",
                     "cpu": 10,
                     "cores": 2,
                     "cache": 10,
                     "new_param": true
                   }
                 ]
               }
            """
        )

        with patch('minindn.config.open', mock_open(read_data=json_config), create=True):
            config = minindn.config.parse('test.conf')

        self.assertEqual(len(config.hosts), 1)

        host = config.hosts[0]
        self.assertEqual(host.name, 'NodeA')
        self.assertEqual(host.params, 'params')
        self.assertEqual(host.cpu, 10)
        self.assertEqual(host.cores, 2)
        self.assertEqual(host.cache, 10)
        self.assertEqual(host.new_param, True)

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

        with patch('minindn.config.open', mock_open(read_data=json_config), create=True):
            config = minindn.config.parse('test.conf')

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

        with patch('minindn.config.open', mock_open(read_data=json_config), create=True):
            config = minindn.config.parse('test.conf')

        self.assertEqual(len(config.links), 1)

        link = config.links[0]
        self.assertEqual(link.host1, 'NodeA')
        self.assertEqual(link.host2, 'NodeB')
        self.assertEqual(link.delay, 1000)
        self.assertEqual(link.bw, 100)
        self.assertEqual(link.jitter, 10)
        self.assertEqual(link.max_queue_size, 128)
        self.assertEqual(link.loss, 15)

    def test_parse_apps(self):
        json_config = textwrap.dedent(
            """minindn-conf:2.0
               {
                 "hosts": [
                   {
                     "name": "NodeA",
                     "apps": [
                       {
                         "name": "nfd",
                         "log_level": "INFO"
                       },
                       {
                         "name": "nlsr",
                         "hyperbolic_state": "hr",
                         "radius": 12.34,
                         "angle": 1.234,
                         "network": "/ndn",
                         "site": "/edu/memphis",
                         "router": "router_name",
                         "log_level": "DEBUG",
                         "max_faces_per_prefix": 4
                       }
                     ]
                   }
                 ]
               }
            """
        )

        with patch('minindn.config.open', mock_open(read_data=json_config), create=True):
            config = minindn.config.parse('test.conf')

        self.assertEqual(len(config.hosts), 1)

        host = config.hosts[0]
        nfd = next(app for app in host.apps if app.name == 'nfd')
        self.assertEqual(nfd.log_level, 'INFO')

        nlsr = next(app for app in host.apps if app.name == 'nlsr')
        self.assertEqual(nlsr.hyperbolic_state, 'hr')


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

        config = minindn.config.parse(temp_file.name)

        # Hosts
        self.assertEqual(len(config.hosts), 4)

        host_names = [host.name for host in config.hosts]
        self.assertTrue('a' in host_names)
        self.assertTrue('b' in host_names)
        self.assertTrue('c' in host_names)
        self.assertTrue('d' in host_names)

        a = next(host for host in config.hosts if host.name == 'a')
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

        link_names = [(link.host1, link.host2) for link in config.links]
        self.assertTrue(('a', 'b') in link_names)
        self.assertTrue(('a', 'c') in link_names)
        self.assertTrue(('b', 'd') in link_names)

        link = next(link for link in config.links if link.host1 == 'a' and link.host2 == 'b')
        self.assertEqual(link.delay, '1000ms')
        self.assertEqual(link.bw, 100)
        self.assertEqual(link.jitter, 10)
        self.assertEqual(link.max_queue_size, 128)
        self.assertEqual(link.loss, 15)

