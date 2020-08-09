import asyncio
from contextlib import asynccontextmanager
import logging
from rsp1570serial.commands import encode_command, encode_volume_direct_command
from rsp1570serial.messages import decode_message_stream
from serial import PARITY_NONE, STOPBITS_ONE
from serial_asyncio import open_serial_connection
import uuid
import weakref

_LOGGER = logging.getLogger(__name__)


class RotelAmpConn:
    """
    Basic connection to a Rotel Amp
    
    Use SharedRotelAmpConn in preference to using this directly
    """

    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.reader = None
        self.writer = None
        self.is_open = False

    async def open(self):
        if not self.is_open:
            self.reader, self.writer = await open_serial_connection(
                url=self.serial_port,
                baudrate=115200,
                timeout=None,
                parity=PARITY_NONE,
                stopbits=STOPBITS_ONE,
            )
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


@asynccontextmanager
async def create_rotel_amp_conn(*args, **kwargs):
    conn = RotelAmpConn(*args, **kwargs)
    try:
        await conn.open()
        yield conn
    finally:
        conn.close()


class SharedRotelAmpConn:
    """Connection to a Rotel Amp that supports multiple clients"""

    def __init__(self, serial_port):
        self.conn = RotelAmpConn(serial_port)
        self.task = None
        self.clients = weakref.WeakValueDictionary()

    async def open(self):
        await self.conn.open()
        self.task = asyncio.create_task(self._consume_messages())

    async def close(self):
        self.conn.close()
        await self.task
        self.task = None

    def new_client_conn(self):
        conn = SharedRotelAmpClientConn(self)
        self.clients[conn.uuid] = conn
        return conn

    async def _consume_messages(self):
        """Background task to consume messages and push them to the client connections"""
        _LOGGER.debug("Started consuming messages")
        async for message in self.conn.read_messages():
            _LOGGER.debug("Message received")
            message.log(logging.DEBUG)
            await self._put_message_to_clients(message)
        _LOGGER.debug("Finished consuming messages")
        await self._put_message_to_clients(SharedRotelAmpConnSentinel())
        _LOGGER.debug("Finished stopping clients")

    async def _put_message_to_clients(self, message):
        """Iterate clients - isolated to prevent any references hanging around inadvertently"""
        for client in self.clients.values():
            await client.put(message)


@asynccontextmanager
async def create_shared_rotel_amp_conn(*args, **kwargs):
    shared_conn = SharedRotelAmpConn(*args, **kwargs)
    try:
        await shared_conn.open()
        yield shared_conn
    finally:
        await shared_conn.close()


class SharedRotelAmpConnSentinel:
    pass


class SharedRotelAmpClientConn:
    POWER_ON_TIME_WINDOW = 5.0
    DEFAULT_TIME_WINDOW = 1.0

    def __init__(self, conn):
        self.uuid = uuid.uuid4()
        self.queue = asyncio.Queue()
        self.conn = conn

    async def put(self, message):
        await self.queue.put(message)

    async def read_messages(self):
        """Iterate messages, waiting if necessary"""
        while True:
            message = await self.queue.get()
            if isinstance(message, SharedRotelAmpConnSentinel):
                break
            yield message

    async def send_command(self, command_code):
        await self.conn.conn.send_command(command_code)

    async def send_volume_direct_command(self, zone, volume):
        await self.conn.conn.send_volume_direct_command(zone, volume)

    def collect_messages(self):
        """Collect all messages currently on the queue"""
        messages = list()
        while True:
            try:
                message = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            messages.append(message)
        _LOGGER.debug("%d messages collected", len(messages))
        return messages

    async def process_command(self, command_code, time_window=DEFAULT_TIME_WINDOW):
        """
        Send a command and collect the response messages that arrive in time_window
        
        Recommended time_windows are provided as class constants
        Note that POWER_ON needs a longer time window than other commands
        """
        if not self.queue.empty():
            _LOGGER.warning("Queue wasn't empty before process_command")
        await self.send_command(command_code)
        _LOGGER.debug("Sent %s", command_code)
        await asyncio.sleep(time_window)
        return self.collect_messages()
