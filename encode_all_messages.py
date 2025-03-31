import logging

from example_runner import process_command_args
from rsp1570serial.messages import MessageCodec
from rsp1570serial.rotel_model_meta import ROTEL_MODELS, RotelModelMeta
from rsp1570serial.utils import pretty_print_bytes


def do_it(meta: RotelModelMeta):
    codec = MessageCodec(meta)
    for cmd in meta.messages.keys():
        encoded = codec.encode_command(cmd)
        print(f"{pretty_print_bytes(encoded)}:{cmd}")


if __name__ == "__main__":
    """Emit all codes for comparison to the protocol spec"""
    logging.basicConfig(level=logging.INFO)
    args = process_command_args()
    do_it(ROTEL_MODELS[args.model])
