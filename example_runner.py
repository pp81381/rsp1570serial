import argparse
import asyncio
import base64
import logging
from typing import Awaitable, Callable, List

from rsp1570serial.connection import RotelAmpConn
from rsp1570serial.emulator import EMULATOR_DEFAULT_PORT
from rsp1570serial.messages import FeedbackMessage, SmartDisplayMessage, TriggerMessage
from rsp1570serial.protocol import decode_protocol_stream
from rsp1570serial.rotel_model_meta import ROTEL_MODELS

COMMAND_DEFAULT_SERIAL_PORT = f"socket://:{EMULATOR_DEFAULT_PORT}"


def process_command_args():
    """Args handler for commands"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model",
        choices=list(ROTEL_MODELS.keys()),
        required=True,
        help="model of device to emulate",
    )
    parser.add_argument(
        "-s",
        "--serial-port",
        type=str,
        default=COMMAND_DEFAULT_SERIAL_PORT,
        help="serial port to send to",
    )
    return parser.parse_args()


def process_example_args(example_names: List[str]):
    """Args handler for examples"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model",
        choices=list(ROTEL_MODELS.keys()),
        default="rsp1570",
        help="model of device to emulate",
    )
    parser.add_argument(
        "-s",
        "--serial-port",
        type=str,
        default=COMMAND_DEFAULT_SERIAL_PORT,
        help="serial port to send to",
    )
    parser.add_argument(
        "-x",
        "--example",
        choices=list(example_names),
        required=True,
        help="name of example to run",
    )
    parser.add_argument(
        "-l",
        "--log-payload",
        action="store_true",
        help="log the payload in each message instead of the decoded message",  # Doesn't work with shared conn
    )
    return parser.parse_args()


async def run_and_log_task(main_task, conn, log_payload=False):
    tasks = {main_task}
    if log_payload:
        tasks.add(asyncio.create_task(payload_logger(conn)))
    else:
        tasks.add(asyncio.create_task(message_logger(conn)))
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for pending_task in pending:
        pending_task.cancel()
    for done_task in done:
        try:
            await done_task
        except:
            logging.error("Unexpected exception thrown by subtask", exc_info=True)


async def send_command_and_log(conn, command_name):
    await conn.send_command(command_name)
    logging.info("send_command(%s)", command_name)


async def send_volume_direct_command_and_log(conn, zone, volume):
    await conn.send_volume_direct_command(zone, volume)
    logging.info("send_volume_direct(zone=%d, volume=%d)", zone, volume)


async def payload_logger(conn):
    try:
        async for payload in decode_protocol_stream(conn.reader):
            logging.info("response payload: %r", payload)
            logging.info("response payload base64: %s", base64.b64encode(payload))
    except asyncio.CancelledError:
        logging.info("Payload Logger cancelled")


async def message_logger(conn):
    try:
        async for message in conn.read_messages():
            if isinstance(
                message,
                (
                    FeedbackMessage,
                    TriggerMessage,
                    SmartDisplayMessage,
                ),
            ):
                message.log()
            else:
                logging.warning("Unknown message type encountered")
    except asyncio.CancelledError:
        logging.info("Message reader cancelled")


async def run_command_n_times(conn, command_name, interval, n):
    for x in range(n):
        await asyncio.sleep(interval)
        logging.info("Writing {} command number {}".format(command_name, x + 1))
        await conn.send_command(command_name)
    logging.info("All instances of {} sent".format(command_name))


async def example_wrapper(
    name: str,
    runner: Callable[[RotelAmpConn], Awaitable[None]],
    conn: RotelAmpConn,
) -> None:
    try:
        logging.info("%s started", name)
        await runner(conn)
        logging.info("%s completed", name)
    except asyncio.CancelledError:
        logging.info("%s cancelled", name)
