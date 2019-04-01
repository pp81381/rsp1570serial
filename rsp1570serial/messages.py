import logging
from rsp1570serial.protocol import decode_protocol_stream, encode_payload

_LOGGER = logging.getLogger(__name__)

DEVICE_ID_RSP1570 = 0xa3

MSGTYPE_PRIMARY_COMMANDS = 0x10
MSGTYPE_MAIN_ZONE_COMMANDS = 0x14
MSGTYPE_RECORD_SOURCE_COMMANDS = 0x15
MSGTYPE_ZONE_2_COMMANDS = 0x16
MSGTYPE_ZONE_3_COMMANDS = 0x17
MSGTYPE_ZONE_4_COMMANDS = 0x18
MSGTYPE_FEEDBACK_STRING = 0x20
MSGTYPE_TRIGGER_STATUS_STRING = 0x21
MSGTYPE_VOLUME_DIRECT_COMMANDS = 0x30
MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS = 0x32
MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS = 0x33
MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS = 0x34
MSGTYPE_TRIGGER_DIRECT_COMMANDS = 0x40

class RotelMessageError(Exception):
    pass

class FeedbackMessage:
    def __init__(self, line1, line2, flags):
        self.lines = [line1, line2]
        self.flags = flags
        self.icons = decode_feedback_message_flags(flags)

    def icons_that_are_on(self):
        # TODO: Consistent order
        return [ k for (k, v) in self.icons.items() if v ]

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
        if line0 == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            is_on = False
        else:
            is_on = True
            source_name = line0[:8].rstrip()
            party_mode_on = line0[10:13] == 'pty'
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
        if line1 == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            pass
        else:
            info = line1.strip().replace('\x19', 'II')
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
            'is_on' : is_on,
            'source_name': source_name,
            'volume': volume,
            'mute_on': mute_on,
            'party_mode_on': party_mode_on,
            'info': info,
            'rec_source': rec_source,
            'zone2_source': zone2_source,
            'zone2_volume': zone2_volume,
            'zone3_source': zone3_source,
            'zone3_volume': zone3_volume,
            'zone4_source': zone4_source,
            'zone4_volume': zone4_volume,
        }

def decode_feedback_message_flags(flags):
    icons = {}
    icons["A"] = bool(flags[0] & 0x01)
    icons["5"] = bool(flags[0] & 0x02)
    icons["4"] = bool(flags[0] & 0x04)
    icons["3"] = bool(flags[0] & 0x08)
    icons["2"] = bool(flags[0] & 0x10)
    icons["1"] = bool(flags[0] & 0x20)
    icons["Coaxial"] = bool(flags[0] & 0x40)
    icons["Optical"] = bool(flags[0] & 0x80)

    icons["x"] = bool(flags[1] & 0x01)
    icons["II"] = bool(flags[1] & 0x02)
    icons["HDMI"] = bool(flags[1] & 0x04)
    icons["EX"] = bool(flags[1] & 0x08)
    icons["ES"] = bool(flags[1] & 0x10)
    icons["dts"] = bool(flags[1] & 0x20)
    icons["Pro Logic"] = bool(flags[1] & 0x40)
    icons["Dolby Digital"] = bool(flags[1] & 0x80)

    icons["Display Mode0"] = bool(flags[2] & 0x01)
    icons["Display Mode1"] = bool(flags[2] & 0x02)
    icons["Zone 2"] = bool(flags[2] & 0x04)
    icons["Standby LED"] = bool(flags[2] & 0x08)

    icons["SB"] = bool(flags[3] & 0x01)
    icons["Zone 4"] = bool(flags[3] & 0x02)
    icons["Zone 3"] = bool(flags[3] & 0x04)
    icons["<"] = bool(flags[3] & 0x08)
    icons[">"] = bool(flags[3] & 0x10)
    icons["7.1"] = bool(flags[3] & 0x20)
    icons["5.1"] = bool(flags[3] & 0x40)
    icons["Zone"] = bool(flags[3] & 0x80)

    icons["CBL"] = bool(flags[4] & 0x01)
    icons["CBR"] = bool(flags[4] & 0x02)
    icons["SW"] = bool(flags[4] & 0x04)
    icons["SR"] = bool(flags[4] & 0x08)
    icons["SL"] = bool(flags[4] & 0x10)
    icons["FR"] = bool(flags[4] & 0x20)
    icons["C"] = bool(flags[4] & 0x40)
    icons["FL"] = bool(flags[4] & 0x80)

    return icons

class TriggerMessage:
    def __init__(self, flags):
        self.flags = flags
    
    def log(self, level=logging.INFO):
        _LOGGER.log(level, self.flags_to_list(self.flags))

    @classmethod
    def _flag_to_list(cls, flag):
        out = []
        out.append('on' if flag & 0x01 else 'off')
        out.append('on' if flag & 0x02 else 'off')
        out.append('on' if flag & 0x04 else 'off')
        out.append('on' if flag & 0x08 else 'off')
        out.append('on' if flag & 0x10 else 'off')
        out.append('on' if flag & 0x20 else 'off')
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
    def __init__(self, message_type, key):
        self.message_type = message_type
        self.key = key

def feedback_message_handler(message_type, data):
    assert message_type == MSGTYPE_FEEDBACK_STRING
    display_line1_bytes = data[0:21] # The II is char 0x19
    display_line2_bytes = data[21:42]
    flags = data[42:47]
    return FeedbackMessage(
        display_line1_bytes.decode(encoding='ascii'),
        display_line2_bytes.decode(encoding='ascii'),
        flags)

# OFF Data was: bytearray(b'\x00\x00\x00\x00\x00')
# ON  Data was: bytearray(b'\x01\x01\x00\x00\x00')
def trigger_message_handler(message_type, data):
    assert message_type == MSGTYPE_TRIGGER_STATUS_STRING
    assert len(data) == 5
    return TriggerMessage(data)

def command_message_handler(message_type, data):
    return CommandMessage(message_type, data)

def decode_message(payload):
    if payload[0] != DEVICE_ID_RSP1570:
        raise RotelMessageError("Didn't get expected Device ID byte.  {} != {}".format(payload[0], DEVICE_ID_RSP1570))

    message_handlers = {
        MSGTYPE_FEEDBACK_STRING: feedback_message_handler,
        MSGTYPE_TRIGGER_STATUS_STRING: trigger_message_handler,
        MSGTYPE_PRIMARY_COMMANDS: command_message_handler,
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
    }
    message_type = payload[1]
    message_handler = message_handlers.get(message_type, None)
    if message_handler is None:
        raise RotelMessageError("Unknown message type byte {:X}".format(message_type))
    
    data = payload[2:]
    return message_handler(message_type, data)

class DecodeMessageIter:
    def __init__(self, ser):
        self.decoder = decode_protocol_stream(ser)

    def __aiter__(self):
        return self

    async def __anext__(self):
        payload = await self.decoder.__anext__()
        return decode_message(payload)

def decode_message_stream(ser):
    return DecodeMessageIter(ser)

# async def decode_message_stream(ser):
#     async for payload in decode_protocol_stream(ser):
#         yield decode_message(payload)