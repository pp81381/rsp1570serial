from unittest import IsolatedAsyncioTestCase, TestCase

from rsp1570serial.protocol import (
    ProtocolDecoder,
    StreamProxy,
    calculate_checksum,
    encode_payload,
)


class RotelTestProtocol(TestCase):
    def test_checksum1(self):
        self.assertEqual(calculate_checksum([0x03, 0xA3, 0x10, 0x1E]), 0xD4)

    def test_checksum2(self):
        self.assertEqual(calculate_checksum([0x03, 0xA3, 0x34, 0x30]), 0x0A)

    def test_checksum3(self):
        self.assertEqual(calculate_checksum(b"\x03\xa3\x34\x30"), 0x0A)

    def test_checksum4(self):
        self.assertEqual(calculate_checksum(bytes([0x03, 0xA3, 0x34, 0x30])), 0x0A)

    def test_encode_payload(self):
        self.assertEqual(encode_payload(b"\xa3\x10\x0a"), b"\xfe\x03\xa3\x10\x0a\xc0")

    def test_meta_encoding_of_escape_byte(self):
        self.assertEqual(
            encode_payload(b"\xa3\x30\x28"), b"\xfe\x03\xa3\x30\x28\xfd\x01"
        )

    def test_meta_encoding_of_start_byte(self):
        self.assertEqual(
            encode_payload(b"\xa3\x33\x24"), b"\xfe\x03\xa3\x33\x24\xfd\x00"
        )


class AsyncRotelTestProtocol(IsolatedAsyncioTestCase):
    async def test_encode_decode_with_meta(self):
        message = encode_payload(b"\xa3\x30\x28")
        decoder = ProtocolDecoder(StreamProxy(message))
        data = await decoder.read_payload()
        self.assertEqual(data, b"\xa3\x30\x28")
