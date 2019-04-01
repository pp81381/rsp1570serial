#   rsp1570serial

An asyncio based package to talk to a Rotel RSP-1570 processor using the RS-232 protocol

See [this document](http://www.rotel.com/sites/default/files/product/rs232/RSP1570%20Protocol.pdf) for the protocol definition

Known to work with a GANA USB to RS-233 DB9 cable on Windows 10 (Python 3.7.0) and on Rapbian Stretch (Python 3.5.3)

The protocol is similar to that used by other older Rotel kit.   For example, it looks as though the RSP-1572 used a protocol like this.  It has a different device id and supports a few more messages but this package could probably be updated to support it.