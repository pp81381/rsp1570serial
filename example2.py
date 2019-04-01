import asyncio
import logging
from rsp1570serial.messages import FeedbackMessage, TriggerMessage
from example_runner import example_runner

async def send_command_and_log(conn, command_name):
    await conn.send_command(command_name)
    logging.info(command_name)

async def send_volume_direct_command_and_log(conn, zone, volume):
    await conn.send_volume_direct_command(zone, volume)
    logging.info("Zone %d, Volume: %d", zone, volume)

async def run_example_commands(conn):
    try:
#        await asyncio.sleep(3)
#        await send_command_and_log(conn, 'POWER_ON')
        await asyncio.sleep(3)
        await send_command_and_log(conn, 'ZONE_4_12V_TRIGGER_6_TOGGLE')
        await asyncio.sleep(3)
        await send_volume_direct_command_and_log(conn, 1, 40)
        await asyncio.sleep(3)
        await send_volume_direct_command_and_log(conn, 1, 45)
        await asyncio.sleep(3)
#        await send_command_and_log(conn, 'POWER_OFF')
#        await asyncio.sleep(3)
        logging.info("run_example_commands completed")
    except asyncio.CancelledError:
        logging.info("run_example_commands cancelled")

async def read_sequences(conn):
    try:
        async for message in conn.read_messages():
            if (isinstance(message, (FeedbackMessage, TriggerMessage))):
                message.log()
            else:
                logging.warning("Unknown message type encountered")
    except asyncio.CancelledError:
        logging.info("Message reader cancelled")

def build_example_tasks(conn):
    return (
        read_sequences(conn),
        run_example_commands(conn)
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    example_runner(build_example_tasks)
