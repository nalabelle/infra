"""Stub for pve_exporter.collector module."""

from typing import Any


class CollectorsOptions:
    """Options for PVE collectors."""

    def __init__(
        self,
        status: bool = False,
        version: bool = False,
        node: bool = False,
        cluster: bool = False,
        resources: bool = False,
        config: bool = False,
        replication: bool = False,
    ) -> None:
        self.status = status
        self.version = version
        self.node = node
        self.cluster = cluster
        self.resources = resources
        self.config = config
        self.replication = replication


def collect_pve(
    config: dict[str, Any],
    host: str,
    cluster: str,
    node: str,
    options: CollectorsOptions,
) -> bytes:
    """Collect PVE metrics.

    Args:
        config: PVE configuration
        host: PVE host
        cluster: Cluster flag
        node: Node flag
        options: Collector options

    Returns:
        Metrics in Prometheus format
    """
    return b""
