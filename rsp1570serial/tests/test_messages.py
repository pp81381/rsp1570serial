import aiounittest
import logging
from rsp1570serial.commands import encode_command, MSGTYPE_PRIMARY_COMMANDS, MSGTYPE_VOLUME_DIRECT_COMMANDS
from rsp1570serial.messages import decode_message_stream, FeedbackMessage
from rsp1570serial.protocol import StreamProxy
import unittest

async def decode_all_messages(ser):
    messages = []
    async for command in decode_message_stream(ser):
        messages.append(command)
    return messages

async def decode_single_message(ser):
    messages = await decode_all_messages(ser)
    assert(len(messages) == 1)
    return messages[0]

class AsyncRotelTestMessages(aiounittest.AsyncTestCase):
    async def test_encode_decode(self):
        message = encode_command('POWER_TOGGLE')
        with self.assertLogs(level=logging.INFO) as cm:
            command = await decode_single_message(StreamProxy(message))
        self.assertEqual(command.message_type, MSGTYPE_PRIMARY_COMMANDS)
        self.assertEqual(command.key, b'\x0a')
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_encode_decode_with_meta(self):
        message = encode_command('VOLUME_40')
        with self.assertLogs(level=logging.INFO) as cm:
            command = await decode_single_message(StreamProxy(message))
        self.assertEqual(command.message_type, MSGTYPE_VOLUME_DIRECT_COMMANDS)
        self.assertEqual(command.key, b'\x28')
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_decode_feedback_message(self):
        with self.assertLogs(level=logging.INFO) as cm:
            display = await decode_single_message(StreamProxy(b'\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2'))
        self.assertEqual(display.lines[0], "FIRE TV       VOL  64")
        self.assertEqual(display.lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(display.icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])
        fields = display.parse_display_lines()
        self.assertEqual(fields['is_on'], True)
        self.assertEqual(fields['source_name'], "FIRE TV")
        self.assertEqual(fields['volume'], 64)
        self.assertEqual(fields['mute_on'], False)
        self.assertEqual(fields['party_mode_on'], False)
        self.assertEqual(fields['info'], "DOLBY PLII C     48K")
        self.assertEqual(fields['rec_source'], None)
        self.assertEqual(fields['zone2_source'], None)
        self.assertEqual(fields['zone2_volume'], None)
        self.assertEqual(fields['zone3_source'], None)
        self.assertEqual(fields['zone3_volume'], None)
        self.assertEqual(fields['zone4_source'], None)
        self.assertEqual(fields['zone4_volume'], None)

    async def test_decode_feedback_after_power_off(self):
        with self.assertLogs(level=logging.INFO) as cm:
            display = await decode_single_message(StreamProxy(b'\xfe1\xa3 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\xfc'))
        self.assertEqual(display.lines[0], '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertEqual(display.lines[1], '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        self.assertCountEqual(display.icons_that_are_on(), ['Standby LED'])
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])
        fields = display.parse_display_lines()
        self.assertEqual(fields['is_on'], False)
        self.assertEqual(fields['source_name'], None)
        self.assertEqual(fields['volume'], None)
        self.assertEqual(fields['mute_on'], None)
        self.assertEqual(fields['party_mode_on'], None)
        self.assertEqual(fields['info'], None)
        self.assertEqual(fields['rec_source'], None)
        self.assertEqual(fields['zone2_source'], None)
        self.assertEqual(fields['zone2_volume'], None)
        self.assertEqual(fields['zone3_source'], None)
        self.assertEqual(fields['zone3_volume'], None)
        self.assertEqual(fields['zone4_source'], None)
        self.assertEqual(fields['zone4_volume'], None)

    async def test_decode_feedback_message_with_rec_source(self):
        display = FeedbackMessage("FIRE TV       VOL  64", "  REC    SOURCE      ", b'\x00F\x08\x00\xfc')
        self.assertCountEqual(display.icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        fields = display.parse_display_lines()
        self.assertEqual(fields['is_on'], True)
        self.assertEqual(fields['source_name'], "FIRE TV")
        self.assertEqual(fields['volume'], 64)
        self.assertEqual(fields['mute_on'], False)
        self.assertEqual(fields['party_mode_on'], False)
        self.assertEqual(fields['info'], "REC    SOURCE")
        self.assertEqual(fields['rec_source'], "SOURCE")
        self.assertEqual(fields['zone2_source'], None)
        self.assertEqual(fields['zone2_volume'], None)
        self.assertEqual(fields['zone3_source'], None)
        self.assertEqual(fields['zone3_volume'], None)
        self.assertEqual(fields['zone4_source'], None)
        self.assertEqual(fields['zone4_volume'], None)

    async def test_decode_feedback_message_with_zone_source(self):
        display = FeedbackMessage("FIRE TV       VOL  64", "  ZONE4  TUNER       ", b'\x00F\x08\x00\xfc')
        self.assertCountEqual(display.icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        fields = display.parse_display_lines()
        self.assertEqual(fields['is_on'], True)
        self.assertEqual(fields['source_name'], "FIRE TV")
        self.assertEqual(fields['volume'], 64)
        self.assertEqual(fields['mute_on'], False)
        self.assertEqual(fields['party_mode_on'], False)
        self.assertEqual(fields['info'], "ZONE4  TUNER")
        self.assertEqual(fields['rec_source'], None)
        self.assertEqual(fields['zone2_source'], None)
        self.assertEqual(fields['zone2_volume'], None)
        self.assertEqual(fields['zone3_source'], None)
        self.assertEqual(fields['zone3_volume'], None)
        self.assertEqual(fields['zone4_source'], 'TUNER')
        self.assertEqual(fields['zone4_volume'], None)

    async def test_decode_feedback_message_with_zone_volume_and_party_mode(self):
        display = FeedbackMessage("FIRE TV   pty VOL  64", "  ZONE3 VOL   55     ", b'\x00F\x08\x00\xfc')
        self.assertCountEqual(display.icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        fields = display.parse_display_lines()
        self.assertEqual(fields['is_on'], True)
        self.assertEqual(fields['source_name'], "FIRE TV")
        self.assertEqual(fields['volume'], 64)
        self.assertEqual(fields['mute_on'], False)
        self.assertEqual(fields['party_mode_on'], True)
        self.assertEqual(fields['info'], "ZONE3 VOL   55")
        self.assertEqual(fields['rec_source'], None)
        self.assertEqual(fields['zone2_source'], None)
        self.assertEqual(fields['zone2_volume'], None)
        self.assertEqual(fields['zone3_source'], None)
        self.assertEqual(fields['zone3_volume'], 55)
        self.assertEqual(fields['zone4_source'], None)
        self.assertEqual(fields['zone4_volume'], None)
    
    async def test_decode_feedback_message_with_meta_escape(self):
        """
        Test feedback message that generates a checksum that needs to be escaped
        I have verified that the real device does generate this message
        """
        with self.assertLogs(level=logging.INFO) as cm:
            display = await decode_single_message(StreamProxy(b'\xfe1\xa3 VIRE TV       VOL  60DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xfd\x01'))
        self.assertEqual(display.lines[0], "VIRE TV       VOL  60")
        self.assertEqual(display.lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(display.icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_decode_trigger_message(self):
        with self.assertLogs(level=logging.INFO) as cm:
            trigger = await decode_single_message(StreamProxy(b'\xfe\x07\xa3\x21\x01\x01\x00\x00\x00\xcd'))
            trigger.log()
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages",
            "INFO:rsp1570serial.messages:["
                "['All', ['on', 'off', 'off', 'off', 'off', 'off']], "
                "['Main', ['on', 'off', 'off', 'off', 'off', 'off']], "
                "['Zone 2', ['off', 'off', 'off', 'off', 'off', 'off']], "
                "['Zone 3', ['off', 'off', 'off', 'off', 'off', 'off']], "
                "['Zone 4', ['off', 'off', 'off', 'off', 'off', 'off']]]",
        ])

    async def test_decode_stream1(self):
        ser = StreamProxy(b'\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99')
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(ser)
        self.assertEqual(len(feedback_messages), 2)
        self.assertEqual(feedback_messages[0].lines[0], "FIRE TV       VOL  64")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(feedback_messages[0].icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(feedback_messages[1].lines[0], "CATV          VOL  63")
        self.assertEqual(feedback_messages[1].lines[1], "DOLBY PL\x19 M     48K  ")
        self.assertCountEqual(feedback_messages[1].icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(cm.output, [
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_decode_stream2(self):
        """ Deliberately removed the start byte from the first message.  Rest of first message will be reported as unexpected bytes. """
        ser = StreamProxy(b'1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99')
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(ser)
        self.assertEqual(len(feedback_messages), 1)
        self.assertEqual(feedback_messages[0].lines[0], "CATV          VOL  63")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 M     48K  ")
        self.assertCountEqual(feedback_messages[0].icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(cm.output, [
            "WARNING:rsp1570serial.protocol:51 unexpected bytes encountered while waiting for START_BYTE: bytearray(b'1\\xa3 FIRE TV       VOL  64DOLBY PL\\x19 C     48K  \\x00F\\x08\\x00\\xfc\\xf2')",
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_decode_stream3(self):
        """ Deliberately close early.  Close method will report discarded payload. """
        ser = StreamProxy(b'\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc')
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(ser)
        self.assertEqual(len(feedback_messages), 1)
        self.assertEqual(feedback_messages[0].lines[0], "FIRE TV       VOL  64")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(feedback_messages[0].icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(cm.output, [
            "ERROR:rsp1570serial.protocol:Unexpected EOF encountered.  Work in progress discarded: bytearray(b'1\\xa3 CATV          VOL  63DOLBY PL\\x19 M     48K  \\x00F\\x08\\x00\\xfc')",
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_decode_stream4(self):
        """
        Deliberately truncate first message.
        Partial message will be discarded when unescaped start byte encountered.
        Next message will be treated as unexpected bytes when EOF encountered.
        """
        ser = StreamProxy(b'\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99')
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(ser)
        self.assertEqual(len(feedback_messages), 0)
        self.assertEqual(cm.output, [
            "ERROR:rsp1570serial.protocol:Invalid byte encountered while processing message content.  Work in progress discarded: bytearray(b'1\\xa3 FIRE TV       VOL  64DOLBY PL\\x19 C     48K  \\x00F\\x08\\x00\\xfc')",
            "WARNING:rsp1570serial.protocol:51 unexpected bytes discarded when EOF encountered: bytearray(b'1\\xa3 CATV          VOL  63DOLBY PL\\x19 M     48K  \\x00F\\x08\\x00\\xfc\\x99')",
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])

    async def test_decode_stream5(self):
        """
        Deliberately truncate first message.
        Partial message will be discarded when unescaped start byte encountered.
        Next message will be treated as unexpected bytes while waiting for a start byte.
        Next message should be read normally
        """
        ser = StreamProxy(b'\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xfe1\xa3 CATV          VOL  63DOLBY PL\x19 M     48K  \x00F\x08\x00\xfc\x99\xfe1\xa3 FIRE TV       VOL  64DOLBY PL\x19 C     48K  \x00F\x08\x00\xfc\xf2')
        with self.assertLogs(level=logging.INFO) as cm:
            feedback_messages = await decode_all_messages(ser)
        self.assertEqual(len(feedback_messages), 1)
        self.assertEqual(feedback_messages[0].lines[0], "FIRE TV       VOL  64")
        self.assertEqual(feedback_messages[0].lines[1], "DOLBY PL\x19 C     48K  ")
        self.assertCountEqual(feedback_messages[0].icons_that_are_on(), ['II', 'HDMI', 'Pro Logic', 'Standby LED', 'SW', 'SR', 'SL', 'FR', 'C', 'FL'])
        self.assertEqual(cm.output, [
            "ERROR:rsp1570serial.protocol:Invalid byte encountered while processing message content.  Work in progress discarded: bytearray(b'1\\xa3 FIRE TV       VOL  64DOLBY PL\\x19 C     48K  \\x00F\\x08\\x00\\xfc')",
            "WARNING:rsp1570serial.protocol:51 unexpected bytes encountered while waiting for START_BYTE: bytearray(b'1\\xa3 CATV          VOL  63DOLBY PL\\x19 M     48K  \\x00F\\x08\\x00\\xfc\\x99')",
            "INFO:rsp1570serial.protocol:Finished reading messages"
        ])