# rsp1570serial

An asyncio based package to talk to a Rotel RSP-1570 processor using the RS-232 protocol

See [this document](http://www.rotel.com/sites/default/files/product/rs232/RSP1570%20Protocol.pdf) for the protocol definition

Known to work with a GANA USB to RS-232 DB9 cable on Windows 10 and on Rapbian Stretch

The protocol is similar to that used by other older Rotel kit.   For example, it looks as though the RSP-1572 used a protocol like this.  It has a different device id and supports a few more messages but this package could probably be updated to support it.

This library was built to support a rotel_rsp1570 media player platform entity for [Home Assistant](https://www.home-assistant.io/) that can be found [here](https://github.com/pp81381/hassdev).

# Usage

## Create a connnection

The connection objects encapsulate most of the functionality of the library.

It is recommended that the [SharedRotelAmpConn](#SharedRotelAmpConn) is used in preference to the basic [RotelAmpConn](#RotelAmpConn).  Either way, use the context manager factory methods to create a connection.  E.g.:

```python
    from rsp1570serial.connection import create_shared_rotel_amp_conn
    from rsp1570serial.utils import get_platform_serial_port

    async def do_something(serial_port=None):
        if serial_port is None:
            serial_port = get_platform_serial_port()

        async with create_shared_rotel_amp_conn(serial_port) as shared_conn:
            conn = shared_conn.new_client_conn()
            # Do something here
```

The serial_port parameter can be anything that can be passed to `serial.serial_for_url()`.  E.g.

* `/dev/ttyUSB0` (Linux)
* `COM3` (Windows)
* `socket://192.168.0.100:50000` (if you are using a TCP/IP to serial  converter)

## send_command(command_code)

Send a command (see `commands.py` for the full list):

```python
    await conn.send_command('MUTE_TOGGLE')
```

## send_volume_direct_command(zone, volume)

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

## read_messages()

Read the input stream from the device:

```python
    async for message in conn.read_messages():
        if (isinstance(message, (FeedbackMessage, TriggerMessage))):
            message.log()
        else:
            logging.warning("Unknown message type encountered")
```

## conn.process_command(command_code, time_window=DEFAULT_TIME_WINDOW)

Send a command and then collect all messages that arrive in `time_window`.  Class constants are provided with recommended time windows.   Note that the 'POWER_ON' command needs a longer time window than other commands.

```python
    async with create_test_shared_conn() as shared_conn:
        conn = shared_conn.new_client_conn()
        messages = await conn.process_command('POWER_ON', conn.POWER_ON_TIME_WINDOW)
```

This command can be handy for scripting-like automations.   See `discovery.py` for an example.

## Messages

The `conn.read_messages()` and `conn.process_command()` methods will return a message-type specific object containing the message data.  Two types of message can be encountered:

* [FeedbackMessage](#FeedbackMessage): Reflects what is shown on the front-panel display.   Received when the display changes.
* [TriggerMessage](#TriggerMessage): Received whenever the 12V triggers change state.

## Source Aliases

The user of a Rotel Amplifier can customise the name shown on the display for each source.   These 'aliases' are the names that will be found in the `source_name` field of the [FeedbackMessage](#FeedbackMessage) rather than the official source names.  For example, a user might configure the name of the 'VIDEO 1' source to be 'CATV'.  In this instance, the client software would need to know to send the 'SOURCE_VIDEO_1' `command_code` in order to select the source that the user knows as 'CATV'.

## discover_source_aliases(serial_port)

This is a utility function that can be used by Home Automation software to discover the aliases for all of the sources.   It returns a dictionary that maps each source alias to the `command_code` needed to switch to that source.   The discovery process is not quick so it is recommended to use this utility in the initial device configuration rather than each time the Home Automation software is started.

```python
        source_map = await discover_source_aliases(serial_port)
        self.assertDictEqual(source_map, {
            'CATV': 'SOURCE_VIDEO_1', 'NMT': 'SOURCE_VIDEO_2',
            'APPLE TV': 'SOURCE_VIDEO_3', 'FIRE TV': 'SOURCE_VIDEO_4',
            'BLU RAY': 'SOURCE_VIDEO_5', 'TUNER': 'SOURCE_TUNER',
            'TAPE': 'SOURCE_TAPE', 'MULTI': 'SOURCE_MULTI_INPUT',
            ' CD': 'SOURCE_CD'})
```

## Examples

Please see example1.py and example2.py and the test suite for fully working examples.

# Objects

## RotelAmpConn

The RotelAmpConn object is the basic connection object.   It can be used to establish a single, dedicated connection to the device, send commands and read responses.  Consider using [SharedRotelAmpConn](#SharedRotelAmpConn) in preference to this lower level object.

Use the `create_rotel_amp_conn` context manager as a factory:

```python
    from rsp1570serial.connection import create_rotel_amp_conn
    from rsp1570serial.utils import get_platform_serial_port

    async def do_something(serial_port=None):
        if serial_port is None:
            serial_port = get_platform_serial_port()

        async with create_rotel_amp_conn(serial_port) as conn:
            # Do something here
```

Method|Description
---|---
`create_rotel_amp_conn(serial_port)`| Context manager to create and open a connection
`conn.send_command(command_code)`| Send a command (see `commands.py` for the full list)
`conn.send_volume_direct_command(zone, volume)`| Set the absolute volume in a zone
`conn.read_messages()`| Iterator that reads the messages from the device.   See [read_messages](#read_messages) for more information.

## SharedRotelAmpConn

Wraps a [RotelAmpConn](#RotelAmpConn) object and allows it to be shared.

Use the `create_shared_rotel_amp_conn` context manager as a factory:

```python
    import asyncio
    from rsp1570serial.connection import create_shared_rotel_amp_conn
    from rsp1570serial.utils import get_platform_serial_port

    async def do_something(serial_port=None):
        if serial_port is None:
            serial_port = get_platform_serial_port()

        async with create_shared_rotel_amp_conn(serial_port) as shared_conn:
            logger_conn = shared_conn.new_client_conn()
            logger_task = asyncio.create_task(do_something_else(logger_conn)
            cmd_conn = shared_conn.new_client_conn()
            await cmd_conn.process_command('POWER_ON', conn.POWER_ON_TIME_WINDOW)
            await cmd_conn.process_command('SOURCE_VIDEO_1')
            await cmd_conn.process_command('VOLUME_UP')
            await logger_task

    async def log_all_messages(conn):
        async for message in conn.read_messages():
            message.log()
        
```

Method|Description
---|---
`create_shared_rotel_amp_conn(serial_port)`| Context manager to create and open a shared connection
`shared_conn.new_client_conn()`| Create a new client connection of type [SharedRotelAmpClientConn](#SharedRotelAmpClientConn)

## SharedRotelAmpClientConn

A client connection.   Supports sending commands and receiving messages.  Also supports a mechanism to send a command and collect all of the messages received in a time window, which can be useful for script-like automation of the amplifier.

If the client code is not consuming messages from the connection then they will be queued up internally until one of the message consuming methods is called.  Two client connections of the same shared connection are completely independent and can be read at different speeds without back pressure.

When finished with the object, simply dereference it and it will be garbage collected.

Method|Description
---|---
`conn.send_command(command_code)`| Send a command (see `commands.py` for the full list)
`conn.send_volume_direct_command(zone, volume)`| Set the absolute volume in a zone
`conn.read_messages()`| Iterator that reads the messages from the device.   See [read_messages](#read_messages) for more information.
`conn.collect_messages()`| Collect all internally queued messages (emptying the queue)
`conn.process_command(command_code, time_window=DEFAULT_TIME_WINDOW)`| Send a command and then collect all messages that arrive in `time_window`.   See constants below for recommended time windows.



Constant|Description
---|---
`conn.POWER_ON_TIME_WINDOW`| Recommended `time_window` to be used after a 'POWER_ON' command
`conn.DEFAULT_TIME_WINDOW`| Recommended `time_window` to be used after most commands


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
The package also includes an RSP-1570 emulator that can be used for demonstration or testing purposes.   It can also be used in Home Assistant with the rotel_rsp1570 media player platform.

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
