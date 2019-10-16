#!/usr/bin/env python3

"""
Command line interface to draw your waveforms
"""

import os
import re
import sys
import argparse
import traceback

import json
import time

import pywave

from pprint import pprint


SUPPORTED_FORMAT = {
    "json": [".json", ".js", ".jsonml", ".jsml"],
    "yaml": [".yaml", ".yml"],
    "toml": [".toml"]
}

SUPPORTED_RENDER = ["svg", "cairo-svg", "cairo-ps", "cairo-eps", "cairo-pdf", "cairo-png", "json"]

ERROR_MSG = {
    "YAML_IMPORT":
        "ERROR: To read yaml file PyYAML is required. Run 'pip install pyyaml'",
    "TOML_IMPORT":
        "ERROR: To read toml file toml is required. Run 'pip install toml'",
    "FILE_NOT_FOUND":
        "ERROR: %s is not found",
    "MISSING_GRP_NAME":
        "ERROR: a group of wave should always have a name property",
    "UNSUPPORTED_FORMAT": (
        "ERROR: this file format is not yet supported\n"
        "For input:\n %s"
        "For output:\n %s"
        ) % (''.join(["\t- %s\n" % f for f in SUPPORTED_FORMAT])  ,''.join(["\t- %s\n" % f for f in SUPPORTED_RENDER]))
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
        content = ' '.join([line[:line.find("//")] if line.find("//") >= 0 else line for line in fp.readlines()])
    # add double quotes around strings
    content = re.sub(r"([{,]?)\s*(\w+)\s*:", r'\1 "\2":', content, flags=re.M)
    # replace single quotes with double quotes
    content = re.sub(r"'([\w\s\<\-\~\|\>,*\_\.:\[\]\(\)]*)\s*'", r'"\1"', content, flags=re.M)
    # remove final extra comma of arrays definition
    content = re.sub(r"(,\s*\])", r"]", content, flags=re.M)
    # change hex numbers to int
    content = re.sub("0'?([xbhdXBHD])([0-9ABCDEF]+)", _number_convert, content, flags=re.M)
    tmp = json.loads(content)
    for k, v in tmp.items():
        if k == "signal":
            for _, sig in enumerate(v):
                n, wave = _parse_wavelane(sig) if isinstance(sig, dict) else _parse_group(sig)
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
        log_Error(ERROR_MSG["FILE_NOT_FOUND"] % cli_args.input)
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
                ans = yaml.load(fp, Loader=yaml.FullLoader)
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
    reg = pywave.Register()
    for field in obj.get("reg", []):
        reg.push_field(field)
    return reg.to_wavelane()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='waveform generator from textual format')
    parser.add_argument("-i", "--input", help="path to the input text file", default=None, type=str)
    parser.add_argument("-f", "--format", help="file format of the output", default="svg", type=str)
    parser.add_argument("-r", "--is_reg", help="is register description", action="store_true", default=False)
    parser.add_argument("-d", "--dpi", help="resolution of the image for png export", default=150.0, type=float)
    parser.add_argument("-o", "--output", help="path to the output file", default=None, type=str)
    cli_args = parser.parse_args()
    # check the input file
    err, obj = parse(cli_args.input)
    if err:
        parser.print_help()
        exit(2)
    if not cli_args.format.lower() in SUPPORTED_RENDER:
        log_Fatal(ERROR_MSG["UNSUPPORTED_FORMAT"])
    # for debug pupose
    if cli_args.format.lower() == "json":
        pprint(obj)
        exit(0)
    else:
        if cli_args.is_reg:
            obj = register_to_wavelane(obj)
        # select the renderer engine
        if cli_args.format == "svg":
            renderer = pywave.SvgRenderer()
        elif cli_args.format.startswith("cairo-"):
            renderer = pywave.CairoRenderer(extension=cli_args.format.split('-')[-1], dpi=cli_args.dpi)
        else:
            renderer = None
        try:
            if cli_args.format.startswith("cairo-"):
                renderer.draw(obj, brick_height=(50 if cli_args.is_reg else 20),
                                   brick_width=(28 if cli_args.is_reg else 40),
                                   is_reg=cli_args.is_reg,
                                   filename=cli_args.output)
            else:
                with open(cli_args.output, "w+") as fp:
                    fp.write(renderer.draw(obj, brick_height=(50 if cli_args.is_reg else 20),
                                                brick_width=(28 if cli_args.is_reg else 40),
                                                is_reg=cli_args.is_reg))
        except Exception as e:
            traceback.print_tb(e.__traceback__)
