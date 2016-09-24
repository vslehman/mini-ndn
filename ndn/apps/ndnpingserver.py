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


class NdnPingServer(object):
    def __init__(self, host, **kwargs):
        self.host = host
        self.freshness = kwargs.get('freshness', None)
        self.satisfy = kwargs.get('satisfy', None)
        self.timestamp = kwargs.get('timestamp', False)
        self.size = kwargs.get('size', None)

    def start(self, name_prefix):
        args = ['ndnpingserver',]
        args.extend(('--freshness', self.freshness)) if self.freshness
        args.extend(('--satisfy', self.satisfy)) if self.satisfy
        args.append('-t') if self.timestamp
        args.extend(('--size', self.size)) if self.size
        args.append(name_prefix)
        args.extend(('>>', log_file)) if self.log_file
        args.append('&')

        host.cmd(' '.join(args))


def ping(host, name_prefix, **kwargs):
    server = NdnPingServer(host, **kwargs)
    server.start(name_prefix)
