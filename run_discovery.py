import asyncio
import logging
from rsp1570serial.discovery import discover_source_aliases

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s"
    )
    # asyncio.run(discover_source_aliases("socket://192.168.50.211:50002"))
    asyncio.run(discover_source_aliases())
