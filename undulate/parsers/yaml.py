import undulate.logger as log

from typing import Dict, Tuple


def parse(filepath: str) -> Tuple[bool, Dict]:
    ans = {}
    try:
        import yaml

        with open(filepath, "r+") as fp:
            ans = yaml.load(fp, Loader=yaml.Loader)
    except ImportError:
        log.fatal(log.YAML_IMPORT)
    except ModuleNotFoundError:
        log.fatal(log.YAML_IMPORT)
    except yaml.YAMLError as e:
        log.fatal(log.SYNTAX_ERROR % (e.lineno, e.msg))
    return (0, ans)
