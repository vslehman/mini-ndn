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

class NdnPing(object):
    def __init__(self, host, **kwargs):
        self.host = host
        self.interval = kwargs.get('interval', None)
        self.timeout = kwargs.get('timeout', None)
        self.count = kwargs.get('count', None)
        self.starting_seq_no = kwargs.get('starting_seq_no', None)
        self.identifier = kwargs.get('identifier', None)
        self.allow_cached_data = kwargs.get('allow_cached_data', False)
        self.print_timestamp = kwargs.get('print_timestamp', False)
        self.log_file = kwargs.get('log_file', None)

    def start(self, name_prefix):
        args = ['ndnping',]
        if self.interval is not None:
            args.extend(('-i', self.interval))
        if self.timeout is not None:
            args.extend(('-o', self.timeout))
        if self.count is not None:
            args.extend(('-c', self.count))
        if self.starting_seq_no is not None:
            args.extend(('-n', self.starting_seq_no))
        if self.identifier is not None:
            args.extend(('-p', self.identifier))
        if self.allow_cached_data:
            args.append('-a')
        if self.print_timestamp:
            args.append('-t')
        args.append(name_prefix)
        if self.log_file is not None:
            args.extend(('>>', self.log_file))
        args.append('&')

        args = [str(arg) for arg in args]
        self.host.cmd(' '.join(args))

def ping(host, name_prefix, **kwargs):
    ping = NdnPing(host, **kwargs)
    ping.start(name_prefix)
