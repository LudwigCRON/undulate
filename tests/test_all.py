#!/usr/bin/env python3
# coding: utf-8

import os
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


class TestUndulate(unittest.TestCase):
    def test_legacy(self):
        input_files = ["legacy_1.jsonml", "legacy_2.jsonml", "legacy_3.jsonml"]
        for input_file in input_files:
            output_file = "%s/legacy/%s" % (
                TEST_DIR,
                input_file.replace(".jsonml", "-jsonml.svg"),
            )
            rc, _ = sh_exec(
                "coverage run -a -m undulate.__init__ -i '%s/%s' -f svg -o '%s'"
                % (TEST_DIR, input_file, output_file)
            )
            assert rc == 0, "'%s' should not generate any error"
            assert os.stat(output_file).st_size > 0, (
                "'%s' should not be empty" % output_file
            )

    def test_internal_svg(self):
        rc, _ = sh_exec("coverage run -a '%s/test_wavedrom.py' -f svg -- -v" % TEST_DIR)
        assert rc == 0, "expect wavedrom basic test ok"

    def test_internal_cairosvg(self):
        rc, _ = sh_exec(
            "coverage run -a '%s/test_wavedrom.py' -f cairo-svg -- -v" % TEST_DIR
        )
        assert rc == 0, "expect wavedrom basic test ok"

    def test_wavetest_json(self):
        output_file = "%s/legacy/wavetest-json.svg" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/wavetest.json' -f svg -o '%s'"
            % (TEST_DIR, output_file)
        )
        assert rc == 0, "'%s' should not generate any error"
        assert os.stat(output_file).st_size > 0, "'%s' should not be empty" % output_file

    def test_wavetest_yaml(self):
        formats = ["svg", "cairo-svg", "cairo-eps", "cairo-ps", "cairo-png", "cairo-pdf"]
        for format in formats:
            f = "-%s" % format.replace("-", ".") if "-" in format else ".%s" % format
            output_file = "%s/legacy/wavetest-yaml%s" % (TEST_DIR, f)
            rc, _ = sh_exec(
                "coverage run -a -m undulate.__init__ -i '%s/wavetest.yaml' -f %s -o '%s'"
                % (TEST_DIR, format, output_file)
            )
            assert rc == 0, "'%s' should not generate any error"
            assert os.stat(output_file).st_size > 0, (
                "'%s' should not be empty" % output_file
            )

    def test_registers(self):
        input_files = ["reg-opivi.jsonml", "reg-vl.jsonml"]
        formats = ["svg", "cairo-svg", "cairo-eps", "cairo-ps", "cairo-png", "cairo-pdf"]
        for format in formats:
            f = "-%s" % format.replace("-", ".") if "-" in format else ".%s" % format
            for input_file in input_files:
                output_file = "%s/legacy/%s" % (
                    TEST_DIR,
                    input_file.replace(".jsonml", f),
                )
                rc, _ = sh_exec(
                    "coverage run -a -m undulate.__init__ -r -i '%s/%s' -f %s -o '%s'"
                    % (TEST_DIR, input_file, format, output_file)
                )
                assert rc == 0, "'%s' should not generate any error"
                assert os.stat(output_file).st_size > 0, (
                    "'%s' should not be empty" % output_file
                )

    def test_annotations(self):
        formats = ["svg", "cairo-svg"]
        for format in formats:
            f = "-%s" % format.replace("-", ".") if "-" in format else ".%s" % format
            output_file = "%s/output/annotation.yaml" % TEST_DIR
            output_file = output_file.replace(".yaml", f)
            rc, _ = sh_exec(
                "coverage run -a -m undulate.__init__ -i '%s/annotation.yaml -f %s -o '%s'"
                % (TEST_DIR, format, output_file)
            )
            assert rc == 0, "'%s' should not generate any error"
            assert os.stat(output_file).st_size > 0, (
                "'%s' should not be empty" % output_file
            )

    def test_annotations(self):
        formats = ["svg", "cairo-svg"]
        for format in formats:
            f = "-%s" % format.replace("-", ".") if "-" in format else ".%s" % format
            output_file = "%s/output/overlay.toml" % TEST_DIR
            output_file = output_file.replace(".toml", f)
            rc, _ = sh_exec(
                "coverage run -a -m undulate.__init__ -i '%s/overlay.toml' -f %s -o '%s'"
                % (TEST_DIR, format, output_file)
            )
            assert rc == 0, "'%s' should not generate any error"
            assert os.stat(output_file).st_size > 0, (
                "'%s' should not be empty" % output_file
            )

    def test_adcec(self):
        output_file = "%s/output/adcec.svg" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/adcec.jsonml' -f svg -o '%s'"
            % (TEST_DIR, output_file)
        )
        assert rc == 0, "'%s' should not generate any error"
        assert os.stat(output_file).st_size > 0, "'%s' should not be empty" % output_file

    def test_alt_css(self):
        output_file = "%s/output/wavetest_alt-json-cairo.png" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -s '%s/ut_css/overload.css' -i '%s/wavetest_alt.json' -f cairo-png -o '%s'"
            % (TEST_DIR, TEST_DIR, output_file)
        )
        assert rc == 0, "'%s' should not generate any error"
        assert os.stat(output_file).st_size > 0, "'%s' should not be empty" % output_file

    def test_wrong_format(self):
        rc, _ = sh_exec("coverage run -a -m undulate.__init__ -f doc")
        assert rc == 5, "wrong engine should be exit(5)"

    def test_inexisting_symbol(self):
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -f svg -i '%s/inexisting_symbol.toml' -o '%s/inexisting_symbol.svg'"
            % (TEST_DIR, TEST_DIR)
        )
        assert rc == 9, "inexisting symbol should be exit(9)"

    def test_wrong_extension(self):
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/wrong_ext.c' -f json" % TEST_DIR
        )
        assert rc == 3, "wrong extension is an unrecognized file and should be exit(3)"

    def test_missing_groupname(self):
        rc, o = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/missing_grp.jsonml' -f json"
            % (TEST_DIR)
        )
        assert rc == 12, "missing group name should be exit(12)"

    def test_missing_args(self):
        rc, _ = sh_exec("coverage run -a -m undulate.__init__")
        assert rc == 1, "missing input file should be exit(1)"
        rc, _ = sh_exec("coverage run -a -m undulate.__init__ -i")
        assert rc == 2, "missing input args should be exit(2)"

    def test_get_help(self):
        rc, o = sh_exec("coverage run -a -m undulate.__init__ -h")
        assert rc == 0, "getting help is not an error"
        assert len(o) > 20, "missing helpful help message"

    def test_local_config(self):
        output_file = "%s/output/local_config_nodes.svg" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/local_config_nodes.yaml' -f svg -o '%s'"
            % (TEST_DIR, output_file)
        )
        assert rc == 0, "local config config should be supported even for nodes"
        assert os.stat(output_file).st_size > 0, "'%s' should not be empty" % output_file

    def test_reg_errors(self):
        output_file = "%s/output/reg_control.svg" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/reg_control.jsonml' -f svg -r -o '%s'"
            % (TEST_DIR, output_file)
        )
        assert rc == 0, "local config config should be supported even for nodes"
        assert os.stat(output_file).st_size > 0, "'%s' should not be empty" % output_file
        output_file = "%s/output/reg_err5.svg" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/reg_err5.jsonml' -f svg -r -o '%s'"
            % (TEST_DIR, output_file)
        )
        assert rc == 7, "Unsupported field should be exit(7)"
        output_file = "%s/output/reg_err6.svg" % TEST_DIR
        rc, _ = sh_exec(
            "coverage run -a -m undulate.__init__ -i '%s/reg_err6.jsonml' -f svg -r -o '%s'"
            % (TEST_DIR, output_file)
        )
        assert rc == 8, "Field overlapping should be exit(8)"


if __name__ == "__main__":
    unittest.main()