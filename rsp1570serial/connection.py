import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from serial import PARITY_NONE, STOPBITS_ONE  # type: ignore[import-untyped]
from serial_asyncio_fast import open_serial_connection  # type: ignore[import-untyped]

from rsp1570serial.messages import AnyMessage, MessageCodec
from rsp1570serial.rotel_model_meta import RotelModelMeta


class RotelAmpConn:
    """Basic connection to a Rotel Amp"""

    def __init__(self, serial_port: str, meta: RotelModelMeta):
        self.serial_port = serial_port
        self.meta = meta
        self.reader = None
        self.writer = None

    @property
    def is_open(self) -> bool:
        return self.writer is not None

    async def open(self):
        if self.writer is not None:
            raise RuntimeError("RotelAmpConn is already open")
        self.reader, self.writer = await open_serial_connection(
            url=self.serial_port,
            baudrate=115200,
            timeout=None,
            parity=PARITY_NONE,
            stopbits=STOPBITS_ONE,
        )

    async def close(self):
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()
            self.reader = None
            self.writer = None

    async def send_command(self, command_name: str):
        if self.writer is not None:
            codec = MessageCodec(self.meta)
            self.writer.write(codec.encode_command(command_name))
            await self.writer.drain()

    async def send_volume_direct_command(self, zone: int, volume: int):
        if self.writer is not None:
            codec = MessageCodec(self.meta)
            self.writer.write(codec.encode_volume_direct_command(zone, volume))
            await self.writer.drain()

    async def read_messages(self) -> AsyncGenerator[AnyMessage, None]:
        assert self.reader is not None
        codec = MessageCodec(self.meta)
        async for message in codec.decode_message_stream(self.reader):
            yield message


@asynccontextmanager
async def create_rotel_amp_conn(serial_port: str, meta: RotelModelMeta):
    conn = RotelAmpConn(serial_port, meta)
    try:
        await conn.open()
        yield conn
    finally:
        await asyncio.sleep(0)
        await conn.close()
