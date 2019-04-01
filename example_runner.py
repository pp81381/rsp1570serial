import asyncio
import logging
from rsp1570serial.connection import RotelAmpConn
from rsp1570serial.utils import get_platform_serial_port

async def main(loop, serial_port, subtask_builder):
    try:
        conn = RotelAmpConn(serial_port)
        await conn.open()
    except:
        logging.error("Could not open connection", exc_info=True)
    else:
        tasks = subtask_builder(conn)

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

        for pending_task in pending:
            pending_task.cancel()

        for done_task in done:
            try:
                await done_task
            except:
                logging.error("Unexpected exception thrown by subtask", exc_info=True)

        conn.close()

async def heartbeat():
    """
    Tells you that the loop is still running
    Also keeps the KeyboardInterrupt running on Windows until Python 3.8 comes along (https://bugs.python.org/issue23057)
    """
    try:
        count = 0
        while True:
            await asyncio.sleep(0.5)
            count += 1
            logging.info("Heartbeat number {}".format(count))
    except asyncio.CancelledError:
        logging.info("Heartbeat cancelled")

def example_runner(build_example_tasks):
    serial_port = get_platform_serial_port()
        
    loop = asyncio.get_event_loop()
    main_task = loop.create_task(main(loop, serial_port, build_example_tasks))
    #pylint: disable=unused-variable
    heartbeat_task = loop.create_task(heartbeat())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down due to keyboard interrupt")

    if main_task.done():
        logging.info("Main Task is done")
        exc = main_task.exception()
        if exc:
            logging.error("Main Task had an exception", exc_info=exc)

    pending = asyncio.Task.all_tasks(loop=loop)
    for pending_task in pending:
        pending_task.cancel()
    group = asyncio.gather(*pending, return_exceptions=True)
    loop.run_until_complete(group)
    loop.close()