#!/usr/bin/env python3

import napalm
import argparse


def main():
    # script arguments
    p = argparse.ArgumentParser()
    p.add_argument("--config-file", help="Provide configuration file")
    p.add_argument("--host", help="Provide hostname or ip")

    args = p.parse_args()

    # Use the appropriate network driver to connect to the device:
    driver = napalm.get_network_driver("junos")

    # connect to device
    device = driver(
        hostname=args.host,
        username="root",
        password="Juniper",
    )

    # create connection
    device.open()

    print(f"Override existing configuration on {args.host}.")
    device.load_replace_candidate(filename=args.config_file)
    device.commit_config()

    device.close()
    print("Done.")


if __name__ == "__main__":
    main()
