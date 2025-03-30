import logging

from example_runner import process_command_args
from rsp1570serial.rotel_model_meta import ROTEL_MODELS, RotelModelMeta
from rsp1570serial.utils import pretty_print_bytes


def do_it(meta: RotelModelMeta):
    for cmd in meta.codec.messages.keys():
        encoded = meta.codec.encode_command(cmd)
        print(f"{pretty_print_bytes(encoded)}:{cmd}")


if __name__ == "__main__":
    """Emit all codes for comparison to the protocol spec"""
    logging.basicConfig(level=logging.INFO)
    args = process_command_args()
    do_it(ROTEL_MODELS[args.model])
