from unittest import TestCase

from rsp1570serial.icons import (
    flags_to_icons,
    icon_dict_to_flags,
    icon_list_to_flags,
    icons_that_are_on,
)


class TestIcons(TestCase):
    def test1(self):
        flags = b"\x00F\x08\x00\xfc"
        icon_dict = flags_to_icons(flags)
        self.assertDictEqual(
            icon_dict,
            {
                "A": False,
                "5": False,
                "4": False,
                "3": False,
                "2": False,
                "1": False,
                "Coaxial": False,
                "Optical": False,
                "x": False,
                "II": True,
                "HDMI": True,
                "EX": False,
                "ES": False,
                "dts": False,
                "Pro Logic": True,
                "Dolby Digital": False,
                "Display Mode0": False,
                "Display Mode1": False,
                "Zone 2": False,
                "Standby LED": True,
                "SB": False,
                "Zone 4": False,
                "Zone 3": False,
                "<": False,
                ">": False,
                "7.1": False,
                "5.1": False,
                "Zone": False,
                "CBL": False,
                "CBR": False,
                "SW": True,
                "SR": True,
                "SL": True,
                "FR": True,
                "C": True,
                "FL": True,
            },
        )
        icon_list = icons_that_are_on(icon_dict)
        self.assertCountEqual(
            icon_list,
            [
                "II",
                "HDMI",
                "Pro Logic",
                "Standby LED",
                "SW",
                "SR",
                "SL",
                "FR",
                "C",
                "FL",
            ],
        )
        flags_from_icon_dict = icon_dict_to_flags(icon_dict)
        self.assertEqual(flags, flags_from_icon_dict)
        flags_from_icon_list = icon_list_to_flags(icon_list)
        self.assertEqual(flags, flags_from_icon_list)

    def test2(self):
        flags = b"\x00\x00\x08\x00\x00"
        icon_list = icons_that_are_on(flags_to_icons(flags))
        self.assertCountEqual(icon_list, ["Standby LED"])
