import logging
from unittest import IsolatedAsyncioTestCase, TestCase

from rsp1570serial.message_types import (
    MSGTYPE_PRIMARY_COMMANDS,
    MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_1,
    MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_2,
    MSGTYPE_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_3_COMMANDS,
)
from rsp1570serial.messages import (
    FeedbackMessage,
    MessageCodec,
    SmartDisplayMessage,
    decode_smart_display_line,
    smart_display_string_1_handler,
    smart_display_string_2_handler,
)
from rsp1570serial.protocol import AnyAsyncReader, StreamProxy
from rsp1570serial.rotel_model_meta import RSP1570_META


async def decode_all_messages(codec: MessageCodec, ser: AnyAsyncReader):
    messages = []
    async for command in codec.decode_message_stream(ser):
        messages.append(command)
    return messages


async def decode_single_message(codec: MessageCodec, ser: AnyAsyncReader):
    messages = await decode_all_messages(codec, ser)
    assert len(messages) == 1
    return messages[0]


class RotelTestReverseLookupCommand(TestCase):
    def setUp(self) -> None:
        self.meta = RSP1570_META

    def test1(self):
        index = self.meta.index_command_messages()
        cmd = index[bytes([MSGTYPE_PRIMARY_COMMANDS, 0x71])]
        self.assertEqual(cmd, "POWER_OFF_ALL_ZONES")

    def test2(self):
        index = self.meta.index_command_messages()
        cmd = index[bytes([MSGTYPE_ZONE_3_COMMANDS, 0x71])]
        self.assertEqual(cmd, "ZONE_3_POWER_OFF_ALL_ZONES")


