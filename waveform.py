#!/usr/bin/env python3

"""
Command line interface to draw your waveforms


"""

import os
import sys
import toml
import yaml
import json
import time
import pywave
import argparse
import traceback

SUPPORTED_FORMAT = [
    [".json", ".js", ".jsonml", ".jsml"],
    [".yaml", ".yml"],
    [".toml"]
]

SUPPORTED_RENDER = ["svg"]

def _parse_wavelane(wavelane: dict):
  _name = wavelane.get("name", "").strip()
  if "name" in wavelane:
    del wavelane["name"]
  if len(_name) == 0:
    _name = f"spacer_{int(time.time())}"
  print(_name, wavelane)
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
    print("JSON file" if not "ml" in ext else "JSONML file")
    with open(filepath, "r+") as fp:
      tmp = json.load(fp)
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

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='waveform generator from textual format')
  parser.add_argument("-i", "--input", help="path to the input text file", default=None)
  parser.add_argument("-f", "--format", help="file format of the output", default="svg")
  parser.add_argument("-o", "--output", help="path to the output file", default=None)
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
      if cli_args.output:
        renderer = None
        if cli_args.format == "svg":
          renderer = pywave.SvgRenderer()
        try:
          with open(cli_args.output, "w+") as fp:
            fp.write(renderer.draw(obj))
        except Exception as e:
          traceback.print_tb(e.__traceback__)
