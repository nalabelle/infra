from typing import TypedDict


def format_list(list_: list[str], pattern: str) -> list[str]:
    """Formats each item in a list according to pattern provided

    Args:
        list_ (list[str]): list of strings to insert into format pattern
        pattern (str): format pattern to apply to each string

    Returns:
        list[str]: list of strings formatted per pattern
    """
    return [pattern % s for s in list_]


class Port(TypedDict):
    name: str
    color: str | None
    default: str | None
    tagged: list[str] | None


class VE(TypedDict):
    v4: str


class PortMap(TypedDict):
    ve: dict[str, VE]
    physical: dict[int, Port]


class VLANBase(TypedDict):
    name: str
    short: str
    id: int


class VLANPorts(TypedDict):
    tagged: list[int]
    untagged: list[int]
    router_interface: int | None


class VLAN(VLANBase, VLANPorts):
    pass


def vlan_map(vlan_list: list[VLANBase], portmap: PortMap) -> list[VLAN]:
    vlans: list[VLAN] = []
    for base_vlan in vlan_list:
        tagged: list[int] = []
        untagged: list[int] = []
        short = base_vlan["short"]
        for id, port in portmap["physical"].items():
            if "default" in port and short == port["default"]:
                # For dual-mode, tag the port in the VLAN and we'll add it to the port definition
                if "tagged" in port:
                    tagged.append(id)
                else:
                    untagged.append(id)
            if "tagged" in port and port["tagged"] and short in port["tagged"]:
                tagged.append(id)
        ports: VLANPorts = {
            "tagged": sorted(tagged),
            "untagged": sorted(untagged),
            "router_interface": base_vlan["id"],
        }
        vlans.append({**base_vlan, **ports})
    return sorted(vlans, key=lambda vlan: vlan["id"])


def vlan_from_short(vlan_list: list[VLANBase], port: Port | None) -> VLANBase | None:
    if not port or not (
        "default" in port and "tagged" in port and port["default"] and port["tagged"]
    ):
        return None
    for vlan in vlan_list:
        if vlan["short"] == port["default"]:
            return vlan
    return None


class FilterModule:
    def filters(self):
        return {
            "format_list": format_list,
            "vlan_map": vlan_map,
            "vlan_from_short": vlan_from_short,
        }
