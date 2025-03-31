import asyncio
from unittest import IsolatedAsyncioTestCase

from rsp1570serial.rotel_model_meta import RSP1570_META
from tests.emulator_test_helper import EmulatorTestHelper


class AsyncTestConnection(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.helper = EmulatorTestHelper(RSP1570_META, is_on=True)
        await self.helper.asyncSetUp()

    async def asyncTearDown(self):
        await self.helper.asyncTearDown()

    async def test_send_command1(self):
        assert self.helper.device is not None
        self.assertEqual(self.helper.device._is_muted, False)
        async with self.helper.create_conn() as conn:
            await conn.send_command("MUTE_TOGGLE")
        self.assertEqual(self.helper.device._is_muted, True)

    async def test_send_command2(self):
        self.assertEqual(self.helper.device._source, self.helper.meta.initial_source)
        async with self.helper.create_conn() as conn:
            await conn.send_command("SOURCE_TUNER")
        self.assertEqual(self.helper.device._source, "TUNER")

    async def test_send_volume_direct_command1(self):
        self.assertEqual(self.helper.device._volume, self.helper.meta.initial_volume)
        async with self.helper.create_conn() as conn:
            await conn.send_volume_direct_command(1, 55)
        self.assertEqual(self.helper.device._volume, 55)
