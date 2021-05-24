#!/usr/bin/env python3

from gns3fy import Gns3Connector, Project, Node
from requests.exceptions import HTTPError
import yaml
import argparse


def main():
    # script arguments
    p = argparse.ArgumentParser()
    p.add_argument("--config", help="Configuration file")
    p.add_argument("--server", help="Provide GNS3 server API")
    p.add_argument("--create-nodes", action="store_true", help="Create node(s)")
    p.add_argument("--create-links", action="store_true", help="Create link(s)")

    args = p.parse_args()

    # open gns3 api
    server = Gns3Connector(args.server)

    # load nodes from yaml
    with open(args.config, "r") as stream:
        config = yaml.safe_load(stream)

    # create project
    project = Project(name=config["project"], connector=server)

    # check if project already exists, otherwise create it
    try:
        project.get()
        print(f"Project {project.name} already created.")
    except HTTPError:
        project.create()
        print(f"Created new project {project.name}.")

    if args.create_nodes:
        # extract existing nodes in the project
        project_nodes = [existing_node.name for existing_node in project.nodes]

        if project_nodes is not None:
                # iterate over nodes list and create them
                for node in config["nodes"]:
                    if node["name"] not in project_nodes:
                        project.create_node(name=node["name"], template=node["template"])
                    elif node["state"].lower() == "absent":
                        _node = project.get_node(node["name"])
                        _node.delete()
                        print(f"Deleted node \'{node['name']}\' ")
                    else:
                        print(f"Node \'{node['name']}\' already created.")
        else:
            for node in config["nodes"]:
                project.create_node(name=node["name"], template=node["template"])
                # arrange nodes in a circular fashion
                project.arrange_nodes_circular(radius=350)

        # output dhcp config for lab hosts
        for node in project.nodes:
            if "em0" in node.ports[0]["name"]:
                print(f'dhcp-host={node.ports[0]["mac_address"]},{node.name}')

    elif args.create_links:
    # iterate over the links and create them
        for link in config["links"]:
            try:
                project.create_link(
                    link["a_node"], link["a_port"], link["b_node"], link["b_port"]
                )
            except ValueError as error:
                print(error)

    if config["start_all_nodes"]:
        project.start_nodes()
        print("Nodes started.")


if __name__ == "__main__":
    main()
