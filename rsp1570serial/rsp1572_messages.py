"""
RSP1572 command definitions
"""

from rsp1570serial.message_types import (
    MSGTYPE_MAIN_ZONE_COMMANDS,
    MSGTYPE_PRIMARY_COMMANDS,
    MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
    MSGTYPE_RECORD_SOURCE_COMMANDS,
    MSGTYPE_TRIGGER_DIRECT_COMMANDS,
    MSGTYPE_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_2_COMMANDS,
    MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_3_COMMANDS,
    MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS,
    MSGTYPE_ZONE_4_COMMANDS,
    MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS,
)

# [message_type, key] pairs
RSP1572_MESSAGES = {
    "POWER_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x0A],
    "POWER_OFF": [MSGTYPE_PRIMARY_COMMANDS, 0x4A],
    "POWER_ON": [MSGTYPE_PRIMARY_COMMANDS, 0x4B],
    "VOLUME_UP": [MSGTYPE_PRIMARY_COMMANDS, 0x0B],
    "VOLUME_DOWN": [MSGTYPE_PRIMARY_COMMANDS, 0x0C],
    "MUTE_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x1E],
    "POWER_OFF_ALL_ZONES": [MSGTYPE_PRIMARY_COMMANDS, 0x71],
    "SOURCE_CD": [MSGTYPE_PRIMARY_COMMANDS, 0x02],
    "SOURCE_TUNER": [MSGTYPE_PRIMARY_COMMANDS, 0x03],
    "SOURCE_VIDEO_1": [MSGTYPE_PRIMARY_COMMANDS, 0x05],
    "SOURCE_VIDEO_2": [MSGTYPE_PRIMARY_COMMANDS, 0x06],
    "SOURCE_VIDEO_3": [MSGTYPE_PRIMARY_COMMANDS, 0x07],
    "SOURCE_VIDEO_4": [MSGTYPE_PRIMARY_COMMANDS, 0x08],
    "SOURCE_VIDEO_5": [MSGTYPE_PRIMARY_COMMANDS, 0x09],
    "SOURCE_VIDEO_6": [MSGTYPE_PRIMARY_COMMANDS, 0x94],
    "SOURCE_IPOD_USB": [MSGTYPE_PRIMARY_COMMANDS, 0x8E],
    "SOURCE_MULTI_INPUT": [MSGTYPE_PRIMARY_COMMANDS, 0x15],
    "STEREO___BYPASS_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x11],
    "DOLBY_3_STEREO": [MSGTYPE_PRIMARY_COMMANDS, 0x12],
    "DOLBY_PLIIX_MODE_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x13],
    "DOLBY_PLIIX_MODE_MUSIC_CINEMA_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0xA2],
    "DSP_MODE_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x14],
    "DOLBY_3_STEREO___PLIIX_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x53],
    "DTS_NEO_6_MUSIC_CINEMA_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x54],
    "DSP_1": [MSGTYPE_PRIMARY_COMMANDS, 0x57],
    "DSP_2": [MSGTYPE_PRIMARY_COMMANDS, 0x58],
    "DSP_3": [MSGTYPE_PRIMARY_COMMANDS, 0x59],
    "DSP_4": [MSGTYPE_PRIMARY_COMMANDS, 0x5A],
    "5_CHANNEL_STEREO": [MSGTYPE_PRIMARY_COMMANDS, 0x5B],
    "7_CHANNEL_STEREO": [MSGTYPE_PRIMARY_COMMANDS, 0x5C],
    "DOLBY_PLIIX_CINEMA": [MSGTYPE_PRIMARY_COMMANDS, 0x5D],
    "DOLBY_PLIIX_MUSIC": [MSGTYPE_PRIMARY_COMMANDS, 0x5E],
    "DOLBY_PLIIX_GAME": [MSGTYPE_PRIMARY_COMMANDS, 0x74],
    "DOLBY_PRO_LOGIC": [MSGTYPE_PRIMARY_COMMANDS, 0x5F],
    "DOLBY_PLIIZ": [MSGTYPE_PRIMARY_COMMANDS, 0x92],
    "DTS_NEO_6_MUSIC": [MSGTYPE_PRIMARY_COMMANDS, 0x60],
    "DTS_NEO_6_CINEMA": [MSGTYPE_PRIMARY_COMMANDS, 0x61],
    "PLII_PANORAMA_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x62],
    "PLII_DIMENSION_UP": [MSGTYPE_PRIMARY_COMMANDS, 0x63],
    "PLII_DIMENSION_DOWN": [MSGTYPE_PRIMARY_COMMANDS, 0x64],
    "PLII_CENTER_WIDTH_UP": [MSGTYPE_PRIMARY_COMMANDS, 0x65],
    "PLII_CENTER_WIDTH_DOWN": [MSGTYPE_PRIMARY_COMMANDS, 0x66],
    "DOLBY_DIGITAL_EX_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x68],
    "NEXT_SURROUND_MODE": [MSGTYPE_PRIMARY_COMMANDS, 0x22],
    "OSD_MENU": [MSGTYPE_PRIMARY_COMMANDS, 0x18],
    "ENTER": [MSGTYPE_PRIMARY_COMMANDS, 0x19],
    "EXIT": [MSGTYPE_PRIMARY_COMMANDS, 0x90],
    "CURSOR_RIGHT_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x1A],
    "CURSOR_RIGHT_KEY_RELEASED": [
        MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
        0x1A,
    ],
    "CURSOR_LEFT_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x1B],
    "CURSOR_LEFT_KEY_RELEASED": [
        MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
        0x1B,
    ],
    "CURSOR_UP_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x1C],
    "CURSOR_UP_KEY_RELEASED": [MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS, 0x1C],
    "CURSOR_DOWN_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x1D],
    "CURSOR_DOWN_KEY_RELEASED": [
        MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
        0x1D,
    ],
    "NUMBER_KEY_1": [MSGTYPE_PRIMARY_COMMANDS, 0x2A],
    "NUMBER_KEY_2": [MSGTYPE_PRIMARY_COMMANDS, 0x2B],
    "NUMBER_KEY_3": [MSGTYPE_PRIMARY_COMMANDS, 0x2C],
    "NUMBER_KEY_4": [MSGTYPE_PRIMARY_COMMANDS, 0x2D],
    "NUMBER_KEY_5": [MSGTYPE_PRIMARY_COMMANDS, 0x2E],
    "NUMBER_KEY_6": [MSGTYPE_PRIMARY_COMMANDS, 0x2F],
    "NUMBER_KEY_7": [MSGTYPE_PRIMARY_COMMANDS, 0x30],
    "NUMBER_KEY_8": [MSGTYPE_PRIMARY_COMMANDS, 0x31],
    "NUMBER_KEY_9": [MSGTYPE_PRIMARY_COMMANDS, 0x32],
    "NUMBER_KEY_0": [MSGTYPE_PRIMARY_COMMANDS, 0x33],
    "PLAY": [MSGTYPE_PRIMARY_COMMANDS, 0x85],
    "PAUSE": [MSGTYPE_PRIMARY_COMMANDS, 0x86],
    "STOP_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x87],
    "STOP_KEY_RELEASED": [MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS, 0x87],
    "TRACK_FORWARD_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x88],
    "TRACK_FORWARD_KEY_RELEASED": [
        MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
        0x88,
    ],
    "TRACK_BACK_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x89],
    "TRACK_BACK_KEY_RELEASED": [MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS, 0x89],
    "SCAN_FORWARD_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x8A],
    "SCAN_FORWARD_KEY_RELEASED": [
        MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS,
        0x8A,
    ],
    "SCAN_BACK_KEY_PRESSED": [MSGTYPE_PRIMARY_COMMANDS, 0x8B],
    "SCAN_BACK_KEY_RELEASED": [MSGTYPE_PRIMARY_KEY_RELEASED_COMMANDS, 0x8B],
    "SHUFFLE": [MSGTYPE_PRIMARY_COMMANDS, 0x8F],
    "REPEAT": [MSGTYPE_PRIMARY_COMMANDS, 0x8C],
    "RECORD_FUNCTION_SELECT": [MSGTYPE_PRIMARY_COMMANDS, 0x17],
    "DYNAMIC_RANGE": [MSGTYPE_PRIMARY_COMMANDS, 0x16],
    "DIGITAL_INPUT_SELECT": [MSGTYPE_PRIMARY_COMMANDS, 0x1F],
    "ZONE_2___MAIN": [MSGTYPE_PRIMARY_COMMANDS, 0x23],
    "TEMPORARY_CENTER_TRIM": [MSGTYPE_PRIMARY_COMMANDS, 0x4C],
    "TEMPORARY_SUBWOOFER_TRIM": [MSGTYPE_PRIMARY_COMMANDS, 0x4D],
    "TEMPORARY_SURROUND_TRIM": [MSGTYPE_PRIMARY_COMMANDS, 0x4E],
    "CINEMA_EQ_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x4F],
    "FRONT_DISPLAY_ON_OFF": [MSGTYPE_PRIMARY_COMMANDS, 0x52],
    "DISPLAY_REFRESH": [MSGTYPE_PRIMARY_COMMANDS, 0xFF],
    "PARTY_MODE_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x6E],
    "OUTPUT_RESOLUTION": [MSGTYPE_PRIMARY_COMMANDS, 0x75],
    "HDMI_AMP_MODE": [MSGTYPE_PRIMARY_COMMANDS, 0x78],
    "HDMI_TV_MODE": [MSGTYPE_PRIMARY_COMMANDS, 0x79],
    "TEMPORARY_ROOM_EQ_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0x67],
    "DISPLAY": [MSGTYPE_PRIMARY_COMMANDS, 0x91],
    "SPEAKER_LEVEL_SETTING_TOGGLE": [MSGTYPE_PRIMARY_COMMANDS, 0xA1],
    "FORCE_FACTORY_DEFAULT": [MSGTYPE_PRIMARY_COMMANDS, 0x93],
    "MAIN_ZONE_POWER_TOGGLE": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x0A],
    "MAIN_ZONE_POWER_OFF": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x4A],
    "MAIN_ZONE_POWER_ON": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x4B],
    "MAIN_ZONE_VOLUME_UP": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x00],
    "MAIN_ZONE_VOLUME_DOWN": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x01],
    "MAIN_ZONE_MUTE_TOGGLE": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x1E],
    "MAIN_ZONE_MUTE_ON": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x6C],
    "MAIN_ZONE_MUTE_OFF": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x6D],
    "MAIN_ZONE_POWER_OFF_ALL_ZONES": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x71],
    "MAIN_ZONE_SOURCE_CD": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x02],
    "MAIN_ZONE_SOURCE_TUNER": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x03],
    "MAIN_ZONE_SOURCE_VIDEO_1": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x05],
    "MAIN_ZONE_SOURCE_VIDEO_2": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x06],
    "MAIN_ZONE_SOURCE_VIDEO_3": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x07],
    "MAIN_ZONE_SOURCE_VIDEO_4": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x08],
    "MAIN_ZONE_SOURCE_VIDEO_5": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x09],
    "MAIN_ZONE_SOURCE_VIDEO_6": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x94],
    "MAIN_ZONE_SOURCE_IPOD_USB": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x8E],
    "MAIN_ZONE_SOURCE_MULTI_INPUT": [MSGTYPE_MAIN_ZONE_COMMANDS, 0x15],
    "RECORD_SOURCE_CD": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x02],
    "RECORD_SOURCE_TUNER": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x03],
    "RECORD_SOURCE_VIDEO_1": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x05],
    "RECORD_SOURCE_VIDEO_2": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x06],
    "RECORD_SOURCE_VIDEO_3": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x07],
    "RECORD_SOURCE_VIDEO_4": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x08],
    "RECORD_SOURCE_VIDEO_5": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x09],
    "RECORD_SOURCE_VIDEO_6": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x94],
    "RECORD_SOURCE_IPOD_USB": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x8E],
    "RECORD_FOLLOW_MAIN_ZONE_SOURCE": [MSGTYPE_RECORD_SOURCE_COMMANDS, 0x6B],
    "ZONE_2_POWER_TOGGLE": [MSGTYPE_ZONE_2_COMMANDS, 0x0A],
    "ZONE_2_POWER_OFF": [MSGTYPE_ZONE_2_COMMANDS, 0x4A],
    "ZONE_2_POWER_ON": [MSGTYPE_ZONE_2_COMMANDS, 0x4B],
    "ZONE_2_VOLUME_UP": [MSGTYPE_ZONE_2_COMMANDS, 0x00],
    "ZONE_2_VOLUME_DOWN": [MSGTYPE_ZONE_2_COMMANDS, 0x01],
    "ZONE_2_MUTE_TOGGLE": [MSGTYPE_ZONE_2_COMMANDS, 0x1E],
    "ZONE_2_MUTE_ON": [MSGTYPE_ZONE_2_COMMANDS, 0x6C],
    "ZONE_2_MUTE_OFF": [MSGTYPE_ZONE_2_COMMANDS, 0x6D],
    "ZONE_2_POWER_OFF_ALL_ZONES": [MSGTYPE_ZONE_2_COMMANDS, 0x71],
    "ZONE_2_SOURCE_CD": [MSGTYPE_ZONE_2_COMMANDS, 0x02],
    "ZONE_2_SOURCE_TUNER": [MSGTYPE_ZONE_2_COMMANDS, 0x03],
    "ZONE_2_SOURCE_VIDEO_1": [MSGTYPE_ZONE_2_COMMANDS, 0x05],
    "ZONE_2_SOURCE_VIDEO_2": [MSGTYPE_ZONE_2_COMMANDS, 0x06],
    "ZONE_2_SOURCE_VIDEO_3": [MSGTYPE_ZONE_2_COMMANDS, 0x07],
    "ZONE_2_SOURCE_VIDEO_4": [MSGTYPE_ZONE_2_COMMANDS, 0x08],
    "ZONE_2_SOURCE_VIDEO_5": [MSGTYPE_ZONE_2_COMMANDS, 0x09],
    "ZONE_2_SOURCE_VIDEO_6": [MSGTYPE_ZONE_2_COMMANDS, 0x94],
    "ZONE_2_SOURCE_IPOD_USB": [MSGTYPE_ZONE_2_COMMANDS, 0x8E],
    "ZONE_2_FOLLOW_MAIN_ZONE_SOURCE": [MSGTYPE_ZONE_2_COMMANDS, 0x6B],
    "ZONE_2_PARTY_MODE_TOGGLE": [MSGTYPE_ZONE_2_COMMANDS, 0x6E],
    "ZONE_3_POWER_TOGGLE": [MSGTYPE_ZONE_3_COMMANDS, 0x0A],
    "ZONE_3_POWER_OFF": [MSGTYPE_ZONE_3_COMMANDS, 0x4A],
    "ZONE_3_POWER_ON": [MSGTYPE_ZONE_3_COMMANDS, 0x4B],
    "ZONE_3_VOLUME_UP": [MSGTYPE_ZONE_3_COMMANDS, 0x00],
    "ZONE_3_VOLUME_DOWN": [MSGTYPE_ZONE_3_COMMANDS, 0x01],
    "ZONE_3_MUTE_TOGGLE": [MSGTYPE_ZONE_3_COMMANDS, 0x1E],
    "ZONE_3_MUTE_ON": [MSGTYPE_ZONE_3_COMMANDS, 0x6C],
    "ZONE_3_MUTE_OFF": [MSGTYPE_ZONE_3_COMMANDS, 0x6D],
    "ZONE_3_POWER_OFF_ALL_ZONES": [MSGTYPE_ZONE_3_COMMANDS, 0x71],
    "ZONE_3_SOURCE_CD": [MSGTYPE_ZONE_3_COMMANDS, 0x02],
    "ZONE_3_SOURCE_TUNER": [MSGTYPE_ZONE_3_COMMANDS, 0x03],
    "ZONE_3_SOURCE_VIDEO_1": [MSGTYPE_ZONE_3_COMMANDS, 0x05],
    "ZONE_3_SOURCE_VIDEO_2": [MSGTYPE_ZONE_3_COMMANDS, 0x06],
    "ZONE_3_SOURCE_VIDEO_3": [MSGTYPE_ZONE_3_COMMANDS, 0x07],
    "ZONE_3_SOURCE_VIDEO_4": [MSGTYPE_ZONE_3_COMMANDS, 0x08],
    "ZONE_3_SOURCE_VIDEO_5": [MSGTYPE_ZONE_3_COMMANDS, 0x09],
    "ZONE_3_SOURCE_VIDEO_6": [MSGTYPE_ZONE_3_COMMANDS, 0x94],
    "ZONE_3_SOURCE_IPOD_USB": [MSGTYPE_ZONE_3_COMMANDS, 0x8E],
    "ZONE_3_FOLLOW_MAIN_ZONE_SOURCE": [MSGTYPE_ZONE_3_COMMANDS, 0x6B],
    "ZONE_3_PARTY_MODE_TOGGLE": [MSGTYPE_ZONE_3_COMMANDS, 0x6E],
    "ZONE_4_POWER_TOGGLE": [MSGTYPE_ZONE_4_COMMANDS, 0x0A],
    "ZONE_4_POWER_OFF": [MSGTYPE_ZONE_4_COMMANDS, 0x4A],
    "ZONE_4_POWER_ON": [MSGTYPE_ZONE_4_COMMANDS, 0x4B],
    "ZONE_4_VOLUME_UP": [MSGTYPE_ZONE_4_COMMANDS, 0x00],
    "ZONE_4_VOLUME_DOWN": [MSGTYPE_ZONE_4_COMMANDS, 0x01],
    "ZONE_4_MUTE_TOGGLE": [MSGTYPE_ZONE_4_COMMANDS, 0x1E],
    "ZONE_4_MUTE_ON": [MSGTYPE_ZONE_4_COMMANDS, 0x6C],
    "ZONE_4_MUTE_OFF": [MSGTYPE_ZONE_4_COMMANDS, 0x6D],
    "ZONE_4_POWER_OFF_ALL_ZONES": [MSGTYPE_ZONE_4_COMMANDS, 0x71],
    "ZONE_4_SOURCE_CD": [MSGTYPE_ZONE_4_COMMANDS, 0x02],
    "ZONE_4_SOURCE_TUNER": [MSGTYPE_ZONE_4_COMMANDS, 0x03],
    "ZONE_4_SOURCE_VIDEO_1": [MSGTYPE_ZONE_4_COMMANDS, 0x05],
    "ZONE_4_SOURCE_VIDEO_2": [MSGTYPE_ZONE_4_COMMANDS, 0x06],
    "ZONE_4_SOURCE_VIDEO_3": [MSGTYPE_ZONE_4_COMMANDS, 0x07],
    "ZONE_4_SOURCE_VIDEO_4": [MSGTYPE_ZONE_4_COMMANDS, 0x08],
    "ZONE_4_SOURCE_VIDEO_5": [MSGTYPE_ZONE_4_COMMANDS, 0x09],
    "ZONE_4_SOURCE_VIDEO_6": [MSGTYPE_ZONE_4_COMMANDS, 0x94],
    "ZONE_4_SOURCE_IPOD_USB": [MSGTYPE_ZONE_4_COMMANDS, 0x8E],
    "ZONE_4_FOLLOW_MAIN_ZONE_SOURCE": [MSGTYPE_ZONE_4_COMMANDS, 0x6B],
    "ZONE_4_PARTY_MODE_TOGGLE": [MSGTYPE_ZONE_4_COMMANDS, 0x6E],
    "VOLUME_MIN": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x00],
    "VOLUME_1": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x01],
    "VOLUME_2": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x02],
    "VOLUME_3": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x03],
    "VOLUME_4": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x04],
    "VOLUME_5": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x05],
    "VOLUME_6": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x06],
    "VOLUME_7": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x07],
    "VOLUME_8": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x08],
    "VOLUME_9": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x09],
    "VOLUME_10": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x0A],
    "VOLUME_16": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x10],
    "VOLUME_32": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x20],
    "VOLUME_38": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x26],
    "VOLUME_48": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x30],
    "VOLUME_64": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x40],
    "VOLUME_80": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x50],
    "VOLUME_95": [MSGTYPE_VOLUME_DIRECT_COMMANDS, 0x5F],
    "ZONE_2_VOLUME_MIN": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x00],
    "ZONE_2_VOLUME_1": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x01],
    "ZONE_2_VOLUME_2": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x02],
    "ZONE_2_VOLUME_3": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x03],
    "ZONE_2_VOLUME_4": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x04],
    "ZONE_2_VOLUME_5": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x05],
    "ZONE_2_VOLUME_6": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x06],
    "ZONE_2_VOLUME_16": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x10],
    "ZONE_2_VOLUME_36": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x24],
    "ZONE_2_VOLUME_48": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x30],
    "ZONE_2_VOLUME_64": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x40],
    "ZONE_2_VOLUME_80": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x50],
    "ZONE_2_VOLUME_95": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x5F],
    "ZONE_2_VOLUME_MAX": [MSGTYPE_ZONE_2_VOLUME_DIRECT_COMMANDS, 0x64],
    "ZONE_3_VOLUME_MIN": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x00],
    "ZONE_3_VOLUME_1": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x01],
    "ZONE_3_VOLUME_2": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x02],
    "ZONE_3_VOLUME_3": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x03],
    "ZONE_3_VOLUME_4": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x04],
    "ZONE_3_VOLUME_5": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x05],
    "ZONE_3_VOLUME_6": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x06],
    "ZONE_3_VOLUME_16": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x10],
    "ZONE_3_VOLUME_34": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x22],
    "ZONE_3_VOLUME_48": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x30],
    "ZONE_3_VOLUME_64": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x40],
    "ZONE_3_VOLUME_80": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x50],
    "ZONE_3_VOLUME_95": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x5F],
    "ZONE_3_VOLUME_MAX": [MSGTYPE_ZONE_3_VOLUME_DIRECT_COMMANDS, 0x64],
    "ZONE_4_VOLUME_MIN": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x00],
    "ZONE_4_VOLUME_1": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x01],
    "ZONE_4_VOLUME_2": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x02],
    "ZONE_4_VOLUME_3": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x03],
    "ZONE_4_VOLUME_4": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x04],
    "ZONE_4_VOLUME_5": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x05],
    "ZONE_4_VOLUME_6": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x06],
    "ZONE_4_VOLUME_16": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x10],
    "ZONE_4_VOLUME_34": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x22],
    "ZONE_4_VOLUME_48": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x30],
    "ZONE_4_VOLUME_64": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x40],
    "ZONE_4_VOLUME_80": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x50],
    "ZONE_4_VOLUME_95": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x5F],
    "ZONE_4_VOLUME_MAX": [MSGTYPE_ZONE_4_VOLUME_DIRECT_COMMANDS, 0x64],
    "MAIN_ZONE_12V_TRIGGER_1_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x00],
    "MAIN_ZONE_12V_TRIGGER_2_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x01],
    "MAIN_ZONE_12V_TRIGGER_3_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x02],
    "MAIN_ZONE_12V_TRIGGER_4_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x03],
    "MAIN_ZONE_12V_TRIGGER_5_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x04],
    "MAIN_ZONE_12V_TRIGGER_6_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x05],
    "ZONE_2_12V_TRIGGER_1_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x06],
    "ZONE_2_12V_TRIGGER_2_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x07],
    "ZONE_2_12V_TRIGGER_3_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x08],
    "ZONE_2_12V_TRIGGER_4_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x09],
    "ZONE_2_12V_TRIGGER_5_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x0A],
    "ZONE_2_12V_TRIGGER_6_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x0B],
    "ZONE_3_12V_TRIGGER_1_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x0C],
    "ZONE_3_12V_TRIGGER_2_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x0D],
    "ZONE_3_12V_TRIGGER_3_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x0E],
    "ZONE_3_12V_TRIGGER_4_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x0F],
    "ZONE_3_12V_TRIGGER_5_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x10],
    "ZONE_3_12V_TRIGGER_6_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x11],
    "ZONE_4_12V_TRIGGER_1_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x12],
    "ZONE_4_12V_TRIGGER_2_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x13],
    "ZONE_4_12V_TRIGGER_3_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x14],
    "ZONE_4_12V_TRIGGER_4_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x15],
    "ZONE_4_12V_TRIGGER_5_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x16],
    "ZONE_4_12V_TRIGGER_6_TOGGLE": [MSGTYPE_TRIGGER_DIRECT_COMMANDS, 0x17],
}
