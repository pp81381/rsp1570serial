import asyncio
import logging

from example_runner import process_command_args
from rsp1570serial.connection import create_rotel_amp_conn
from rsp1570serial.discovery import discover_source_aliases
from rsp1570serial.rotel_model_meta import ROTEL_MODELS, RotelModelMeta


async def do_it(serial_port: str, meta: RotelModelMeta):
    async with create_rotel_amp_conn(serial_port, meta) as conn:
        source_map = await discover_source_aliases(conn)
    print(source_map)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(message)s",
    )
    args = process_command_args()
    asyncio.run(do_it(args.serial_port, ROTEL_MODELS[args.model]))
