#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import threading


def run_iperf(servers, clients):
    threads = []

    for server in servers:
        server.cmd(f'iperf -u -s &')
        server_thread = threading.Thread(target=lambda s=server: s.cmd(f'iperf -u -s &'))
        server_thread.start()
        threads.append(server_thread)

    time.sleep(1)

    for client in clients:
        client_thread = threading.Thread(
            target=lambda c=client: (time.sleep(0.5), c.cmd(f"iperf -u -c {servers[0].IP()} -t {5}")))
        client_thread.start()
        threads.append(client_thread)

    for thread in threads:
        thread.join()

    for server in servers:
        server.sendInt()


def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch, link=TCLink)

    info('*** Adding controller\n')
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', protocol='tcp', port=6653)

    info('*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    info('*** Add hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')  # Server 1
    h2 = net.addHost('h2', ip='10.0.0.2')  # Server 2
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(s1, h3)
    net.addLink(s1, h4)
    net.addLink(s1, h5)

    info('*** Starting network\n')
    net.build()
    c0.start()
    s1.start([c0])

    info('*** Running performance tests\n')
    servers = [h1, h2]
    clients = [h3, h4, h5]
    run_iperf(servers, clients)
    time.sleep(5)

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
