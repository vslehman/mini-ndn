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

import logging

from mininet.topo import Topo as MnTopo

class Topology(MnTopo):
    def __init__(self, config, work_dir, **opts):
        MnTopo.__init__(self, **opts)

        self.hosts_conf = config.hosts
        self.switches_conf = config.switches
        self.links_conf = config.links

        self.is_tc_link = False
        self.is_limited = False

        for host in self.hosts_conf:
            if host.cpu is not None and self.is_limited is False:
                self.is_limited = True

            self.addHost(
                host.name,
                apps=host.apps,
                params=host.params,
                cpu=host.cpu,
                cores=host.cores,
                cache=host.cache,
                workdir=work_dir
            )

        for switch in self.switches_conf:
            self.addSwitch(switch.name)

        for link in self.links_conf:
            if len(link.link_dict) == 0:
                self.addLink(link.host1, link.host2)
            else:
                self.addLink(link.host1, link.host2, **link.link_dict)
                self.is_tc_link = True

        logging.info('Done parsing {}'.format(config.name))

