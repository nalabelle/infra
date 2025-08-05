#!/usr/bin/env python3
import argparse

from lib.nextdns import Tracker
from lib.nextdns_config import NextDNSConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Update NextDNS rewrites")
    parser.add_argument("file", help="File containing rewrites", nargs="?", default=None)
    args = parser.parse_args()

    config = NextDNSConfig()
    tracker = Tracker(config)

    if args.file is None:
        rewrites = config.dns_rewrites
        tracker.update_rewrites(tracker.read_rewrites_from_file(None, content=rewrites))
    else:
        tracker.update_rewrites(tracker.read_rewrites_from_file(args.file))


if __name__ == "__main__":
    main()
