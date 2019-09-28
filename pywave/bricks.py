#!/usr/bin/env python3
# spell-checker: disable

"""
bricks.py declare the basic building block
to generate a waveform
"""

import pywave
from enum import Enum, unique


@unique
class BRICKS(Enum):
    """
    BRICKS enumerate the different allowed block
    and symbol to describe a waveform
    """
    repeat = '.'
    nclk = "n"
    pclk = "p"
    Nclk = "N"
    Pclk = "P"
    low = "l"
    Low = "L"
    high = "h"
    High = "H"
    zero = "0"
    one = "1"
    gap = "|"
    highz = "z"
    x = "x"
    data = "="
    up = "u"
    down = "d"
    meta = "m"
    Meta = "M"
    ana = "a"
    step = "s"
    cap = "c"
    imp = "i"
    Imp = "I"
    field_start = "["
    field_end = "]"
    field_mid = ":"
    field_bit = "b"

    @staticmethod
    def transform_y(y: float, height: float = 20):
        """
        change y coordinate to represente voltage between VSSA and VDDA
        if current VSSA <-> ISSA / VDDA <-> IDDA
        """
        scaled_value = (y - pywave.CONTEXT["VSSA"]) / (
            pywave.CONTEXT["VDDA"] - pywave.CONTEXT["VSSA"]
        )
        return height - height * scaled_value

    @staticmethod
    def from_str(s: str):
        """
        from_str return the corresponding enumeration from a char
        """
        if s in "23456789":
            return BRICKS.data
        a = [b for b in BRICKS if b.value == s]
        return a[0] if a else None

    @staticmethod
    def ignore_transition(from_symb, to_symb):
        """
        define special case when transition are skipped to prevent
        glitches by default
        """
        if (from_symb, to_symb) in [
            (BRICKS.x, BRICKS.low),
            (BRICKS.x, BRICKS.zero),
            (BRICKS.x, BRICKS.high),
            (BRICKS.x, BRICKS.one),
            (BRICKS.data, BRICKS.zero),
            (BRICKS.data, BRICKS.one),
            (BRICKS.low, BRICKS.Low),
            (BRICKS.high, BRICKS.High),
            (BRICKS.Low, BRICKS.Low),
            (BRICKS.High, BRICKS.High)
        ]:
            return True
        return False
