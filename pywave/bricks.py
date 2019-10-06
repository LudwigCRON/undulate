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

    It defines the mapping between symbols and their
    character representation inside the input file
    """
    repeat = '.'#: repeat the previous character
    nclk = "n"  #: falling edge clock without arrow
    pclk = "p"  #: rising edge clock without arrow
    Nclk = "N"  #: falling edge clock with arrow
    Pclk = "P"  #: rising edge clock with arrow
    low = "l"   #: forced low value in sync with clock edge
    Low = "L"   #: forced low value in sync with clock edge and with arrow
    high = "h"  #: forced high value in sync with clock edge
    High = "H"  #: forced high value in sync with clock edge and arrow
    zero = "0"  #: data set to 0
    one = "1"   #: data set to 1
    gap = "|"   #: single line time compression
    highz = "z" #: high impedance signal
    x = "x"     #: unknown bit
    X = "X"     #: unknown data
    data = "="  #: data
    up = "u"    #: rc settling to 1
    down = "d"  #: rc settling to 0
    meta = "m"  #: metastable state settling to 0
    Meta = "M"  #: metastable state settling to 1
    ana = "a"   #: analogue signal based on equation
    step = "s"  #: analogue signal stepping
    cap = "c"   #: analogue signal charging (rc)
    imp = "i"   #: impulse down or glitch
    Imp = "I"   #: impulse up or glitch
    field_start = "[" #: new field internal representation of a register
    field_end = "]"   #: end of field internal representation
    field_mid = ":"   #: bit seperation
    field_bit = "b"   #: single bit field internal represention

    @staticmethod
    def transform_y(y: float, height: float = 20):
        """
        change y coordinate to represente voltage between VSSA and VDDA
        if current VSSA <-> ISSA / VDDA <-> IDDA

        Args:
            y: y-coordinate between VSSA and VDDA
            height: height of a brick in the wavelane
        Returns:
            the new y-coordinate between 0 and height
        """
        scaled_value = (y - pywave.CONTEXT["VSSA"]) / (
            pywave.CONTEXT["VDDA"] - pywave.CONTEXT["VSSA"]
        )
        return height - height * scaled_value

    @staticmethod
    def from_str(c: str):
        """
        Give the corresponding enumeration from a char
        Args:
            c: character representing the symbol
        Returns:
            the enumeration corresponding to c
            or None
        """
        if c in "23456789":
            return BRICKS.data
        a = [b for b in BRICKS if b.value == c]
        return a[0] if a else None

    @staticmethod
    def ignore_transition(from_symb, to_symb) -> bool:
        """
        define special case when transition are skipped to prevent
        glitches by default

        Args:
            from_symb (pywave.BRICKS): symbol from which start the transition
            to_symb (pywave.BRICKS): target symbol of the transition
        Returns:
            boolean result corresponding to the statement
            'transition should be skipped'
        """
        if (from_symb, to_symb) in [
            (BRICKS.x, BRICKS.low),
            (BRICKS.x, BRICKS.zero),
            (BRICKS.x, BRICKS.high),
            (BRICKS.x, BRICKS.one),
            (BRICKS.X, BRICKS.low),
            (BRICKS.X, BRICKS.zero),
            (BRICKS.X, BRICKS.high),
            (BRICKS.X, BRICKS.one),
            (BRICKS.data, BRICKS.zero),
            (BRICKS.data, BRICKS.one),
            (BRICKS.low, BRICKS.Low),
            (BRICKS.high, BRICKS.High),
            (BRICKS.Low, BRICKS.Low),
            (BRICKS.High, BRICKS.High),
            (BRICKS.one, BRICKS.Pclk),
            (BRICKS.zero, BRICKS.Nclk)
        ]:
            return True
        return False
