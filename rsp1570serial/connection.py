import asyncio
import logging
from contextlib import asynccontextmanager
from weakref import WeakSet

from serial import (  # type: ignore[import-untyped]
    PARITY_NONE,
    STOPBITS_ONE,
    SerialException,
)
from serial_asyncio_fast import open_serial_connection  # type: ignore[import-untyped]

from rsp1570serial import DEVICE_ID_RSP1570
from rsp1570serial.commands import encode_command, encode_volume_direct_command
from rsp1570serial.messages import decode_message_stream

_LOGGER = logging.getLogger(__name__)


class RotelAmpConnConnectionError(Exception):
    pass


class RotelAmpConn:
    """
    Basic connection to a Rotel Amp

    Use SharedRotelAmpConn in preference to using this directly
    """

    def __init__(self, serial_port, device_id=DEVICE_ID_RSP1570):
        self.serial_port = serial_port
        self.device_id = device_id
        self.reader = None
        self.writer = None

    @property
    def is_open(self) -> bool:
        return self.writer is not None

    async def open(self):
        if self.writer is not None:
            raise RuntimeError("RotelAmpConn is already open")
        try:
            self.reader, self.writer = await open_serial_connection(
                url=self.serial_port,
                baudrate=115200,
                timeout=None,
                parity=PARITY_NONE,
                stopbits=STOPBITS_ONE,
            )
        except SerialException as exc:
            raise RotelAmpConnConnectionError(str(exc)) from exc

    def close(self):
        if self.writer is not None:
            self.writer.close()
            self.reader = None
            self.writer = None

    async def send_command(self, command_name):
        if self.writer is not None:
            self.writer.write(encode_command(self.device_id, command_name))
            await self.writer.drain()

    async def send_volume_direct_command(self, zone, volume):
        if self.writer is not None:
            self.writer.write(
                encode_volume_direct_command(self.device_id, zone, volume)
            )
            await self.writer.drain()

    def read_messages(self):
        return decode_message_stream(self.device_id, self.reader)


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
        self.serial_port = serial_port
        self._conn = None
        self._clients = None

    async def open(self):
        self._conn = RotelAmpConn(self.serial_port)
        self._clients = WeakSet()
        await self._conn.open()

    async def close(self):
        if self._clients is not None:
            await self._put_eom_message_to_clients()
            self._clients = None
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        await asyncio.sleep(0)

    def new_client_conn(self):
        if self._conn is None or self._clients is None:
            raise RuntimeError("Connection not open")
        client = SharedRotelAmpClientConn(self)
        self._clients.add(client)
        return client

    async def process_messages(self):
        if self._conn is None or self._clients is None:
            raise RuntimeError("Connection not open")
        _LOGGER.debug("Started processing messages")
        try:
            async for message in self._conn.read_messages():
                _LOGGER.debug("Message received")
                message.log(logging.DEBUG)
                await self._put_message_to_clients(message)
        except asyncio.CancelledError:
            _LOGGER.debug("process_messages cancelled")
        _LOGGER.debug("Finished processing messages")
        await self._put_eom_message_to_clients()
        _LOGGER.debug("End of messages message sent to clients")

    async def _put_message_to_clients(self, message):
        """Iterate clients - isolated to prevent any references hanging around inadvertently"""
        if self._conn is None or self._clients is None:
            raise RuntimeError("Connection not open")
        for client in self._clients:
            await client.put(message)

    async def _put_eom_message_to_clients(self):
        await self._put_message_to_clients(SharedRotelAmpConnEndOfMessages())


class SharedRotelAmpConnEndOfMessages:
    pass


class SharedRotelAmpClientConn:
    POWER_ON_TIME_WINDOW = 5.0
    DEFAULT_TIME_WINDOW = 1.0

    def __init__(self, conn):
        self.queue = asyncio.Queue()
        self.conn = conn

    async def put(self, message):
        _LOGGER.debug("Message put")
        await self.queue.put(message)

    async def read_messages(self):
        """Iterate messages, waiting if necessary"""
        while True:
            message = await self.queue.get()
            if isinstance(message, SharedRotelAmpConnEndOfMessages):
                break
            yield message

    async def send_command(self, command_code):
        await self.conn._conn.send_command(command_code)

    async def send_volume_direct_command(self, zone, volume):
        await self.conn._conn.send_volume_direct_command(zone, volume)

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
        _LOGGER.debug("Collecting messages")
        return self.collect_messages()


class RotelAmpMessageProcessor:
    """Processes messages in a background task"""

    def __init__(self, serial_port):
        self.serial_port = serial_port
        self._conn = None
        self._task = None

    async def open(self):
        self._conn = SharedRotelAmpConn(self.serial_port)
        await self._conn.open()
        self._task = asyncio.create_task(self._conn.process_messages())

    @property
    def conn(self):
        if self._conn is None:
            raise RuntimeError("Processor not opened")
        return self._conn

    async def close(self):
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                _LOGGER.debug("Processor task cancelled")
            self._task = None
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
        await asyncio.sleep(0)


@asynccontextmanager
async def create_shared_rotel_amp_conn(*args, **kwargs):
    processor = RotelAmpMessageProcessor(*args, **kwargs)
    try:
        await processor.open()
        yield processor.conn
    finally:
        await processor.close()


@asynccontextmanager
async def create_message_processor_client(*args, **kwargs):
    async with create_shared_rotel_amp_conn(*args, **kwargs) as processor:
        yield processor.new_client_conn()
