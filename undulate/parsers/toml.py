import undulate.logger as log


def parse(filepath: str) -> tuple[bool, dict]:
    ans = {}
    try:
        import toml

        with open(filepath, "r+") as fp:
            ans = toml.load(fp)
    except ImportError:
        log.fatal(log.TOML_IMPORT)
    except ModuleNotFoundError:
        log.fatal(log.TOML_IMPORT)
    except toml.TomlDecodeError as e:
        log.fatal(log.SYNTAX_ERROR % (e.lineno, e.msg))
    return (0, ans)
