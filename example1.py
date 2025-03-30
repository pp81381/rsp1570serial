import asyncio
import logging

from example_runner import process_command_args
from rsp1570serial.connection import create_rotel_amp_conn
from rsp1570serial.process_command import process_command
from rsp1570serial.rotel_model_meta import ROTEL_MODELS


async def main():
    args = process_command_args()
    async with create_rotel_amp_conn(
        args.serial_port, ROTEL_MODELS[args.model]
    ) as conn:
        logging.info("Sending POWER_TOGGLE")
        messages = await process_command(conn, "POWER_TOGGLE")
        logging.info(
            "Finished sending POWER_TOGGLE: %d message(s) collected", len(messages)
        )
        for m in messages:
            m.log()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(message)s",
    )
    asyncio.run(main())
