import asyncio
from example_runner import (
    run_and_log_task,
    send_command_and_log,
    send_volume_direct_command_and_log,
)
import logging
from rsp1570serial.connection import create_shared_rotel_amp_conn
from rsp1570serial.utils import get_platform_serial_port


async def run_example_commands(conn):
    try:
        #        await asyncio.sleep(3)
        #        await send_command_and_log(conn, 'POWER_ON')
        await asyncio.sleep(3)
        await send_command_and_log(conn, "DISPLAY_REFRESH")
        await asyncio.sleep(0.5)
        await send_command_and_log(conn, "RECORD_FUNCTION_SELECT")
        await asyncio.sleep(0.5)
        await send_command_and_log(conn, "TONE_CONTROL_SELECT")
        await asyncio.sleep(0.5)
        await send_command_and_log(conn, "TREBLE_UP")
        await asyncio.sleep(0.5)
        await send_command_and_log(conn, "RECORD_FUNCTION_SELECT")
        await asyncio.sleep(0.5)
        await send_command_and_log(conn, "TONE_CONTROL_SELECT")
        await asyncio.sleep(0.5)
        await send_command_and_log(conn, "TREBLE_DOWN")
        await asyncio.sleep(3)
        #        await send_command_and_log(conn, 'POWER_OFF')
        #        await asyncio.sleep(3)
        logging.info("run_example_commands completed")
    except asyncio.CancelledError:
        logging.info("run_example_commands cancelled")


async def run_example_mute_commands(conn):
    try:
        await asyncio.sleep(3)
        await send_command_and_log(conn, "POWER_ON")
        await asyncio.sleep(3)
        await send_command_and_log(conn, "DISPLAY_REFRESH")
        await asyncio.sleep(3)
        await send_command_and_log(conn, "MUTE_TOGGLE")
        await asyncio.sleep(3)
        await send_volume_direct_command_and_log(conn, 1, 60)  # Will unmute
        await asyncio.sleep(3)
        await send_command_and_log(conn, "MUTE_TOGGLE")
        await asyncio.sleep(3)
        await send_command_and_log(conn, "POWER_ON")  # Will unmute
        await asyncio.sleep(3)
        await send_command_and_log(conn, "POWER_ON")  # Will do nothing
        await asyncio.sleep(3)
        await send_command_and_log(conn, "POWER_OFF")
        await asyncio.sleep(3)
        logging.info("run_example_commands completed")
    except asyncio.CancelledError:
        logging.info("run_example_commands cancelled")


async def main(serial_port=None, heartbeat=True, log_payload=False):
    if serial_port is None:
        serial_port = get_platform_serial_port()
    async with create_shared_rotel_amp_conn(serial_port) as shared_conn:
        conn = shared_conn.new_client_conn()
        main_task = asyncio.create_task(run_example_mute_commands(conn))
        await run_and_log_task(main_task, conn, heartbeat, log_payload)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # asyncio.run(main(heartbeat=False))
    # asyncio.run(main("socket://192.168.50.211:50002", heartbeat=False))
    asyncio.run(main("socket://:50001", heartbeat=False))
