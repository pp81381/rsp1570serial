import asyncio
from itertools import count
from typing import AsyncContextManager, Dict, Optional

from rsp1570serial.connection import RotelAmpConn, create_rotel_amp_conn
from rsp1570serial.emulator import (
    RotelRSP1570Emulator,
    create_device,
    make_message_handler,
)
from rsp1570serial.rotel_model_meta import RotelModelMeta


class EmulatorTestHelper:
    PORT_ITER = count(50050)

    def __init__(
        self,
        meta: RotelModelMeta,
        is_on: bool = False,
        aliases: Optional[Dict[str, str]] = None,
    ) -> None:
        self.meta = meta
        self.is_on = is_on
        self.aliases = aliases
        self.port = next(self.PORT_ITER)

    async def asyncSetUp(self):
        self._device_context = create_device(self.meta, self.aliases, self.is_on)
        self._device = await self._device_context.__aenter__()
        handle_messages = make_message_handler(self._device)
        self._server = await asyncio.start_server(handle_messages, port=self.port)

    async def asyncTearDown(self):
        assert self._server is not None
        assert self._device_context is not None
        self._server.close()
        await self._server.wait_closed()
        await self._device_context.__aexit__(None, None, None)
        self._server = None
        self._device = None
        self._device_context = None

    def create_conn(self) -> AsyncContextManager[RotelAmpConn]:
        url = f"socket://:{self.port}"
        return create_rotel_amp_conn(url, self.meta)

    @property
    def device(self) -> RotelRSP1570Emulator:
        assert self._device is not None
        return self._device
