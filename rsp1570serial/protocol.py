"""
Utility classes and functions for working with Rotel RSP-1570 RS-232 protocol messages

Protocol and terminology:
Messages take the form "start byte", "content"
The "content" is meta-encoded (start byte and escape byte are escaped)
The "content" takes the form "body", "checksum"
The checksum is calculated on the body
The body is comprised "byte count", "payload"
The "byte count" is the count of bytes in the payload
The payload is of the form "device id", "message type", "data"
"""

import io
import logging

_LOGGER = logging.getLogger(__name__)

START_BYTE = 0xfe
ESCAPE_BYTE = 0xfd

class RotelProtocolError(Exception):
    pass

class RotelEOFError(Exception):
    pass

class RotelInvalidByteError(Exception):
    pass

class RotelUnexpectedStartByteError(RotelInvalidByteError):
    """
    For now this is treated the same as an invalid byte error.
    However, it might make sense to treat it like the start of a new message,
    in which case it would invalidate the old message but we would then reset
    in read_payload and immediately start capturing content again.
    """
    pass

class StreamProxy:
    """
    Wraps an io.BytesIO object and presents an interface compatible with the Decoder.
    Handy class for testing purposes.
    """
    def __init__(self, message):
        self.buf = io.BytesIO(message)
    
    async def read(self, n):
        return self.buf.read(n)

class ProtocolDecoder():
    def __init__(self, ser):
        self.ser = ser
        self.bytes_received = 0

    async def next_char_without_meta_decoding(self):
        b = await self.ser.read(1)
        self.bytes_received += 1
        if len(b) == 0:
            raise RotelEOFError("Encountered EOF after {} bytes".format(self.bytes_received))
        assert(len(b) == 1)
        return b[0]

    async def next_char_with_meta_decoding(self):
        c1 = await self.next_char_without_meta_decoding()
        if c1 == START_BYTE:
            raise RotelUnexpectedStartByteError("Unexpected unescaped start byte encountered within message content.")
        elif c1 != ESCAPE_BYTE:
            return c1
        c2 = await self.next_char_without_meta_decoding()
        if c2 == 0x00:
            return ESCAPE_BYTE
        elif c2 == 0x01:
            return START_BYTE
        else:
            raise RotelInvalidByteError("Invalid byte following ESCAPE_BYTE ({:X}).".format(c2))

    async def wait_for_start_byte(self):
        unexpected_bytes = bytearray()
        while True:
            try:
                c = await self.next_char_without_meta_decoding()
            except RotelEOFError:
                if len(unexpected_bytes) > 0:
                    _LOGGER.warning("%d unexpected bytes discarded when EOF encountered: %r", len(unexpected_bytes), unexpected_bytes)
                raise
            if c == START_BYTE:
                break
            unexpected_bytes.append(c)
        if len(unexpected_bytes) > 0:
            _LOGGER.warning("%d unexpected bytes encountered while waiting for START_BYTE: %r", len(unexpected_bytes), unexpected_bytes)
        _LOGGER.debug("Start byte encountered at byte %d in stream", self.bytes_received)

    async def read_payload(self):
        await self.wait_for_start_byte()
        content = bytearray()
        try:
            content.append(await self.next_char_with_meta_decoding())
            #pylint: disable=unused-variable
            for x in range(content[0]):
                content.append(await self.next_char_with_meta_decoding())
            content.append(await self.next_char_with_meta_decoding())
        except RotelEOFError:
            raise RotelProtocolError("Unexpected EOF encountered.  Work in progress discarded: {}".format(content))
        except RotelInvalidByteError:
            raise RotelProtocolError("Invalid byte encountered while processing message content.  Work in progress discarded: {}".format(content))

        body = content[0:-1]
        expected_checksum = content[-1:][0]
        actual_checksum = calculate_checksum(body)
        if expected_checksum != actual_checksum:
            raise RotelProtocolError("Invalid checksum.\nBody: {!r}\nLen body: {}, Expected checksum: {:X}, Actual checksum: {:X}".format(body, len(body), expected_checksum, actual_checksum))
        _LOGGER.debug("Valid content of length %d received: %r", len(content), content)
        return content[1:-1]

class DecodeProtocolStreamIter:
    def __init__(self, ser):
        self.decoder = ProtocolDecoder(ser)

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            try:
                payload = await self.decoder.read_payload()
            except RotelProtocolError as err:
                _LOGGER.error(err)
            except RotelEOFError:
                _LOGGER.info("Finished reading messages")
                raise StopAsyncIteration
            else:
                return payload

def decode_protocol_stream(ser):
    return DecodeProtocolStreamIter(ser)

# async def decode_protocol_stream(ser):
#     decoder = ProtocolDecoder(ser)
#     while True:
#         try:
#             payload = await decoder.read_payload()
#         except RotelProtocolError as err:
#             _LOGGER.error(err)
#         except RotelEOFError:
#             break
#         else:
#             yield payload
#     _LOGGER.info("Finished reading messages")

def encode_payload(payload):
    body = [len(payload)]
    body.extend(payload)
    checksum = calculate_checksum(body)
    content = body
    content.append(checksum)
    message = meta_escape(content)
    message.insert(0, START_BYTE)
    return bytes(message)

def calculate_checksum(sequence):
    cs = 0
    for item in sequence:
        cs += item
    return cs & 0xff

def meta_escape(raw_message):
    message = []
    for b in raw_message:
        if b == ESCAPE_BYTE:
            message.extend([ESCAPE_BYTE, 0x00])
        elif b == START_BYTE:
            message.extend([ESCAPE_BYTE, 0x01])
        else:
            message.append(b)
    return message
