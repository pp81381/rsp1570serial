from dataclasses import dataclass
from typing import Dict, List

from rsp1570serial.rsp1570_messages import RSP1570_MESSAGES
from rsp1570serial.rsp1572_messages import RSP1572_MESSAGES


@dataclass
class RotelSourceMeta:
    """
    Source meta data comprising standard name and command code
    Note that the source names may be aliased in the device
    The names that come back from the device in a feedback
    message are the aliases
    """

    standard_name: str
    command_code: str


INITIAL_VOLUME = 50
INITIAL_SOURCE = "VIDEO 1"

RSP1570_DEVICE_ID = 0xA3
RSP1570_MIN_VOLUME = 0x00
RSP1570_MAX_VOLUME = 0x60

RSP1572_DEVICE_ID = 0xA5
RSP1572_MIN_VOLUME = 0x00
RSP1572_MAX_VOLUME = 0x64

RSP1570_SOURCES = [
    RotelSourceMeta(" CD", "SOURCE_CD"),
    RotelSourceMeta("TUNER", "SOURCE_TUNER"),
    RotelSourceMeta("TAPE", "SOURCE_TAPE"),
    RotelSourceMeta("VIDEO 1", "SOURCE_VIDEO_1"),
    RotelSourceMeta("VIDEO 2", "SOURCE_VIDEO_2"),
    RotelSourceMeta("VIDEO 3", "SOURCE_VIDEO_3"),
    RotelSourceMeta("VIDEO 4", "SOURCE_VIDEO_4"),
    RotelSourceMeta("VIDEO 5", "SOURCE_VIDEO_5"),
    RotelSourceMeta("MULTI", "SOURCE_MULTI_INPUT"),
]
RSP1572_SOURCES = [
    RotelSourceMeta(" CD", "SOURCE_CD"),
    RotelSourceMeta("TUNER", "SOURCE_TUNER"),
    RotelSourceMeta("VIDEO 1", "SOURCE_VIDEO_1"),
    RotelSourceMeta("VIDEO 2", "SOURCE_VIDEO_2"),
    RotelSourceMeta("VIDEO 3", "SOURCE_VIDEO_3"),
    RotelSourceMeta("VIDEO 4", "SOURCE_VIDEO_4"),
    RotelSourceMeta("VIDEO 5", "SOURCE_VIDEO_5"),
    RotelSourceMeta("VIDEO 6", "SOURCE_VIDEO_6"),
    RotelSourceMeta("iPod/USB", "SOURCE_IPOD_USB"),  # TODO: Verify
    RotelSourceMeta("MULTI", "SOURCE_MULTI_INPUT"),
]


@dataclass
class RotelModelMeta:
    name: str
    device_id: int
    messages: Dict[str, List[int]]
    min_volume: int
    max_volume: int
    initial_volume: int
    sources: List[RotelSourceMeta]
    initial_source: str

    def index_command_messages(self) -> Dict[bytes, str]:
        command_code_lookup = {}
        for code, value in self.messages.items():
            command_code_lookup[bytes(value)] = code
        return command_code_lookup


RSP1570_META = RotelModelMeta(
    "rsp1570",
    RSP1570_DEVICE_ID,
    RSP1570_MESSAGES,
    RSP1570_MIN_VOLUME,
    RSP1570_MAX_VOLUME,
    INITIAL_VOLUME,
    RSP1570_SOURCES,
    INITIAL_SOURCE,
)
RSP1572_META = RotelModelMeta(
    "rsp1572",
    RSP1572_DEVICE_ID,
    RSP1572_MESSAGES,
    RSP1570_MIN_VOLUME,
    RSP1570_MAX_VOLUME,
    INITIAL_VOLUME,
    RSP1572_SOURCES,
    INITIAL_SOURCE,
)


ROTEL_MODELS = {
    "rsp1570": RSP1570_META,
    "rsp1572": RSP1572_META,
}
