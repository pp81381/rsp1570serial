import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Callable, Dict, List, Union

from rsp1570serial.icons import flags_to_icons, icons_that_are_on
from rsp1570serial.message_types import (
    MSGTYPE_FEEDBACK_STRING,
    MSGTYPE_MAIN_ZONE_COMMANDS,
    MSGTYPE_PRIMARY_COMMANDS,
    MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
    MSGTYPE_RECORD_SOURCE_COMMANDS,
    MSGTYPE_TRIGGER_DIRECT_COMMANDS,
    MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_1,
    MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_2,
    MSGTYPE_TRIGGER_STATUS_STRING,
    MSGTYPE_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_2_COMMANDS,
    MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_3_COMMANDS,
    MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_4_COMMANDS,
    MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS,
)
from rsp1570serial.protocol import (
    AnyAsyncReader,
    decode_protocol_stream,
    encode_payload,
)
from rsp1570serial.rotel_model_meta import RotelModelMeta
from rsp1570serial.utils import pretty_print_bytes

_LOGGER = logging.getLogger(__name__)


INVERT_F_BYTES = "\N{CIRCLED LATIN CAPITAL LETTER F}".encode("utf-8")
INVERT_M_BYTES = "\N{CIRCLED LATIN CAPITAL LETTER M}".encode("utf-8")
INVERT_T_BYTES = "\N{CIRCLED LATIN CAPITAL LETTER T}".encode("utf-8")
INVERT_R_BYTES = "\N{CIRCLED LATIN CAPITAL LETTER R}".encode("utf-8")
INVERT_S_BYTES = "\N{CIRCLED LATIN CAPITAL LETTER S}".encode("utf-8")
INVERT_A_BYTES = "\N{CIRCLED LATIN CAPITAL LETTER A}".encode("utf-8")
FULL_BAR_BYTES = "\N{BOX DRAWINGS LIGHT HORIZONTAL}".encode("utf-8")
RIGHT_BYTES = "\N{BLACK MEDIUM RIGHT-POINTING TRIANGLE}".encode("utf-8")
PAUSE_BYTES = "\N{DOUBLE VERTICAL BAR}".encode("utf-8")
STOP_BYTES = "\N{BLACK SQUARE FOR STOP}".encode("utf-8")
LEFT_BYTES = "\N{BLACK MEDIUM LEFT-POINTING TRIANGLE}".encode("utf-8")
CURSOR_RIGHT_BYTES = "\N{RIGHTWARDS DOUBLE ARROW}".encode("utf-8")
CURSOR_LEFT_BYTES = "\N{LEFTWARDS DOUBLE ARROW}".encode("utf-8")


class RotelMessageError(Exception):
    pass


