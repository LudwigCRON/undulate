#!/usr/bin/env python3
# coding: utf-8

import os
import unittest
import undulate.skin as us
import undulate.parsers.css as css

UT_CSS_DIR = os.path.join(os.path.dirname(__file__), "./ut_css")
DEFAULT_STYLE = {
    "root": {
        "padding-top": (1.0, css.SizeUnit.EM),
        "padding-bottom": (1.0, css.SizeUnit.EM),
    },
    "title": {
        "fill": (0, 65, 196, 255),
        "font-weight": 500,
        "font-size": (0.5, css.SizeUnit.EM),
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.RIGHT,
        "text-anchor": "end",
        "dominant-baseline": "middle",
        "alignment-baseline": "central",
    },
    "text": {
        "fill": (0, 0, 0, 255),
        "font-size": (0.9, css.SizeUnit.EM),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 500,
        "font-stretch": "normal",
        "text-align": css.TextAlign.CENTER,
        "font-family": "Fira Mono",
    },
    "attr": {
        "fill": (0, 0, 0, 255),
        "font-size": (9.0, css.SizeUnit.PX),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 200,
        "font-stretch": "normal",
        "text-align": css.TextAlign.CENTER,
        "font-family": "Fira Mono",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
        "alignment-baseline": "central",
    },
    "path": {
        "fill": None,
        "stroke": (0, 0, 0, 255),
        "stroke-width": 1,
        "stroke-linecap": css.LineCap.ROUND,
        "stroke-linejoin": css.LineJoin.MITER,
        "stroke-miterlimit": 4,
        "stroke-dasharray": None,
    },
    "stripe": {
        "fill": None,
        "stroke": (0, 0, 0, 255),
        "stroke-width": 0.5,
        "stroke-linecap": css.LineCap.ROUND,
        "stroke-linejoin": css.LineJoin.MITER,
        "stroke-miterlimit": 4,
        "stroke-dasharray": None,
    },
    "data": {
        "fill": (0, 0, 0, 255),
        "font-size": (0.4, css.SizeUnit.EM),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 500,
        "font-stretch": "normal",
        "text-align": css.TextAlign.CENTER,
        "font-family": "Fira Mono",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
        "alignment-baseline": "central",
    },
    "hatch": {"fill": (200, 200, 200, 255)},
    "s2-polygon": {"fill": (0, 0, 0, 0), "stroke": None},
    "s3-polygon": {"fill": (255, 255, 176, 255), "stroke": None},
    "s4-polygon": {"fill": (255, 224, 185, 255), "stroke": None},
    "s5-polygon": {"fill": (185, 224, 255, 255), "stroke": None},
    "s6-polygon": {"fill": (0, 53, 75, 200), "stroke": None},
    "s7-polygon": {"fill": (101, 187, 169, 200), "stroke": None},
    "s8-polygon": {"fill": (221, 65, 54, 200), "stroke": None},
    "s9-polygon": {"fill": (237, 165, 34, 200), "stroke": None},
    "tick": {
        "stroke": (136, 136, 136, 128),
        "stroke-width": 0.5,
        "stroke-dasharray": [1, 3],
    },
    "big_gap": {
        "stroke": (136, 136, 136, 255),
        "stroke-width": 0.5,
        "stroke-dasharray": None,
    },
    "border": {"stroke-width": 1.25, "stroke": (0, 0, 0, 255)},
    "hide": {
        "fill": (255, 255, 255, 255),
        "stroke": (255, 255, 255, 255),
        "stroke-width": 2,
    },
    "edge": {"fill": None, "stroke": (0, 0, 255, 255), "stroke-width": 1},
    "edge-arrow": {"fill": (0, 0, 255, 255), "stroke": None, "overflow": "visible"},
    "edge-text": {
        "font-family": "Fira Mono",
        "font-size": (0.625, css.SizeUnit.EM),
        "fill": (0, 0, 0, 255),
        "filter": "#solid",
        "transform": "translate(0, 2.5px)",
        "text-anchor": "middle",
    },
    "edge-background": {
        "fill": (255, 255, 255, 255),
        "stroke": (255, 255, 255, 255),
        "stroke-width": 2,
    },
    "arrow": {"fill": (0, 0, 0, 255), "stroke": None},
    "h1": {
        "fill": (0, 0, 0, 255),
        "font-size": (12.0, css.SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h2": {
        "fill": (0, 0, 0, 255),
        "font-size": (10.0, css.SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h3": {
        "fill": (0, 0, 0, 255),
        "font-size": (8.0, css.SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h4": {
        "fill": (0, 0, 0, 255),
        "font-size": (6.0, css.SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h5": {
        "fill": (0, 0, 0, 255),
        "font-size": (5.0, css.SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h6": {
        "fill": (0, 0, 0, 255),
        "font-size": (4.0, css.SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "Fira Mono",
        "text-align": css.TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "reg-data": {
        "fill": (0, 0, 0, 255),
        "font-size": (0.8, css.SizeUnit.EM),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 500,
        "font-stretch": "normal",
        "text-align": css.TextAlign.CENTER,
        "font-family": "Fira Mono",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
        "alignment-baseline": "central",
    },
    "reg-pos": {
        "fill": (0, 0, 0, 255),
        "font-size": (0.6, css.SizeUnit.EM),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 500,
        "font-stretch": "normal",
        "text-align": css.TextAlign.CENTER,
        "font-family": "Fira Mono",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
        "alignment-baseline": "central",
    },
}


from pprint import pprint


class TestCss(unittest.TestCase):
    def test_loading(self):
        with open("%s/supported.css" % UT_CSS_DIR, "r+") as fp:
            style = css.parser(css.tokenizer(fp))
        with open("%s/../../undulate/default.css" % UT_CSS_DIR, "r+") as fp:
            style = css.parser(css.tokenizer(fp))
        self.assertEqual(DEFAULT_STYLE, style)

    def test_rules(self):
        pass

    def test_unsupported_properties(self):
        pass


if __name__ == "__main__":
    unittest.main()
