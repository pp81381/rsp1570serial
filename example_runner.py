import asyncio
import base64
import logging
from rsp1570serial.messages import FeedbackMessage, TriggerMessage
from rsp1570serial.protocol import decode_protocol_stream


async def run_and_log_task(main_task, conn, heartbeat=True, log_payload=False):
    tasks = {main_task}
    if log_payload:
        tasks.add(asyncio.create_task(payload_logger(conn)))
    else:
        tasks.add(asyncio.create_task(message_logger(conn)))
    if heartbeat:
        tasks.add(asyncio.create_task(heartbeat_loop()))
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for pending_task in pending:
        pending_task.cancel()
    for done_task in done:
        try:
            await done_task
        except:
            logging.error("Unexpected exception thrown by subtask", exc_info=True)


async def heartbeat_loop():
    """
    Tells you that the loop is still running
    Also keeps the KeyboardInterrupt running on Windows until Python 3.8 comes along (https://bugs.python.org/issue23057)
    """
    try:
        count = 0
        while True:
            await asyncio.sleep(0.5)
            count += 1
            logging.info("Heartbeat number {}".format(count))
    except asyncio.CancelledError:
        logging.info("Heartbeat cancelled")


async def send_command_and_log(conn, command_name):
    await conn.send_command(command_name)
    logging.info(command_name)


async def send_volume_direct_command_and_log(conn, zone, volume):
    await conn.send_volume_direct_command(zone, volume)
    logging.info("send_volume_direct(zone=%d, volume=%d)", zone, volume)


async def payload_logger(conn):
    try:
        async for payload in decode_protocol_stream(conn.reader):
            logging.info("response payload: %r", payload)
            logging.info("response payload base64: %s", base64.b64encode(payload))
    except asyncio.CancelledError:
        logging.info("Message reader cancelled")


async def message_logger(conn):
    try:
        async for message in conn.read_messages():
            if isinstance(message, (FeedbackMessage, TriggerMessage)):
                message.log()
            else:
                logging.warning("Unknown message type encountered")
    except asyncio.CancelledError:
        logging.info("Message reader cancelled")
