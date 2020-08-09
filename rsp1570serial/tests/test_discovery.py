import asyncio
import aiounittest
from contextlib import asynccontextmanager
from rsp1570serial.discovery import discover_source_aliases
from rsp1570serial.emulator import create_device, make_message_handler

TEST_PORT = 50051


@asynccontextmanager
async def start_emulator(device, port=TEST_PORT):
    handle_messages = make_message_handler(device)
    async with await asyncio.start_server(handle_messages, port=port) as server:
        yield server


class AsyncTestDiscovery(aiounittest.AsyncTestCase):
    async def test_process_command3(self):
        aliases = {
            "VIDEO 1": "CATV",
            "VIDEO 2": "NMT",
            "VIDEO 3": "APPLE TV",
            "VIDEO 4": "FIRE TV",
            "VIDEO 5": "BLU RAY",
        }
        async with create_device(is_on=True, aliases=aliases) as device:
            async with start_emulator(device):
                source_map = await discover_source_aliases(f"socket://:{TEST_PORT}")
                self.assertDictEqual(
                    source_map,
                    {
                        "CATV": "SOURCE_VIDEO_1",
                        "NMT": "SOURCE_VIDEO_2",
                        "APPLE TV": "SOURCE_VIDEO_3",
                        "FIRE TV": "SOURCE_VIDEO_4",
                        "BLU RAY": "SOURCE_VIDEO_5",
                        "TUNER": "SOURCE_TUNER",
                        "TAPE": "SOURCE_TAPE",
                        "MULTI": "SOURCE_MULTI_INPUT",
                        " CD": "SOURCE_CD",
                    },
                )

