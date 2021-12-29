import re
import json

import undulate.logger as log

from typing import Dict, Tuple

# counter to have distinct spacer id
SPACER_COUNT = 0


def _number_convert(match):
    prefix, base, number = match.groups()
    if prefix is not None:
        return str(match.group(0))
    if base in "xh":
        return str(int(number, 16))
    if base == "b":
        return str(int(number, 2))
    return str(int(number, 10))


def _make_signal_unique(signal_name: str, db: dict) -> str:
    new_name = signal_name
    while new_name in db:
        new_name += " "
    return new_name


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
        log.fatal(log.GROUP_MISSING_NAME)
    for _, wavelane in enumerate(wavegroup[1:]):
        if isinstance(wavelane, dict):
            n, wave = _parse_wavelane(wavelane)
        if isinstance(wavelane, list):
            n, wave = _parse_group(wavelane)
        ans[n] = wave
    return (_name, ans)


def _prune_json(filepath: str) -> str:
    """
    assume the file exists and:
    - remove comments
    - replace single quotes by double quotes around string
    - remove final extra comma
    - parse numbers
    """
    with open(filepath, "r+") as fp:
        content = " ".join(
            [
                line[: line.find("//")] if line.find("//") >= 0 else line
                for line in fp.readlines()
            ]
        )
    if not content:
        log.fatal(log.FILE_EMPTY)
    # add double quotes around strings
    content = re.sub(r"([{,]?)\s*(\w+)\s*:", r'\1 "\2":', content, flags=re.M)
    # replace single quotes with double quotes
    content = re.sub(
        r"'([\w\s\<\-\~\|\>,*\_\.:\[\]\(\)]*)\s*'", r'"\1"', content, flags=re.M
    )
    # remove final extra comma of arrays definition
    content = re.sub(r"(,\s*\])", r"]", content, flags=re.M)
    # change hex numbers to int but not CSS hexa colors
    content = re.sub(
        "(#[0-9abcdedABCDEF]*)?0'?([xbhdXBHD])([0-9abcdefABCDEF]+)",
        _number_convert,
        content,
        flags=re.M,
    )
    return content


def parse(filepath: str) -> Tuple[bool, Dict]:
    """
    parse a json file after pre-processing the file
    to allow extra comments if needed
    """
    ans = {}
    content = _prune_json(filepath)
    # parse the pre-processed content
    try:
        tmp = json.loads(content)
    except json.decoder.JSONDecodeError as e:
        log.fatal(log.SYNTAX_ERROR % (e.msg, e.lineno))
    # post-process to normalize the db
    for k, v in tmp.items():
        if k == "signal":
            for _, signal in enumerate(v):
                signal_name, wave = (
                    _parse_wavelane(signal)
                    if isinstance(signal, dict)
                    else _parse_group(signal)
                )
                if signal_name in ans.keys():
                    log.warning(log.SIGNAL_DUPLICATED % signal_name)
                    signal_name = _make_signal_unique(signal_name, ans)
                ans[signal_name] = wave
        else:
            ans[k] = v
    return (0, ans)
