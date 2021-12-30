import undulate.logger as log

from typing import Dict, Tuple


def parse(filepath: str) -> Tuple[bool, Dict]:
    """
    Parse a yaml file
    """
    ans = {}
    try:
        import yaml

        with open(filepath, "r+") as fp:
            ans = yaml.load(fp, Loader=yaml.Loader)
    except ImportError:
        log.fatal(log.YAML_IMPORT)
    except yaml.YAMLError as e:
        if "lineno" in dir(e):
            log.fatal(log.SYNTAX_ERROR % (e.lineno, e.msg))
        else:
            log.fatal(
                "\n".join(
                    [
                        str(e.context),
                        str(e.context_mark),
                        str(e.problem),
                        str(e.problem_mark),
                    ]
                )
            )
    return (0, ans)
