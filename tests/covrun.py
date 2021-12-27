#!/usr/bin/env python3
# coding: utf-8

import sys
import subprocess

if __name__ == "__main__":
    command = " ".join(sys.argv[1:])
    # if followed by '; test ...' keep only cmd before ';'
    command = command.split(";", maxsplit=1)[-1]
    # replace 'undulate' by 'undulate.cli' the module name
    command_cov = command.replace("undulate", "undulate.cli")
    subprocess.call(f"coverage run -a -m {command_cov}", shell=True)
    exit_code = subprocess.call(command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
    exit(exit_code)
