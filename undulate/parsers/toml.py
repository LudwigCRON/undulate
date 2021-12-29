import undulate.logger as log

from typing import Dict, Tuple


def parse(filepath: str) -> Tuple[bool, Dict]:
    ans = {}
    try:
        import toml

        with open(filepath, "r+") as fp:
            ans = toml.load(fp)
    except ImportError:
        log.fatal(log.TOML_IMPORT)
    except toml.TomlDecodeError as e:
        log.fatal(log.SYNTAX_ERROR % (e.msg, e.lineno))
    return (0, ans)
