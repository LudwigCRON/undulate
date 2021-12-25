import sys
import logging
from typing import Iterable

YAML_IMPORT = "To read yaml file PyYAML is required. Run 'pip install pyyaml'"
TOML_IMPORT = "To read toml file toml is required. Run 'pip install toml'"
CAIRO_IMPORT = "To use cairo-* renderer cairo should be installed. Run 'pip install cairo'"
FILE_NOT_FOUND = "File '%s' is not found"
NO_INPUT_FILE = "An input file shall be given"
EMPTY_FILE = "The input file shall not be empty"
SYNTAX_ERROR = "Parsing Error detected: %s at line %d"
MISSING_GRP_NAME = "A group of wave should always have a property 'name'"
UNSUPPORTED_FORMAT = (
    "This file format is not yet supported\n" "choose one of the following:\n %s"
)
UNSUPPORTED_ENGINE = (
    "This rendering engine is not yet supported\n" "choose one of the following:\n %s"
)
DUPLICATED_SIGNAL = "Signal %s is duplicated"
NO_OUTPUT_FILE = "No output file given. Generated at %s"
UNKNOWN_SYMBOL = "Unknown symbol '%s' in signal '%s' used"
WRONG_WAVE_START = "A waveform cannot start with '%s'"


def list_vars(values: Iterable) -> str:
    return "".join(("\t- %s\n" % value for value in values))


def note(msg):
    logging.info(msg)


def warning(msg):
    logging.warning(msg)


def error(msg):
    logging.error(msg)


def fatal(msg):
    logging.critical(msg)
    sys.exit(1)