class AsyncRotelTestMessages(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.codec = MessageCodec(RSP1570_META)

    async def test_encode_decode(self):
        message = self.codec.encode_command("POWER_TOGGLE")
        with self.assertLogs(level=logging.INFO) as cm:
            logging.info("Dummy message")  # Hack: assertNoLogs not in Python 3.9
            command = await decode_single_message(self.codec, StreamProxy(message))
        self.assertEqual(cm.output, ["INFO:root:Dummy message"])
        self.assertEqual(command.message_type, MSGTYPE_PRIMARY_COMMANDS)
        self.assertEqual(command.key, b"\x0a")

    async def test_encode_decode_with_meta(self):
        message = self.codec.encode_command("VOLUME_40")
        with self.assertLogs(level=logging.INFO) as cm:
            logging.info("Dummy message")  # Hack: assertNoLogs not in Python 3.9
            command = await decode_single_message(self.codec, StreamProxy(message))
        self.assertEqual(cm.output, ["INFO:root:Dummy message"])
        self.assertEqual(command.message_type, MSGTYPE_VOLUME_DIRECT_COMMANDS)
        self.assertEqual(command.key, b"\x28")

    async def test_decode_feedback_message(self):
        with self.assertLogs(level=logging.INFO) as cm:
            logging.info("Dummy message")  # Hack: assertNoLogs not in Python 3.9
            display = await decode_single_message(
                self.codec,
                StreamProxy(
                    b"\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2"
                ),
            )
        self.assertEqual(cm.output, ["INFO:root:Dummy message"])
        self.assertEqual(display.lines[0], "FIRE TV       VOL  64")
        self.assertEqual(display.lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            display.icons_that_are_on(),
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
        fields = display.parse_display_lines()
        self.assertEqual(fields["is_on"], True)
        self.assertEqual(fields["source_name"], "FIRE TV")
        self.assertEqual(fields["volume"], 64)
        self.assertEqual(fields["mute_on"], False)
        self.assertEqual(fields["party_mode_on"], False)
        self.assertEqual(fields["info"], "DOLBY PLII C     48K")
        self.assertEqual(fields["rec_source"], None)
        self.assertEqual(fields["zone2_source"], None)
        self.assertEqual(fields["zone2_volume"], None)
        self.assertEqual(fields["zone3_source"], None)
        self.assertEqual(fields["zone3_volume"], None)
        self.assertEqual(fields["zone4_source"], None)
        self.assertEqual(fields["zone4_volume"], None)

    async def test_decode_feedback_after_power_off(self):
        with self.assertLogs(level=logging.INFO) as cm:
            logging.info("Dummy message")  # Hack: assertNoLogs not in Python 3.9
            display = await decode_single_message(
                self.codec,
                StreamProxy(
                    b"\xfe1\xa3 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\xfc"
                ),
            )
        self.assertEqual(cm.output, ["INFO:root:Dummy message"])
        self.assertEqual(
            display.lines[0],
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertEqual(
            display.lines[1],
            "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )
        self.assertCountEqual(display.icons_that_are_on(), ["Standby LED"])
        fields = display.parse_display_lines()
        self.assertEqual(fields["is_on"], False)
        self.assertEqual(fields["source_name"], None)
        self.assertEqual(fields["volume"], None)
        self.assertEqual(fields["mute_on"], None)
        self.assertEqual(fields["party_mode_on"], None)
        self.assertEqual(fields["info"], None)
        self.assertEqual(fields["rec_source"], None)
        self.assertEqual(fields["zone2_source"], None)
        self.assertEqual(fields["zone2_volume"], None)
        self.assertEqual(fields["zone3_source"], None)
        self.assertEqual(fields["zone3_volume"], None)
        self.assertEqual(fields["zone4_source"], None)
        self.assertEqual(fields["zone4_volume"], None)

    async def test_decode_feedback_message_with_rec_source(self):
        display = FeedbackMessage(
            "FIRE TV       VOL  64", "  REC    SOURCE      ", b"\x00F\x08\x00\xfc"
        )
        self.assertCountEqual(
            display.icons_that_are_on(),
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
        fields = display.parse_display_lines()
        self.assertEqual(fields["is_on"], True)
        self.assertEqual(fields["source_name"], "FIRE TV")
        self.assertEqual(fields["volume"], 64)
        self.assertEqual(fields["mute_on"], False)
        self.assertEqual(fields["party_mode_on"], False)
        self.assertEqual(fields["info"], "REC    SOURCE")
        self.assertEqual(fields["rec_source"], "SOURCE")
        self.assertEqual(fields["zone2_source"], None)
        self.assertEqual(fields["zone2_volume"], None)
        self.assertEqual(fields["zone3_source"], None)
        self.assertEqual(fields["zone3_volume"], None)
        self.assertEqual(fields["zone4_source"], None)
        self.assertEqual(fields["zone4_volume"], None)

    async def test_decode_feedback_message_with_zone_source(self):
        display = FeedbackMessage(
            "FIRE TV       VOL  64", "  ZONE4  TUNER       ", b"\x00F\x08\x00\xfc"
        )
        self.assertCountEqual(
            display.icons_that_are_on(),
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
        fields = display.parse_display_lines()
        self.assertEqual(fields["is_on"], True)
        self.assertEqual(fields["source_name"], "FIRE TV")
        self.assertEqual(fields["volume"], 64)
        self.assertEqual(fields["mute_on"], False)
        self.assertEqual(fields["party_mode_on"], False)
        self.assertEqual(fields["info"], "ZONE4  TUNER")
        self.assertEqual(fields["rec_source"], None)
        self.assertEqual(fields["zone2_source"], None)
        self.assertEqual(fields["zone2_volume"], None)
        self.assertEqual(fields["zone3_source"], None)
        self.assertEqual(fields["zone3_volume"], None)
        self.assertEqual(fields["zone4_source"], "TUNER")
        self.assertEqual(fields["zone4_volume"], None)

    async def test_decode_feedback_message_with_zone_volume_and_party_mode(self):
        display = FeedbackMessage(
            "FIRE TV   pty VOL  64", "  ZONE3 VOL   55     ", b"\x00F\x08\x00\xfc"
        )
        self.assertCountEqual(
            display.icons_that_are_on(),
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
        fields = display.parse_display_lines()
        self.assertEqual(fields["is_on"], True)
        self.assertEqual(fields["source_name"], "FIRE TV")
        self.assertEqual(fields["volume"], 64)
        self.assertEqual(fields["mute_on"], False)
        self.assertEqual(fields["party_mode_on"], True)
        self.assertEqual(fields["info"], "ZONE3 VOL   55")
        self.assertEqual(fields["rec_source"], None)
        self.assertEqual(fields["zone2_source"], None)
        self.assertEqual(fields["zone2_volume"], None)
        self.assertEqual(fields["zone3_source"], None)
        self.assertEqual(fields["zone3_volume"], 55)
        self.assertEqual(fields["zone4_source"], None)
        self.assertEqual(fields["zone4_volume"], None)

    async def test_decode_feedback_message_with_meta_escape(self):
        """
        Test feedback message that generates a checksum that needs to be escaped
        I have verified that the real device does generate this message
        """
        with self.assertLogs(level=logging.INFO) as cm:
            logging.info("Dummy message")  # Hack: assertNoLogs not in Python 3.9
            display = await decode_single_message(
                self.codec,
                StreamProxy(
                    b"\xfe1\xa3 VIRE TV       VOL  60DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xfd\x01"
                ),
            )
        self.assertEqual(cm.output, ["INFO:root:Dummy message"])
        self.assertEqual(display.lines[0], "VIRE TV       VOL  60")
        self.assertEqual(display.lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            display.icons_that_are_on(),
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

    async def test_decode_trigger_message(self):
        with self.assertLogs(level=logging.INFO) as cm:
            trigger = await decode_single_message(
                self.codec, StreamProxy(b"\xfe\x07\xa3\x21\x01\x01\x00\x00\x00\xcd")
            )
            trigger.log()
        self.assertEqual(
            cm.output,
            [
                "INFO:rsp1570serial.messages:["
                "['All', ['on', 'off', 'off', 'off', 'off', 'off']], "
                "['Main', ['on', 'off', 'off', 'off', 'off', 'off']], "
                "['Zone 2', ['off', 'off', 'off', 'off', 'off', 'off']], "
                "['Zone 3', ['off', 'off', 'off', 'off', 'off', 'off']], "
                "['Zone 4', ['off', 'off', 'off', 'off', 'off', 'off']]]",
            ],
        )

    async def test_decode_stream1(self):
        ser = StreamProxy(
            b"\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99"
        )
        with self.assertLogs(level=logging.INFO) as cm:
            logging.info("Dummy message")  # Hack: assertNoLogs not in Python 3.9
            feedback_messages = await decode_all_messages(self.codec, ser)
        self.assertEqual(cm.output, ["INFO:root:Dummy message"])
        self.assertEqual(len(feedback_messages), 2)
        self.assertEqual(feedback_messages[0].lines[0], "FIRE TV       VOL  64")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            feedback_messages[0].icons_that_are_on(),
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
        self.assertEqual(feedback_messages[1].lines[0], "CATV          VOL  63")
        self.assertEqual(feedback_messages[1].lines[1], "DOLBY PL\x19 M     48K  ")
        self.assertCountEqual(
            feedback_messages[1].icons_that_are_on(),
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

    async def test_decode_stream2(self):
        """Deliberately removed the start byte from the first message.  Rest of first message will be reported as unexpected bytes."""
        ser = StreamProxy(
            b"1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99"
        )
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(self.codec, ser)
        self.assertEqual(len(feedback_messages), 1)
        self.assertEqual(feedback_messages[0].lines[0], "CATV          VOL  63")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 M     48K  ")
        self.assertCountEqual(
            feedback_messages[0].icons_that_are_on(),
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
        self.assertEqual(
            cm.output,
            [
                "WARNING:rsp1570serial.protocol:51 unexpected bytes encountered while waiting for START_BYTE: bytearray(b'1\\xa3 FIRE TV       VOL  64DOLBY PL\\x19 C     48K  \\x00F\\x08\\x00\\xfc\\xf2')",
            ],
        )

    async def test_decode_stream3(self):
        """Deliberately close early.  Close method will report discarded payload."""
        ser = StreamProxy(
            b"\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc"
        )
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(self.codec, ser)
        self.assertEqual(len(feedback_messages), 1)
        self.assertEqual(feedback_messages[0].lines[0], "FIRE TV       VOL  64")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            feedback_messages[0].icons_that_are_on(),
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
        self.assertEqual(
            cm.output,
            [
                "ERROR:rsp1570serial.protocol:Unexpected EOF encountered.  Work in progress discarded: bytearray(b'1\\xa3 CATV          VOL  63DOLBY PL\\x19 M     48K  \\x00F\\x08\\x00\\xfc')",
            ],
        )

    async def test_decode_stream4(self):
        """
        Deliberately truncate first message.
        Partial message will be discarded when unescaped start byte encountered.
        Next message will be treated as unexpected bytes when EOF encountered.
        """
        ser = StreamProxy(
            b"\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99"
        )
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(self.codec, ser)
        self.assertEqual(len(feedback_messages), 0)
        self.assertEqual(
            cm.output,
            [
                "ERROR:rsp1570serial.protocol:Invalid byte encountered while processing message content.  Work in progress discarded: bytearray(b'1\\xa3 FIRE TV       VOL  64DOLBY PL\\x19 C     48K  \\x00F\\x08\\x00\\xfc')",
                "WARNING:rsp1570serial.protocol:51 unexpected bytes discarded when EOF encountered: bytearray(b'1\\xa3 CATV          VOL  63DOLBY PL\\x19 M     48K  \\x00F\\x08\\x00\\xfc\\x99')",
            ],
        )

    async def test_decode_stream5(self):
        """
        Deliberately truncate first message.
        Partial message will be discarded when unescaped start byte encountered.
        Next message will be treated as unexpected bytes while waiting for a start byte.
        Next message should be read normally
        """
        ser = StreamProxy(
            b"\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2"
        )
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(self.codec, ser)
        self.assertEqual(len(feedback_messages), 1)
        self.assertEqual(feedback_messages[0].lines[0], "FIRE TV       VOL  64")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(
            feedback_messages[0].icons_that_are_on(),
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
        self.assertEqual(
            cm.output,
            [
                "ERROR:rsp1570serial.protocol:Invalid byte encountered while processing message content.  Work in progress discarded: bytearray(b'1\\xa3 FIRE TV       VOL  64DOLBY PL\\x19 C     48K  \\x00F\\x08\\x00\\xfc')",
                "WARNING:rsp1570serial.protocol:51 unexpected bytes encountered while waiting for START_BYTE: bytearray(b'1\\xa3 CATV          VOL  63DOLBY PL\\x19 M     48K  \\x00F\\x08\\x00\\xfc\\x99')",
            ],
        )


class SmartMessageDecoderTest(TestCase):
    def test1(self):
        result = decode_smart_display_line(b"Hello World")
        self.assertEqual(result, "Hello World")

    def test2(self):
        result = decode_smart_display_line(b"Hello World \x80")
        self.assertEqual(result, "Hello World \N{CIRCLED LATIN CAPITAL LETTER F}")

    def test3(self):
        result = decode_smart_display_line(b"Hello World \x00\x80")
        self.assertEqual(result, "Hello World  \N{CIRCLED LATIN CAPITAL LETTER F}")

    def test4(self):
        with self.assertLogs(level=logging.WARNING) as cm:
            result = decode_smart_display_line(b"Hello World \x8d")
        self.assertEqual(result, "INVALID LINE")
        self.assertEqual(
            cm.output,
            [
                "WARNING:rsp1570serial.messages:Error decoding smart display line: "
                "b'Hello World \\x8d'"
            ],
        )


class SmarSmartDisplayMessageTest(TestCase):
    def test1(self):
        m = SmartDisplayMessage(["Line2", "Line3"], 2)
        with self.assertLogs(level=logging.INFO) as cm:
            m.log()
        self.assertEqual(
            cm.output,
            [
                "INFO:rsp1570serial.messages:Display line 2: 'Line2'",
                "INFO:rsp1570serial.messages:Display line 3: 'Line3'",
            ],
        )

    def test2(self):
        data = b"\x00\x00" + b"12345678901234567890123456"
        m = smart_display_string_1_handler(MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_1, data)
        self.assertEqual(m.lines, ["12345678901234567890123456"])
        self.assertEqual(m.start, 1)

    def test3(self):
        data = (
            b"Line 2                    "
            b"Line 3                    "
            b"Line 4                    "
            b"Line 5                    "
            b"Line 6                    "
            b"Line 7                    "
            b"Line 8                    "
            b"Line 9                    "
            b"Line 10                   "
        )
        m = smart_display_string_2_handler(MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_2, data)
        self.assertEqual(
            m.lines,
            [
                "Line 2",
                "Line 3",
                "Line 4",
                "Line 5",
                "Line 6",
                "Line 7",
                "Line 8",
                "Line 9",
                "Line 10",
            ],
        )
        self.assertEqual(m.start, 2)
