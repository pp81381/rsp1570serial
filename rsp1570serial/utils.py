""" Misc utilities. """

import platform

def get_system_serial_port(system):
    """ Work out the most likely serial port given the type of system. YMMV. """
    if system == 'Windows':
        return 'COM3'
    elif system == 'Linux':
        return '/dev/ttyUSB0'
    else:
        raise ValueError("Invalid system - unable to determine serial_port")

def get_platform_serial_port():
    """ Work out the most likely serial port given the platform. """
    return get_system_serial_port(platform.system())