import asyncio
import aiounittest
from contextlib import asynccontextmanager
from rsp1570serial.connection import (
    SharedRotelAmpConn,
    RotelAmpConnConnectionError,
    create_shared_rotel_amp_conn,
    create_message_processor_client,
)
from rsp1570serial.emulator import (
    make_message_handler,
    create_device,
    INITIAL_SOURCE,
    INITIAL_VOLUME,
)
from serial import SerialException  # type: ignore[import-untyped]

TEST_PORT = 50050
TEST_URL = f"socket://:{TEST_PORT}"
BAD_TEST_PORT = TEST_PORT + 1


@asynccontextmanager
async def start_emulator(device, port=TEST_PORT):
    handle_messages = make_message_handler(device)
    async with await asyncio.start_server(handle_messages, port=port) as server:
        yield server
    await asyncio.sleep(0)


class AsyncTestConnection(aiounittest.AsyncTestCase):
    async def test_process_command1(self):
        import logging

        logging.basicConfig(level=logging.DEBUG)
        async with create_device(is_on=False) as device:
            async with start_emulator(device):
                self.assertEqual(device._is_on, False)
                async with create_message_processor_client(TEST_URL) as conn:
                    messages = await conn.process_command(
                        "POWER_ON", conn.POWER_ON_TIME_WINDOW
                    )
                    self.assertEqual(len(messages), 1)
                self.assertEqual(device._is_on, True)

    async def test_process_command2(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._is_muted, False)
                async with create_message_processor_client(TEST_URL) as conn:
                    await conn.process_command("MUTE_TOGGLE")
                self.assertEqual(device._is_muted, True)

    async def test_process_command3(self):
        aliases = {
            " CD": "CD ALIAS",
        }
        async with create_device(is_on=True, aliases=aliases) as device:
            async with start_emulator(device):
                self.assertEqual(device._source, INITIAL_SOURCE)
                async with create_message_processor_client(TEST_URL) as conn:
                    messages = await conn.process_command("SOURCE_CD")
                self.assertEqual(device._source, " CD")
                self.assertEqual(len(messages), 1)
                self.assertEqual(messages[0].lines[0], "CD ALIAS      VOL  50")

    async def test_send_command1(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._is_muted, False)
                async with create_message_processor_client(TEST_URL) as conn:
                    await conn.send_command("MUTE_TOGGLE")
                self.assertEqual(device._is_muted, True)

    async def test_send_command2(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._source, INITIAL_SOURCE)
                async with create_message_processor_client(TEST_URL) as conn:
                    await conn.send_command("SOURCE_TUNER")
                self.assertEqual(device._source, "TUNER")

    async def test_send_volume_direct_command1(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                self.assertEqual(device._volume, INITIAL_VOLUME)
                async with create_message_processor_client(TEST_URL) as conn:
                    await conn.send_volume_direct_command(1, 55)
                self.assertEqual(device._volume, 55)

    async def test_multi_clients1(self):
        async with create_device(is_on=True) as device:
            async with start_emulator(device):
                async with create_shared_rotel_amp_conn(TEST_URL) as shared_conn:
                    conn1 = shared_conn.new_client_conn()
                    conn2 = shared_conn.new_client_conn()
                    conn3 = shared_conn.new_client_conn()
                    await conn1.send_command("SOURCE_TUNER")
                    await conn1.send_command("SOURCE_CD")
                    await asyncio.sleep(0.2)
                    self.assertEqual(conn1.queue.qsize(), 2)
                    self.assertEqual(conn2.queue.qsize(), 2)
                    self.assertEqual(conn3.queue.qsize(), 2)
                    assert shared_conn._clients is not None
                    self.assertEqual(len(shared_conn._clients), 3)
                    conn2 = None
                    self.assertEqual(len(shared_conn._clients), 2)
                    await conn1.send_command("SOURCE_VIDEO_1")
                    await asyncio.sleep(0.2)
                    self.assertEqual(conn1.queue.qsize(), 3)
                    self.assertEqual(conn3.queue.qsize(), 3)

    async def test_connection_failure1(self):
        shared_conn = SharedRotelAmpConn(f"socket://:{BAD_TEST_PORT}")
        # Connection refused by host
        with self.assertRaises(RotelAmpConnConnectionError) as cm:
            await shared_conn.open()
        self.assertIsInstance(cm.exception.__cause__, SerialException)

    async def test_connection_failure2(self):
        shared_conn = SharedRotelAmpConn(f"socket://192.168.51.1:{TEST_PORT}")
        # Timed out due to made up IP address
        with self.assertRaises(RotelAmpConnConnectionError) as cm:
            await shared_conn.open()
        self.assertIsInstance(cm.exception.__cause__, SerialException)

    async def test_connection_failure3(self):
        shared_conn = SharedRotelAmpConn(f"socket://made_up_hostname:{TEST_PORT}")
        # getaddrinfo failed
        with self.assertRaises(RotelAmpConnConnectionError) as cm:
            await shared_conn.open()
        self.assertIsInstance(cm.exception.__cause__, SerialException)
