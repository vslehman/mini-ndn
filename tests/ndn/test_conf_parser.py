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
import unittest

from ndn import conf_parser

class TestConfParser(unittest.TestCase):
    def test_parse_hosts(self):
        json_config = """
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

        hosts = conf_parser._parse_hosts(json.loads(json_config))
        print hosts

    def test_parse_switches(self):
        json_config = """
            {
              "switches": [
                {
                  "name": "switchA"
                }
              ]
            }
        """

        switches = conf_parser._parse_switches(json.loads(json_config))
        print switches

    def test_parse_links(self):
        json_config = """
            {
              "links": [
                {
                  "host1": "A",
                  "host2": "B",
                  "bandwidth": 100,
                  "jitter": 10,
                  "max_queue_size": 128,
                  "loss_rate": 10.0
                }
              ]
            }
        """

        links = conf_parser._parse_links(json.loads(json_config))
        print links

