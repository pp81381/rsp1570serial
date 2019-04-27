# rsp1570serial

An asyncio based package to talk to a Rotel RSP-1570 processor using the RS-232 protocol

See [this document](http://www.rotel.com/sites/default/files/product/rs232/RSP1570%20Protocol.pdf) for the protocol definition

Known to work with a GANA USB to RS-232 DB9 cable on Windows 10 (Python 3.7.0) and on Rapbian Stretch (Python 3.5.3)

The protocol is similar to that used by other older Rotel kit.   For example, it looks as though the RSP-1572 used a protocol like this.  It has a different device id and supports a few more messages but this package could probably be updated to support it.

This library was built to support a rotel_rsp1570 media player platform entity for [Home Assistant](https://www.home-assistant.io/) that can be found [here](https://github.com/pp81381/hassdev).

# Usage

The RotelAmpConn object encapsulates all of the functionality of the library:

```python
    from rsp1570serial.connection import RotelAmpConn

    try:
        conn = RotelAmpConn(serial_port)
        await conn.open()
    except:
        logging.error("Could not open connection", exc_info=True)
    else:
        # Do something here
        conn.close()
```

The serial_port parameter can be anything that can be passed to `serial.serial_for_url()`.  E.g.

* `/dev/ttyUSB0` (Linux)
* `COM3` (Windows)
* `socket://192.168.0.100:50000` (if you are using a TCP/IP to serial  converter)

Send a command (see `commands.py` for the full list):

```python
    await conn.send_command('MUTE_TOGGLE')
```

Send a volume direct command to a zone:

```python
    from rsp1570serial.commands import MIN_VOLUME, MAX_VOLUME

    zone = 1
    await conn.send_volume_direct_command(zone, MAX_VOLUME)
    await asyncio.sleep(1)
    await conn.send_volume_direct_command(zone, MIN_VOLUME)
    await asyncio.sleep(1)
    await conn.send_volume_direct_command(zone, 50)
```

Read the input stream from the device:

```python
    async for message in conn.read_messages():
        if (isinstance(message, (FeedbackMessage, TriggerMessage))):
            message.log()
        else:
            logging.warning("Unknown message type encountered")
```

Please see example1.py and example2.py for fully working examples.

The `conn.read_messages()` will return a message-type specific object containing the message data.  Two types of message can be encountered:

* `FeedbackMessage`: Reflects what is shown on the front-panel display.   Received when the display changes.
* `TriggerMessage`: Received whenever the 12V triggers change state.

## FeedbackMessage

This message reflects what is shown on the display of the device and will be recieved whenever the display changes.   This would typically be after an RS-232 or InfraRed command has been received or after a front panel button has been pressed.

The object has 3 properties:

Property|Type|Description
--------|----|-----------
`msg.lines`|two element list|The two lines of the display
`msg.flags`|bytes|Flags representing the state of the icons on the display
`msg.icons`|dict of str:bool|A dictionary keyed on icon code reflecting the on/off state of each icon

Methods of interest are:

Method|Description
---|---
`msg.icons_that_are_on()`|Returns a list of the icon codes of any display icons that are on.   Primarily used for testing and debugging.
`msg.parse_display_lines()`|   Parse the display lines and return as much as we can infer about the state of the amp in a dict.

The following table shows the contents of the dict returned by the `parse_display_lines()` method.

Key|Description
---|---
`is_on`| On flag (bool)
`source_name`| Source Name (max. 8 characters)
`volume`| Volume (int)
`mute_on`|Mute On Flag (bool),
`party_mode_on`| Party Mode Flag (bool)
`info`| Display Line 2

The following table shows all of the icon codes.

Code|Name|Category|Friendly Name
---|---|---|---
 `A`|`rsp1570_input_analog`|`input_icons`| Analog
 `5`|`rsp1570_input_5`|`input_icons`| Input 5
 `4`|`rsp1570_input_4`|`input_icons`| Input 4
 `3`|`rsp1570_input_3`|`input_icons`| Input 3
 `2`|`rsp1570_input_2`|`input_icons`| Input 2
 `1`|`rsp1570_input_1`|`input_icons`| Input 1
 `Coaxial`|`rsp1570_input_coaxial`|`input_icons`| Coaxial
 `Optical`|`rsp1570_input_optical`|`input_icons`| Optical
 `HDMI`|`rsp1570_input_hdmi`|`input_icons`| HDMI
 `Pro Logic`|`rsp1570_sound_mode_pro_logic`|`sound_mode_icons`| Pro Logic
 `II`|`rsp1570_sound_mode_ii`|`sound_mode_icons`| II
 `x`|`rsp1570_sound_mode_x`|`sound_mode_icons`| x
 `Dolby Digital`|`rsp1570_sound_mode_dolby_digital`|`sound_mode_icons`| Dolby Digital
 `EX`|`rsp1570_sound_mode_ex`|`sound_mode_icons`| EX
 `dts`|`rsp1570_sound_mode_dts`|`sound_mode_icons`| dts
 `ES`|`rsp1570_sound_mode_es`|`sound_mode_icons`| ES
 `7.1`|`rsp1570_sound_mode_71`|`sound_mode_icons`|7.1
 `5.1`|`rsp1570_sound_mode_51`|`sound_mode_icons`|5.1
 `Display Mode0`|`rsp1570_state_display_mode0`|`state_icons`| Display Mode 0
 `Display Mode1`|`rsp1570_state_display_mode1`|`state_icons`| Display Mode 1
 `Standby LED`|`rsp1570_state_standby_led`|`state_icons`| Standby LED
 `Zone 2`|`rsp1570_state_zone2`|`state_icons`| Zone 2
 `Zone 3`|`rsp1570_state_zone3`|`state_icons`| Zone 3
 `Zone 4`|`rsp1570_state_zone4`|`state_icons`| Zone 4
 `Zone`|`rsp1570_state_zone`|`state_icons`| Zone
 `FR`|`rsp1570_speaker_front_right`|`speaker_icons`| Front Right
 `C`|`rsp1570_speaker_center`|`speaker_icons`| Center
 `FL`|`rsp1570_speaker_front_left`|`speaker_icons`| Front Left
 `SW`|`rsp1570_speaker_subwoofer`|`speaker_icons`| Subwoofer
 `SR`|`rsp1570_speaker_surround_right`|`speaker_icons`| Surround Right
 `SL`|`rsp1570_speaker_surround_left`|`speaker_icons`| Surround Left
 `CBL`|`rsp1570_speaker_center_back_left`|`speaker_icons`| Center Back Left
 `CBR`|`rsp1570_speaker_center_back_right`|`speaker_icons`| Center Back Right
 `SB`|`rsp1570_speaker_center_back`|`speaker_icons`| Center Back
 `<`|`rsp1570_misc_lt`|`misc_icons`| Misc <
 `>`|`rsp1570_misc_gt`|`misc_icons`| Misc >

## TriggerMessage

This object has one property called `flags` of type `bytes` that reflects the state of the 12V triggers by zone.

The method `flags_to_list()` returns a list of the following form:

```python
[
    ['All', ['on', 'off', 'off', 'off', 'off', 'off']],
    ['Main', ['on', 'off', 'off', 'off', 'off', 'off']],
    ['Zone 2', ['off', 'off', 'off', 'off', 'off', 'off']],
    ['Zone 3', ['off', 'off', 'off', 'off', 'off', 'off']],
    ['Zone 4', ['off', 'off', 'off', 'off', 'off', 'off']],
]
```

# Emulator
The package also includes an RSP-1570 emulator that can be used for demonstration or testing purposes.

Examples of usage:

```
# Start the emulator on port 50000
python3 -m rsp1570serial.emulator

# Start the emulator on port 50002
python3 -m rsp1570serial.emulator -p 50002

# Start the emulator on port 50002 and provide aliases for some of the sources
python3 -m rsp1570serial.emulator -p 50002 --alias_video_1  CATV --alias_video_2 NMT --alias_video_3 "APPLE TV" --alias_video_4 "FIRE TV" --alias_video_5 "BLU RAY"

# Start the emulator in the on state
python3 -m rsp1570serial.emulator --is_on
```

Full list of options:

Option|Description
--|--
`-p <num>` or `--port <num>`|Port number
`-o` or `--is_on`|If set then the emulator will be turned on initially
`--cd <str>` or `--alias_cd <str>`|Alias for the CD source
`--tape <str>` or `--alias_tape <str>`|Alias for the TAPE source
`--tuner <str>` or `--alias_tuner <str>`|Alias for the TUNER source
`--video_1 <str>` or `--alias_video_1 <str>`|Alias for the VIDEO 1 source
`--video_2 <str>` or `--alias_video_2 <str>`|Alias for the VIDEO 2 source
`--video_3 <str>` or `--alias_video_3 <str>`|Alias for the VIDEO 3 source
`--video_4 <str>` or `--alias_video_4 <str>`|Alias for the VIDEO 4 source
`--video_5 <str>` or `--alias_video_5 <str>`|Alias for the VIDEO 5 source
`--multi <str>` or `--alias_multi <str>`|Alias for the MULTI source

The emulator can be used in Home Assistant with the rotel_rsp1570 media player platform.   Example configuration:

```yaml
media_player:
- platform: rotel_rsp1570
  name: "Rotel RSP-1570 emulator"
  device: socket://192.168.2.119:50002
  source_aliases:
    VIDEO 1: CATV
    VIDEO 2: NMT
    VIDEO 3: APPLE TV
    VIDEO 4: FIRE TV
    VIDEO 5: BLU RAY
```