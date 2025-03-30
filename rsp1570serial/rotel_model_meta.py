from dataclasses import dataclass
from typing import List

from rsp1570serial.messages import MessageCodec
from rsp1570serial.rsp1570_meta import RSP1570_CODEC
from rsp1570serial.rsp1572_meta import RSP1572_CODEC


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


ROTEL_RSP1570_SOURCES = [
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

ROTEL_RSP1572_SOURCES = [
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
    codec: MessageCodec
    sources: List[RotelSourceMeta]


RSP1570_META = RotelModelMeta("rsp1570", RSP1570_CODEC, ROTEL_RSP1570_SOURCES)
RSP1572_META = RotelModelMeta("rsp1572", RSP1572_CODEC, ROTEL_RSP1572_SOURCES)


ROTEL_MODELS = {
    "rsp1570": RSP1570_META,
    "rsp1572": RSP1572_META,
}
