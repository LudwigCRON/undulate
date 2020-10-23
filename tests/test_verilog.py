#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import shlex
import unittest
import subprocess
from subprocess import CalledProcessError

TEST_DIR = os.path.dirname(__file__)


def sh_exec(cmd):
    args = shlex.split(cmd)
    try:
        out = subprocess.check_output(args)
        return 0, out
    except CalledProcessError as e:
        return e.returncode, e.stderr


class TestVerilog(unittest.TestCase):
    def test_dbg(self):
        rc, o = sh_exec("undulate -f verilog -i '%s/adcec.jsonml'" % TEST_DIR)
        print(rc)
        for line in o.split(b"\r\n"):
            print(line.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()