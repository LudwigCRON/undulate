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
import yaml
import toml

import pywave

from pprint import pprint


SUPPORTED_FORMAT = [
    [".json", ".js", ".jsonml", ".jsml"],
    [".yaml", ".yml"],
    [".toml"]
]

SUPPORTED_RENDER = ["svg", "eps", "cairo-svg", "cairo-ps", "cairo-eps", "cairo-pdf", "cairo-png", "json"]

def _number_convert(match):
  base, number = match.group(1).lower(), match.group(2)
  if base in "xh":
    return str(int(number, 16))
  elif base == "b":
    return str(int(number, 2))
  else:
    return str(int(number, 10))

def _parse_wavelane(wavelane: dict):
  _name = wavelane.get("name", "").strip()
  if "name" in wavelane:
    del wavelane["name"]
  if not _name:
    _name = f"spacer_{int(time.time())}"
  return (_name, wavelane)

def _parse_group(wavegroup: list):
  ans = {}
  _name = wavegroup[0] if isinstance(wavegroup[0], str) else None
  if not _name:
    print("ERROR: a group of wave should always have a name property", file=sys.stderr)
    return None
  for _, wavelane in enumerate(wavegroup[1:]):
    if isinstance(wavelane, dict):
      n, wave = _parse_wavelane(wavelane)
    if isinstance(wavelane, list):
      n, wave = _parse_group(wavelane)
    ans[n] = wave
  return (_name, ans)

def parse(filepath: str) -> (bool, object):
  """
  parse the input file into a compatible dict for processing
  """
  err, ans = False, {}
  # file existence
  err = not os.path.exists(filepath)
  if err:
    print((
        f"ERROR: {cli_args.input} is not found, "
        "please check the existence of your file"), file=sys.stderr)
  _, ext = os.path.splitext(filepath)
  # supported extension
  err = not any([ext in cat for cat in SUPPORTED_FORMAT])
  if err:
    print("ERROR: this filetype is not yet supported", file=sys.stderr)
  # call parser
  if ext in SUPPORTED_FORMAT[0]:
    print("JSON file")
    with open(filepath, "r+") as fp:
      content = ' '.join([line[:line.find("//")] if line.find("//") >= 0 else line for line in fp.readlines()])
    # add double quotes around strings
    content = re.sub(r"([{,]?)\s*(\w+)\s*:", r'\1 "\2":', content, flags=re.M)
    # replace single quotes with double quotes
    content = re.sub(r"'([\w\s\<\-\~\|\>,\.:\[\]\(\)]*)\s*'", r'"\1"', content, flags=re.M)
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
  elif ext in SUPPORTED_FORMAT[1]:
    print("YAML file")
    with open(filepath, "r+") as fp:
      ans = yaml.load(fp)
  else:
    print("TOML file")
    with open(filepath, "r+") as fp:
      ans = toml.load(fp)
  return (err, ans if not err else None)

def register_to_wavelane(obj: dict) -> object:
  """
  convert a register definition as a wavelane
  """
  reg = pywave.Register()
  for field in obj.get("reg", []):
    reg.push_field(pywave.Field.from_dict(field))
  return reg.to_wavelane()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='waveform generator from textual format')
  parser.add_argument("-i", "--input", help="path to the input text file", default=None, type=str)
  parser.add_argument("-f", "--format", help="file format of the output", default="svg", type=str)
  parser.add_argument("-r", "--is_reg", help="is register description", action="store_true", default=False)
  parser.add_argument("-o", "--output", help="path to the output file", default=None, type=str)
  cli_args = parser.parse_args()
  # check the input file
  err, obj = parse(cli_args.input)
  if not err:
    if not cli_args.format in SUPPORTED_RENDER:
      print(f"ERROR: output file format {cli_args.format} is not yet supported", file=sys.stderr)
      print("the format supported are:", file=sys.stderr)
      for f in SUPPORTED_RENDER:
        print(f"  - {f}", file=sys.stderr)
    else:
      if cli_args.is_reg:
        obj = register_to_wavelane(obj)
      if cli_args.format == "json":
        pprint(obj)
        exit(0)
      if cli_args.output:
        renderer = None
        if cli_args.format == "svg":
          renderer = pywave.SvgRenderer()
        elif cli_args.format == "eps":
          renderer = pywave.EpsRenderer()
        elif cli_args.format.startswith("cairo-"):
          renderer = pywave.CairoRenderer(extension=cli_args.format.split('-')[-1])
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
