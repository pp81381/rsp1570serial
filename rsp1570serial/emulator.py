import argparse
import asyncio
from contextlib import asynccontextmanager
from functools import wraps
import logging
from rsp1570serial.commands import messages
from rsp1570serial.icons import icon_list_to_flags
from rsp1570serial.messages import (
    decode_message_stream,
    CommandMessage,
    DEVICE_ID_RSP1570,
    MSGTYPE_FEEDBACK_STRING,
    MSGTYPE_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS,
)
from rsp1570serial.protocol import encode_payload

MIN_VOLUME = 0
MAX_VOLUME = 96
INITIAL_VOLUME = 50
INITIAL_SOURCE = "VIDEO 1"

VOLUME_DIRECT_MESSAGE_TYPES = set(
    [
        MSGTYPE_VOLUME_DIRECT_COMMANDS,
        MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS,
        MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS,
        MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS,
    ]
)


class SourceAttribs:
    def __init__(self, info, icon_list, alias_args, argparse_dest):
        self.info = info
        self.icon_list = icon_list
        self.alias_args = alias_args
        self.argparse_dest = argparse_dest


# A set of realistic looking attributes to apply when each source is selected
SOURCE_ATTRIB_MAP = {
    " CD": SourceAttribs(
        "STEREO          44.1K",
        ["A", "Standby LED", "SW", "FR", "FL"],
        ["--cd", "--alias_cd"],
        "alias_cd",
    ),
    "TUNER": SourceAttribs(
        "STEREO          44.1K",
        ["A", "Standby LED", "SW", "FR", "FL"],
        ["--tuner", "--alias_tuner"],
        "alias_tuner",
    ),
    "TAPE": SourceAttribs(
        "STEREO          44.1K",
        ["A", "Standby LED", "SW", "FR", "FL"],
        ["--tape", "--alias_tape"],
        "alias_tape",
    ),
    "VIDEO 1": SourceAttribs(
        "DOLBY PL\x19 C     48K  ",
        ["II", "HDMI", "Pro Logic", "Standby LED", "SW", "SR", "SL", "FR", "C", "FL"],
        ["--video_1", "--alias_video_1"],
        "alias_video_1",
    ),
    "VIDEO 2": SourceAttribs(
        "DOLBY PL\x19 M     48K  ",
        ["II", "HDMI", "Pro Logic", "Standby LED", "SW", "SR", "SL", "FR", "C", "FL"],
        ["--video_2", "--alias_video_2"],
        "alias_video_2",
    ),
    "VIDEO 3": SourceAttribs(
        "DOLBY DIGITAL   48K  ",
        [
            "HDMI",
            "Optical",
            "1",
            "Dolby Digital",
            "Standby LED",
            "SW",
            "SR",
            "SL",
            "FR",
            "C",
            "FL",
        ],
        ["--video_3", "--alias_video_3"],
        "alias_video_3",
    ),
    "VIDEO 4": SourceAttribs(
        "5CH STEREO      48K  ",
        ["A", "Standby LED", "SW", "SR", "SL", "FR", "C", "FL"],
        ["--video_4", "--alias_video_4"],
        "alias_video_4",
    ),
    "VIDEO 5": SourceAttribs(
        "PCM 2CH         48K  ",
        ["A", "Standby LED", "SW", "FR", "FL"],
        ["--video_5", "--alias_video_5"],
        "alias_video_5",
    ),
    "MULTI": SourceAttribs(
        "BYPASS          48K  ",
        ["Standby LED", "CBL", "CBR", "SW", "SR", "SL", "FR", "C", "FL"],
        ["--multi", "--alias_multi"],
        "alias_multi",
    ),
}


class Blinker:
    def __init__(self, func):
        self._func = func
        self._blink_task = None

    def start(self):
        self._blink_task = asyncio.create_task(self.blinker())

    async def stop(self):
        if self._blink_task is not None:
            self._blink_task.cancel()
            await self._blink_task
            self._blink_task = None

    async def blinker(self):
        try:
            logging.info("Blinker started")
            while True:
                await asyncio.sleep(0.5)
                await self._func()
        except asyncio.CancelledError:
            logging.info("Blinker stopped")


def only_if_on(f):
    @wraps(f)
    async def wrapper(*args, **kwds):
        if not args[0]._is_on:
            return
        return await f(*args, **kwds)

    return wrapper


