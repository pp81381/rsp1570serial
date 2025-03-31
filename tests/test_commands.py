from unittest import TestCase

from rsp1570serial.messages import MessageCodec
from rsp1570serial.rotel_model_meta import RSP1570_META


class RotelTestCommands(TestCase):
    def setUp(self) -> None:
        self.codec = MessageCodec(RSP1570_META)

    def test_encode_power_toggle(self):
        self.assertEqual(
            self.codec.encode_command("POWER_TOGGLE"),
            b"\xfe\x03\xa3\x10\x0a\xc0",
        )

    def test_encode_mute_toggle(self):
        self.assertEqual(
            self.codec.encode_command("MUTE_TOGGLE"),
            b"\xfe\x03\xa3\x10\x1e\xd4",
        )

    def test_meta_encoding_of_escape_byte(self):
        self.assertEqual(
            self.codec.encode_command("VOLUME_40"),
            b"\xfe\x03\xa3\x30\x28\xfd\x01",
        )

    def test_meta_encoding_of_start_byte(self):
        self.assertEqual(
            self.codec.encode_command("ZONE_3_VOLUME_36"),
            b"\xfe\x03\xa3\x33\x24\xfd\x00",
        )

    def test_volume_direct_command(self):
        self.assertEqual(
            self.codec.encode_volume_direct_command(3, 36),
            b"\xfe\x03\xa3\x33\x24\xfd\x00",
        )

    def test_volume_direct_command2(self):
        self.assertEqual(
            self.codec.encode_volume_direct_command(4, 80),
            b"\xfe\x03\xa3\x34\x50\x2a",
        )
        self.assertEqual(
            self.codec.encode_volume_direct_command(4, 95),
            b"\xfe\x03\xa3\x34\x5f\x39",
        )  # Wrong in protocol spec
        self.assertEqual(
            self.codec.encode_volume_direct_command(4, 96),
            b"\xfe\x03\xa3\x34\x60\x3a",
        )  # Wrong in protocol spec

    def test_make_invalid_command(self):
        with self.assertRaises(KeyError):
            self.codec.encode_command("INVALID_COMMAND")

    def test_make_invalid_volume_direct_commands(self):
        with self.assertRaises(ValueError):
            self.codec.encode_volume_direct_command(5, 50)
        with self.assertRaises(ValueError):
            self.codec.encode_volume_direct_command(1, -1)
        with self.assertRaises(ValueError):
            self.codec.encode_volume_direct_command(1, 97)
