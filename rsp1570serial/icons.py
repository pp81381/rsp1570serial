"""
Module that contains all icon definitions
and icon/flag mappings
Not much of this is used yet but it may be handy in future
"""


class DisplayIconDefinition:
    def __init__(self, name, category, friendly_name, icon, flag_index, flag):
        self.name = name
        self.category = category
        self.friendly_name = friendly_name
        self.icon = icon
        self.flag_index = flag_index
        self.flag = flag


DISPLAY_ICON_DEFINITIONS = [
    DisplayIconDefinition(
        "rsp1570_input_analog", "input_icons", "Analog", "A", 0, 0x01
    ),
    DisplayIconDefinition("rsp1570_input_5", "input_icons", "Input 5", "5", 0, 0x02),
    DisplayIconDefinition("rsp1570_input_4", "input_icons", "Input 4", "4", 0, 0x04),
    DisplayIconDefinition("rsp1570_input_3", "input_icons", "Input 3", "3", 0, 0x08),
    DisplayIconDefinition("rsp1570_input_2", "input_icons", "Input 2", "2", 0, 0x10),
    DisplayIconDefinition("rsp1570_input_1", "input_icons", "Input 1", "1", 0, 0x20),
    DisplayIconDefinition(
        "rsp1570_input_coaxial", "input_icons", "Coaxial", "Coaxial", 0, 0x40
    ),
    DisplayIconDefinition(
        "rsp1570_input_optical", "input_icons", "Optical", "Optical", 0, 0x80
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_x", "sound_mode_icons", "x", "x", 1, 0x01
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_ii", "sound_mode_icons", "II", "II", 1, 0x02
    ),
    DisplayIconDefinition("rsp1570_input_hdmi", "input_icons", "HDMI", "HDMI", 1, 0x04),
    DisplayIconDefinition(
        "rsp1570_sound_mode_ex", "sound_mode_icons", "EX", "EX", 1, 0x08
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_es", "sound_mode_icons", "ES", "ES", 1, 0x10
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_dts", "sound_mode_icons", "dts", "dts", 1, 0x20
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_pro_logic",
        "sound_mode_icons",
        "Pro Logic",
        "Pro Logic",
        1,
        0x40,
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_dolby_digital",
        "sound_mode_icons",
        "Dolby Digital",
        "Dolby Digital",
        1,
        0x80,
    ),
    DisplayIconDefinition(
        "rsp1570_state_display_mode0",
        "state_icons",
        "Display Mode 0",
        "Display Mode0",
        2,
        0x01,
    ),
    DisplayIconDefinition(
        "rsp1570_state_display_mode1",
        "state_icons",
        "Display Mode 1",
        "Display Mode1",
        2,
        0x02,
    ),
    DisplayIconDefinition(
        "rsp1570_state_zone2", "state_icons", "Zone 2", "Zone 2", 2, 0x04
    ),
    DisplayIconDefinition(
        "rsp1570_state_standby_led",
        "state_icons",
        "Standby LED",
        "Standby LED",
        2,
        0x08,
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_center_back", "speaker_icons", "Center Back", "SB", 3, 0x01
    ),
    DisplayIconDefinition(
        "rsp1570_state_zone4", "state_icons", "Zone 4", "Zone 4", 3, 0x02
    ),
    DisplayIconDefinition(
        "rsp1570_state_zone3", "state_icons", "Zone 3", "Zone 3", 3, 0x04
    ),
    DisplayIconDefinition("rsp1570_misc_lt", "misc_icons", "Misc <", "<", 3, 0x08),
    DisplayIconDefinition("rsp1570_misc_gt", "misc_icons", "Misc >", ">", 3, 0x10),
    DisplayIconDefinition(
        "rsp1570_sound_mode_71", "sound_mode_icons", "7.1", "7.1", 3, 0x20
    ),
    DisplayIconDefinition(
        "rsp1570_sound_mode_51", "sound_mode_icons", "5.1", "5.1", 3, 0x40
    ),
    DisplayIconDefinition("rsp1570_state_zone", "state_icons", "Zone", "Zone", 3, 0x80),
    DisplayIconDefinition(
        "rsp1570_speaker_center_back_left",
        "speaker_icons",
        "Center Back Left",
        "CBL",
        4,
        0x01,
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_center_back_right",
        "speaker_icons",
        "Center Back Right",
        "CBR",
        4,
        0x02,
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_subwoofer", "speaker_icons", "Subwoofer", "SW", 4, 0x04
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_surround_right",
        "speaker_icons",
        "Surround Right",
        "SR",
        4,
        0x08,
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_surround_left", "speaker_icons", "Surround Left", "SL", 4, 0x10
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_front_right", "speaker_icons", "Front Right", "FR", 4, 0x20
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_center", "speaker_icons", "Center", "C", 4, 0x40
    ),
    DisplayIconDefinition(
        "rsp1570_speaker_front_left", "speaker_icons", "Front Left", "FL", 4, 0x80
    ),
]

DISPLAY_ICON_DEFINITIONS_BY_ICON = {d.icon: d for d in DISPLAY_ICON_DEFINITIONS}

# DISPLAY_ICON_DEFINITIONS_BY_NAME = {d.name: d for d in DISPLAY_ICON_DEFINITIONS}


def flags_to_icons(flags):
    icons = {}
    for d in DISPLAY_ICON_DEFINITIONS:
        icons[d.icon] = bool(flags[d.flag_index] & d.flag)
    return icons


def icon_list_to_flags(icon_list):
    flags = bytearray([0x00] * 5)
    for i in icon_list:
        d = DISPLAY_ICON_DEFINITIONS_BY_ICON[i]
        flags[d.flag_index] |= d.flag
    return flags


def icon_dict_to_flags(icon_dict):
    return icon_list_to_flags([i for i, v in icon_dict.items() if v])


def icons_that_are_on(icon_dict):
    # TODO: Consistent order
    return [i for (i, v) in icon_dict.items() if v]

