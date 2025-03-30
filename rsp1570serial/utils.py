"""Misc utilities."""

import platform


def get_system_serial_port(system: str) -> str:
    """Work out the most likely serial port given the type of system. YMMV."""
    if system == "Windows":
        return "COM3"
    elif system == "Linux":
        return "/dev/ttyUSB0"
    else:
        raise ValueError("Invalid system - unable to determine serial_port")


def get_platform_serial_port() -> str:
    """Work out the most likely serial port given the platform."""
    return get_system_serial_port(platform.system())


def pretty_print_bytes(b: bytes) -> str:
    s = b.hex().upper()
    return " ".join([s[i : i + 2] for i in range(0, len(s), 2)])
