#!/usr/bin/env python3

"""
Command line interface to draw your waveforms
"""

import os
import argparse
import traceback
import importlib

import undulate.logger as log
import undulate.skin as skin
import undulate.parsers.register as register

from pprint import pprint

SUPPORTED_FORMAT = {
    "json": [".json", ".js", ".jsonml", ".jsml"],
    "yaml": [".yaml", ".yml"],
    "toml": [".toml"],
}

SUPPORTED_RENDERER = [
    "svg",
    "cairo-svg",
    "cairo-ps",
    "cairo-eps",
    "cairo-pdf",
    "cairo-png",
    "json",
]

# ==== Parser Selection ====
def parse(filepath: str) -> tuple[bool, object]:
    """
    parse the input file into a compatible dict for processing
    """
    err, ans = False, {}
    # file existence
    if filepath is None:
        log.fatal(log.FILE_NOT_GIVEN)
    if not os.path.exists(filepath):
        log.fatal(log.FILE_NOT_FOUND % filepath)
    _, ext = os.path.splitext(filepath)
    # call appropriate parser
    if ext in SUPPORTED_FORMAT["json"]:
        import undulate.parsers.jsonml as parser
    elif ext in SUPPORTED_FORMAT["yaml"]:
        import undulate.parsers.yaml as parser
    elif ext in SUPPORTED_FORMAT["toml"]:
        import undulate.parsers.toml as parser
    else:
        log.fatal(log.UNSUPPORTED_FORMAT % log.list_vars(SUPPORTED_FORMAT))
    return parser.parse(filepath)


def process(
    input_path: str,
    output_path: str,
    rendering_engine: str,
    is_reg: bool = False,
    dpi: float = 150.0,
) -> bool:
    # supported rendering engine
    if not rendering_engine.lower() in SUPPORTED_RENDERER:
        log.fatal(log.UNSUPPORTED_ENGINE % log.list_vars(SUPPORTED_RENDERER))
    # check the input file
    err, obj = parse(input_path)
    if err:
        return err
    # convert register description into wavelane
    if is_reg:
        err, obj = register.convert(obj)
    if err:
        return err
    # for debug purpose
    if rendering_engine == "json":
        pprint(obj)
        exit(0)

    # default output file
    if output_path is None:
        file_name, ext = os.path.splitext(input_path)
        file_name = os.path.basename(file_name)
        if "-" in rendering_engine:
            ext = rendering_engine.split("-")[-1]
        output_path = "./%s.%s" % (file_name, ext)
        log.warning(log.FILE_NO_OUTPUT % output_path)
    # load the bricks
    for brick_module in [
        "undulate.bricks.analogue",
        "undulate.bricks.digital",
        "undulate.bricks.register",
    ]:
        mod = importlib.import_module(brick_module)
        mod.initialize()
    # load the renderering engine
    if rendering_engine == "svg":
        engine = importlib.import_module("undulate.renderers.svgrenderer")
        renderer = engine.SvgRenderer()
    elif rendering_engine.startswith("cairo-"):
        engine = importlib.import_module("undulate.renderers.cairorenderer")
        renderer = engine.CairoRenderer(extension=rendering_engine.split("-")[-1], dpi=dpi)
    try:
        renderer.draw(
            obj,
            brick_height=(50 if is_reg else 20),
            brick_width=(28 if is_reg else 40),
            is_reg=is_reg,
            filename=output_path,
        )
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        exit(3)


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
        skin.update_style(cli_args.style)
    # process following data
    process(
        cli_args.input or cli_args.mangled_input,
        cli_args.output,
        cli_args.format,
        cli_args.is_reg,
        cli_args.dpi,
    )
