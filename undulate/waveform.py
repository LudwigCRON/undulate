#!/usr/bin/env python3

"""
Command line interface to draw your waveforms
"""

import os
import re
import sys
import traceback

import json

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
]

ERROR_MSG = {
    "YAML_IMPORT": "ERROR: To read yaml file PyYAML is required. Run 'pip install pyyaml'",
    "TOML_IMPORT": "ERROR: To read toml file toml is required. Run 'pip install toml'",
    "FILE_NOT_FOUND": "ERROR: %s is not found",
    "MISSING_GRP_NAME": "ERROR: a group of wave should always have a name property",
    "UNSUPPORTED_FORMAT": (
        "ERROR: this file format is not yet supported\n"
        "For input:\n %s"
        "For output:\n %s"
    )
    % (
        "".join(["\t- %s\n" % f for f in SUPPORTED_FORMAT]),
        "".join(["\t- %s\n" % f for f in SUPPORTED_RENDER]),
    ),
}

SPACER_COUNT = 0


# ==== Simple Logging Utility ====
# this should be used only there
def log_Fatal(msg: str):
    print(msg, file=sys.stderr)
    exit(1)


def log_Error(msg: str):
    print(msg, file=sys.stderr)


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
        log_Fatal(ERROR_MSG["MISSING_GRP_NAME"])
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
                    print("Signal %s is duplicated" % n)
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
    err, ans = False, {}
    # file existence
    err = filepath is None or not os.path.exists(filepath)
    if err:
        log_Error(ERROR_MSG["FILE_NOT_FOUND"] % filepath)
        return (err, None)
    _, ext = os.path.splitext(filepath)
    # supported extension
    err = not any([ext in cat for cat in SUPPORTED_FORMAT.values()])
    if err:
        log_Error(ERROR_MSG["UNSUPPORTED_FORMAT"])
        return (err, None)
    # call appropriate parser
    if ext in SUPPORTED_FORMAT["json"]:
        ans.update(_prune_json(filepath))
    elif ext in SUPPORTED_FORMAT["yaml"]:
        try:
            import yaml

            with open(filepath, "r+") as fp:
                ans = yaml.load(fp, Loader=yaml.Loader)
        except ImportError:
            log_Error(ERROR_MSG["YAML_IMPORT"])
    else:
        try:
            import toml

            with open(filepath, "r+") as fp:
                ans = toml.load(fp)
        except ImportError:
            log_Error(ERROR_MSG["TOML_IMPORT"])
    return (err, ans if not err else None)


def register_to_wavelane(obj: dict) -> object:
    """
    convert a register definition as a wavelane
    """
    reg = undulate.Register()
    for field in obj.get("reg", []):
        reg.push_field(field)
    return reg.to_wavelane()


def cli_main(
    input_path: str,
    output_path: str,
    file_format: str,
    is_reg: bool = False,
    dpi: float = 150.0,
    cb_help=print,
):
    # check the input file
    err, obj = parse(input_path)
    if err:
        cb_help()
        exit(2)
    if not file_format.lower() in SUPPORTED_RENDER:
        log_Fatal(ERROR_MSG["UNSUPPORTED_FORMAT"])
    # for debug pupose
    if file_format.lower() == "json":
        pprint(obj)
        exit(0)
    else:
        if is_reg:
            obj = register_to_wavelane(obj)
        # select the renderer engine
        if file_format == "svg":
            renderer = undulate.SvgRenderer()
        elif file_format.startswith("cairo-"):
            renderer = undulate.CairoRenderer(extension=file_format.split("-")[-1], dpi=dpi)
        try:
            config = obj.get("config", {})
            vs = config.get("vscale", 1.0)
            hs = config.get("hscale", 1.0)
            renderer.draw(
                obj,
                brick_height=vs * (50 if is_reg else 20),
                brick_width=hs * (28 if is_reg else 40),
                is_reg=is_reg,
                filename=output_path,
            )
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            exit(3)
