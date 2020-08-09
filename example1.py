import asyncio
from example_runner import run_and_log_task
import logging
from rsp1570serial.connection import create_rotel_amp_conn
from rsp1570serial.utils import get_platform_serial_port


async def run_command_n_times(conn, command_name, interval, n):
    for x in range(n):
        await asyncio.sleep(interval)
        logging.info("Writing {} command number {}".format(command_name, x + 1))
        await conn.send_command(command_name)
    logging.info("All instances of {} sent".format(command_name))


async def main(serial_port=None, heartbeat=True, log_payload=False):
    if serial_port is None:
        serial_port = get_platform_serial_port()
    async with create_rotel_amp_conn(serial_port) as conn:
        main_task = asyncio.create_task(
            run_command_n_times(conn, "MUTE_TOGGLE", 3.0, 4)
        )
        await run_and_log_task(main_task, conn, heartbeat, log_payload)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    # asyncio.run(main("socket://192.168.50.211:50002"))

