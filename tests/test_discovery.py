import asyncio
from unittest import IsolatedAsyncioTestCase

from rsp1570serial.discovery import discover_source_aliases
from rsp1570serial.rotel_model_meta import RSP1570_META
from tests.emulator_test_helper import EmulatorTestHelper


class AsyncTestDiscovery(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.helper = EmulatorTestHelper(
            RSP1570_META,
            is_on=True,
            aliases={
                "VIDEO 1": "CATV",
                "VIDEO 2": "NMT",
                "VIDEO 3": "APPLE TV",
                "VIDEO 4": "FIRE TV",
                "VIDEO 5": "BLU RAY",
            },
        )
        await self.helper.asyncSetUp()

    async def asyncTearDown(self):
        await self.helper.asyncTearDown()

    async def test_discover_source_aliases(self):
        async with self.helper.create_conn() as conn:
            source_map = await discover_source_aliases(conn)
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
