import logging
from typing import Dict

from .connection import RotelAmpConn
from .messages import FeedbackMessage
from .process_command import process_command

_LOGGER = logging.getLogger(__name__)


class RotelAmpSourceDiscoveryError(Exception):
    pass


def get_newest_feedback_message(messages):
    # Note that it is common for there to be multiple feedback messages after
    # a command is sent:
    # - changing the source might trigger a change in sound mode
    # - the display flashes when mute is on
    # Given the latency of a serial line it is possible for messages to overlap
    # command time windows so older messages could relate to the previous command
    # The most recent message is usually safe to use
    feedback_messages = [m for m in messages if isinstance(m, FeedbackMessage)]
    if len(feedback_messages) == 0:
        raise RotelAmpSourceDiscoveryError("No feedback messages received")
    return feedback_messages[-1]


def get_source_name_from_messages(messages):
    feedback_message = get_newest_feedback_message(messages)
    return feedback_message.parse_display_lines()["source_name"]


def get_mute_on_from_messages(messages):
    feedback_message = get_newest_feedback_message(messages)
    return feedback_message.parse_display_lines()["mute_on"]


async def discover_source_aliases(conn: RotelAmpConn) -> Dict[str, str]:
    """
    Discover the alias configured for each input

    Cycle through the device sources and get the alias from the feedback message
    Restore the original source (which we can only do once we know its alias)

    Note that:
    - the device will be powered on and off if it is initially off
    - the device will be muted during the discovery process
    """

    # If no messages are received then the Amp is probably off
    messages = await process_command(conn, "DISPLAY_REFRESH")
    was_probably_off = len(messages) == 0
    _LOGGER.info(f"was_probably_off: '{was_probably_off}'")

    if was_probably_off:
        # Note that:
        # - If the power is already on then there is no Feedback message
        # - If the power is off then it is a few seconds before the messages come through
        # - POWER_ON has the side effect of un-muting
        _LOGGER.info("Power appears to be off so trying to turn on")
        messages = await process_command(conn, "POWER_ON")

    orig_source_alias = get_source_name_from_messages(messages)
    _LOGGER.info(f"orig_source_alias: '{orig_source_alias}'")

    orig_mute_on = get_mute_on_from_messages(messages)
    _LOGGER.info(f"orig_mute_on: '{orig_mute_on}'")
    if not orig_mute_on:
        _LOGGER.info("Muting to avoid loud surprises")
        await process_command(conn, "MUTE_TOGGLE")

    source_map = {}
    for source_meta in conn.meta.sources:
        messages = await process_command(conn, source_meta.command_code)
        source_alias = get_source_name_from_messages(messages)
        _LOGGER.info(f"Alias for '{source_meta.standard_name}': '{source_alias}'")
        source_map[source_alias] = source_meta.command_code

    messages = await process_command(conn, source_map[orig_source_alias])
    final_source_alias = get_source_name_from_messages(messages)
    _LOGGER.info(f"Final source alias: '{final_source_alias}'")

    if final_source_alias != orig_source_alias:
        _LOGGER.warning(
            "%s was not set back to the original source after alias discovery",
            conn.meta.name,
        )

    if was_probably_off:
        _LOGGER.info(
            "Power appeared to be off initially so turning back off before we finish"
        )
        await process_command(conn, "POWER_OFF")
    elif not orig_mute_on:
        _LOGGER.info("Unmuting")
        await process_command(conn, "MUTE_TOGGLE")

    return source_map
