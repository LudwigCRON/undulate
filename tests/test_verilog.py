#!/usr/bin/env python3
# coding: utf-8

import os
import shlex
import undulate
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
    def test_verilog_multiple_def(self):
        rc, o = sh_exec(
            "coverage run -a -m undulate.__init__ -f verilog -i '%s/adcec.jsonml'"
            % TEST_DIR
        )
        print(rc)
        for line in o.split(b"\r\n"):
            print(line.decode("utf-8"))

    def test_verilog_is_reg(self):
        pass

    def test_verilog_real(self):
        pass

    def test_verilog_unsupported_symbol(self):
        pass

    def test_verilog_data_width(self):
        f = undulate.VerilogRenderer._get_data_width
        assert f("") == (0, 0), "empty signal should be 0 width, 0 data"
        assert f("0xdeadbeef") == (32, 0xDEADBEEF), "0xdeadbeef should be 32-bits wide"
        assert f("0hdeadbeef") == (32, 0xDEADBEEF), "0hdeadbeef should be 32-bits wide"
        assert f("Ah") == (4, 10), "0hA should be 4-bits wide"
        assert f("'hcafef00d") == (32, 0xCAFEF00D), "0xcafef00d should be 32-bits wide"
        assert f("13'h0e4f") == (13, 0xE4F), "0x0e4f should be 13-bits wide"
        assert f("127") == (7, 127), "127 should be 7-bits wide"
        assert f("'d128") == (8, 128), "128 should be 8-bits wide"
        assert f("57d") == (6, 57), "57 should be 6-bits wide"
        assert f("'b0101") == (3, 5), "0b0101 should be 3-bits wide"
        assert f("101b") == (3, 5), "0b101 should be 3-bits wide"
        assert f("0d3971") == (12, 3971), "3971 should be 12-bits wide"
        assert f("0b1100101") == (7, 101), "0b1100101 should be 7-bits wide"

    def test_verilog_signal_width(self):
        f = undulate.VerilogRenderer._get_signal_width
        assert f("") == 0, "empty signal should be 0 width"
        assert f() == 0, "None signal should be 0 width"
        assert f("a[4009:11]") == 3999, "a[4009:11] is 3999 bits wide"
        assert f("a[0:15]") == 16, "a[0:15] is 16 bits wide"
        assert f("a") == 1, "a is a 1-bit signal"


if __name__ == "__main__":
    unittest.main()