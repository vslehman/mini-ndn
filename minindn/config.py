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
#
# This file incorporates work covered by the following copyright and
# permission notice:
#
#   Mininet 2.2.1 License
#
#   Copyright (c) 2013-2015 Open Networking Laboratory
#   Copyright (c) 2009-2012 Bob Lantz and The Board of Trustees of
#   The Leland Stanford Junior University
#
#   Original authors: Bob Lantz and Brandon Heller
#
#   We are making Mininet available for public use and benefit with the
#   expectation that others will use, modify and enhance the Software and
#   contribute those enhancements back to the community. However, since we
#   would like to make the Software available for broadest use, with as few
#   restrictions as possible permission is hereby granted, free of charge, to
#   any person obtaining a copy of this Software to deal in the Software
#   under the copyrights without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#   TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#   The name and trademarks of copyright holder(s) may NOT be used in
#   advertising or publicity pertaining to the Software or any derivatives
#   without specific, written prior permission.

import ConfigParser
import json
import re
import shlex


class Config(object):
    def __init__(self, name):
        self.name = name
        self.hosts = []
        self.switches = []
        self.links = []


def parse(template_file):
    with open(template_file, 'r') as config_file:
        config_str = config_file.read()

    try:
        version_pair = config_str.split('\n', 1)[0].strip().split(':')

        if version_pair[0] == 'minindn-conf':
            version = version_pair[1]
        else:
            version = '1.0'
    except:
        version = '1.0'

    config = Config(template_file)

    if version == '1.0':
        config.hosts = _parse_hosts_v1_0(template_file)
        config.switches = _parse_switches_v1_0(template_file)
        config.links = _parse_links_v1_0(template_file)
    else:
        json_config = json.loads(config_str.split('\n', 1)[1])
        config.hosts = _parse_hosts(json_config)
        config.switches = _parse_switches(json_config)
        config.links = _parse_links(json_config)

    return config


class AppConfig(object):
    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return 'app: {}'.format(self.name)


class HostConfig(object):
    def __init__(self, params):
        self.apps = []
        self.cpu = None
        self.params = {}

        for key, value in params.iteritems():
            if key == 'apps':
                for app in value:
                    self.apps.append(AppConfig(app))
            else:
                setattr(self, key, value)

    def __repr__(self):
        return 'Name: '    + self.name + \
               ' App: '    + self.app + \
               ' URIS: '   + str(self.uri_tuples) + \
               ' CPU: '    + str(self.cpu) + \
               ' Cores: '  + str(self.cores) + \
               ' Cache: '  + str(self.cache) + \
               ' NLSR Parameters: ' + self.nlsrParameters


class SwitchConfig(object):
    def __init__(self, params):
        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return 'switch: {}'.format(self.name)


class LinkConfig(object):
    def __init__(self, host1, host2, params):
        self.host1 = host1
        self.host2 = host2
        self.link_dict = params

        for key, value in params.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return 'host1: ' + self.host1 + ' host2: ' + self.host2 + ' params: ' + str(self.link_dict)


#######################
# Mini-NDN Config v2.0
#######################
def _parse_hosts(json_config):
    'Parse hosts section from the conf file.'
    hosts = []

    try:
        hosts_section = json_config['hosts']
    except KeyError:
        return []

    for host in hosts_section:
        hosts.append(HostConfig(host))

    return hosts


def _parse_switches(json_config):
    'Parse switches section from the conf file.'
    switches = []

    try:
        switches_section = json_config['switches']
    except KeyError:
        return []

    for switch in switches_section:
        switches.append(SwitchConfig(switch))

    return switches


def _parse_links(json_config):
    'Parse links section from the conf file.'
    links = []

    try:
        links_section = json_config['links']
    except KeyError:
        return []

    for link in links_section:
        link_params = {
            'delay': link['delay'],
            'bw': link['bandwidth'],
            'jitter': link['jitter'],
            'max_queue_size': link['max_queue_size'],
            'loss': link['loss_rate']
        }
        links.append(LinkConfig(link['host1'], link['host2'], link_params))

    return links


#######################
# Mini-NDN Config v1.0
#######################
def _parse_hosts_v1_0(conf_arq):
    'Parse hosts section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    hosts = []

    items = config.items('nodes')

        #makes a first-pass read to hosts section to find empty host sections
    for item in items:
        name = item[0]
        rest = item[1].split()
        if len(rest) == 0:
            config.set('nodes', name, '_')
        #updates 'items' list
    items = config.items('nodes')

        #makes a second-pass read to hosts section to properly add hosts
    for item in items:

        name = item[0]

        rest = shlex.split(item[1])

        uris = rest
        params = {}
        cpu = None
        cores = None
        cache = None

        for uri in uris:
            if re.match("cpu", uri):
                cpu = float(uri.split('=')[1])
            elif re.match("cores", uri):
                cores = uri.split('=')[1]
            elif re.match("cache", uri):
                cache = uri.split('=')[1]
            elif re.match("mem", uri):
                mem = uri.split('=')[1]
            elif re.match("app", uri):
                app = uri.split('=')[1]
            elif re.match("_", uri):
                app = ""
            else:
                params[uri.split('=')[0]] = uri.split('=')[1]

        nfd = {
            'name': 'nfd'
        }

        apps = [nfd]

        host_params = {
            'name': name,
            'app': app,
            'apps': apps,
            'cpu': cpu,
            'cores': cores,
            'cache': cache,
            'params': params,
            'uri_tuples': params,
            'nlsrParameters': params
        }
        hosts.append(HostConfig(host_params))

    return hosts


def _parse_switches_v1_0(conf_arq):
    'Parse switches section from the conf file.'
    config = ConfigParser.RawConfigParser()
    config.read(conf_arq)

    switches = []

    try:
        items = config.items('switches')
    except ConfigParser.NoSectionError:
        return switches

    for item in items:
        switch_params = {
            'name': item[0]
        }
        switches.append(SwitchConfig(switch_params))

    return switches


def _parse_links_v1_0(conf_arq):
    'Parse links section from the conf file.'
    arq = open(conf_arq, 'r')

    links = []

    while True:
        line = arq.readline()
        if line == '[links]\n':
            break

    while True:
        line = arq.readline()
        if line == '':
            break

        args = line.split()

        #checks for non-empty line
        if len(args) == 0:
            continue

        host1, host2 = args.pop(0).split(':')

        link_dict = {}

        for arg in args:
            arg_name, arg_value = arg.split('=')
            key = arg_name
            value = arg_value
            if key in ['bw', 'jitter', 'max_queue_size']:
                value = int(value)
            if key in ['loss']:
                value = float(value)
            link_dict[key] = value

        links.append(LinkConfig(host1, host2, link_dict))


    return links
