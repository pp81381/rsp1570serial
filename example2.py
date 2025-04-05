import asyncio
import logging

from example_runner import (
    example_wrapper,
    process_example_args,
    run_and_log_task,
    run_command_n_times,
    send_command_and_log,
    send_volume_direct_command_and_log,
)
from rsp1570serial.connection import RotelAmpConn, create_rotel_amp_conn
from rsp1570serial.rotel_model_meta import ROTEL_MODELS


async def run_power_toggle(conn: RotelAmpConn) -> None:
    await asyncio.sleep(0.1)
    await send_command_and_log(conn, "POWER_TOGGLE")
    await asyncio.sleep(3)


async def run_misc_commands(conn: RotelAmpConn) -> None:
    await asyncio.sleep(3)
    await send_command_and_log(conn, "DISPLAY_REFRESH")
    await asyncio.sleep(0.5)
    await send_command_and_log(conn, "RECORD_FUNCTION_SELECT")
    await asyncio.sleep(0.5)
    await send_command_and_log(conn, "TONE_CONTROL_SELECT")
    await asyncio.sleep(0.5)
    await send_command_and_log(conn, "TREBLE_UP")
    await asyncio.sleep(0.5)
    await send_command_and_log(conn, "RECORD_FUNCTION_SELECT")
    await asyncio.sleep(0.5)
    await send_command_and_log(conn, "TONE_CONTROL_SELECT")
    await asyncio.sleep(0.5)
    await send_command_and_log(conn, "TREBLE_DOWN")
    await asyncio.sleep(3)


async def run_mute_commands(conn: RotelAmpConn) -> None:
    await asyncio.sleep(3)
    await send_command_and_log(conn, "POWER_ON")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "DISPLAY_REFRESH")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "MUTE_TOGGLE")
    await asyncio.sleep(3)
    await send_volume_direct_command_and_log(conn, 1, 60)  # Will unmute
    await asyncio.sleep(3)
    await send_command_and_log(conn, "MUTE_TOGGLE")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "POWER_ON")  # Will unmute
    await asyncio.sleep(3)
    await send_command_and_log(conn, "POWER_ON")  # Will do nothing
    await asyncio.sleep(3)
    await send_command_and_log(conn, "POWER_OFF")
    await asyncio.sleep(3)


async def probe_rsp1572(conn: RotelAmpConn) -> None:
    await asyncio.sleep(3)
    await send_command_and_log(conn, "POWER_ON")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "DISPLAY_REFRESH")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "SOURCE_IPOD_USB")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "DISPLAY_REFRESH")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "PLAY")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "DISPLAY_REFRESH")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "PAUSE")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "DISPLAY_REFRESH")
    await asyncio.sleep(3)
    await send_command_and_log(conn, "POWER_OFF")
    await asyncio.sleep(3)


async def run_multi_mute(conn: RotelAmpConn) -> None:
    await run_command_n_times(conn, "MUTE_TOGGLE", 3.0, 4)


async def main():
    EXAMPLES = {
        "toggle": run_power_toggle,
        "misc": run_misc_commands,  # Power should be on
        "mute": run_mute_commands,  # Power should be off
        "multi_mute": run_multi_mute,  # Power should be on
        "probe_rsp1572": probe_rsp1572,  # Power should be off, model should be rsp1572
    }
    args = process_example_args(list(EXAMPLES.keys()))
    async with create_rotel_amp_conn(
        args.serial_port,
        ROTEL_MODELS[args.model],
    ) as conn:
        task = asyncio.create_task(
            example_wrapper(args.example, EXAMPLES[args.example], conn)
        )
        await run_and_log_task(task, conn, args.log_payload)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s:%(message)s",
    )
    asyncio.run(main())
