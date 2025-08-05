#!/usr/bin/env python3

import os

from pve_exporter.collector import CollectorsOptions, collect_pve
from pve_exporter.config import config_from_env


def main() -> None:
    host = os.getenv("PVE_HOST", "localhost")
    collectors = CollectorsOptions(
        status=True, version=True, node=True, cluster=True, resources=True, config=True, replication=True
    )
    conf = config_from_env(os.environ)["default"]
    print(collect_pve(config=conf, host=host, cluster="1", node="1", options=collectors).decode(), end="")


if __name__ == "__main__":
    main()
