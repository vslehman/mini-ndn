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
import unittest
from mock import mock_open, patch

import minindn
from minindn.topology import Topology

class TestTopology(unittest.TestCase):
    def test_basic(self):
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
                   },
                   {
                     "name": "NodeB",
                     "cores": 2,
                     "cache": 10,
                     "new_param": true
                   }
                 ],
                 "switches": [
                   {
                     "name": "switchA"
                   }
                 ],
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

        topo = Topology(config, 'work_dir')
        self.assertEqual(len(topo.hosts_conf), 2)
        self.assertEqual(len(topo.switches_conf), 1)
        self.assertEqual(len(topo.links_conf), 1)
        self.assertTrue(topo.is_tc_link)
        self.assertTrue(topo.is_limited)

