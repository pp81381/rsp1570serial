import asyncio
import socket
from unittest import IsolatedAsyncioTestCase

from rsp1570serial.emulator import CommandHandler, RotelRSP1570Emulator
from rsp1570serial.rotel_model_meta import RSP1570_META


async def simulate_server_activity(async_server_writer_func):
    """
    Set up a test harness that lets you call a server side method
    and see what the client will receive
    """
    rsock, wsock = socket.socketpair()
    client_reader, client_writer = await asyncio.open_connection(sock=rsock)
    server_writer = (await asyncio.open_connection(sock=wsock))[1]
    await async_server_writer_func(server_writer)
    server_writer.close()  # So that client_reader will receive an EOF
    await server_writer.wait_closed()

    data = await client_reader.read()
    client_writer.close()
    await client_writer.wait_closed()
    wsock.close()
    return data


class AsyncTestEmulatorCommands(IsolatedAsyncioTestCase):
    async def test_initial_state(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        self.assertEqual(
            e.display_line_1,
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertEqual(
            e.info,
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertCountEqual(e.icon_list, ["Standby LED"])

    async def test_turn_on_and_off(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        await e.turn_on()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  50")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        on_message = e.encode_feedback_message()
        self.assertEqual(
            on_message,
            b"\xfe1\xa3 VIDEO 1       VOL  50DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xc5",
        )
        await e.turn_off()
        self.assertEqual(
            e.display_line_1,
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertEqual(
            e.info,
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertCountEqual(e.icon_list, ["Standby LED"])
        off_message = e.encode_feedback_message()
        self.assertEqual(
            off_message,
            b"\xfe1\xa3 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\xfc",
        )

    async def test_toggle(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        await e.toggle()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  50")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        await e.toggle()
        self.assertEqual(
            e.display_line_1,
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertEqual(
            e.info,
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertCountEqual(e.icon_list, ["Standby LED"])

    async def test_party(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        await e.turn_on()
        await e.set_party_mode(True)
        self.assertEqual(e.display_line_1, "VIDEO 1   pty VOL  50")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )

    async def test_mute(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        await e.turn_on()
        await e.mute_on()
        await asyncio.sleep(0)  # Let the Blinker task start, or mute_off will throw
        self.assertEqual(e.display_line_1, "VIDEO 1       MUTE ON")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        await e.mute_blink()  # Called too quickly for Blinker to interfere with the outcome
        self.assertEqual(e.display_line_1, "VIDEO 1              ")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        await e.mute_blink()
        self.assertEqual(e.display_line_1, "VIDEO 1       MUTE ON")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        await e.mute_off()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  50")
        self.assertEqual(e.info, "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )

    async def test_set_volume(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        await e.turn_on()
        await e.set_volume(68)
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  68")
        await e.volume_up()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  69")
        await e.volume_down()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  68")
        await e.set_volume(0)
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  00")
        await e.volume_down()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  00")
        await e.volume_up()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  01")
        await e.set_volume(100)
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  01")
        await e.set_volume(96)
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  96")
        await e.volume_up()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  96")
        await e.volume_down()
        self.assertEqual(e.display_line_1, "VIDEO 1       VOL  95")

    async def test_set_source(self):
        e = RotelRSP1570Emulator(RSP1570_META)
        await e.turn_on()
        await e.set_source("VIDEO 2")
        self.assertEqual(e.display_line_1, "VIDEO 2       VOL  50")
        self.assertEqual(e.info, "DOLBY PL\x19 M     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        await e.set_source("BAD SOURCE")
        self.assertEqual(e.display_line_1, "VIDEO 2       VOL  50")
        self.assertEqual(e.info, "DOLBY PL\x19 M     48K  ")
        self.assertCountEqual(
            e.icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        await e.set_source(" CD")
        self.assertEqual(e.display_line_1, " CD           VOL  50")
        self.assertEqual(e.info, "STEREO          44.1K")
        self.assertCountEqual(e.icon_list, ["A", "Standby LED", "SW", "FR", "FL"])

    async def test_aliases(self):
        e = RotelRSP1570Emulator(
            RSP1570_META, {"VIDEO 1": "CATV", "VIDEO 2": "APPLE TV"}
        )
        await e.turn_on()
        await e.set_volume(68)
        self.assertEqual(e.display_line_1, "CATV          VOL  68")
        await e.set_source("VIDEO 2")  # Uses the actual source and not the alias!
        self.assertEqual(e.display_line_1, "APPLE TV      VOL  68")

    async def test_power_on(self):
        e = RotelRSP1570Emulator(RSP1570_META)

        async def simulate_commands(writer):
            e.add_observer(writer)
            c = CommandHandler(e)
            await c.apply_simple_command_code("POWER_ON")

        response = await simulate_server_activity(simulate_commands)
        expected = b"\xfe1\xa3 VIDEO 1       VOL  50DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xc5"
        self.assertEqual(response, expected)

    async def test_power_on_volume_up(self):
        e = RotelRSP1570Emulator(RSP1570_META)

        async def simulate_commands(writer):
            e.add_observer(writer)
            c = CommandHandler(e)
            await c.apply_simple_command_code("POWER_ON")
            await c.apply_simple_command_code("VOLUME_UP")

        response = await simulate_server_activity(simulate_commands)
        expected = (
            b"\xfe1\xa3 VIDEO 1       VOL  50DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xc5"
            b"\xfe1\xa3 VIDEO 1       VOL  51DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xc6"
        )
        self.assertEqual(response, expected)

    async def test_reconnect(self):
        e = RotelRSP1570Emulator(RSP1570_META, is_on=True)

        async def simulate_commands(writer):
            e.add_observer(writer)
            c = CommandHandler(e)
            await c.apply_simple_command_code("DISPLAY_REFRESH")

        response1 = await simulate_server_activity(simulate_commands)
        response2 = await simulate_server_activity(simulate_commands)
        expected = b"\xfe1\xa3 VIDEO 1       VOL  50DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xc5"
        self.assertEqual(response1, expected)
        self.assertEqual(
            response2, expected
        )  # E.g. state hasn't changed after reconnect
