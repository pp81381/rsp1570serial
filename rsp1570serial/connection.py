from rsp1570serial.commands import encode_command, encode_volume_direct_command
from rsp1570serial.messages import decode_message_stream
from serial import PARITY_NONE, STOPBITS_ONE
from serial_asyncio import open_serial_connection

class RotelAmpConn:
    """ Connection to a Rotel Amp. """
    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.reader = None
        self.writer = None
        self.is_open = False

    async def open(self):
        if not self.is_open:
            self.reader, self.writer = await open_serial_connection(
                url=self.serial_port, baudrate=115200, timeout=None,
                parity=PARITY_NONE, stopbits=STOPBITS_ONE)
            self.is_open = True

    def close(self):
        if self.is_open:
            self.writer.close()
            self.is_open = False

    async def send_command(self, command_name):
        self.writer.write(encode_command(command_name))
        await self.writer.drain()

    async def send_volume_direct_command(self, zone, volume):
        self.writer.write(encode_volume_direct_command(zone, volume))
        await self.writer.drain()

    def read_messages(self):
        return decode_message_stream(self.reader)