class RotelRSP1570Emulator:
    def __init__(self, aliases=None, is_on=False):
        self._writer = None
        self._aliases = {} if aliases is None else aliases
        self._is_on = is_on
        self._is_muted = False
        self._mute_blink_count = 0
        self._blinker = Blinker(self.mute_blink)
        self._is_party_mode = False
        self._volume = INITIAL_VOLUME
        self._source = INITIAL_SOURCE

    @only_if_on
    async def turn_off(self):
        self._is_on = False
        await self._blinker.stop()
        await self.write_feedback_message()

    async def turn_on(self):
        if self._is_on:
            if self._is_muted:
                await self._mute_off_no_feedback()
                await self.write_feedback_message()
        else:
            self._is_on = True
            self._volume = INITIAL_VOLUME
            await asyncio.sleep(1.5)
            await self._mute_off_no_feedback()
            await self.write_feedback_message()

    async def toggle(self):
        if self._is_on:
            await self.turn_off()
        else:
            await self.turn_on()

    @only_if_on
    async def set_volume(self, level):
        if self._is_muted:
            await self._mute_off_no_feedback()
        if level < MIN_VOLUME or level > MAX_VOLUME:
            return
        self._volume = level
        await self.write_feedback_message()

    @only_if_on
    async def volume_up(self):
        await self.set_volume(self._volume + 1)

    @only_if_on
    async def volume_down(self):
        await self.set_volume(self._volume - 1)

    @only_if_on
    async def set_party_mode(self, flag):
        self._is_party_mode = flag
        await self.write_feedback_message()

    async def mute_blink(self):
        self._mute_blink_count += 1
        await self.write_feedback_message()

    @only_if_on
    async def mute_on(self):
        if self._is_muted:
            return
        self._is_muted = True
        self._mute_blink_count = 0  # Must be set before feedback message is generated
        await self.write_feedback_message()
        self._blinker.start()

    @only_if_on
    async def mute_off(self):
        if not self._is_muted:
            return
        await self._mute_off_no_feedback()
        await self.write_feedback_message()

    async def _mute_off_no_feedback(self):
        self._is_muted = False
        await self._blinker.stop()

    @only_if_on
    async def mute_toggle(self):
        if self._is_muted:
            await self.mute_off()
        else:
            await self.mute_on()

    @only_if_on
    async def set_source(self, source):
        if source not in SOURCE_ATTRIB_MAP:
            return
        self._source = source
        await self.write_feedback_message()

    @only_if_on
    async def display_refresh(self):
        await self.write_feedback_message()

    @property
    def info(self):
        if self._is_on:
            return SOURCE_ATTRIB_MAP[self._source].info
        return "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    @property
    def icon_list(self):
        if self._is_on:
            return SOURCE_ATTRIB_MAP[self._source].icon_list
        return ["Standby LED"]

    @property
    def formatted_volume(self):
        """
        Returns formatted volume.
        Doesn't check whether the amplifier is off.
        """
        if self._is_muted:
            if self._mute_blink_count % 2 == 0:
                return "MUTE ON"
            else:
                return "       "
        return "VOL  {:02d}".format(self._volume)

    @property
    def display_line_1(self):
        if self._is_on:
            return "{:8.8s}  {:3.3s} {:7.7s}".format(
                self._aliases.get(self._source, self._source),
                "pty" if self._is_party_mode else "",
                self.formatted_volume,
            )
        return "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

    def encode_feedback_message(self):
        payload = bytearray([DEVICE_ID_RSP1570, MSGTYPE_FEEDBACK_STRING])
        payload.extend(self.display_line_1.encode())
        payload.extend(self.info.encode())
        payload.extend(icon_list_to_flags(self.icon_list))
        return encode_payload(payload)

    def handle_client_connection(self, writer):
        self._writer = writer
        logging.info("New client connected")

    def handle_client_disconnection(self):
        self._writer = None
        logging.info("Client disconnected")

    async def write_feedback_message(self):
        if self._writer is None:
            logging.info("Write feedback message called but no client connected")
        else:
            msg = self.encode_feedback_message()
            self._writer.write(msg)
            await self._writer.drain()
            logging.info("Feedback message written: %r", msg)


def index_command_messages():
    command_code_lookup = {}
    for code, value in messages.items():
        command_code_lookup[bytes(value)] = code
    return command_code_lookup


