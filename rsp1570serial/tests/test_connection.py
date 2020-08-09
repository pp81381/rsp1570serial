import asyncio
import aiounittest
from contextlib import asynccontextmanager
from rsp1570serial.connection import SharedRotelAmpConn
from rsp1570serial.emulator import (
    make_message_handler,
    create_device,
    INITIAL_SOURCE,
    INITIAL_VOLUME,
)

TEST_PORT = 50050


@asynccontextmanager
async def start_emulator(device, port=TEST_PORT):
    handle_messages = make_message_handler(device)
    async with await asyncio.start_server(handle_messages, port=port) as server:
        yield server


@asynccontextmanager
async def create_test_shared_conn():
    try:
        shared_conn = SharedRotelAmpConn(f"socket://:{TEST_PORT}")
        await shared_conn.open()
        yield shared_conn
    finally:
        # Yield to the loop to ensure that the device.handle_client_disconnection
        # call happens before the connection is closed
        # This ensures that the handler doesn't throw if the Blinker
        # is still generating messages
        # This also helps with tests that just send a command and then don't process
        # any messages
        # TODO: how to catch the exception that is raised in handle_messages if I don't do this
        await asyncio.sleep(0.2)
        await shared_conn.close()


class AsyncTestConnection(aiounittest.AsyncTestCase):
    async def test_process_command1(self):
        async with create_device(is_on=False) as device:
            async with start_emulator(device):
                self.assertEqual(device._is_on, False)
                async with create_test_shared_conn() as shared_conn:
                    conn = shared_conn.new_client_conn()
                    messages = await conn.process_command(
                        "POWER_ON", conn.POWER_ON_TIME_WINDOW
                    )
                    self.assertEqual(len(messages), 1)
                self.assertEqual(device._is_on, True)

    async def test_process_command2(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._is_muted, False)
                async with create_test_shared_conn() as shared_conn:
                    conn = shared_conn.new_client_conn()
                    await conn.process_command("MUTE_TOGGLE")
                self.assertEqual(device._is_muted, True)

    async def test_process_command3(self):
        aliases = {
            " CD": "CD ALIAS",
        }
        async with create_device(is_on=True, aliases=aliases) as device:
            async with start_emulator(device):
                self.assertEqual(device._source, INITIAL_SOURCE)
                async with create_test_shared_conn() as shared_conn:
                    conn = shared_conn.new_client_conn()
                    messages = await conn.process_command("SOURCE_CD")
                self.assertEqual(device._source, " CD")
                self.assertEqual(len(messages), 1)
                self.assertEqual(messages[0].lines[0], "CD ALIAS      VOL  50")

    async def test_send_command1(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._is_muted, False)
                async with create_test_shared_conn() as shared_conn:
                    conn = shared_conn.new_client_conn()
                    await conn.send_command("MUTE_TOGGLE")
                self.assertEqual(device._is_muted, True)

    async def test_send_command2(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._source, INITIAL_SOURCE)
                async with create_test_shared_conn() as shared_conn:
                    conn = shared_conn.new_client_conn()
                    await conn.send_command("SOURCE_TUNER")
                self.assertEqual(device._source, "TUNER")

    async def test_send_volume_direct_command1(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._volume, INITIAL_VOLUME)
                async with create_test_shared_conn() as shared_conn:
                    conn = shared_conn.new_client_conn()
                    await conn.send_volume_direct_command(1, 55)
                self.assertEqual(device._volume, 55)

    async def test_multi_clients1(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                async with create_test_shared_conn() as shared_conn:
                    conn1 = shared_conn.new_client_conn()
                    conn2 = shared_conn.new_client_conn()
                    conn3 = shared_conn.new_client_conn()
                    await conn1.send_command("SOURCE_TUNER")
                    await conn1.send_command("SOURCE_CD")
                    await asyncio.sleep(0.2)
                    self.assertEqual(conn1.queue.qsize(), 2)
                    self.assertEqual(conn2.queue.qsize(), 2)
                    self.assertEqual(conn3.queue.qsize(), 2)
                    self.assertEqual(len(shared_conn.clients), 3)
                    conn2 = None
                    self.assertEqual(len(shared_conn.clients), 2)
                    await conn1.send_command("SOURCE_VIDEO_1")
                    await asyncio.sleep(0.2)
                    self.assertEqual(conn1.queue.qsize(), 3)
                    self.assertEqual(conn3.queue.qsize(), 3)

