#!/usr/bin/env python3
import os
import json
import argparse
import logging

# ==== configure log utility ====
conf_path = os.path.join(os.path.dirname(__file__), "logging.json")
conf_path = conf_path.replace("\\", "/")
with open(conf_path, "r+") as fp:
    logging.config.dictConfig(json.load(fp))

from .bricks import BRICKS
from .generic import Brick, generate_brick, safe_eval
from .analogue import CONTEXT, generate_analogue_symbol
from .digital import generate_digital_symbol
from .register import Register, Field, generate_register_symbol
from .skin import (
    text_bbox,
    text_align,
    apply_fill,
    apply_font,
    apply_stroke,
    get_style,
    Engine,
    update_style,
)
from .renderer import Renderer
from .svgrenderer import SvgRenderer
from .waveform import cli_main

try:
    from .cairorenderer import CairoRenderer
except ImportError:
    logging.error("Cairo is not installed and cannot be used")


def main():
    parser = argparse.ArgumentParser(description="waveform generator from textual format")
    parser.add_argument(
        "-i", "--input", help="path to the input text file", default=None, type=str
    )
    parser.add_argument(
        "-f", "--format", help="file format of the output", default="cairo-png", type=str
    )
    parser.add_argument(
        "-r", "--is_reg", help="is register description", action="store_true", default=False
    )
    parser.add_argument(
        "-d",
        "--dpi",
        help="resolution of the image for png export",
        default=150.0,
        type=float,
    )
    parser.add_argument(
        "-o", "--output", help="path to the output file", default=None, type=str
    )
    parser.add_argument(
        "-s", "--style", help="path to custom css file", default=None, type=str
    )
    parser.add_argument("mangled_input", nargs="?", default=None, type=str)
    cli_args = parser.parse_args()
    # update default style
    if cli_args.style is not None:
        update_style(cli_args.style)
    # process following data
    cli_main(
        cli_args.input or cli_args.mangled_input,
        cli_args.output,
        cli_args.format,
        cli_args.is_reg,
        cli_args.dpi,
        parser.print_help,
    )


if __name__ == "__main__":
    main()
