#!/usr/bin/env python3

"""
Command line interface to draw your waveforms
"""

import os
import re
import sys
import traceback

import json
import logging
import undulate

from pprint import pprint


SUPPORTED_FORMAT = {
    "json": [".json", ".js", ".jsonml", ".jsml"],
    "yaml": [".yaml", ".yml"],
    "toml": [".toml"],
}

SUPPORTED_RENDER = [
    "svg",
    "cairo-svg",
    "cairo-ps",
    "cairo-eps",
    "cairo-pdf",
    "cairo-png",
    "json",
    "verilog",
]

ERROR_MSG = {
    "YAML_IMPORT": "To read yaml file PyYAML is required. Run 'pip install pyyaml'",
    "TOML_IMPORT": "To read toml file toml is required. Run 'pip install toml'",
    "FILE_NOT_FOUND": "%s is not found",
    "NO_FILE": "An input file shall be given",
    "MISSING_GRP_NAME": "A group of wave should always have a name property",
    "UNSUPPORTED_FORMAT": (
        "This file format is not yet supported\n" "choose one of the following:\n %s"
    )
    % ("".join(["\t- %s\n" % f for f in SUPPORTED_FORMAT]),),
    "UNSUPPORTED_ENGINE": (
        "This rendering engine is not yet supported\n" "choose one of the following:\n %s"
    )
    % ("".join(["\t- %s\n" % f for f in SUPPORTED_RENDER]),),
}

SPACER_COUNT = 0


# ==== Normalization ====
def _number_convert(match):
    base, number = match.group(1).lower(), match.group(2)
    if base in "xh":
        return str(int(number, 16))
    elif base == "b":
        return str(int(number, 2))
    else:
        return str(int(number, 10))


def _parse_wavelane(wavelane: dict):
    """
    normalize the the wavelane name and if no name is given
    the function consider it is a spacer
    """
    global SPACER_COUNT
    _name = wavelane.get("name", "").strip()
    if "name" in wavelane:
        del wavelane["name"]
    if not _name:
        SPACER_COUNT += 1
        _name = "spacer_%f" % SPACER_COUNT
    return (_name, wavelane)


def _parse_group(wavegroup: list):
    """
    convert traditionnal group of wavedrom into
    the new structure
    """
    ans = {}
    _name = wavegroup[0] if isinstance(wavegroup[0], str) else None
    if not _name:
        logging.fatal(ERROR_MSG["MISSING_GRP_NAME"])
        exit(12)
    for _, wavelane in enumerate(wavegroup[1:]):
        if isinstance(wavelane, dict):
            n, wave = _parse_wavelane(wavelane)
        if isinstance(wavelane, list):
            n, wave = _parse_group(wavelane)
        ans[n] = wave
    return (_name, ans)


def _prune_json(filepath: str):
    """
    assume the file exists and:
    - remove comments
    - replace single quotes by double quotes around string
    - remove final extra comma
    - parse numbers
    """
    ans = {}
    with open(filepath, "r+") as fp:
        content = " ".join(
            [
                line[: line.find("//")] if line.find("//") >= 0 else line
                for line in fp.readlines()
            ]
        )
    # add double quotes around strings
    content = re.sub(r"([{,]?)\s*(\w+)\s*:", r'\1 "\2":', content, flags=re.M)
    # replace single quotes with double quotes
    content = re.sub(
        r"'([\w\s\<\-\~\|\>,*\_\.:\[\]\(\)]*)\s*'", r'"\1"', content, flags=re.M
    )
    # remove final extra comma of arrays definition
    content = re.sub(r"(,\s*\])", r"]", content, flags=re.M)
    # change hex numbers to int
    content = re.sub("0'?([xbhdXBHD])([0-9ABCDEF]+)", _number_convert, content, flags=re.M)
    tmp = json.loads(content)
    for k, v in tmp.items():
        if k == "signal":
            for _, sig in enumerate(v):
                n, wave = (
                    _parse_wavelane(sig) if isinstance(sig, dict) else _parse_group(sig)
                )
                if n in ans.keys():
                    logging.info("Signal %s is duplicated" % n)
                    while n in ans:
                        n += " "
                ans[n] = wave
        else:
            ans[k] = v
    return ans


def parse(filepath: str) -> (bool, object):
    """
    parse the input file into a compatible dict for processing
    """
    ans = {}
    # file existence
    if filepath is None:
        logging.fatal(ERROR_MSG["NO_FILE"])
        exit(1)
    if not os.path.exists(filepath):
        logging.fatal(ERROR_MSG["FILE_NOT_FOUND"] % filepath)
        exit(2)
    _, ext = os.path.splitext(filepath)
    # supported extension
    if not any([ext in cat for cat in SUPPORTED_FORMAT.values()]):
        logging.fatal(ERROR_MSG["UNSUPPORTED_FORMAT"])
        exit(3)
    # call appropriate parser
    if ext in SUPPORTED_FORMAT["json"]:
        ans.update(_prune_json(filepath))
    elif ext in SUPPORTED_FORMAT["yaml"]:
        try:
            import yaml

            with open(filepath, "r+") as fp:
                ans = yaml.load(fp, Loader=yaml.Loader)
        except ImportError:
            logging.fatal(ERROR_MSG["YAML_IMPORT"])
            exit(4)
    else:
        try:
            import toml

            with open(filepath, "r+") as fp:
                ans = toml.load(fp)
        except ImportError:
            logging.fatal(ERROR_MSG["TOML_IMPORT"])
            exit(4)
    return ans


def register_to_wavelane(obj: dict) -> object:
    """
    convert a register definition as a wavelane
    """
    reg = undulate.Register()
    # name of the register
    reg.name = [name for name in obj.keys() if name not in ["config", "head", "foot"]][-1]
    for field in obj.get(reg.name, []):
        reg.push_field(field)
    # default value from wavedrom format
    if reg.name == "reg":
        reg.name = ""
    reg.config = obj.get("config", {})
    return reg.to_wavelane()


def cli_main(
    input_path: str,
    output_path: str,
    file_format: str,
    is_reg: bool = False,
    dpi: float = 150.0,
    cb_help=print,
):
    # supported rendering engine
    if not file_format.lower() in SUPPORTED_RENDER:
        logging.fatal(ERROR_MSG["UNSUPPORTED_ENGINE"])
        exit(5)
    # check the input file
    obj = parse(input_path)
    # for debug pupose
    if file_format.lower() == "json":
        pprint(obj)
        exit(0)
    else:
        if is_reg:
            obj = register_to_wavelane(obj)
        # default output file
        if output_path is None:
            file_name, _ = os.path.splitext(input_path)
            file_name = os.path.basename(file_name)
            ext = file_format if file_format == "svg" else file_format.split("-")[-1]
            output_path = "./%s.%s" % (file_name, ext)
            logging.warning("No output file given. Generated at %s" % output_path)
        # select the renderer engine
        if file_format == "svg":
            renderer = undulate.SvgRenderer()
        elif file_format.startswith("cairo-"):
            renderer = undulate.CairoRenderer(extension=file_format.split("-")[-1], dpi=dpi)
        elif file_format == "verilog":
            renderer = undulate.VerilogRenderer()
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
            logging.error(e)
            exit(6)
