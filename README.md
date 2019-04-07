# rsp1570serial

An asyncio based package to talk to a Rotel RSP-1570 processor using the RS-232 protocol

See [this document](http://www.rotel.com/sites/default/files/product/rs232/RSP1570%20Protocol.pdf) for the protocol definition

Known to work with a GANA USB to RS-233 DB9 cable on Windows 10 (Python 3.7.0) and on Rapbian Stretch (Python 3.5.3)

The protocol is similar to that used by other older Rotel kit.   For example, it looks as though the RSP-1572 used a protocol like this.  It has a different device id and supports a few more messages but this package could probably be updated to support it.

## Usage

The RotelAmpConn object encapsulates all of the functionality of the library:

```python
    try:
        conn = RotelAmpConn(serial_port)
        await conn.open()
    except:
        logging.error("Could not open connection", exc_info=True)
    else:
        # Do something here
        conn.close()
```

Send a command (see commands.py for the full list):

```python
    await conn.send_command('MUTE_TOGGLE')
```

Send a volume direct command to a zone:

```python
    zone = 1
    volume = 50
    await conn.send_volume_direct_command(zone, volume)
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

This library was built to support a rotel_rsp1570 media player platform entity for [Home Assistant](https://www.home-assistant.io/) that I will also make available shortly.