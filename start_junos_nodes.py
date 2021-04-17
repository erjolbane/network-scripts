#!/usr/bin/env python

from gns3fy import Gns3Connector, Project
from jnpr.junos import Device
from jnpr.junos.exception import ConnectUnknownHostError, RpcError, ConnectTimeoutError
import time
import napalm



def is_up(hostname):
    driver = napalm.get_network_driver("junos")

    device = driver(
        hostname=hostname + ".lab",
        username="root",
        password="Juniper",
    )
    try:
        device.open()
        status = device.is_alive()
        return status
    except ConnectUnknownHostError:
        print(f"Device {hostname} is not reachable")
    except ConnectTimeoutError:
        print(f"Device {hostname} is not reachable")


def reboot_junos(telnet_port):
    with Device(
        host="labsrv.home",
        user="root",
        passwd="Juniper",
        mode="telnet",
        port=str(telnet_port)
    ) as dev:
        dev.rpc.request_reboot()

def main():
    # connect to GNS3 API
    gns3_server = Gns3Connector("http://labsrv:3080")

    # open project
    project = Project(name="routing", connector=gns3_server)
    project.get()

    # generate list of devices to start
    nodes = [node.name for node in project.nodes if node.node_type == "qemu"]
    print(f"Starting the following nodes \n {nodes}")

    # iterate over the device and start them
    for node in project.nodes:
        if node.name in nodes:
            node.start()

    time.sleep(150)

    for node in project.nodes:
        if node.name in nodes:
            if not is_up(node.name):
                while True:
                    try:
                        print(f"Attempting reboot on device {node.name}")
                        reboot_junos(node.console)
                    except RuntimeError:
                        print(f"Something went wrong on {node.name}. Retrying...")
                        pass
                    except RpcError:
                        print(f"Skipping reboot on {node.name}. Already running")
                        break


if __name__ == "__main__":
    main()