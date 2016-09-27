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

import logging
import optparse
import os
import shutil
import signal
import sys
from datetime import datetime
from subprocess import call

from mininet.cli import CLI
import mininet.node
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.util import ipStr, ipParse

import minindn
import minindn.common as minindn_common
import minindn.config as minindn_config
import ndn
import ndn.nlsr as nlsr
from minindn.topology import Topology

from ndn.ndn_host import NdnHost, CpuLimitedNdnHost

def print_experiment_names(option, opt, value, parser):
    print 'Mini-NDN experiments:'
    for experiment in ndn.ExperimentManager.getExperimentNames():
        print "  {}".format(experiment)
    sys.exit()

def print_version(option, opt, value, parser):
    print 'Mini-NDN v{}'.format(minindn_common.VERSION_NUMBER)
    sys.exit()

def create_results_dir(result_dir, faces, is_hr_enabled):
    if faces == 0:
        faces = "all"
    routing_type = "hr" if is_hr_enabled else 'ls'

    result_dir = os.path.join(str(result_dir), routing_type, str(faces))
    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)
        logging.info("Results will be stored at: {}".format(result_dir))
    else:
        logging.critical("Results directory '{}' already exists!".format(result_dir))
        sys.exit(1)
    return result_dir


def parse_args():
    usage = """Usage: minindn [template_file] [ -t | --testbed ]
    If no template_file is given, ndn_utils/default-topology.conf (given sample file)
    will be used.
    If --testbed is used, minindn will run the NDN Project Testbed.
    """
    parser = optparse.OptionParser(usage)
    parser.add_option(
        "--ctime",
        action="store",
        dest="ctime",
        type="int",
        default=60,
        help="Specify convergence time for the topology (Default: 60 seconds)"
    )
    parser.add_option(
        "--experiment",
        action="store",
        dest="experiment_name",
        default=None,
        help="Runs the specified experiment"
    )
    parser.add_option(
        "--faces",
        action="store",
        dest="num_faces",
        type="int",
        default=3,
        help="Specify number of faces 0-60"
    )
    parser.add_option(
        "--hr",
        action="store_true",
        dest="is_hr_enabled",
        default=False,
        help="--hr is used to turn on hyperbolic routing"
    )
    parser.add_option(
        "--list-experiments",
        action="callback",
        callback=print_experiment_names,
        help="Lists the names of all available experiments"
    )
    parser.add_option(
        "--no-cli",
        action="store_false",
        dest="is_cli_enabled",
        default=True,
        help="Run experiments and exit without showing the command line interface"
    )
    parser.add_option(
        "--num_pings",
        action="store",
        dest="num_pings",
        type="int",
        default=300,
        help="Number of pings to perform between each node in the experiment"
    )
    parser.add_option(
        "--nlsr-security",
        action="store_true",
        dest="nlsr_security",
        default=False,
        help="Enables NLSR security"
    )
    parser.add_option(
        "-t",
        "--testbed",
        action="store_true",
        dest="testbed",
        default=False,
        help="instantiates NDN Testbed"
    )
    parser.add_option(
        "--work-dir",
        action="store",
        dest="work_dir",
        default='/tmp',
        help="Specify the working directory; default is /tmp"
    )
    parser.add_option(
        "--result-dir",
        action="store",
        dest="result_dir",
        default=None,
        help="Specify the full path destination folder where experiment results will be moved"
    )
    parser.add_option(
        "--pct-traffic",
        action="store",
        dest="pct_traffic",
        type="float",
        default=1.0,
        help="Specify the percentage of nodes each node should ping"
    )
    parser.add_option(
        '--version',
        '-V',
        action='callback',
        callback=print_version,
        help='Displays version information'
    )

    (options, args) = parser.parse_args()

    if options.experiment_name is not None and options.experiment_name not in ndn.ExperimentManager.getExperimentNames():
        logging.critical("No experiment named {}".format(options.experiment_name))
        sys.exit()

    if options.experiment_name is not None and options.result_dir is None:
        logging.info("No results folder specified; experiment results will remain in the working directory")

    if len(args) == 0:
        options.template_file = ''
    else:
        options.template_file = args[0]

    return options


def get_template_file(options):
    if options.testbed:
        return os.path.join(minindn_common.MINI_NDN_INSTALL_DIR, 'minindn.testbed.conf')
    elif options.template_file == '':
        return os.path.join(minindn_common.MINI_NDN_INSTALL_DIR, 'default-topology.conf')

    return None

def execute(options):
    "Create a network based on template_file"
    template_file = get_template_file(options)
    if template_file is None or os.path.exists(template_file) is False:
        sys.exit('No template file given and default template file cannot be found. Exiting...\n')

    try:
        ndn.nfd.setup()
    except IOError as e:
        sys.exit(e)

    if options.result_dir is not None:
        options.result_dir = create_results_dir(options.result_dir, options.num_faces, options.is_hr_enabled)

    start_time = datetime.now()

    config = minindn_config.parse(template_file)
    topo = Topology(config, options.work_dir)

    if topo.is_tc_link is True and topo.is_limited is True:
        net = Mininet(topo, host=CpuLimitedNdnHost, link=TCLink)
    elif topo.is_tc_link is True and topo.is_limited is False:
        net = Mininet(topo, host=NdnHost, link=TCLink)
    elif topo.is_tc_link is False and topo.is_limited is True:
        net = Mininet(topo, host=CpuLimitedNdnHost)
    else:
        net = Mininet(topo, host=NdnHost)

    net.start()

    # Giving proper IPs to intf so neighbor nodes can communicate
    # This is one way of giving connectivity, another way could be
    # to insert a switch between each pair of neighbors
    ndn_net_base = "1.0.0.0"
    interfaces = []
    for host in net.hosts:
        for intf in host.intfList():
            link = intf.link
            node1, node2 = link.intf1.node, link.intf2.node

            if node1 in net.switches or node2 in net.switches:
                continue

            if link.intf1 not in interfaces and link.intf2 not in interfaces:
                interfaces.append(link.intf1)
                interfaces.append(link.intf2)
                node1.setIP(ipStr(ipParse(ndn_net_base) + 1) + '/30', intf=link.intf1)
                node2.setIP(ipStr(ipParse(ndn_net_base) + 2) + '/30', intf=link.intf2)
                ndn_net_base = ipStr(ipParse(ndn_net_base) + 4)

    # Used later to check prefix name in checkFIB
    nodes = ','.join([str(host.name) for host in net.hosts])

    nlsr_opts = {
        'security': options.nlsr_security,
        'max-faces-per-prefix': options.num_faces,
        'hyperbolic-state': options.is_hr_enabled
    }
    nlsr.setup(net, topo.hosts_conf, options.work_dir, nlsr_opts)

    logging.info('Setup time: {}'.format((start_time - datetime.now()).seconds))

    # Load experiment
    if options.experiment_name is not None:
        experiment_args = {
            "net": net,
            "nodes": nodes,
            "ctime": options.ctime,
            "num_pings": options.num_pings,
            "pct_traffic": options.pct_traffic
        }
        ndn.ExperimentManager.run(options.experiment_name, experiment_args)

    if options.is_cli_enabled:
        CLI(net)

    net.stop()

    if options.result_dir is not None:
        logging.info("Moving results to {}".format(options.result_dir))
        shutil.move(options.work_dir, options.result_dir)

def signal_handler(signal, frame):
    logging.info("Cleaning up...")
    call(['nfd-stop'])
    call(['sudo', 'mn', '--clean'])
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    options = parse_args()

    setLogLevel('info')
    execute(options)


if __name__ == '__main__':
    main()
