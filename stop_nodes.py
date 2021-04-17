#!/usr/bin/env python


from gns3fy import Gns3Connector, Project, Node
import time


gns3_server = Gns3Connector("http://labsrv:3080")

project = Project(name="routing", connector=gns3_server)

project.get()

vqfx = [node.name for node in project.nodes if node.name.startswith("vqfx")]

csr = [node.name for node in project.nodes if node.name.startswith("csr")]

freebsd = [node.name for node in project.nodes if node.name.startswith("core")]

nodes = vqfx + csr + freebsd

for node in project.nodes:
    if node.name in nodes:
        node.stop()
    time.sleep(1)
