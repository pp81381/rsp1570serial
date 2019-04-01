import asyncio
import logging
from rsp1570serial.messages import FeedbackMessage, TriggerMessage
from example_runner import example_runner

async def run_command_n_times(conn, command_name, interval, n):
    try:
        for x in range(n):
            await asyncio.sleep(interval)
            logging.info("Writing {} command number {}".format(command_name, x + 1))
            await conn.send_command(command_name)
        logging.info("All instances of {} sent".format(command_name))
    except asyncio.CancelledError:
        logging.info("Sending of {} cancelled".format(command_name))

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
        run_command_n_times(conn, 'MUTE_TOGGLE', 3.0, 4)
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    example_runner(build_example_tasks)