class FeedbackMessage:
    def __init__(self, line1, line2, flags):
        self.lines = [line1, line2]
        self.flags = flags
        self.icons = flags_to_icons(flags)

    def icons_that_are_on(self):
        return icons_that_are_on(self.icons)

    def log(self, level=logging.INFO):
        _LOGGER.log(level, "Display line 1: '%s'", self.lines[0])
        _LOGGER.log(level, "Display line 2: '%s'", self.lines[1])
        _LOGGER.log(level, "Icons: %r", self.icons_that_are_on())

    def parse_display_lines(self):
        """
        Parse the display lines and return as much
        as we can infer about the state of the amp.
        Note that the maximum length of sources is 8 characters.
        Display line 2 is an informational display with multiple
        purposes so we decode what we can but it's up to the caller
        to decide what to do when one item disappears when another
        appears.  It is copied out verbatim in the 'info' field and
        it is probably safest to just display that to the user
        and leave it at that.
        """
        is_on = None
        source_name = None
        volume = None
        mute_on = None
        party_mode_on = None
        info = None
        rec_source = None
        zone2_source = None
        zone2_volume = None
        zone3_source = None
        zone3_volume = None
        zone4_source = None
        zone4_volume = None

        line0 = self.lines[0]
        if len(line0) != 21:
            _LOGGER.error("Display line 1 must be exactly 21 bytes")
        if (
            line0
            == "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            is_on = False
        else:
            is_on = True
            source_name = line0[:8].rstrip()
            party_mode_on = line0[10:13] == "pty"
            vol_str = line0[14:]
            if (vol_str == "MUTE ON") or (vol_str == "       "):
                mute_on = True
                volume = None
            elif vol_str[0:3] != "VOL":
                _LOGGER.error("Could not verify VOL string: %s", vol_str)
            else:
                mute_on = False
                volume = int(vol_str[3:])

        line1 = self.lines[1]
        if len(line1) != 21:
            _LOGGER.error("Display line 2 must be exactly 21 bytes")
        if (
            line1
            == "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            pass
        else:
            info = line1.strip().replace("\x19", "II")
            if line1[:9] == "  REC    ":
                rec_source = line1[9:].rstrip()
            elif line1[:9] == "  ZONE2  ":
                zone2_source = line1[9:].rstrip()
            elif line1[:14] == "  ZONE2 VOL   ":
                zone2_volume = int(line1[14:16])
            elif line1[:9] == "  ZONE3  ":
                zone3_source = line1[9:].rstrip()
            elif line1[:14] == "  ZONE3 VOL   ":
                zone3_volume = int(line1[14:16])
            elif line1[:9] == "  ZONE4  ":
                zone4_source = line1[9:].rstrip()
            elif line1[:14] == "  ZONE4 VOL   ":
                zone4_volume = int(line1[14:16])

        return {
            "is_on": is_on,
            "source_name": source_name,
            "volume": volume,
            "mute_on": mute_on,
            "party_mode_on": party_mode_on,
            "info": info,
            "rec_source": rec_source,
            "zone2_source": zone2_source,
            "zone2_volume": zone2_volume,
            "zone3_source": zone3_source,
            "zone3_volume": zone3_volume,
            "zone4_source": zone4_source,
            "zone4_volume": zone4_volume,
        }


class TriggerMessage:
    def __init__(self, flags):
        self.flags = flags

    def log(self, level=logging.INFO):
        _LOGGER.log(level, self.flags_to_list(self.flags))

    @classmethod
    def _flag_to_list(cls, flag):
        out = []
        out.append("on" if flag & 0x01 else "off")
        out.append("on" if flag & 0x02 else "off")
        out.append("on" if flag & 0x04 else "off")
        out.append("on" if flag & 0x08 else "off")
        out.append("on" if flag & 0x10 else "off")
        out.append("on" if flag & 0x20 else "off")
        return out

    @classmethod
    def flags_to_list(cls, flags):
        out = []
        out.append(["All", cls._flag_to_list(flags[0])])
        out.append(["Main", cls._flag_to_list(flags[1])])
        out.append(["Zone 2", cls._flag_to_list(flags[2])])
        out.append(["Zone 3", cls._flag_to_list(flags[3])])
        out.append(["Zone 4", cls._flag_to_list(flags[4])])
        return out


class CommandMessage:
    def __init__(self, message_type: int, key: bytes):
        self.message_type = message_type
        self.key = key

    def log(self, level=logging.INFO):
        pretty_key = pretty_print_bytes(self.key)
        _LOGGER.log(
            level,
            f"Command Message: message_type={self.message_type}, key={pretty_key}",
        )


class SmartDisplayMessage:
    def __init__(self, lines, start):
        self.lines = lines
        self.start = start

    def log(self, level=logging.INFO):
        for lineno, line in enumerate(self.lines, self.start):
            _LOGGER.log(level, f"Display line {lineno}: '{line}'")


# Type alias for all message types
AnyMessage = Union[
    FeedbackMessage,
    CommandMessage,
    TriggerMessage,
    SmartDisplayMessage,
]


def feedback_message_handler(message_type: int, data: bytes) -> FeedbackMessage:
    assert message_type == MSGTYPE_FEEDBACK_STRING
    display_line1_bytes = data[0:21]  # The II is char 0x19
    display_line2_bytes = data[21:42]
    flags = data[42:47]
    return FeedbackMessage(
        display_line1_bytes.decode(encoding="ascii"),
        display_line2_bytes.decode(encoding="ascii"),
        flags,
    )


# OFF Data was: bytearray(b'\x00\x00\x00\x00\x00')
# ON  Data was: bytearray(b'\x01\x01\x00\x00\x00')
def trigger_message_handler(message_type: int, data: bytes) -> TriggerMessage:
    assert message_type == MSGTYPE_TRIGGER_STATUS_STRING
    assert len(data) == 5
    return TriggerMessage(data)


def command_message_handler(message_type: int, data: bytes) -> CommandMessage:
    return CommandMessage(message_type, data)


def decode_smart_display_line(line_bytes: bytes) -> str:
    """
    Decode a smart display line

    Convert special characters to appropriate unicode equivalents
    Note - this should really be a codec but it works OK
    """
    line_bytes = (
        line_bytes.replace(b"\x80", INVERT_F_BYTES)
        .replace(b"\x81", INVERT_M_BYTES)
        .replace(b"\x82", INVERT_T_BYTES)
        .replace(b"\x83", INVERT_R_BYTES)
        .replace(b"\x84", INVERT_S_BYTES)
        .replace(b"\x85", INVERT_A_BYTES)
        .replace(b"\x86", FULL_BAR_BYTES)
        .replace(b"\x87", RIGHT_BYTES)
        .replace(b"\x88", PAUSE_BYTES)
        .replace(b"\x89", STOP_BYTES)
        .replace(b"\x8a", LEFT_BYTES)
        .replace(b"\x8b", CURSOR_RIGHT_BYTES)
        .replace(b"\x8c", CURSOR_LEFT_BYTES)
    )
    try:
        line = line_bytes.decode(encoding="utf-8")
    except UnicodeDecodeError as e:
        _LOGGER.warning("Error decoding smart display line: %r", line_bytes)
        line = "INVALID LINE"

    return line.rstrip()


def smart_display_string_1_handler(
    message_type: int,
    data: bytes,
) -> SmartDisplayMessage:
    assert message_type == MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_1
    assert len(data) == 28
    assert data[0:2] == b"\x00\x00"
    lines = [
        decode_smart_display_line(data[2:28]),
    ]
    return SmartDisplayMessage(lines, 1)


def smart_display_string_2_handler(
    message_type: int,
    data: bytes,
) -> SmartDisplayMessage:
    assert message_type == MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_2
    assert len(data) == 234
    lines = [
        decode_smart_display_line(data[0:26]),
        decode_smart_display_line(data[26:52]),
        decode_smart_display_line(data[52:78]),
        decode_smart_display_line(data[78:104]),
        decode_smart_display_line(data[104:130]),
        decode_smart_display_line(data[130:156]),
        decode_smart_display_line(data[156:182]),
        decode_smart_display_line(data[182:208]),
        decode_smart_display_line(data[208:234]),
    ]
    return SmartDisplayMessage(lines, 2)


def get_volume_direct_message_type(zone: int) -> int:
    if zone == 1:
        return MSGTYPE_VOLUME_DIRECT_COMMANDS
    elif zone == 2:
        return MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS
    elif zone == 3:
        return MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS
    elif zone == 4:
        return MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS
    else:
        raise ValueError("Invalid zone: {}".format(zone))


def get_message_handler(message_type: int) -> Callable[[int, bytes], AnyMessage]:
    message_handlers: Dict[int, Callable[[int, bytes], AnyMessage]] = {
        MSGTYPE_FEEDBACK_STRING: feedback_message_handler,
        MSGTYPE_TRIGGER_STATUS_STRING: trigger_message_handler,
        MSGTYPE_PRIMARY_COMMANDS: command_message_handler,
        MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS: command_message_handler,
        MSGTYPE_MAIN_ZONE_COMMANDS: command_message_handler,
        MSGTYPE_RECORD_SOURCE_COMMANDS: command_message_handler,
        MSGTYPE_ZONE_2_COMMANDS: command_message_handler,
        MSGTYPE_ZONE_3_COMMANDS: command_message_handler,
        MSGTYPE_ZONE_4_COMMANDS: command_message_handler,
        MSGTYPE_VOLUME_DIRECT_COMMANDS: command_message_handler,
        MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS: command_message_handler,
        MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS: command_message_handler,
        MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS: command_message_handler,
        MSGTYPE_TRIGGER_DIRECT_COMMANDS: command_message_handler,
        MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_1: smart_display_string_1_handler,
        MSGTYPE_TRIGGER_SMART_DISPLAY_STRING_2: smart_display_string_2_handler,
    }
    if message_type in message_handlers:
        return message_handlers[message_type]
    else:
        raise RotelMessageError("Unknown message type byte {:X}".format(message_type))


@dataclass
class MessageCodec:
    meta: RotelModelMeta

    def encode_command(self, command_name: str) -> bytes:
        [message_type, key] = self.meta.messages[command_name]
        return encode_payload([self.meta.device_id, message_type, key])

    def encode_volume_direct_command(self, zone: int, volume: int) -> bytes:
        message_type = get_volume_direct_message_type(zone)

        if volume < self.meta.min_volume or volume > self.meta.max_volume:
            raise ValueError("Volume out of range: {}".format(volume))

        return encode_payload([self.meta.device_id, message_type, volume])

    def decode_message(self, payload: bytes) -> AnyMessage:
        if payload[0] != self.meta.device_id:
            raise RotelMessageError(
                "Didn't get expected Device ID byte.  {} != {}".format(
                    payload[0], self.meta.device_id
                )
            )

        message_type = payload[1]
        data = payload[2:]
        message_handler = get_message_handler(message_type)
        return message_handler(message_type, data)

    async def decode_message_stream(
        self, ser: AnyAsyncReader
    ) -> AsyncGenerator[AnyMessage, None]:
        async for payload in decode_protocol_stream(ser):
            yield self.decode_message(payload)
