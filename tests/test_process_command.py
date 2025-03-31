from unittest import IsolatedAsyncioTestCase

from rsp1570serial.messages import FeedbackMessage
from rsp1570serial.process_command import process_command
from rsp1570serial.rotel_model_meta import RSP1570_META
from tests.emulator_test_helper import EmulatorTestHelper


class AsyncTestProcessCommandFromOff(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.helper = EmulatorTestHelper(RSP1570_META)
        await self.helper.asyncSetUp()

    async def asyncTearDown(self):
        await self.helper.asyncTearDown()

    async def test_process_power_on(self):
        self.assertEqual(self.helper.device._is_on, False)
        async with self.helper.create_conn() as conn:
            messages = await process_command(conn, "POWER_ON")
            self.assertEqual(len(messages), 1)
        self.assertEqual(self.helper.device._is_on, True)


class AsyncTestProcessCommandFromOn(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.helper = EmulatorTestHelper(
            RSP1570_META, is_on=True, aliases={" CD": "CD ALIAS"}
        )

    async def asyncSetUp(self):
        await self.helper.asyncSetUp()

    async def asyncTearDown(self):
        await self.helper.asyncTearDown()

    async def test_process_mute_toggle(self):
        self.assertEqual(self.helper.device._is_muted, False)
        async with self.helper.create_conn() as conn:
            await process_command(conn, "MUTE_TOGGLE")
        self.assertEqual(self.helper.device._is_muted, True)

    async def test_process_source_cd(self):
        self.assertEqual(self.helper.device._source, self.helper.meta.initial_source)
        async with self.helper.create_conn() as conn:
            messages = await process_command(conn, "SOURCE_CD")
        self.assertEqual(self.helper.device._source, " CD")
        self.assertEqual(len(messages), 1)
        assert isinstance(messages[0], FeedbackMessage)
        self.assertEqual(messages[0].lines[0], "CD ALIAS      VOL  50")