class CommandHandler:
    def __init__(self, device):
        self._command_code_lookup = index_command_messages()
        self._device = device

    async def handle_command_stream(self, reader):
        async for message in decode_message_stream(reader):
            if isinstance(message, CommandMessage):
                await self.handle_command(message)
            else:
                logging.warning("Unknown message type encountered")

    async def handle_command(self, command):
        if command.message_type in VOLUME_DIRECT_MESSAGE_TYPES:
            await self.apply_volume_direct_command(command)
        else:
            await self.apply_simple_command(command)

    async def apply_volume_direct_command(self, command):
        if command.message_type == MSGTYPE_VOLUME_DIRECT_COMMANDS:
            logging.info(
                "Processing volume direct command.  Setting Volume to %d",
                command.key[0],
            )
            await self._device.set_volume(command.key[0])
        else:
            logging.info(
                "Unsupported volume direct command: '%r', Key: '%r' ignored",
                command.message_type,
                command.key,
            )

    async def apply_simple_command(self, command):
        command_code = self._command_code_lookup.get(
            bytes((command.message_type, command.key[0])), None
        )
        logging.info(
            "Message Type: '%r', Key: '%r', Code: '%s'",
            command.message_type,
            command.key,
            command_code,
        )
        await self.apply_simple_command_code(command_code)

    async def apply_simple_command_code(self, command_code):
        if command_code == "POWER_TOGGLE":
            await self._device.toggle()
        elif command_code == "POWER_ON":
            await self._device.turn_on()
        elif command_code == "POWER_OFF":
            await self._device.turn_off()
        elif command_code == "VOLUME_UP":
            await self._device.volume_up()
        elif command_code == "VOLUME_DOWN":
            await self._device.volume_down()
        elif command_code == "MUTE_TOGGLE":
            await self._device.mute_toggle()
        elif command_code == "SOURCE_CD":
            await self._device.set_source(" CD")
        elif command_code == "SOURCE_TUNER":
            await self._device.set_source("TUNER")
        elif command_code == "SOURCE_TAPE":
            await self._device.set_source("TAPE")
        elif command_code == "SOURCE_VIDEO_1":
            await self._device.set_source("VIDEO 1")
        elif command_code == "SOURCE_VIDEO_2":
            await self._device.set_source("VIDEO 2")
        elif command_code == "SOURCE_VIDEO_3":
            await self._device.set_source("VIDEO 3")
        elif command_code == "SOURCE_VIDEO_4":
            await self._device.set_source("VIDEO 4")
        elif command_code == "SOURCE_VIDEO_5":
            await self._device.set_source("VIDEO 5")
        elif command_code == "SOURCE_MULTI_INPUT":
            await self._device.set_source("MULTI")
        elif command_code == "DISPLAY_REFRESH":
            await self._device.display_refresh()
        else:
            logging.info("Unsupported command code '%s' ignored", command_code)


async def heartbeat():
    """
    Tells you that the loop is still running
    Also keeps the KeyboardInterrupt running on Windows until
    Python 3.8 comes along (https://bugs.python.org/issue23057)
    """
    try:
        count = 0
        while True:
            await asyncio.sleep(2)
            count += 1
            logging.info("Heartbeat number {}".format(count))
    except asyncio.CancelledError:
        logging.info("Heartbeat cancelled")


def make_message_handler(device):
    async def handle_messages(reader, writer):
        device.handle_client_connection(writer)
        command_handler = CommandHandler(device)
        await command_handler.handle_command_stream(reader)
        device.handle_client_disconnection()

    return handle_messages


@asynccontextmanager
async def create_device(*args, **kwargs):
    device = RotelRSP1570Emulator(*args, **kwargs)
    try:
        yield device
    finally:
        await device._blinker.stop()


async def run_server(port, aliases, is_on):
    # pylint: disable=unused-variable
    heartbeat_task = asyncio.create_task(heartbeat())

    async with create_device(aliases, is_on) as device:
        handle_messages = make_message_handler(device)
        async with await asyncio.start_server(handle_messages, port=port) as server:
            for s in server.sockets:
                print("Serving on {}".format(s.getsockname()))
            try:
                await server.serve_forever()
            except asyncio.CancelledError:
                logging.info("Emulator task cancelled")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port", type=int, default=50001, help="port to serve on"
    )
    parser.add_argument(
        "-o", "--is_on", action="store_true", help="emulator starts up in the on state"
    )
    for name, attribs in SOURCE_ATTRIB_MAP.items():
        parser.add_argument(
            *attribs.alias_args,
            type=str,
            dest=attribs.argparse_dest,
            help="alias for '{}' input".format(name)
        )
    args = parser.parse_args()

    aliases = {}
    for name, attribs in SOURCE_ATTRIB_MAP.items():
        alias = getattr(args, attribs.argparse_dest, None)
        if alias is not None:
            aliases[name] = alias
            logging.info("Source '%s' aliased to '%s'", name, alias)

    asyncio.run(run_server(args.port, aliases, args.is_on))
