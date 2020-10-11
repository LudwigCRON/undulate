#!/usr/bin/env python3
# coding: utf-8

import os
import unittest
import undulate.skin as us

UT_CSS_DIR = os.path.join(os.path.dirname(__file__), "./ut_css")


from pprint import pprint


class TestCss(unittest.TestCase):
    def test_loading(self):
        with open(f"{UT_CSS_DIR}/supported.css", "r+") as fp:
            css = us.css_parser(us.css_tokenizer(fp))
        pprint(css)

    def test_tokenizer(self):
        with open(f"{UT_CSS_DIR}/supported.css", "r+") as fp:
            for token in us.css_tokenizer(fp):
                print(token)

    def test_rules(self):
        pass

    def test_unsupported_properties(self):
        pass


if __name__ == "__main__":
    unittest.main()