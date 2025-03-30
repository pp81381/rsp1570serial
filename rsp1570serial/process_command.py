import asyncio
import logging
from typing import List

from .connection import RotelAmpConn
from .messages import AnyMessage

_LOGGER = logging.getLogger(__name__)

POWER_ON_TIME_WINDOW = 5.0
DEFAULT_TIME_WINDOW = 1.0


async def process_command(conn: RotelAmpConn, command_code: str) -> List[AnyMessage]:
    """Send a command and collect the response messages that arrive within a short time window"""
    time_window = (
        POWER_ON_TIME_WINDOW if "POWER" in command_code else DEFAULT_TIME_WINDOW
    )
    return await process_command_ll(conn, command_code, time_window)


async def process_command_ll(
    conn: RotelAmpConn,
    command_code,
    time_window=DEFAULT_TIME_WINDOW,
) -> List[AnyMessage]:
    """
    Send a command and collect the response messages that arrive in time_window

    Note that POWER_ON and similar commands need a longer time window than other commands
    Recommended time_windows are provided as class constants
    """
    messages: List[AnyMessage] = []

    async def collect_messages(conn: RotelAmpConn):
        _LOGGER.debug("Started collecting messages")
        try:
            async for message in conn.read_messages():
                _LOGGER.debug("Message received")
                message.log(logging.DEBUG)
                messages.append(message)
        except asyncio.CancelledError:
            _LOGGER.debug("collect_messages cancelled")
        _LOGGER.debug("Finished collecting messages")

    collector = asyncio.create_task(collect_messages(conn))

    await conn.send_command(command_code)
    _LOGGER.debug("Sent command %s", command_code)

    await asyncio.sleep(time_window)

    collector.cancel()
    await collector

    return messages
