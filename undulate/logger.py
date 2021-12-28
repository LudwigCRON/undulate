import os
import sys
import json
import logging
import logging.config
from typing import Iterable

# ==== configure log utility ====
conf_path = os.path.join(os.path.dirname(__file__), "logging.json")
conf_path = conf_path.replace("\\", "/")
with open(conf_path, "r+") as fp:
    logging.config.dictConfig(json.load(fp))

YAML_IMPORT = "To read yaml file PyYAML is required. Run 'pip install pyyaml'"
TOML_IMPORT = "To read toml file toml is required. Run 'pip install toml'"
CAIRO_IMPORT = "To use cairo-* renderer cairo should be installed. Run 'pip install cairo'"
CAIRO_FORMAT = "Unsupported cairo-%s format"
FILE_NOT_FOUND = "File '%s' is not found"
FILE_NOT_GIVEN = "An input file shall be given"
FILE_EMPTY = "The input file shall not be empty"
FILE_NO_OUTPUT = "No output file given. Generated at %s"
SYNTAX_ERROR = "Parsing Error detected: %s at line %d"
UNSUPPORTED_FORMAT = (
    "This file format is not yet supported\n" "choose one of the following:\n %s"
)
UNSUPPORTED_ENGINE = (
    "This rendering engine is not yet supported\n" "choose one of the following:\n %s"
)
GROUP_MISSING_NAME = "A group of signals should always have a property 'name'"
SIGNAL_DUPLICATED = "Signal %s is duplicated"
SIGNAL_WRONG_START = "A waveform cannot start with '%s'"
BRICK_SYMBOL_UNDEFINED = "The symbol '%s' is not defined"
FIELD_UNSUPPORTED_TYPE = "Unsupported type '%s' of field"
FIELD_OVERLAP = "Detected position overlap for '%s'. Please check position"
ANNOTATION_PATTERN_UNDEFINED = "The pattern '%s' is not defined"


def list_vars(values: Iterable) -> str:
    return "".join(("\t- %s\n" % value for value in values))


def debug(msg):
    logging.debug(msg)


def note(msg):
    logging.info(msg)


def warning(msg):
    logging.warning(msg)


def error(msg):
    logging.error(msg)


def fatal(msg, num: int = 1):
    logging.critical(msg)
    sys.exit(num)
