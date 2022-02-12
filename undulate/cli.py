#!/usr/bin/env python3

"""
Command line interface to draw your waveforms
"""

import os
import json
import argparse
import traceback
import importlib

import undulate.logger as log
import undulate.skin as skin
import undulate.parsers.register as register

from pprint import pprint
from typing import Any, Tuple


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "plugins.json")

# ==== Parser Selection ====
def parse(filepath: str) -> Tuple[bool, Any]:
    """
    parse the input file into a compatible dict for processing
    """
    # file existence
    if filepath is None:
        log.fatal(log.FILE_NOT_GIVEN)
    if not os.path.exists(filepath):
        log.fatal(log.FILE_NOT_FOUND % filepath)
    _, ext = os.path.splitext(filepath)
    # load config file
    with open(CONFIG_FILE, "rt+") as fp:
        config = json.load(fp)
        allowed_extensions = config.get("extensions", {})
    # call appropriate parser
    if ext[1:] not in allowed_extensions:
        log.fatal(log.UNSUPPORTED_FORMAT % log.list_vars(allowed_extensions))
    parser = importlib.import_module(allowed_extensions.get(ext[1:]))
    return parser.parse(filepath)


def process(
    input_path: str,
    output_path: str,
    rendering_engine: str,
    is_reg: bool,
    dpi: float,
    eol: str,
) -> None:
    # load config file
    with open(CONFIG_FILE, "rt+") as fp:
        config = json.load(fp)
        bricks_modules = config.get("bricks", [])
        rendering_engines = config.get("engines", {})
    # supported rendering engine
    if rendering_engine.lower() not in rendering_engines:
        log.fatal(log.UNSUPPORTED_ENGINE % log.list_vars(rendering_engines))
    # check the input file
    _, obj = parse(input_path)
    # convert register description into wavelane
    if is_reg:
        _, obj = register.convert(obj)
    # for debug purpose
    if rendering_engine == "json":
        pprint(obj)
        exit(0)
    # load the bricks
    for brick_module in bricks_modules:
        mod = importlib.import_module(brick_module)
        mod.initialize()
    # load the renderering engine
    engine_info = rendering_engines.get(rendering_engine)
    engine = importlib.import_module(engine_info.get("module"))
    renderer = getattr(engine, engine_info.get("classname"))
    engine_params = {
        k: v for k, v in engine_info.items() if k not in ["module", "classname"]
    }
    if "dpi" in engine_params:
        engine_params["dpi"] = dpi
    renderer = renderer(**engine_params)
    # default output file
    if output_path is None:
        file_name, ext = os.path.splitext(input_path)
        file_name = os.path.basename(file_name)
        ext = engine_info.get("extension")
        output_path = f"./{file_name}.{ext}"
        log.warning(log.FILE_NO_OUTPUT % output_path)
    try:
        renderer.draw(
            obj,
            brick_height=(50 if is_reg else 20),
            brick_width=(28 if is_reg else 40),
            is_reg=is_reg,
            filename=output_path,
            eol=eol,
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
    parser.add_argument(
        "--eol", help="define the end of line in term renderer", default="\n", type=str
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
        cli_args.eol.replace("cr", "\r").replace("lf", "\n"),
    )


if __name__ == "__main__":
    main()
