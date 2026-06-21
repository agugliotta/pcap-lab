import socket


def list_interfaces():
    try:
        return [name for _, name in socket.if_nameindex()]
    except OSError:
        return []


def interface_exists(interface: str) -> bool:
    return interface in list_interfaces()


def default_interface() -> str:
    interfaces = list_interfaces()
    if "lo0" in interfaces:
        return "lo0"
    if "lo" in interfaces:
        return "lo"
    return interfaces[0] if interfaces else "lo"
