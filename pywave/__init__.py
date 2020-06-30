#!/usr/bin/env python3
import argparse

from .bricks import BRICKS
from .generic import Brick, generate_brick
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
)
from .renderer import Renderer
from .svgrenderer import SvgRenderer
from .waveform import cli_main

try:
    from .cairorenderer import CairoRenderer
except ImportError:
    print("Cairo is not installed and cannot be used")


def main():
    parser = argparse.ArgumentParser(description="waveform generator from textual format")
    parser.add_argument(
        "-i", "--input", help="path to the input text file", default=None, type=str
    )
    parser.add_argument(
        "-f", "--format", help="file format of the output", default="svg", type=str
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
    cli_args = parser.parse_args()
    cli_main(
        cli_args.input,
        cli_args.output,
        cli_args.format,
        cli_args.is_reg,
        cli_args.dpi,
        parser.print_help,
    )


if __name__ == "__main__":
    main()
