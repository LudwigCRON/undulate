#!/usr/bin/env python3

import os
import sys
import argparse
import unittest

# imports as in undulate.py
import importlib
from undulate.renderers.renderer import Renderer
from undulate.renderers.svgrenderer import SvgRenderer
from undulate.renderers.cairorenderer import CairoRenderer
from undulate.bricks.generic import NodeBank, Point

RENDERER = None


class TestSvgMethods(unittest.TestCase):
    """
    perform some test on the rendering with the internal
    dict format of data
    """

    def setUpClass() -> None:
        modules = [
            "undulate.bricks.digital",
            "undulate.bricks.analogue",
            "undulate.bricks.shape",
        ]
        for module in modules:
            mod = importlib.import_module(module)
            mod.initialize()

    def test_wavedrom_step1(self):
        """
        test supported state of a signal
        """
        filename = "%s/wavedrom_step1.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "Alfa": {"wave": "01.zx=ud.23.45"},
            "SAlfa": {"wave": "01.zx=ud.23.45", "slewing": 8},
            "compatibility": {"wave": "p||||......"},
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step2(self):
        """
        test clock generation
        """
        filename = "%s/wavedrom_step2.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "pclk": {"wave": "p......."},
            "Pclk": {"wave": "P......."},
            "nclk": {"wave": "n......."},
            "Nclk": {"wave": "N......."},
            "clk0": {"wave": "phnlPHNL"},
            "clk1": {"wave": "xhlhLHl."},
            "clk2": {"wave": "hpHplnLn"},
            "clk3": {"wave": "nhNhplPl"},
            "clk4": {"wave": "xlh.L.Hx"},
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step3(self):
        """
        small bus example
        """
        filename = "%s/wavedrom_step3.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "clk": {"wave": "P......"},
            "bus": {"wave": "x.==.=x", "data": ["head", "body", "tail", "data"]},
            "wire": {"wave": "0.1..0."},
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step4(self):
        """
        spacer and gaps
        """
        filename = "%s/wavedrom_step4.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "clk": {"wave": "p.....|..."},
            "Data": {"wave": "x.345x|=.x", "data": ["head", "body", "tail", "data"]},
            "Request": {"wave": "0.1..0|1.0"},
            "spacer_0": {},
            "Acknowledge": {"wave": "1.....|01."},
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step5(self):
        """
        groups support
        """
        filename = "%s/wavedrom_step5.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "clk": {"wave": "p..Pp..P"},
            "Master": {
                "ctrl": {"write": {"wave": "01.0...."}, "read": {"wave": "0...1..0"}},
                "addr": {"wave": "x3.x4..x", "data": "A1 A2"},
                "wdata": {"wave": "x3.x....", "data": "D1"},
            },
            "spacer_1": {},
            "Slave": {
                "ctrl": {"ack": {"wave": "x01x0.1x"}},
                "rdata": {"wave": "x.....4x", "data": "Q2"},
            },
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step6(self):
        """
        phase and period
        """
        filename = "%s/wavedrom_step6.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "CK": {"wave": "P.......", "period": 2},
            "CMD": {
                "wave": "x.3x=x4x=x=x=x=x",
                "data": "RAS NOP CAS NOP NOP NOP NOP",
                "phase": 0.5,
            },
            "ADDR": {"wave": "x.=x..=x........", "data": "ROW COL", "phase": 0.5},
            "DQS": {"wave": "z.......0.1010z."},
            "DQ": {"wave": "z.........5555z.", "data": "D0 D1 D2 D3"},
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step7(self):
        """
        Arrows
        """
        filename = "%s/wavedrom_step7.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "A": {"wave": "01........0....", "node": ".a........j"},
            "B": {"wave": "0.1.......0.1..", "node": "..b.......i"},
            "C": {"wave": "0..1....0...1..", "node": "...c....h.."},
            "D": {"wave": "0...1..0.....1.", "node": "....d..g..."},
            "E": {"wave": "0....10.......1", "node": ".....ef...."},
            "F": {"wave": "0....10.......1", "node": ".....#..... ms_adc.isd.eoc"},
            "G": {"wave": "0......10.....1", "node": ".......#... interface.new_sample"},
            "edge": [
                "a~b t1",
                "c-~a t2",
                "c-~>d time 3",
                "d~-e",
                "e~>f",
                "f->g",
                "g-~>h",
                "h~>i some text",
                "h~->j",
                "ms_adc.isd.eoc~>interface.new_sample youpi",
            ],
            "adjustment": [{"edge": 10, "dx": -10, "dy": 0}],
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step8(self):
        """
        Sharp edge lines
        """
        filename = "%s/wavedrom_step8.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "A": {"wave": "01..0..", "node": ".a..e.."},
            "B": {"wave": "0.1..0.", "node": "..b..d.", "phase": 0.5},
            "C": {"wave": "0..1..0", "node": "...c..f"},
            " ": {"node": "...g..h"},
            "edge": [
                "b-|a t1",
                "a-|c t2",
                "b-|-c t3",
                "c-|->e t4",
                "e-|>f more text",
                "e|->d t6",
                "c-g",
                "f-h",
                "g<->h 3 ms",
            ],
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step9(self):
        """
        phase and period
        """
        filename = "%s/wavedrom_step9.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "CK": {"wave": "P.......", "period": 2},
            "CMD": {
                "wave": "x.3x=x4x",
                "repeat": 2,
                "data": "RAS NOP CAS NOP NOP NOP NOP",
                "phase": 0.5,
            },
            "ADDR": {"wave": "x.=x..=x", "repeat": 2, "data": "ROW COL", "phase": 0.5},
            "DQS": {"wave": "z......m0.1010z."},
            "DQS_1": {"wave": "z.....M.0.1010z."},
            "DQS_2": {"wave": "z....m..0.1010z."},
            "DQS_3": {"wave": "z...M...0.1010z."},
            "DQ": {"wave": "z.........5555z.", "data": "D0 D1 D2 D3"},
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_wavedrom_step10(self):
        """
        phase and period
        """
        filename = "%s/wavedrom_step10.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "CK": {"wave": "P.......", "repeat": 2},
            "GBF": {
                "wave": "a...",
                "repeat": 4,
                "analogue": [
                    "[(t, t*VDDA/Tmax) for t in time]",
                    "[(t, VDDA/2*cos(32*pi*t/Tmax)+VDDA/2) for t in time]",
                    "[(t, exp(-t/Tmax)*VDDA/2*cos(32*pi*t/Tmax)+VDDA/2) for t in time]",
                    "[(t, cos(4*pi*t/Tmax)*sin(16*pi*t/Tmax)*VDDA/2+VDDA/2) for t in time]",
                ],
            },
            "INT_S": {
                "wave": "ssss",
                "repeat": 4,
                "vscale": 2,
                "slewing": 12,
                "analogue": [0.4 * (i % 4) + 0.1 for i in range(16)],
            },
            "INT_C": {
                "wave": "cccc",
                "repeat": 4,
                "vscale": 2,
                "slewing": 12,
                "analogue": [0.4 * (3 - i % 4) + 0.1 for i in range(16)],
            },
            "trigger": {"wave": "0i1I0I1iI"},
            "pwm": {"wave": "p...n...P...N...", "duty_cycles": [i / 16 for i in range(16)]},
            "adaptive_clock": {
                "wave": "p...............",
                "periods": [i / 8 for i in range(16)],
            },
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_extra_mux_recirc(self):
        """
        real phase use case
        """
        filename = "%s/recirc_bus.%s" % (
            os.getenv("OUTPATH", "."),
            cli_args.format.replace("-", "."),
        )
        wavelanes = {
            "F1": {"wave": "P...........", "node": "........."},
            "F2": {"wave": "P...", "node": ".........", "period": 3, "phase": -0.1},
            "BUS": {"wave": "x.=.......x.", "data": "COFFEE"},
            "ENABLE": {"wave": "0111........", "node": ".a......."},
            "ENABLE_1": {"wave": "0..1........", "node": "...b.....", "phase": -0.3},
            "ENABLE_2": {"wave": "0.....1.....", "node": "......c..", "phase": -0.3},
            "BUS_2": {"wave": "0..=", "data": "COFFEE", "period": 3, "phase": -0.3},
            "edge": [],
        }
        RENDERER.draw(wavelanes, filename=filename)

    def test_from_to_parsing(self):
        """
        parsing of different possible from/to format
        """
        width, height = 100, 100
        bwidth, bheight = 40, 20
        NodeBank.nodes = {}
        Renderer.y_steps = []
        NodeBank.register("a_t", Point(bwidth * 2, bheight * 3 + 10.25))
        from_to = [
            "",
            "(1.0, 2.0)",
            (1.0, 2.0),
            1.0,
            "3.14",
            "10.5%",
            "(5%, 6.1%)",
            "a_t",
            "a_t  +(0.5, -0.15)",
            None,
        ]
        expected = [
            Point(0, 0),
            Point(bwidth, 2 * bheight),
            Point(bwidth, 2 * bheight),
            Point(bwidth, bheight),
            Point(3.14 * bwidth, 3.14 * bheight),
            Point(0.105 * width, 0.105 * height),
            Point(0.05 * width, 0.061 * height),
            Point(bwidth * 2, bheight * 3 + 10.25),
            Point(bwidth * 2.5, bheight * 2.85 + 10.25),
            Point(0, 0),
        ]
        for ft, e in zip(from_to, expected):
            p = RENDERER.from_to_parser(ft, width, height, bwidth, bheight)
            print(f"Parsing of {ft}")
            assert p.x == e.x, f"Wrong x position for {p!r} expected {e.x} for {ft!r}"
            assert p.y == e.y, f"Wrong y position for {p!r} expected {e.y} for {ft!r}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--format", help="export format", default="svg")
    parser.add_argument("unittest_args", nargs="*")
    cli_args = parser.parse_args()
    if cli_args.format == "svg":
        RENDERER = SvgRenderer()
    elif "cairo-" in cli_args.format:
        RENDERER = CairoRenderer(extension=cli_args.format.split("-")[-1])
    sys.argv[1:] = cli_args.unittest_args
    unittest.main(verbosity=2)
